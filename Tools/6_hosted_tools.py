import asyncio
from openai import AsyncOpenAI
from agents import Agent, OpenAIResponsesModel, Runner, WebSearchTool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini API Key from .env
gemini_api_key = os.getenv('GEMINI_API_KEY')

# Initialize AsyncOpenAI client for Gemini
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Define the Agent with tool support
agent = Agent(
    name="Assistant",
    instructions="You are an expert of agentic AI.",
    model=OpenAIResponsesModel(
        model="gemini-2.0-flash",
        openai_client=client
    ),
    tools=[
        WebSearchTool(),
    ]
)

# Take input from user
query = input("Enter the query: ")

# Run synchronously
result = Runner.run_sync(agent, query)

# Print final output
print(result.final_output)
