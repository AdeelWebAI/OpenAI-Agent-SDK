from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel,Runner, function_tool
from dotenv import load_dotenv
import os

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

@function_tool
def bill_calculator(unit_consumed:float) -> float:
    """
    goal:
        calculate the bill bases on the consumed units.
    args:
        The number of units consumed.
    returns:
        The calculated bill amount
    """
    try:
        rate_per_unit = int(input("Enter the rate per unit in your country: "))
        bill_amount = unit_consumed * rate_per_unit
        return bill_amount
    
    except Exception as e:
        raise ValueError(f"Error calculating bill: {e}")
    
agent = Agent(
    name="Bill Calculator Agent",
    instructions="You are an expert of calculate bill.You need to calculate the bill based on their consumed units",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    tools=[bill_calculator]
)

query = input("Enter the amount of units consumed: ")

result = Runner.run_sync(agent,query)

print(result.final_output)