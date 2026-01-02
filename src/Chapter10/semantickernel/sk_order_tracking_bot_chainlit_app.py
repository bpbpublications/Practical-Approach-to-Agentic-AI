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
from semantic_kernel.functions import kernel_function

import chainlit as cl
from tnt_mart_plugins import TnTMartPlugin


# Load environment variables from .env file
current_dir = pathlib.Path(__file__).parent
env_path = current_dir / ".env"
load_dotenv(dotenv_path=env_path)

# Find the correct path to the MCP server script
mcp_server_path = current_dir / "mcp_server.py"

@cl.on_chat_start
async def start_chat():
    # Make sure the server script exists
    if not mcp_server_path.exists():
        await cl.Message(content=f"Error: MCP server script not found at {mcp_server_path}").send()
        return

    # Initialize the kernel
    kernel = Kernel()

    # Add an OpenAI service with function calling enabled
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key:
        await cl.Message(content="Error: AZURE_OPENAI_API_KEY environment variable is not set.").send()
        return

    service_id = "pgsql_mcp_demo_service"
    service = AzureChatCompletion(
        service_id=service_id,
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        deployment_name=os.getenv("AZURE_OPENAI_CHAT_COMPLETION_MODEL"),
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )

    kernel.add_service(service)
    kernel.add_plugin(TnTMartPlugin(), plugin_name="getETA")
    

    # Configure and use the MCP plugin for our calculator
    mcp_plugin = MCPStdioPlugin(
        name="PGSQLMCPServer",
        command="python",
        args=[str(mcp_server_path)]  # Use absolute path to our MCP server script
    )
    
    # It's important to start the plugin process
    await mcp_plugin.__aenter__()

    # Register the MCP plugin with the kernel
    try:
        kernel.add_plugin(mcp_plugin, plugin_name="order_tracking_plugin")
    except Exception as e:
        await cl.Message(content=f"Error: Could not register the MCP plugin: {str(e)}").send()
        return
    
    

    history = ChatHistory()
    history.add_system_message(

            """
                ### Order Tracking Assistant

                You are a proactive and hlpful assistant for TnTMart. 
                Your goal is to act as a helpful assistant for **TnTMart** and encourage customer **Shweta Kamath ** (customer ID: **4**) to track her order. 
                You'll use the **order_tracker** plugin to access customer and product data, manage their shopping cart, and personalize the conversation.
                You must use the Schema Definitions section below to understand the structure of the database tables.
                Here is a breakdown of the specific actions you need to take, DO NOT MISS ANY STEP and DO NOT DEVIATE FROM THE STEPS at any cost:

                * **Initial Engagement**: Begin by warmly greeting Shweta by name and asking if he would like to track her order.
                * **Get order Details**: 
                    * Retrieve the orders from the orders table where status is "Dispatched" or "Ready to dispatch".
                    * Summarize the order details based on the information present in the orders table including order id, order date, total amount, status and expected delivery date.
                    * Ask if she would like to know more details of any specific order?
                * Next, you need to provide details of orders which the customer is interested in. For each order:
                    * Check if the status is either "Dispatched" or "Ready to dispatch".
                        * if the order is "Dispatched", do the following:
                            * Retrieve the order items details from the order_item table based on the order id.
                            * For each product id, check the warehouse_product table to find which warehouse has the product in stock.
                            * For each warehouse that has the product, get the warehouse details from the warehouse table.
                            * Next, get the address of the customer from the address table. The user_id in address table is same as customer_id in customer table.
                            * And, get the address of the warehouse from warehouse table.
                            * By comparing the two locations, determine whether the warehouse is in the same state as the customer.
                            * If the warehouse is in the same state as the customer, pass the value "Local" to the getETA function of LocationPlugin.
                            * If the warehouse is not in the same state as the customer , pass the value "Non-Local" to the getETA function of LocationPlugin.
                            * Use the response from the **getETA** function from the **LocationPlugin** to provide an estimated ETA for the order.
                            * DO NOT MISS to provide all the details to the customer at the end of this step.

                        * if the order is "Ready to dispatch", do the following:
                            * Retrieve the order items details from the order_item table based on the order id.
                            * For each product id, check the warehouse_product table to find which warehouse has the product in stock.
                            * For each warehouse that has the product, get the warehouse details from the warehouse table.
                            * Next, get the address of the customer from the address table. The user_id in address table is same as customer_id in customer table.
                            * And, get the address of the warehouse from warehouse table.
                            * By comparing the two locations, determine whether the warehouse is in the same state as the customer.
                            * If the warehouse is in the same state as the customer:
                                * pass the value "Local" to the getETA function of LocationPlugin.
                            * If the warehouse is not in the same state as the customer , 
                                * pass the value "Non-Local" to the getETA function of LocationPlugin.
                                * Inform the customer that since the product is not available in the same state as hers, we might need to source it from a different state.
                                * Inform the customer that this might lead to a difference in payment and she will need to pay the difference if the amount is more.
                                * If the customer agrees to pay the difference, insert a new record in the payment table where the amount is the difference between the original amount and the new amount.
                                * Also, update the order_item table to reflect the new product_id, quantity and amount for the specific order.
                                * Once the database updates are done, confirm to the custoer that the order has been updated and provide the new ETA by passing the value "Local" to the getETA function of LocationPlugin.
                            * DO NOT MISS to provide all the details to the customer once all the above is done and you have the information.

        
                * **Proactive Assistance**: After providing the order details, ask if there is anything else you can assist with, such as tracking another order or answering questions about products.
                * **Polite Closure**: If the customer indicates they do not need further assistance, politely close the conversation by thanking them for choosing TnTMart and inviting them to return if they need help in the
                    
                
                * **Schema Definitions** Here is the schema of all the tables you have access to. Use this to formulate your queries and use the **order_tracker** plugin to fetch this information.
                    * The **customer** table contains `customer_id`, `name`, `email`,'phone','type','last_active' and `credits_available`.
                    * The **orders** table contains `order_id`, `order_date`, `customer_id`, `total_amount`,'status','expected_delivery_date','actual_delivery_date' and `delay_handling_preference`.
                    * The **order_item** table contains `order_item_id`, `order_id`, `product_id`, `quantity`,'amount' and `status`.
                    * The **warehouse_product** table contains `warehouse_id`, `product_id` and `product_quantity`.
                    * The **warehouse** table contains `warehouse_id`, `warehouse_code`, `address`, `latitude` , 'longitude' and `active`.
                    * The **address** table contains `address_id`, `user_id`, `address_line_1`, `address_line_2`, `city`, `state`, `postal_cd`,`country`, `latitude`, `longitude` and `landmark`.
                    * The **payment** table contains `payment_id`, `order_id`, `payment_time`, `amount`, `payment_mode`, `status` and `transaction_id`.
                    * The **product** table contains `product_id`, `product_code`, `product_category`, `price`, `description`, `active` and `regularly_purchased`.
            """
        )
    cl.user_session.set("kernel", kernel)
    cl.user_session.set("history", history)
    cl.user_session.set("mcp_plugin", mcp_plugin)

    await cl.Message(content="TnTMart welcomes you to the customer assistant. This message is to track your orders. Would you like me to continue?").send()    

