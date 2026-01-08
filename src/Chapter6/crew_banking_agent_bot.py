from crewai import Agent, Task, Crew, Process, LLM
from crewai.flow.flow import Flow, listen, router, start
from crewai.tools import tool
from pydantic import BaseModel
from enum import Enum


import dotenv
dotenv.load_dotenv()

llm = LLM(
    model="azure/gpt-4o-mini",
    api_version="2025-01-01-preview"
)

# define tools
@tool
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

@tool
def unlock_card(customer_id: str, cardno: str) -> str:
    """Unlock a locked card."""
    # Simulate unlocking a locked card
    print(f"Unlocking card for customer {customer_id} with card number {cardno}.")
    # Here you would implement the logic to unlock the card
    # simulating a successful unlock
    return f"Card {cardno} for customer {customer_id} has been unlocked successfully."

@tool
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
    

@tool
def update_customer_address(customer_id: str, cardno: str, address: str) -> str:
    """Update the customer's address."""
    
    # Here you would implement the logic to update the address  
    # simulating a successful update
    print(f"Updating address for customer {customer_id} with card number {cardno}.")
    if address:
        return f"Address for customer {customer_id} with card number {cardno} has been updated to {address}."
    else:
        return f"Failed to update address for customer {customer_id} with card number {cardno}. Please provide a valid address."
    

class BankingCrew:
    def __init__(self, conversation_history):
        self.conversation_history = conversation_history
    
    def create_card_unlock_agent_crew(self, input: dict) -> Crew:
        """Create a crew of banking agents to handle customer requests related to card unlocking."""

        # create indvidual agents with reasoning enabled

        agent_investigate_card = Agent(
            name="InvestigateCardAgent",
            description="Investigates locked cards to determine the reason for locking and initiates unlocking if necessary.",
            role="investigator",
            goal="Investigate locked cards and determine the reason for locking and initiate unlocking if necessary.",
            backstory=f"""You are a banking agent specialized in investigating locked cards. 
                You will determine the reason for locking and initiate unlocking if necessary. 
                Use the given input {input} to investigate the locked card.""",  
            llm=llm,
            allow_delegation=True,
            verbose=True,
        )
        
        # create tasks for each agent
        task_investigate_card = Task(
            name="InvestigateCardTask",
            description="Investigate a locked card and determine the reason for locking using tool investigate_card and unlock the card using tool unlock_card.",
            expected_output="Response from the investigation of the locked card.",
            agent=agent_investigate_card,
            tools=[investigate_card, unlock_card],
        ) 
        
        # create a crew and run the tasks
        crew = Crew(
            name="BankingAgentCrew",
            description="A crew of banking agents to handle customer requests.",
            agents=[agent_investigate_card],
            tasks=[task_investigate_card],

            process=Process.sequential,
            
        )

        return crew
    
    def create_pin_reset_agent_crew(self, input: dict) -> Crew:
        """Create a crew of banking agents to handle customer requests related to PIN reset."""

        # create indvidual agents with reasoning enabled
        agent_reset_pin = Agent(
            name="ResetPinAgent",
            description="Handles PIN reset requests by verifying customer identity and resetting the PIN.",
            role="pin_resetter",
            goal="Reset the customer's PIN after verifying their identity.",
            backstory=f"""You are a banking agent specialized in resetting customer PINs. 
                You will verify the customer's identity using the provided input {input} and reset the PIN if the verification is successful.""",  
            llm=llm,
            allow_delegation=True,
            #verbose=True,
        )
        
        # create tasks for each agent
        task_reset_pin = Task(
            name="ResetPinTask",
            description="Reset the customer's PIN using tool reset_pin.",
            expected_output="Response from the PIN reset operation.",
            agent=agent_reset_pin,
            tools=[reset_pin],
        ) 
        
        # create a crew and run the tasks
        crew = Crew(
            name="BankingPinResetCrew",
            description="A crew of banking agents to handle customer requests related to PIN reset.",
            agents=[agent_reset_pin],
            tasks=[task_reset_pin],

            process=Process.sequential,
            
        )

        return crew
    
    def create_address_change_agent_crew(self, input: dict) -> Crew:
        """Create a crew of banking agents to handle customer requests related to address change."""

        # create indvidual agents with reasoning enabled
        agent_address_change = Agent(
            name="AddressChangeAgent",
            description="Handles address change requests by updating the customer's address in the system.",
            role="address_changer",
            goal="Update the customer's address in the system.",
            backstory=f"""You are a banking agent specialized in changing customer addresses. 
                You will update the customer's address using the provided input {input}.""",  
            llm=llm,
            allow_delegation=True,
            #verbose=True,
        )
        
        # create tasks for each agent
        task_address_change = Task(
            name="AddressChangeTask",
            description="Update the customer's address using tool update_customer_address.",
            expected_output="Response from the address change operation.",
            agent=agent_address_change,
            tools=[update_customer_address],
        ) 
        
        # create a crew and run the tasks
        crew = Crew(
            name="BankingAddressChangeCrew",
            description="A crew of banking agents to handle customer requests related to address change.",
            agents=[agent_address_change],
            tasks=[task_address_change],

            process=Process.sequential,
            
        )

        return crew
    
