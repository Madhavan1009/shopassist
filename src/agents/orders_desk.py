from agno.agent import Agent
from agno.models.openai import OpenAIChat

from src.core.config import MODEL
from src.core.instructions import ORDERS_DESK_INSTRUCTIONS
from src.tools.order_tools import ORDER_TOOLS

orders_desk = Agent(
                    id           = "orders-desk",
                    name         = "Orders Desk",
                    role         = "Order status, deliveries, returns and refunds for the signed-in customer",
                    model        = OpenAIChat(id=MODEL, temperature=0),
                    tools        = ORDER_TOOLS,
                    instructions = ORDERS_DESK_INSTRUCTIONS,
                    markdown     = True,
                   )
