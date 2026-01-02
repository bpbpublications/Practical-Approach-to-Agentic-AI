#from langgraph_supervisor import create_supervisor
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver 
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm
import os

load_dotenv()

# Initialize Azure OpenAI model
llm = AzureChatOpenAI(
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment=os.getenv("MODEL_DEPLOYMENT_NAME"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

# tool to handle card unlocking requests
def unlock_cards(customer_id: str, cardno: str):
    """Specialist Agent that unlocks cards for users

    Handles requests to unlock cards for a specific customer. 

    Args:
        customer_id (str): The ID of the customer whose card needs to be unlocked
        cardno (str): The card number to be unlocked

    Returns:
        str: Confirmation message indicating the card has been unlocked
    """
    
    # Simulate unlocking the card

    return f"Card {cardno} for customer {customer_id} has been successfully unlocked."

# tool to determine why the card got locked
def reason_card_unlock(customer_id: str, cardno: str):
    """Reasoning Agent that determines why the card got locked

    Checks why the card was locked and if it can be unlocked.

    Args:
        customer_id (str): The ID of the customer whose card needs to be checked
        cardno (str): The card number to be checked

    Returns:
        str: a reason why the card got locked
    """
    
    # Simulate reasoning logic
    # Simulate investigating a locked card
    print(f"Investigating locked card for customer {customer_id} with card number {cardno}.")
    # Here you would implement the logic to investigate the  card
    # simulating a successful investigation
    multiple_incorrent_login_attempts = True  # Simulate condition
    check_dormant_account = False  # Simulate condition
    check_withdrawal_history = False  # Simulate condition
    check_payment_dues = False  # Simulate condition

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


# tool to reset the PIN
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
    

# tool to update the customer's address
def update_customer_address(customer_id: str, cardno: str, address: str) -> str:
    """Update the customer's address."""
    
    # Here you would implement the logic to update the address  
    # simulating a successful update
    print(f"Updating address for customer {customer_id} with card number {cardno}.")
    if address:
        return f"Address for customer {customer_id} with card number {cardno} has been updated to {address}."
    else:
        return f"Failed to update address for customer {customer_id} with card number {cardno}. Please provide a valid address."
    


# Create the agents with their respective tools and prompts

# creare the card unlock agent
card_unlock_agent = create_react_agent(
    model=llm,
    tools=[reason_card_unlock, unlock_cards, create_handoff_tool(agent_name="pin_reset_agent"), create_handoff_tool(agent_name="kyc_agent")],
    name="card_unlock_agent",
    prompt=(
        "You are a card lock troubleshooting agent who helps find the reason card was locked and then unlock it."
        "For any requests related to PIN reset, you MUST use the handoff tool to transfer the request to pin_reset_agent. "
        "For any requests related to address change, you MUST use the handoff tool to transfer the request to kyc_agent. "
        "Only help unlock the cards yourself."
    )
)

# create the pin reset agent
pin_reset_agent = create_react_agent(
    model=llm,
    tools=[reset_pin, create_handoff_tool(agent_name="card_unlock_agent"), create_handoff_tool(agent_name="kyc_agent")],
    prompt=(
        "You are a PIN reset agent who helps customers reset their PINs. "
        "If the request is related to locked card, use the handoff tool to transfer it to card_unlock_agent. "
        "For any requests related to address change, you MUST use the handoff tool to transfer the request to kyc_agent."
    ),
    name="pin_reset_agent"
)

#create the KYC agent
kyc_agent = create_react_agent(
    model=llm,
    tools=[update_customer_address, create_handoff_tool(agent_name="card_unlock_agent"), create_handoff_tool(agent_name="pin_reset_agent")],
    prompt=(
        "You are a KYC agent. Your primary task is to help customers keep their information up-to-date:\n"
        "1. When user asks for help with address update, ask them for the new address\n"
        "2. When user provides text the new address (e.g., 'update my address to 123 Main St'), update immediately\n"
        "3. When user provides only customer ID and card number, ask for the new address\n"
        "4. For requests related to PIN reset, transfer to pin_reset_agent\n"
        "5. If the request is related to locked card, use the handoff tool to transfer it to card_unlock_agent.\n"
        
    ),
    name="kyc_agent"
)

# Initialize the supervisor and application
checkpoint = InMemorySaver()
supervisor = create_swarm(
    agents=[card_unlock_agent, pin_reset_agent, kyc_agent],
    default_active_agent="card_unlock_agent",
)
app = supervisor.compile(checkpointer=checkpoint)

# Save the workflow diagram
image = app.get_graph().draw_mermaid_png()
with open("swarm.png", "wb") as f:
    f.write(image)

# Configuration for the conversation thread
config = {"configurable": {"thread_id": "1"}}

# Main interaction loop
print("Welcome to the Banking Support Bot!")
while True:
    user_input = input("\nPlease tell me your request (or 'exit' to quit): ")

    if user_input.lower() == 'exit':
        print("Goodbye!")
        break

    result = app.invoke(
        {"messages": [{
            "role": "user",
            "content": user_input
        }]},
        config,
    )

    # Display the response
    for m in result["messages"]:
        print(m.pretty_print())
