from __future__ import annotations as _annotations

import asyncio, os
from pydantic import BaseModel

from agents import (
    Agent,
    HandoffOutputItem,
    ItemHelpers,
    MessageOutputItem,
    Runner,
    ToolCallItem,
    ToolCallOutputItem,
    TResponseInputItem,
    function_tool,
    OpenAIChatCompletionsModel,
    set_default_openai_api
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

load_dotenv()

azure_client = AsyncAzureOpenAI(
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

#set_default_openai_client(azure_client, use_for_tracing=False)
set_default_openai_api("chat_completions")

### CONTEXT
class BankingAgentContext(BaseModel):
    customer_id: str | None = None
    cardno: str | None = None
    date_of_birth: str | None = None
    email: str | None = None
    address: str | None = None

### TOOLS

@function_tool(name_override="investigate_card", description_override="Investigate a locked card for a customer.")
async def investigate_card(customer_id: str, cardno: str) -> str:
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

@function_tool(name_override="unlock_card", description_override="Unlock a locked card for a customer.")
async def unlock_card(customer_id: str, cardno: str) -> str:
    """Unlock a locked card."""
    # Simulate unlocking a locked card
    print(f"Unlocking card for customer {customer_id} with card number {cardno}.")
    # Here you would implement the logic to unlock the card
    # simulating a successful unlock
    return f"Card {cardno} for customer {customer_id} has been unlocked successfully."

@function_tool(name_override="reset_pin", description_override="Reset the PIN for a customer's card after verifying identity.")
async def reset_pin(customer_id: str, cardno: str, date_of_birth: str, email: str) -> str:
    """Help the customer reset their PIN. Ask for date of birth, and email to verify identity."""
    # Simulate reseting a PIN
    print(f"Resetting PIN for customer {customer_id} with card number {cardno}.")
    # Here you would implement the logic to reset the PIN
    # simulating a successful reset
    if date_of_birth and email:
        return f"PIN for card {cardno} has been reset successfully for customer {customer_id}. A confirmation email has been sent to {email}."
    else:
        return f"Failed to reset PIN for card {cardno} for customer {customer_id}. Please provide valid date of birth and email."
    
@function_tool(name_override="update_customer_address", description_override="Update the address for a customer.")    
async def update_customer_address(customer_id: str, cardno: str, address: str) -> str:
    """Update the customer's address."""
    
    # Here you would implement the logic to update the address  
    # simulating a successful update
    print(f"Updating address for customer {customer_id} with card number {cardno}.")
    if address:
        return f"Address for customer {customer_id} with card number {cardno} has been updated to {address}."
    else:
        return f"Failed to update address for customer {customer_id} with card number {cardno}. Please provide a valid address."


### AGENTS

pin_agent = Agent[BankingAgentContext](
    name="PIN Agent",
    handoff_description="A helpful agent that helps customers with PIN related issues.",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a helpful customer support agent. If you are speaking to a customer, you probably were transferred to from the triage agent.
    First greet the customer and ask how you can assist them.
    Use the following routine to support the customer.
    # Routine
    1. If the customer needs to reset their PIN, use the reset_pin tool after verifying their identity.
    2. After resetting the PIN, inform the customer of the successful reset.
    3. If you cannot answer the question, transfer back to the triage agent.""",
    tools=[reset_pin],
    model=OpenAIChatCompletionsModel(
        model=os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME'),
        openai_client=azure_client,
    ),
)

card_agent = Agent[BankingAgentContext](
    name="Card Agent",
    handoff_description="A helpful agent that helps customers with card related issues.",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a helpful customer support agent. If you are speaking to a customer, you probably were transferred to from the triage agent.
    First greet the customer and ask how you can assist them.
    Use the following routine to support the customer.
    # Routine
    1. If the customer has a locked card, use the investigate_card tool to find the reason.
    2. If the card can be unlocked, use the unlock_card tool to unlock it.
    3. Inform the customer of the actions taken.
    4. If you cannot answer the question, transfer back to the triage agent.""",
    tools=[investigate_card, unlock_card],
    model=OpenAIChatCompletionsModel(
        model=os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME'),
        openai_client=azure_client,
    ),
)

address_update_agent = Agent[BankingAgentContext](
    name="Address Update Agent",
    handoff_description="A helpful agent that helps customers update their address.",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a helpful customer support agent. If you are speaking to a customer, you probably were transferred to from the triage agent.
    First greet the customer and ask how you can assist them.
    Use the following routine to support the customer.
    # Routine
    1. If the customer wants to update their address, use the update_customer_address tool.
    2. Inform the customer of the successful update.
    3. If you cannot answer the question, transfer back to the triage agent.""",
    tools=[update_customer_address],
    model=OpenAIChatCompletionsModel(
        model=os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME'),
        openai_client=azure_client,
    ),
)  
triage_agent = Agent[BankingAgentContext](
    name="Triage Agent",
    handoff_description="A helpful agent that triages customer issues to specialized agents.",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a helpful customer support agent. Your job is to understand the customer's issue and transfer them to the appropriate specialized agent.
    # Routine
    1. If the customer has a PIN related issue, transfer them to the PIN Agent.
    2. If the customer has a card related issue, transfer them to the Card Agent.
    3. If the customer wants to update their address, transfer them to the Address Update Agent.
    4. If you cannot determine the issue, ask the customer for more information.""",
    handoffs=[
        pin_agent,
        card_agent,
        address_update_agent,
    ],
)

pin_agent.handoffs.append(triage_agent)
card_agent.handoffs.append(triage_agent)
address_update_agent.handoffs.append(triage_agent)

### RUN

async def main():
    current_agent: Agent[BankingAgentContext] = triage_agent
    input_items: list[TResponseInputItem] = []
    context = BankingAgentContext()

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        else:
            input_items.append({"content": user_input, "role": "user"})
            result = await Runner.run(current_agent, input_items, context=context)

            for new_item in result.new_items:
                agent_name = new_item.agent.name
                if isinstance(new_item, MessageOutputItem):
                    print(f"{agent_name}: {ItemHelpers.text_message_output(new_item)}")
                elif isinstance(new_item, HandoffOutputItem):
                    print(
                        f"Handed off from {new_item.source_agent.name} to {new_item.target_agent.name}"
                    )
                elif isinstance(new_item, ToolCallItem):
                    print(f"{agent_name}: Calling a tool")
                elif isinstance(new_item, ToolCallOutputItem):
                    print(f"{agent_name}: Tool call output: {new_item.output}")
                else:
                    print(f"{agent_name}: Skipping item: {new_item.__class__.__name__}")
            input_items = result.to_input_list()
            current_agent = result.last_agent

if __name__ == "__main__":
    asyncio.run(main())