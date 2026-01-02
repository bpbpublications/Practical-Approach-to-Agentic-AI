import asyncio
from typing import Annotated
from pydantic import Field
from agent_framework import ChatAgent, ai_function
from agent_framework.azure import AzureOpenAIResponsesClient
import os
import pathlib
from dotenv import load_dotenv
import chainlit as cl

# Load environment variables from .env file
current_dir = pathlib.Path(__file__).parent
env_path = current_dir / ".env"

print(f" Loading env from path: {env_path}")

load_dotenv(dotenv_path=env_path)

@ai_function(name="get_weather", description="Gets the weather for a city")
def get_weather(city: Annotated[str, Field(description="The city to get weather for")]) -> str:
    """Retrieves the weather for a given city."""
    weather_data = {
        "paris": "The weather in Paris is 20°C and sunny.",
        "london": "The weather in London is 15°C and cloudy.",
        "berlin": "The weather in Berlin is 18°C and rainy.",
        "new york": "The weather in New York is 25°C and sunny.",
        "tokyo": "The weather in Tokyo is 22°C and rainy.",
    }
    return weather_data.get(city.lower(), f"Sorry, I don't have the weather for {city}.")

@cl.on_chat_start
async def start_chat():
    
    # create Azure OpenAI Responses client
    chat_client = AzureOpenAIResponsesClient(
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment_name=os.environ["AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
    )

    agent = chat_client.create_agent(
        name="WeatherAgent",
        instructions="""You are a helpful assistant that provides weather information for various cities.
        Use the get_weather function to fetch weather details when the user asks about the weather in a specific city.""",
        tools=[get_weather]
    )
    
    thread = agent.get_new_thread()
    cl.user_session.set("agent", agent)
    cl.user_session.set("thread", thread)
    
    print(f" User session id is :: {cl.user_session.get('id')}")
    
    welcome_message = "Hello! I am your Weather Agent. Ask me about the weather in any city."
    await cl.Message(content=welcome_message, author="Weather Agent").send()

@cl.on_message
async def handle_message(message: str):
    agent = cl.user_session.get("agent")
    thread = cl.user_session.get("thread")
    response = await agent.run(message.content, thread=thread)
    await cl.Message(content=response).send()
