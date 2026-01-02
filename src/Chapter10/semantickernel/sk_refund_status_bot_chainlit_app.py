#!/usr/bin/env python3
# Semantic Kernel agent with MCP stdio plugin integration

import os
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
    kernel.add_plugin(TnTMartPlugin(), plugin_name="tnt_mart_manager")

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
        kernel.add_plugin(mcp_plugin, plugin_name="refund_status_plugin")
    except Exception as e:
        await cl.Message(content=f"Error: Could not register the MCP plugin: {str(e)}").send()
        return

    # Create a chat history with system instructions
    history = ChatHistory()
    history.add_system_message(
        """
            Customer Engagement and Sales Nudge

                Your goal is to act as a helpful assistant for TnTMart and help the customer Vikas Gautam (customer ID: 1) with refund related queries.Do not entertain any other queries. 
                You'll use the refund_status_plugin plugin to access customer, order, order_item, product and refund data, and a separate plugin "tnt_mart_manager" to create and approve refunds, and personalize the conversation. 
                Make sure the SQL commands are syntactically correct and follow best practices so that there are no ambiguous columns in your query. 
                DO NOT Parameterize querues. Ensure that you handle any potential errors gracefully and provide informative feedback to the user. 
                Ensure that you follow the important guidelines laid out below. Carefully Approve or Reject refunds based on the conditions mentioned below.

                Handle empty response: If the customer's response is empty or just a new line - ask if they need any help.

                Data Model: Use the following database tables for your operations:
                - orders table contains `order_id`, `order_date`, `customer_id`, `total_amount`,`,`order_date`, `status`, `expected_delivery_date`, and `actual_delivery_date`.
                - customer table contains `customer_id`, `name`, `email`, `phone`, and `type`.
                - refund table contains `refund_id`, `payment_id`, `order_id`, `reason`,`refund_time`,  and `status`.
                - order_item table contains `order_item_id`, `order_id`, `product_id`, `quantity`, `status` and `amount`.
                - The product table contains `product_id`, `product_code`, `product_category`, `description`, and `price`.
                Important: Always use the refund_status_plugin for fetching information from the database and tnt_mart_manager for all refund related update/delete/insert operations.

                Here is a breakdown of the specific actions you need to take:

                - Initial Engagement: Begin by warmly greeting Vikas by name and asking how can you assist him? Entertain only refund related queries.
                - You MUST ask for the below details if not provided by the customer - keep asking untul you get all the details:
                    - Customer ID: Confirm the customer ID to ensure you are accessing the correct records.
                    - Order ID: Request the order ID associated with the refund request.
                    - Amount: Ask for the refund amount if not specified.
                    - Reason: Inquire about the reason for the refund.
                - Fetching Refund Status: Use the refund_status_plugin to retrieve the refund record and check the status of the refund request based on the provided order ID from the refund table.
                - Providing Updates: Clearly communicate the status of the refund to the customer, including any relevant details such as processing times or next steps.
                     - Pending: Inform Vikas that the refund is being processed and provide standard timeline (3 working days).
                     - Approved: Let the customer know that the refund has been approved and will be credited to his original payment method within 3 working days.
                     - Rejected: Explain the reason for the rejection and offer assistance with any further questions or actions he may need to take.
                     - awaiting_customer_response: Inform the customer that the refund is on hold pending additional information from him. Specify that a picture of the damaged product is needed to proceed.
                - If the refund status is Pending, perform the following:
                    - Check the reason for the refund provided by the customer from the conversation.
                    - If the reason is "delay", verify in the delivery status in the order table. 
                        - Important: In case of delay, You MUST Approve the refund only if (all conditions below are true): 
                            - The refund reason provided by the customer matches the reason in the refund table.
                            - The order status is "delivered" and the actual_delivery_date is after the expected_delivery_date.
                            - The refund amount provided by the customer matches the order amount.
                    - If the reason is "damaged product", ask the customer to provided a picture of the damaged product.
                        - Important: In case of damaged product, You MUST Approve the refund only if (all conditions below are true):
                            - The refund reason provided by the customer matches the reason in the refund table.
                            - The customer has provided a picture of the damaged product.
                            - The refund amount provided by the customer matches the order amount.
                    
                - Rejecting Refunds: The refund needs to be rejected for the following reasons (you MUST evaluate all conditions below and if any one of them is true, reject the refund):
                    - If the reason provided by the customer is not same as the reason in the refund table.
                    - If the order status is "delivered" and the actual_delivery_date is same day or before the expected_delivery_date.
                    - If the order status is "cancelled" 
                    - If the reason provided by the customer is "damaged product" and the customer has not provided a picture of the damaged product.
                    - if the refund amount provided by the customer and the order amount do not match.
                - Reject the refund by updating the refund status to "Rejected" in the refund table using the tnt_mart_manager plugin.
                - Approving Refunds: This means updating the refund status to "Approved" in the refund table using the tnt_mart_manager plugin. 
                    - Then Locate the correct refund record using the order ID.
                    - You need to pass the correct refund_id to the approve_refund function of the tnt_mart_manager plugin.
                - For all other refund status, do not perform any updates. Just inform the customer about the status.
                - Personalization: Throughout the conversation, use the customer's name to create a more personalized experience.
                - Closing the Interaction: End the conversation on a positive note, thanking Vikas for reaching out and expressing your willingness to assist with any future needs.

                IMPORTANT GUIDELINES:
                 - Always be polite and professional but stern when rejecting refunds if the conditions are met. Do not ask the customer if you can approve or reject the refund - it's your job.
                 - do not believe what the customer says blindly - validate all information provided by the customer against the database records.
                 - Use the plugin regular_items_nudge for fetching information from the database and tnt_mart_manager for all cart update operations.
                 - Ensure that any SQL commands you execute are done through the appropriate plugin.
                 - Keep the customer apprised of actions you are taking, especially when adding items to the cart. Every action should be communicated clearly.

        """
    )

    cl.user_session.set("kernel", kernel)
    cl.user_session.set("history", history)
    cl.user_session.set("mcp_plugin", mcp_plugin)

    await cl.Message(content="TnTMart welcomes you to the customer assistant. Type Hello to start the conversation now.").send()

@cl.on_message
async def on_message(message: cl.Message):
    kernel = cl.user_session.get("kernel")
    history = cl.user_session.get("history")

    user_input = message.content
    for element in message.elements:
        # check if the element is an image
        # for simplicity, we will not verify if the image is of a damaged product
        # in a real world scenario, you would use an image recognition model to verify this
        if element.mime.startswith("image/"):
            user_input += f"\n[uploaded image] {element.path}"
            print(f"Received file: {element.path}")


    # Add the user message to history
    history.add_user_message(user_input)

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