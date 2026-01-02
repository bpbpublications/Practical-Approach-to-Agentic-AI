from pydantic import BaseModel, Field, ValidationError
import json

# 1. Define Data Schemas
class OrderDetails(BaseModel):
    order_id: str = Field(pattern=r"^ORD-\d{6}$")
    customer_email: str = Field(..., description="Email of the customer.")
    total_amount: float = Field(ge=0.0)
    items: list[str] = Field(min_length=1)

class AgentAction(BaseModel):
    action_type: str = Field(description="Type of action to perform (e.g., 'process_order', 'send_email').")
    payload: dict = Field(description="Data payload for the action.")

# Simulate an LLM generating a response
def mock_llm_response(prompt: str) -> str:
    if "order 123456" in prompt:
        return '{"order_id": "ORD-123456", "customer_email": "test@example.com", "total_amount": 99.99, "items": ["Laptop", "Mouse"]}'
    elif "invalid order" in prompt:
        return '{"order_id": "INVALID-ID", "customer_email": "bad-email", "total_amount": -10.0}'
    else:
        return '{"action_type": "unknown", "payload": {}}'

# Agent's processing logic
def process_order_request(user_input: str) -> dict:
    # 2. Input Validation (Implicit here, assuming mock_llm_response handles initial parsing)

    # Agent's Reasoning/Tool Use - LLM attempts to generate structured output
    print(f"LLM processing: '{user_input}'")
    llm_raw_output = mock_llm_response(user_input)

    try:
        # 2. Integrate Validation - Parsing LLM output to Pydantic model
        order_details = OrderDetails.model_validate_json(llm_raw_output)
        print(f"Successfully parsed order: {order_details.model_dump_json(indent=2)}")

        # Agent decides on an action based on parsed data
        action = AgentAction(
            action_type="process_order",
            payload=order_details.model_dump() # Payload is the validated order details
        )
        return {"status": "success", "action": action.model_dump()}

    except ValidationError as e:
        print(f"LLM output validation failed: {e.json()}")
        # 3. Error Handling - Returning structured error response
        return {"status": "failed", "error": "Invalid LLM output, unable to parse order details."}
    except json.JSONDecodeError:
        print(f"LLM output is not valid JSON: {llm_raw_output}")
        return {"status": "failed", "error": "LLM output is not valid JSON."}

# --- Simulate agent interactions ---
print("\n--- Valid Order Scenario ---")
result_valid = process_order_request("I want to place order 123456 for a Laptop and Mouse.")
print(f"Agent Result: {json.dumps(result_valid, indent=2)}")

print("\n--- Invalid Order Scenario ---")
result_invalid = process_order_request("Please process an invalid order for me.")
print(f"Agent Result: {json.dumps(result_invalid, indent=2)}")