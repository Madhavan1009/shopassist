from agno.agent import Agent
from agno.models.openai import OpenAIChat

from src.core.config import MODEL
from src.core.instructions import PRODUCT_DESK_INSTRUCTIONS
from src.tools.product_tools import PRODUCT_TOOLS

product_desk = Agent(
                     id           = "product-desk",
                     name         = "Product Desk",
                     role         = "Product search, prices and stock in the ShopEase catalogue",
                     model        = OpenAIChat(id=MODEL, temperature=0),
                     tools        = PRODUCT_TOOLS,
                     instructions = PRODUCT_DESK_INSTRUCTIONS,
                     markdown     = True,
                    )