@cl.on_message
async def on_message(message: cl.Message):
    kernel = cl.user_session.get("kernel")
    history = cl.user_session.get("history")

    # Add the user message to history
    history.add_user_message(message.content)

    # Create the completion service request settings
    settings = OpenAIChatPromptExecutionSettings(function_choice_behavior=FunctionChoiceBehavior.Auto())

    # Prepare arguments with history and settings
    arguments = KernelArguments(
        settings=settings,
        chat_history=history,
    )

    # Define a simple chat function
    chat_function = kernel.add_function(
        plugin_name="chat",
        function_name="respond",
        prompt="{{$chat_history}}"
    )

    try:
        # Stream the response
        response_msg = cl.Message(content="")
        await response_msg.send()
        
        response_chunks = []
        async for message_chunk in kernel.invoke_stream(chat_function, arguments=arguments):
            chunk = message_chunk[0]
            if isinstance(chunk, StreamingChatMessageContent) and chunk.role == AuthorRole.ASSISTANT:
                content = str(chunk)
                await response_msg.stream_token(content)
                response_chunks.append(chunk)
        
        await response_msg.update()

        # Add the full response to history
        full_response = "".join(str(chunk) for chunk in response_chunks)
        history.add_assistant_message(full_response)

    except Exception as e:
        await cl.Message(content=f"Error: {str(e)}").send()
