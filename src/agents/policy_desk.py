from agno.agent import Agent
from agno.models.openai import OpenAIChat

from src.core.config import MODEL
from src.core.instructions import POLICY_DESK_INSTRUCTIONS
from src.tools.policy_tool import search_policy

policy_desk = Agent(
                    id           = "policy-desk",
                    name         = "Policy Desk",
                    role         = "General store rules from the ShopEase Store Policy PDF",
                    model        = OpenAIChat(id=MODEL, temperature=0),
                    tools        = [search_policy],
                    instructions = POLICY_DESK_INSTRUCTIONS,
                    markdown     = True,
                   )
