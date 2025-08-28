from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel,Runner
from agents import function_tool as tool
from dotenv import load_dotenv
import os

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

@tool
def fetch_weather(location) -> str:
    """
    Goal:
        Get the weather of a location.
    Args:
        location: The location to get the weather of.
    Returns:
        The weather of the location.
    """
    print(f"Fetching weather for {location}....")
    return f"The weather of {location} is sunny."


agent = Agent(
    name="Weather Agent",
    instructions="You are a weather agent that fetch a location and tells the details about the weather of that location.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash",openai_client=client),
    tools=[fetch_weather]
)
query = input("Enter the location to get the weather of: ")
result = Runner.run_sync(agent,query)
print(result.final_output)








