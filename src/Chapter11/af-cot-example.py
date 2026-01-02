import asyncio
import json
import os
from datetime import datetime
from typing import Annotated

from dotenv import load_dotenv
from pydantic import Field
from azure.identity.aio import AzureCliCredential

from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient

load_dotenv()

# Define the function tool directly (no plugin class needed)
def reason_about_refund(
    request: Annotated[str, Field(description="Free-form description of the refund request, could include reason like 'item defective'")],
    order_date: Annotated[str, Field(description="Order date in YYYY-MM-DD format")],
    order_amount: Annotated[float, Field(description="Original order total amount")],
    requested_amount: Annotated[float, Field(description="Refund amount requested by customer")]
) -> dict:
    """
    Decide whether to approve a refund and how much store credit to give.
    Evaluates refund requests based on return policy window and validity checks.
    """
    return_policy_days = 30
    
    today = datetime.today().date()
    order_date_obj = datetime.strptime(order_date, "%Y-%m-%d").date()
    days_since_order = (today - order_date_obj).days

    reasoning_steps = []
    decision = ""

    # Step 1: Check return window
    if days_since_order <= return_policy_days:
        reasoning_steps.append(
            f"Step 1: Order placed {days_since_order} days ago, within {return_policy_days}-day return window ✔"
        )
        within_window = True
    else:
        reasoning_steps.append(
            f"Step 1: Order placed {days_since_order} days ago, beyond {return_policy_days}-day window ✖"
        )
        within_window = False

    # Step 2: Check refund amount validity
    if requested_amount <= order_amount:
        reasoning_steps.append("Step 2: Requested amount ≤ order amount ✔")
        valid_amount = True
    else:
        reasoning_steps.append("Step 2: Requested amount exceeds order amount ✖")
        valid_amount = False

    # Step 3: Decision logic
    if "defective" in request.lower() or "wrong item" in request.lower():
        reasoning_steps.append("Step 3: Item defective/wrong → always approve ✔")
        decision = f"APPROVE ${requested_amount:.2f} store credit"
    elif within_window and valid_amount:
        reasoning_steps.append("Step 3: Conditions satisfied → approve refund ✔")
        decision = f"APPROVE ${requested_amount:.2f} store credit"
    else:
        reasoning_steps.append("Step 3: Conditions not satisfied → deny refund ✖")
        decision = f"DENY refund (outside policy)"

    # Return structured response
    return {
        "reasoningSteps": reasoning_steps,
        "finalDecision": decision
    }


async def run_conversation(user_request: str, context_data: dict):
    """Run a single conversation with the agent."""
    load_dotenv()
    
    # Create the Azure OpenAI chat client
    async with AzureCliCredential() as credential:
        chat_client = AzureOpenAIChatClient(
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            credential=credential,
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        )
        
        # Create the agent with the tool
        # The agent is created with instructions and tools
        agent = ChatAgent(
            chat_client=chat_client,
            name="RefundDecisionAgent",
            instructions="You decide refunds. Provide step-by-step reasoning. "
                        "When a customer requests a refund, use the reason_about_refund tool "
                        "to evaluate the request based on the order details provided.",
            tools=[reason_about_refund]  # Pass the function directly
        )
        
        # Create a thread to maintain conversation state
        thread = agent.get_new_thread()
        
        # Construct the user message with context
        user_message = (
            f"{user_request}\n"
            f"Order Date: {context_data['order_date']}\n"
            f"Order Amount: ${context_data['order_amount']}\n"
            f"Requested Amount: ${context_data['requested_amount']}"
        )
        
        # Run the agent (non-streaming)
        response = await agent.run(user_message, thread=thread)
        
        # The agent automatically calls the tool and provides reasoning
        # Extract the response text
        print("\n" + "="*80)
        print("AGENT RESPONSE:")
        print("="*80)
        print(response.text)
        print("="*80 + "\n")
        
        # Build JSON log for audit trail
        log_entry = {
            "input": context_data,
            "user_request": user_request,
            "agent_response": response.text,
            "timestamp": datetime.now().isoformat()
        }
        
        # Optional: Pretty print the log
        print("LOG ENTRY:")
        print(json.dumps(log_entry, indent=2))
        
        return response


async def main():
    """Run multiple test cases."""
    # Example usage - positive case (within window)
    print("\n" + "="*80)
    print("TEST CASE 1: Recent order within return window")
    print("="*80)
    user_request = "Customer 123 requests $50 refund for order #789."
    context_data = {
        "customerId": 123,
        "orderId": 789,
        "order_date": "2025-11-06",  # Recent date
        "request": user_request,
        "order_amount": 50.0,
        "requested_amount": 50.0
    }
    await run_conversation(user_request, context_data)
    
    print("\n\n")
    
    # Example usage - negative case (outside window)
    print("="*80)
    print("TEST CASE 2: Old order outside return window")
    print("="*80)
    user_request = "Customer 121 requests $50 refund for order #678."
    context_data = {
        "customerId": 121,
        "orderId": 678,
        "order_date": "2024-07-01",  # Old date
        "request": user_request,
        "order_amount": 50.0,
        "requested_amount": 50.0
    }
    await run_conversation(user_request, context_data)


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())