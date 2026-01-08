import uuid, asyncio, os, json
from typing import List, Tuple

from autogen_core import (
    FunctionCall,
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    TopicId,
    TypeSubscription,
    message_handler,
)
from autogen_core.models import (
    AssistantMessage,
    ChatCompletionClient,
    FunctionExecutionResult,
    FunctionExecutionResultMessage,
    LLMMessage,
    SystemMessage,
    UserMessage,
)
from autogen_core.tools import FunctionTool, Tool
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()

class UserLogin(BaseModel):
    pass

class UserTask(BaseModel):
    context: List[LLMMessage]

class AgentResponse(BaseModel):
    reply_to_topic_type: str
    context: List[LLMMessage]

class AIAgent(RoutedAgent):
    def __init__(
        self,
        description: str,
        system_message: SystemMessage,
        model_client: ChatCompletionClient,
        tools: List[Tool],
        delegate_tools: List[Tool],
        agent_topic_type: str,
        user_topic_type: str,
    ) -> None:
        super().__init__(description)
        self._system_message = system_message
        self._model_client = model_client
        self._tools = dict([(tool.name, tool) for tool in tools])
        self._tool_schema = [tool.schema for tool in tools]
        self._delegate_tools = dict([(tool.name, tool) for tool in delegate_tools])
        self._delegate_tool_schema = [tool.schema for tool in delegate_tools]
        self._agent_topic_type = agent_topic_type
        self._user_topic_type = user_topic_type

    @message_handler
    async def handle_task(self, message: UserTask, ctx: MessageContext) -> None:
        # Send the task to the LLM.
        llm_result = await self._model_client.create(
            messages=[self._system_message] + message.context,
            tools=self._tool_schema + self._delegate_tool_schema,
            cancellation_token=ctx.cancellation_token,
        )
        print(f"{'-'*80}\n{self.id.type}:\n{llm_result.content}", flush=True)
        # Process the LLM result.
        while isinstance(llm_result.content, list) and all(isinstance(m, FunctionCall) for m in llm_result.content):
            tool_call_results: List[FunctionExecutionResult] = []
            delegate_targets: List[Tuple[str, UserTask]] = []
            # Process each function call.
            for call in llm_result.content:
                arguments = json.loads(call.arguments)
                if call.name in self._tools:
                    # Execute the tool directly.
                    result = await self._tools[call.name].run_json(arguments, ctx.cancellation_token)
                    result_as_str = self._tools[call.name].return_value_as_string(result)
                    tool_call_results.append(
                        FunctionExecutionResult(call_id=call.id, content=result_as_str, is_error=False, name=call.name)
                    )
                elif call.name in self._delegate_tools:
                    # Execute the tool to get the delegate agent's topic type.
                    result = await self._delegate_tools[call.name].run_json(arguments, ctx.cancellation_token)
                    topic_type = self._delegate_tools[call.name].return_value_as_string(result)
                    # Create the context for the delegate agent, including the function call and the result.
                    delegate_messages = list(message.context) + [
                        AssistantMessage(content=[call], source=self.id.type),
                        FunctionExecutionResultMessage(
                            content=[
                                FunctionExecutionResult(
                                    call_id=call.id,
                                    content=f"Transferred to {topic_type}. Adopt persona immediately.",
                                    is_error=False,
                                    name=call.name,
                                )
                            ]
                        ),
                    ]
                    delegate_targets.append((topic_type, UserTask(context=delegate_messages)))
                else:
                    raise ValueError(f"Unknown tool: {call.name}")
            if len(delegate_targets) > 0:
                # Delegate the task to other agents by publishing messages to the corresponding topics.
                for topic_type, task in delegate_targets:
                    print(f"{'-'*80}\n{self.id.type}:\nDelegating to {topic_type}", flush=True)
                    await self.publish_message(task, topic_id=TopicId(topic_type, source=self.id.key))
            if len(tool_call_results) > 0:
                print(f"{'-'*80}\n{self.id.type}:\n{tool_call_results}", flush=True)
                # Make another LLM call with the results.
                message.context.extend(
                    [
                        AssistantMessage(content=llm_result.content, source=self.id.type),
                        FunctionExecutionResultMessage(content=tool_call_results),
                    ]
                )
                llm_result = await self._model_client.create(
                    messages=[self._system_message] + message.context,
                    tools=self._tool_schema + self._delegate_tool_schema,
                    cancellation_token=ctx.cancellation_token,
                )
                print(f"{'-'*80}\n{self.id.type}:\n{llm_result.content}", flush=True)
            else:
                # The task has been delegated, so we are done.
                return
        # The task has been completed, publish the final result.
        assert isinstance(llm_result.content, str)
        message.context.append(AssistantMessage(content=llm_result.content, source=self.id.type))
        await self.publish_message(
            AgentResponse(context=message.context, reply_to_topic_type=self._agent_topic_type),
            topic_id=TopicId(self._user_topic_type, source=self.id.key),
        )

