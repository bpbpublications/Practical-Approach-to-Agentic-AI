import asyncio

from semantic_kernel.agents import Agent, ChatCompletionAgent, HandoffOrchestration, OrchestrationHandoffs
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import AuthorRole, ChatMessageContent, FunctionCallContent, FunctionResultContent
from semantic_kernel.functions import kernel_function

import dotenv, os
dotenv.load_dotenv()

"""
The following sample demonstrates how to create a handoff orchestration that represents
a customer support triage system for a Bank. The orchestration consists of 4 agents, each specialized
in a different area of customer support: triage, card issues, PIN changes, and KYC updates.

Depending on the customer's request, agents can hand off the conversation to the appropriate
agent.

Human in the loop is achieved via a callback function. Note that in the handoff orchestration, all agents have access to the
human response function.

This sample demonstrates the basic steps of creating and starting a runtime, creating
a handoff orchestration, invoking the orchestration, and finally waiting for the results.
"""

class CardPlugin:
    @kernel_function
    def investigate_card(self, customer_id: str, cardno: str) -> str:
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
    
    @kernel_function
    def unlock_card(self, customer_id: str, cardno: str) -> str:
        """Unlock a locked card."""
        # Simulate unlocking a locked card
        print(f"Unlocking card for customer {customer_id} with card number {cardno}.")
        # Here you would implement the logic to unlock the card
        # simulating a successful unlock
        return f"Card {cardno} for customer {customer_id} has been unlocked successfully."

class PINManagementPlugin:
    @kernel_function
    def reset_pin(self, customer_id: str, cardno: str, date_of_birth: str, email: str) -> str:
        """Help the customer reset their PIN. Ask for date of birth, and email to verify identity."""
        # Simulate reseting a PIN
        print(f"Resetting PIN for customer {customer_id} with card number {cardno}.")
        # Here you would implement the logic to reset the PIN
        # simulating a successful reset
        if date_of_birth and email:
            return f"PIN for card {cardno} has been reset successfully for customer {customer_id}. A confirmation email has been sent to {email}."
        else:
            return f"Failed to reset PIN for card {cardno} for customer {customer_id}. Please provide valid date of birth and email."
        
class UpdateAddressPlugin:
    @kernel_function
    def update_customer_address(self, customer_id: str, cardno: str, address: str) -> str:
        """Update the customer's address."""
        
        # Here you would implement the logic to update the address  
        # simulating a successful update
        print(f"Updating address for customer {customer_id} with card number {cardno}.")
        if address:
            return f"Address for customer {customer_id} with card number {cardno} has been updated to {address}."
        else:
            return f"Failed to update address for customer {customer_id} with card number {cardno}. Please provide a valid address."
        
    
def get_agents() -> tuple[list[Agent], OrchestrationHandoffs]:
    """Return a list of agents that will participate in the Handoff orchestration and the handoff relationships.

    Feel free to add or remove agents and handoff connections.
    """
    support_agent = ChatCompletionAgent(
        name="TriageAgent",
        description="A customer support agent that triages issues.",
        instructions="Handle customer requests.",
        service=AzureChatCompletion(service_id="support_agent", 
                                        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                        deployment_name=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
                                        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                                        ),
    )

    pin_agent = ChatCompletionAgent(
        name="PINManagementAgent",
        description="A customer support agent that handles PIN reset requests.",
        instructions="Handle PIN reset requests.",
        service=AzureChatCompletion(service_id="pin_agent", 
                                        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                        deployment_name=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
                                        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                                        ),
        plugins=[PINManagementPlugin()],
    )

    card_agent = ChatCompletionAgent(
        name="CardAgent",
        description="A customer support agent that handles card requests.",
        instructions="Handle card requests.",   

        service=AzureChatCompletion(service_id="card_agent", 
                                        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                        deployment_name=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
                                        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                                        ),
        plugins=[CardPlugin()],
    )

    address_update_agent = ChatCompletionAgent(
        name="AddressUpdateAgent",
        description="A customer support agent that handles address update requests.",
        instructions="Handle address update requests.",
        service=AzureChatCompletion(service_id="address_update_agent", 
                                        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                        deployment_name=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
                                        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                                        ),
        plugins=[UpdateAddressPlugin()],
    )

    # Define the handoff relationships between agents
    handoffs = (
        OrchestrationHandoffs()
        .add_many(
            source_agent=support_agent.name,
            target_agents={
                pin_agent.name: "Transfer to this agent if the issue is PIN related",
                card_agent.name: "Transfer to this agent if the issue is card related",
                address_update_agent.name: "Transfer to this agent if the issue is address update related",
            },
        )
        .add(
            source_agent=pin_agent.name,
            target_agent=support_agent.name,
            description="Transfer to this agent if the issue is not PIN related",
        )
        .add(
            source_agent=card_agent.name,
            target_agent=support_agent.name,
            description="Transfer to this agent if the issue is not card related",
        )
        .add(
            source_agent=address_update_agent.name,
            target_agent=support_agent.name,
            description="Transfer to this agent if the issue is not address update related",
        )
    )

    return [support_agent, pin_agent, card_agent, address_update_agent], handoffs


def agent_response_callback(message: ChatMessageContent) -> None:
    """Observer function to print the messages from the agents.

    Please note that this function is called whenever the agent generates a response,
    including the internal processing messages (such as tool calls) that are not visible
    to other agents in the orchestration.
    """
    print(f"{message.name}: {message.content}")
    for item in message.items:
        if isinstance(item, FunctionCallContent):
            print(f"Calling '{item.name}' with arguments '{item.arguments}'")
        if isinstance(item, FunctionResultContent):
            print(f"Result from '{item.name}' is '{item.result}'")


def human_response_function() -> ChatMessageContent:
    """Observer function to print the messages from the agents."""
    user_input = input("User: ")
    return ChatMessageContent(role=AuthorRole.USER, content=user_input)


async def main():
    """Main function to run the agents."""
    # 1. Create a handoff orchestration with multiple agents
    agents, handoffs = get_agents()
    handoff_orchestration = HandoffOrchestration(
        members=agents,
        handoffs=handoffs,
        agent_response_callback=agent_response_callback,
        human_response_function=human_response_function,
    )

    # 2. Create a runtime and start it
    runtime = InProcessRuntime()
    runtime.start()

    # 3. Invoke the orchestration with a task and the runtime
    orchestration_result = await handoff_orchestration.invoke(
        task="Greet the customer who is reaching out for support.",
        runtime=runtime,
    )

    # 4. Wait for the results
    value = await orchestration_result.get()
    print(value)

    # 5. Stop the runtime after the invocation is complete
    await runtime.stop_when_idle()

if __name__ == "__main__":
    asyncio.run(main())