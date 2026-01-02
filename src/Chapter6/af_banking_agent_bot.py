import asyncio, os
from collections.abc import AsyncIterable

from agent_framework import (
    HandoffBuilder,
    HandoffUserInputRequest,
    RequestInfoEvent,
    WorkflowEvent,
    ai_function, ToolMode,
    WorkflowViz,
)

from agent_framework.azure import AzureOpenAIChatClient
from dotenv import load_dotenv

load_dotenv()

# tools
@ai_function(name="investigate_card", description="Investigate a locked card for a customer.")
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

@ai_function(name="unlock_card", description="Unlock a locked card for a customer.")
def unlock_card(customer_id: str, cardno: str) -> str:
    """Unlock a locked card."""
    # Simulate unlocking a locked card
    print(f"Unlocking card for customer {customer_id} with card number {cardno}.")
    # Here you would implement the logic to unlock the card
    # simulating a successful unlock
    return f"Card {cardno} for customer {customer_id} has been unlocked successfully."

@ai_function(name="reset_pin", description="Reset the PIN for a customer's card after verifying identity.")
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
    
@ai_function(name="update_customer_address", description="Update the address for a customer.")    
def update_customer_address(customer_id: str, cardno: str, address: str) -> str:
    """Update the customer's address."""
    
    # Here you would implement the logic to update the address  
    # simulating a successful update
    print(f"Updating address for customer {customer_id} with card number {cardno}.")
    if address:
        return f"Address for customer {customer_id} with card number {cardno} has been updated to {address}."
    else:
        return f"Failed to update address for customer {customer_id} with card number {cardno}. Please provide a valid address."

def create_agents(chat_client: AzureOpenAIChatClient):
    """Create triage and specialist agents with multi-tier handoff capabilities.

    Returns:
        Tuple of (triage_agent, pin_agent, card_agent, address_update_agent)
    """
    triage = chat_client.create_agent(
        instructions=(
            "You are a customer support triage agent. Assess the user's issue and route appropriately:\n"
            "- For PIN reset issues: call handoff_to_pin_agent\n"
            "- For card issues and inquiries: call handoff_to_card_agent\n"
            "- For address updates issues: call handoff_to_address_update_agent\n"
            "Be concise and friendly."
        ),
        name="triage_agent",
    )
    
    pin_agent = chat_client.create_agent(
        instructions=(
            "You handle PIN reset requests. Ask for date of birth, and email to verify identity.\n"
            "Help the customer reset their PIN. Be concise and helpful."
        ),
        name="pin_agent",
        tools=[reset_pin],
        tool_choice=ToolMode.AUTO,
    )

    card_agent = chat_client.create_agent(
        instructions=(
            "You are a customer support agent that handles card requests. Help with locked cards, replacements, "
            "Ask for customer id and card number.\n"
            "When a locked card request comes, first investigate why the card was locked\n"
            "using the investigate_card tool, then unlock the card using the unlock_card tool.\n"
            "Be concise and clear."
        ),
        name="card_agent",
        tools=[investigate_card, unlock_card],
        tool_choice= ToolMode.AUTO,
    )

    address_update_agent = chat_client.create_agent(
        instructions=(
            "You handle address update requests. Ask for customer id, card number, and new address.\n"
            "Update the customer's address using the update_customer_address tool for KYC compliance "
            "Be concise and clear"
        ),
        name="billing_agent",
        tools=[update_customer_address],
        tool_choice=ToolMode.AUTO
    )

    return triage, pin_agent, card_agent, address_update_agent


async def _drain(stream: AsyncIterable[WorkflowEvent]) -> list[WorkflowEvent]:
    """Collect all events from an async stream into a list."""
    return [event async for event in stream]


def _handle_events(events: list[WorkflowEvent]) -> list[RequestInfoEvent]:
    """Process workflow events and extract pending user input requests."""
    requests: list[RequestInfoEvent] = []

    for event in events:
        if isinstance(event, RequestInfoEvent):
            if isinstance(event.data, HandoffUserInputRequest):
                _print_handoff_request(event.data)
            requests.append(event)

    return requests


def _print_handoff_request(request: HandoffUserInputRequest) -> None:
    """Display a user input request with conversation context."""
    # Filter out messages with no text for cleaner display
    messages_with_text = [msg for msg in request.conversation if msg.text.strip()]
    
    for message in messages_with_text[-1:]:  # Show last 5 for brevity
        speaker = message.author_name or message.role.value
        text = message.text
        print(f"  {speaker}: {text}")
    

async def main() -> None:    
    """Demonstrate multi-tier specialist-to-specialist handoff workflow."""
    chat_client = AzureOpenAIChatClient(
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment_name=os.environ["AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
    )
    
    triage, pin_agent, card_agent, address_update_agent = create_agents(chat_client)

    # Configure multi-tier handoffs using fluent add_handoff() API
    # This allows specialists to hand off to other specialists
    workflow = (
        HandoffBuilder(
            name="multi_tier_support",
            participants=[triage, pin_agent, card_agent, address_update_agent],
        )
        .set_coordinator(triage)
        .add_handoff(triage, [pin_agent, card_agent, address_update_agent])  # Triage can route to any specialist
        .add_handoff(card_agent, [pin_agent, address_update_agent])  # Replacement can delegate to delivery or billing
        .add_handoff(pin_agent, [card_agent, address_update_agent])  # Delivery can escalate to billing
        .add_handoff(address_update_agent, [pin_agent, card_agent])  # Billing can escalate to other specialists
        # Termination condition: Stop when more than 8 user messages exist.
        # This allows agents to respond to the 7th user message before the 8th triggers termination.
        .with_termination_condition(lambda conv: sum(1 for msg in conv if msg.role.value == "user") > 8)
        .build()
    )
    
    # 2.5) Generate workflow visualization
    print("Generating workflow visualization...")
    viz = WorkflowViz(workflow)
    # Print out the mermaid string.
    print("Mermaid string: \n=======")
    print(viz.to_mermaid())
    print("=======")

    # Start the workflow with the initial user message
    # run_stream() returns an async iterator of WorkflowEvent
    print("\n[Starting workflow with initial user message...]")
    events = await _drain(workflow.run_stream("Hello, I need some assistance, could you help me?"))
    pending_requests = _handle_events(events)

    print("Welcome to the Banking Support Bot!")
    
    # Process the request/response cycle
    # The workflow will continue requesting input until:
    # 1. The termination condition is met (8 user messages in this case), OR
    # 2. The users types 'exit' to quit
    while pending_requests:
        # Get the next scripted response
        user_response = input("\nUser: ")
        if user_response.lower() == 'exit':
            print("Goodbye!")
            break

        # Send response(s) to all pending requests
        # In this demo, there's typically one request per cycle, but the API supports multiple
        responses = {req.request_id: user_response for req in pending_requests}

        # Send responses and get new events
        events = await _drain(workflow.send_responses_streaming(responses))
        pending_requests = _handle_events(events)


if __name__ == "__main__":
    asyncio.run(main())