class HumanAgent(RoutedAgent):
    def __init__(self, description: str, agent_topic_type: str, user_topic_type: str) -> None:
        super().__init__(description)
        self._agent_topic_type = agent_topic_type
        self._user_topic_type = user_topic_type

    @message_handler
    async def handle_user_task(self, message: UserTask, ctx: MessageContext) -> None:
        human_input = input("Human agent input: ")
        print(f"{'-'*80}\n{self.id.type}:\n{human_input}", flush=True)
        message.context.append(AssistantMessage(content=human_input, source=self.id.type))
        await self.publish_message(
            AgentResponse(context=message.context, reply_to_topic_type=self._agent_topic_type),
            topic_id=TopicId(self._user_topic_type, source=self.id.key),
        )

class UserAgent(RoutedAgent):
    def __init__(self, description: str, user_topic_type: str, agent_topic_type: str) -> None:
        super().__init__(description)
        self._user_topic_type = user_topic_type
        self._agent_topic_type = agent_topic_type

    @message_handler
    async def handle_user_login(self, message: UserLogin, ctx: MessageContext) -> None:
        print(f"{'-'*80}\nUser login, session ID: {self.id.key}.", flush=True)
        # Get the user's initial input after login.
        user_input = input("User: ")
        print(f"{'-'*80}\n{self.id.type}:\n{user_input}")
        await self.publish_message(
            UserTask(context=[UserMessage(content=user_input, source="User")]),
            topic_id=TopicId(self._agent_topic_type, source=self.id.key),
        )

    @message_handler
    async def handle_task_result(self, message: AgentResponse, ctx: MessageContext) -> None:
        # Get the user's input after receiving a response from an agent.
        user_input = input("User (type 'exit' to close the session): ")
        print(f"{'-'*80}\n{self.id.type}:\n{user_input}", flush=True)
        if user_input.strip().lower() == "exit":
            print(f"{'-'*80}\nUser session ended, session ID: {self.id.key}.")
            return
        message.context.append(UserMessage(content=user_input, source="User"))
        await self.publish_message(
            UserTask(context=message.context), topic_id=TopicId(message.reply_to_topic_type, source=self.id.key)
        )

def investigate_card(customer_id: str, cardno: str) -> str:
        """Investigate a locked card."""
        # Simulate investigating a locked card
        print(f"Investigating locked card for customer {customer_id} with card number {cardno}.")
        # Here you would implement the logic to investigate the  card
        # simulating a successful investigation
        multiple_incorrent_login_attempts = False  # Simulate condition
        check_dormant_account = False  # Simulate condition
        check_withdrawal_history = False  # Simulate condition
        check_payment_dues = True  # Simulate condition

        if multiple_incorrent_login_attempts:
            return f"Card {cardno} is locked for customer {customer_id} due to multiple incorrect login attempts."
        elif check_dormant_account:
            return f"Card {cardno} is locked for customer {customer_id} was due to inactivity"
        elif check_withdrawal_history:
            return f"Card {cardno} is locked for customer {customer_id} due to suspicious withdrawal history"
        elif check_payment_dues:
            return f"Card {cardno} is locked for customer {customer_id} due to payment dues."
        else: 
            return f"Card {cardno} is locked for customer {customer_id} due to unknown reasons. Please contact your brcanch for further assistance."

def unlock_card(customer_id: str, cardno: str) -> str:
        """Unlock a locked card."""
        # Simulate unlocking a locked card
        print(f"Unlocking card for customer {customer_id} with card number {cardno}.")
        # Here you would implement the logic to unlock the card
        # simulating a successful unlock
        return f"Card {cardno} for customer {customer_id} has been unlocked successfully."

