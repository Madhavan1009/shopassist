from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.team import Team
from agno.team.mode import TeamMode

from src.agents.orders_desk import orders_desk
from src.agents.policy_desk import policy_desk
from src.agents.product_desk import product_desk
from src.core.config import DB_FILE, MODEL
from src.core.instructions import TEAM_INSTRUCTIONS

shop_team = Team(
                 id                          = "shopassist",
                 name                        = "ShopAssist",
                 mode                        = TeamMode.coordinate,
                 model                       = OpenAIChat(id=MODEL, temperature=0),
                 members                     = [orders_desk, policy_desk, product_desk],
                 instructions                = TEAM_INSTRUCTIONS,
                 db                          = SqliteDb(db_file=str(DB_FILE)),
                 add_history_to_context      = True,
                 num_history_runs            = 4,
                 add_dependencies_to_context = True,
                 store_member_responses      = True,
                 markdown                    = True,
                )