# create an enum with the support topics PINReset, AddressChange, CardLocked
class SupportTopic(Enum):
    PINReset = "PINReset"
    AddressChange = "AddressChange"
    CardLocked = "CardLocked"

class SupportTopicChoice(BaseModel):
    topic: SupportTopic = SupportTopic.PINReset  # Default choice
    customerId: str = ""
    cardNo: str = ""
    email: str = ""
    dateOfBirth: str = ""
    address: str = ""

class RouterFlow(Flow[SupportTopicChoice]):

    @start()
    def start_method(self):
        """Start method to initialize the flow and gather user input."""
        
        print("Welcome to the Banking Support Bot!")
        choice = input("Please select a support topic (PINReset, AddressChange, CardLocked): ")
        print(f"User selected topic: {choice}")

        # if the chice is CardLocked, get customer ID and card number
        if choice == "CardLocked":
            print("You selected Card Locked. Please provide your customer ID and card number.")
            customerId = input("Please enter your customer ID: ")
            cardNo = input("Please enter your card number: ")
            self.state.customerId = customerId
            self.state.cardNo = cardNo
        elif choice == "AddressChange":
            # if the choice is AddressChange, get customer ID, card number and address
            print("You selected Address Change. Please provide your customer ID, card number and new address.")
            customerId = input("Please enter your customer ID: ")
            cardNo = input("Please enter your card number: ")
            address = input("Please enter your new address: ")
            self.state.customerId = customerId
            self.state.cardNo = cardNo
            self.state.address = address
        elif choice == "PINReset":
            # if the choice is PINReset, get customer ID, card number, date of birth and email
            print("You selected PIN Reset. Please provide your customer ID, card number, date of birth and email.")
            customerId = input("Please enter your customer ID: ")
            cardNo = input("Please enter your card number: ")
            dateOfBirth = input("Please enter your date of birth (YYYY-MM-DD): ")
            email = input("Please enter your email: ")
            self.state.customerId = customerId
            self.state.cardNo = cardNo
            self.state.dateOfBirth = dateOfBirth
            self.state.email = email
        else:
            print("Invalid choice. Please select a valid support topic.")
            raise ValueError("Invalid support topic selected.")
        
        self.state.topic = SupportTopic(choice) if choice in SupportTopic.__members__ else SupportTopic.PINReset
        print(f"Selected topic: {self.state.topic}")
        print(f"Customer ID: {self.state.customerId}, Card Number: {self.state.cardNo}")

    @router(start_method)
    def second_method(self):
        if self.state.topic == SupportTopic.PINReset:
            return "pin_reset"
        elif self.state.topic == SupportTopic.AddressChange:
            return "address_change"
        elif self.state.topic == SupportTopic.CardLocked:
            return "card_locked"
        else:
            return "unknown_topic"

    @listen("pin_reset")
    def handle_pin_reset(self):
        print("Handling PIN Reset request")
        crew_input = {
            "customer_id": self.state.customerId,
            "cardno": self.state.cardNo,
            "date_of_birth": self.state.dateOfBirth,
            "email": self.state.email
        }
        banking_crew = BankingCrew(conversation_history=[])
        crew = banking_crew.create_pin_reset_agent_crew(crew_input)
        print(f"Running crew for topic: {self.state.topic}")
        print(f"Customer ID: {self.state.customerId}, Card Number: {self.state.cardNo}, Date of Birth: {self.state.dateOfBirth}, Email: {self.state.email}")
        result = crew.kickoff(inputs=crew_input)
        print(result)

    @listen("address_change")
    def handle_address_change(self):
        print("Handling Address Change request")
        crew_input = {
            "customer_id": self.state.customerId,
            "cardno": self.state.cardNo,
            "address": self.state.address
        }
        banking_crew = BankingCrew(conversation_history=[])
        crew = banking_crew.create_address_change_agent_crew(crew_input)
        print(f"Running crew for topic: {self.state.topic}")
        print(f"Customer ID: {self.state.customerId}, Card Number: {self.state.cardNo}, Address: {self.state.address}")
        result = crew.kickoff(inputs=crew_input)
        print(result)

    @listen("card_locked")
    def handle_card_locked(self):
        print("Handling Card Locked request")
        
        crew_input = {
            "customer_id": self.state.customerId,
            "cardno": self.state.cardNo
        }
        banking_crew = BankingCrew(conversation_history=[])
        crew = banking_crew.create_card_unlock_agent_crew(crew_input)
        print(f"Running crew for topic: {self.state.topic}")
        print(f"Customer ID: {self.state.customerId}, Card Number: {self.state.cardNo}")
        result = crew.kickoff(inputs=crew_input)
        print(result)

flow = RouterFlow()
flow.plot("src/Chapter6/crew_banking_agent_bot_flow.html")
flow.kickoff()