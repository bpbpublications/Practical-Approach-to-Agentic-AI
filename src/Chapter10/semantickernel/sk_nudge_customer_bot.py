# Semantic Kernel agent with MCP stdio plugin integration

import asyncio
import os
import sys
import pathlib
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from semantic_kernel.contents import ChatHistory
from semantic_kernel.contents.streaming_chat_message_content import StreamingChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.functions import KernelArguments
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

import chainlit as cl
from tnt_mart_plugins import TnTMartPlugin

async def main():
    # Load environment variables from .env file
    current_dir = pathlib.Path(__file__).parent
    env_path = current_dir / ".env"
    load_dotenv(dotenv_path=env_path)
    
    # Find the correct path to the MCP server script
    mcp_server_path = current_dir / "mcp_server.py"
    
    # Make sure the server script exists
    if not mcp_server_path.exists():
        print(f"Error: MCP server script not found at {mcp_server_path}")
        print(f"Make sure {mcp_server_path} is in the same directory as this script.")
        sys.exit(1)
    
    print("TnTMart welcomes you to the customer assistant. " \
    "This message is to remind you about some regular items you have purchased in the past."
    "Would you like me to continue?")
    
    # Initialize the kernel
    kernel = Kernel()
    
    # Add an OpenAI service with function calling enabled
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key:
        print("Error: AZURE_OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or environment variables.")
        sys.exit(1)
    
    service_id = "pgsql_mcp_demo_service"
    service = AzureChatCompletion(service_id=service_id, 
                                        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                        deployment_name=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
                                        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                                        )

    kernel.add_service(service)
    kernel.add_plugin(TnTMartPlugin(), plugin_name="tnt_mart_manager")

    
    # Create the completion service request settings
    settings = OpenAIChatPromptExecutionSettings()
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
    
    # Configure and use the MCP plugin for our calculator using async context manager
    async with MCPStdioPlugin(
        name="PGSQLMCPServer", 
        command="python",
        args=[str(mcp_server_path)]  # Use absolute path to our MCP server script
    ) as mcp_plugin:
        # Register the MCP plugin with the kernel
        try:
            kernel.add_plugin(mcp_plugin, plugin_name="regular_items_nudge")
        except Exception as e:
            print(f"Error: Could not register the MCP plugin: {str(e)}")
            sys.exit(1)
        
        # Create a chat history with system instructions
        history = ChatHistory()
        history.add_system_message(
            """
                Customer Engagement and Sales Nudge

                Your goal is to act as a helpful assistant for TnTMart and encourage customer Vikas Gautam (customer ID: 1) to purchase items that he frequently buys. You'll use the regular_items_nudge plugin to access customer and product data, and a separate plugin "tnt_mart_manager" to manage their shopping cart, and personalize the conversation. Make sure the SQL commands are syntactically correct and follow best practices so that there are no ambiguous columns in your query. DO NOT Parameterize querues. Ensure that you handle any potential errors gracefully and provide informative feedback to the user. Ensure that you follow the important guidelines laid out below. Do not add items already in the cart.

                Handle empty response: If the customer's response is empty or just a new line - ask if they need any help.

                Data Model: Use the following database tables for your operations:
                - The customer_regular_items table contains `item_id`, `customer_id`, `product_id`, and `quantity`.
                - The product table contains `product_id`, `product_code`, `product_category`, `description`, and `price`.
                - The shopping_cart table contains `customer_id`, `product_id`, `quantity`, and `unit_price`.

                Here is a breakdown of the specific actions you need to take:

                - Initial Engagement: Begin by warmly greeting Vikas by name and asking if he would like to see the items he regularly purchases.
                - Fetching Regular Items: If Vikas expresses interest, retrieve his regular items from the customer_regular_items.
                - Presenting Items: Clearly present the list of regular items to Vikas, including details such as product name, quantity, and price. Make sure to format the information in an easy-to-read manner and include product descriptions where possible.
                - Encouraging Purchase: Politely nudge Vikas towards making a purchase by highlighting the convenience and benefits of buying his regular items.
                - Calculating Total: If Vikas asks for the total cost, calculate the sum of the prices of all the suggested items.
                - Adding to Cart: If Vikas agrees to buy, use the regular_items_nudge plugin first check 
                    - if the same items are already present. 
                    - Only if they are not, add the items to his shopping_cart. 
                    - You MUST ENSURE that only the products in the customer_regular_items for this customer are added in the shopping_cart. DO NOT add random products to the cart.
                    - You will need to execute an SQL `INSERT` statement. Ensure you include the correct `customer_id`, `product_id`, `quantity`, and `unit_price` for each item. 
                    - After adding the items, you must inform the customer that they have been placed in his cart.
                - Avoid Duplicates: YOU MUST make sure that the items get added only once to the shopping cart. 
                    - Query the shopping cart before adding items. Use customer_id and product_id combination to verify if an item is already in the cart.
                    - If any of the items is already present, ask the customer if they would like to update the quantity for those items.
                    - Only if the customer agrees, update the quantity using the tnt_mart_manager plugin. You must fetch and pass the correct customer_id, product_id from the shopping_cart table to the tnt_mart_manager plugin. Note that the customer may provides description of the product and not the product_id or the product_code when asking a particular item to be updated. Write your SQL queries accordingly.
                    - Only add items that are not already present and provide a summary of what was added to the cart, what was already there and have been updated.
                - Personalization: Throughout the conversation, use the customer's name to create a more personalized experience.
                - Handling Rejection: If the customer declines the offer, politely end the conversation.

                IMPORTANT GUIDELINES:
                 - Always be polite and professional.
                 - Use the plugin regular_items_nudge for fetching information from the database and tnt_mart_manager for all cart update operations.
                 - Ensure that any SQL commands you execute are done through the appropriate plugin.
                 - Keep the customer apprised of actions you are taking, especially when adding items to the cart. Every action should be communicated clearly.

            """
        )
        
        # Define a simple chat function
        chat_function = kernel.add_function(
            plugin_name="chat",
            function_name="respond", 
            prompt="{{$chat_history}}"
        )
        
        print(". ┌──────────────────────────────────────────────┐ .")
        print(". │    Customer Regular Items Nudge Assistant    │ .")
        print(". └──────────────────────────────────────────────┘ .")
        print("Type 'exit' to end the conversation.")
        
        
        while True:
            user_input = input("\nUser:> ")
            if user_input.lower() == "exit":
                break
                
            # Add the user message to history
            history.add_user_message(user_input)
            
            # Prepare arguments with history and settings
            arguments = KernelArguments(
                chat_history=history,
                settings=settings
            )
            
            try:
                # Stream the response
                print("Assistant:> ", end="", flush=True)
                
                response_chunks = []
                async for message in kernel.invoke_stream(
                    chat_function,
                    arguments=arguments
                ):
                    chunk = message[0]
                    if isinstance(chunk, StreamingChatMessageContent) and chunk.role == AuthorRole.ASSISTANT:
                        print(str(chunk), end="", flush=True)
                        response_chunks.append(chunk)
                
                print()  # New line after response
                
                # Add the full response to history
                full_response = "".join(str(chunk) for chunk in response_chunks)
                history.add_assistant_message(full_response)
                
            except Exception as e:
                print(f"\nError: {str(e)}")
                print("Please try another question.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting the Customer Regular Items Nudge Assistant. Goodbye!")
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("The application has encountered a problem and needs to close.") 