def reset_pin(customer_id: str, cardno: str, date_of_birth: str, email: str) -> str:
        """Help the customer reset their PIN. Ask for date of birth, and email to verify identity."""
        # Simulate reseting a PIN
        print(f"Resetting PIN for customer {customer_id} with card number {cardno}.")
        # Here you would implement the logic to reset the PIN
        # simulating a successful reset
        if date_of_birth and email:
            return f"PIN for card {cardno} has been reset successfully for customer {customer_id}. A confirmation email has been sent to {email}."
        else:
            return f"Failed to reset PIN for card {cardno} for customer {customer_id}. Please provide valid date of birth and email."

def update_customer_address(customer_id: str, cardno: str, address: str) -> str:
        """Update the customer's address."""
        
        # Here you would implement the logic to update the address  
        # simulating a successful update
        print(f"Updating address for customer {customer_id} with card number {cardno}.")
        if address:
            return f"Address for customer {customer_id} with card number {cardno} has been updated to {address}."
        else:
            return f"Failed to update address for customer {customer_id} with card number {cardno}. Please provide a valid address."
        

investigate_card_tool = FunctionTool(
    investigate_card, 
    description="This tool checks why the card was locked and returns a reason why it was locked."
    )

unlock_card_tool = FunctionTool(unlock_card, description="This tool unlocks a locked card for the customer.")
reset_pin_tool = FunctionTool(
    reset_pin, description="This tool helps the customer reset their PIN. It requires date of birth and email to verify identity."
)
update_customer_address_tool = FunctionTool(
    update_customer_address, description="This tool updates the customer's address."
)


unlock_card_agent_topic_type = "UnlockCardAgent"
pin_reset_agent_topic_type = "PINResetAgent"
kyc_agent_topic_type = "KYCAgent"
triage_agent_topic_type = "TriageAgent"
human_agent_topic_type = "HumanAgent"
user_topic_type = "User"

def transfer_to_card_unloack_agent() -> str:
    return unlock_card_agent_topic_type


def transfer_to_pin_reset_agent() -> str:
    return pin_reset_agent_topic_type

def transfer_to_kyc_agent() -> str:
    return kyc_agent_topic_type


def transfer_back_to_triage() -> str:
    return triage_agent_topic_type


def escalate_to_human() -> str:
    return human_agent_topic_type


transfer_to_card_unlock_tool = FunctionTool(
    transfer_to_card_unloack_agent, description="Use for anything related to card unlocking or investigation."
)

transfer_to_pin_reset_tool = FunctionTool(
    transfer_to_pin_reset_agent, description="Use for pin reset requests"
)

transfer_to_kyc_tool = FunctionTool(
    transfer_to_kyc_agent, description="Use for any requests related to address change."
)

transfer_back_to_triage_tool = FunctionTool(
    transfer_back_to_triage,
    description="Call this if the user brings up a topic outside of your purview,\nincluding escalating to human.",
)

escalate_to_human_tool = FunctionTool(escalate_to_human, description="Only call this if explicitly asked to.")

runtime = SingleThreadedAgentRuntime()

model_client = AzureOpenAIChatCompletionClient(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    model=os.getenv("MODEL_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

async def main():

    # Register the triage agent.
    triage_agent_type = await AIAgent.register(
        runtime,
        type=triage_agent_topic_type,  # Using the topic type as the agent type.
        factory=lambda: AIAgent(
            description="A triage agent.",
            system_message=SystemMessage(
                content="You are a customer service bot for TNT Bank. "
                "Introduce yourself. Always be very brief. "
                "Gather information to direct the customer to the right agent. "
                "But make your questions subtle and natural."
                "if the user asks for a card unlock, transfer to the card unlock agent.\n"
                "if the user asks for a pin reset, transfer to the pin reset agent.\n"
                "if the user asks for an address change, transfer to the KYC agent.\n"
                "if the user asks for anything else, transfer to the human agent.\n"
            ),
            model_client=model_client,
            tools=[],
            delegate_tools=[
                transfer_to_card_unlock_tool,
                transfer_to_kyc_tool,
                transfer_to_pin_reset_tool,
                escalate_to_human_tool,
            ],
            agent_topic_type=triage_agent_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    # Add subscriptions for the triage agent: it will receive messages published to its own topic only.
    await runtime.add_subscription(TypeSubscription(topic_type=triage_agent_topic_type, agent_type=triage_agent_type.type))

    # Register the card unlock agent.
    unlock_card_type = await AIAgent.register(
        runtime,
        type=unlock_card_agent_topic_type,  # Using the topic type as the agent type.
        factory=lambda: AIAgent(
            description="A card unlock agent.",
            system_message=SystemMessage(
                content="You are a card unlock agent for TNT Bank. Your primary task is to help customers investigate why their card is locked and then unlock it.\n"
                "Always ask them for their customer ID and card number.\n"
                "find out the reason why the card was locked and then unlock it.\n"
                "If the user asks for anything other than locked card, transfer back to triage agent"
                ""
            ),
            model_client=model_client,
            tools=[unlock_card_tool, investigate_card_tool],
            delegate_tools=[transfer_back_to_triage_tool],
            agent_topic_type=unlock_card_agent_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    # Add subscriptions for the card unlock agent: it will receive messages published to its own topic only.
    await runtime.add_subscription(TypeSubscription(topic_type=unlock_card_agent_topic_type, agent_type=unlock_card_type.type))

    # Register the pin reset agent.
    pin_reset_agent_type = await AIAgent.register(
        runtime,
        type=pin_reset_agent_topic_type,  # Using the topic type as the agent type.
        factory=lambda: AIAgent(
            description="A PIN reset agent.",
            system_message=SystemMessage(
                content="You are a customer support agent for TNT bank."
                "Always ask the user for their customer ID and card number, date of birth and email.\n and then help them reset their PIN.\n"
                "if the user does not provide date of birth and email, ask them to provide it.\n"
                "5. If the user asks anything not related to PIN reset, transfer back to triage agent."
            ),
            model_client=model_client,
            tools=[reset_pin_tool],
            delegate_tools=[transfer_back_to_triage_tool],
            agent_topic_type=pin_reset_agent_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    # Add subscriptions for the pin reset agent: it will receive messages published to its own topic only.
    await runtime.add_subscription(
        TypeSubscription(topic_type=pin_reset_agent_topic_type, agent_type=pin_reset_agent_type.type)
    )

    kyc_agent_type = await AIAgent.register(
        runtime,
        type=kyc_agent_topic_type,  # Using the topic type as the agent type.
        factory=lambda: AIAgent(
            description="A KYC agent. You help customers keep their information up-to-date.",
            system_message=SystemMessage(
                content="You are a customer support agent for TNT bank."
                "Always ask the user for their customer ID and card number, and the new address.\n and then help them update their address\n"
                "if the user does not provide required infromation, ask them to provide it.\n"
                "5. If the user asks anything not related address update, transfer back to triage agent."
            ),
            model_client=model_client,
            tools=[update_customer_address_tool],
            delegate_tools=[transfer_back_to_triage_tool],
            agent_topic_type=kyc_agent_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    # Add subscriptions for the kyc update agent: it will receive messages published to its own topic only.
    await runtime.add_subscription(
        TypeSubscription(topic_type=kyc_agent_topic_type, agent_type=kyc_agent_type.type)
    )

    # Register the human agent.
    human_agent_type = await HumanAgent.register(
        runtime,
        type=human_agent_topic_type,  # Using the topic type as the agent type.
        factory=lambda: HumanAgent(
            description="A human agent.",
            agent_topic_type=human_agent_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    # Add subscriptions for the human agent: it will receive messages published to its own topic only.
    await runtime.add_subscription(TypeSubscription(topic_type=human_agent_topic_type, agent_type=human_agent_type.type))

    # Register the user agent.
    user_agent_type = await UserAgent.register(
        runtime,
        type=user_topic_type,
        factory=lambda: UserAgent(
            description="A user agent.",
            user_topic_type=user_topic_type,
            agent_topic_type=triage_agent_topic_type,  # Start with the triage agent.
        ),
    )
    # Add subscriptions for the user agent: it will receive messages published to its own topic only.
    await runtime.add_subscription(TypeSubscription(topic_type=user_topic_type, agent_type=user_agent_type.type))

    # Start the runtime.
    runtime.start()

    # Create a new session for the user.
    session_id = str(uuid.uuid4())
    await runtime.publish_message(UserLogin(), topic_id=TopicId(user_topic_type, source=session_id))

    # Run until completion.
    await runtime.stop_when_idle()
    await model_client.close()

# Run the async main function
asyncio.run(main())