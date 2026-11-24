import re
import time
import traceback

from src.team.shop_team import shop_team
from src.tools.store_data import customer


def session_for(customer_id):
    return "web-" + customer_id


def _short(value, limit=220):
    text = str(value)
    return text if len(text) <= limit else text[:limit] + "..."


def _steps(result):
    steps   = []
    members = {"orders-desk": "Orders Desk", "policy-desk": "Policy Desk", "product-desk": "Product Desk"}
    for tool in result.tools or []:
        if tool.tool_name == "delegate_task_to_member":
            args = tool.tool_args or {}
            steps.append({"kind": "delegate", "agent": "ShopAssist", "to": members.get(args.get("member_id"), args.get("member_id")), "detail": _short(args.get("task", ""))})
    for member in result.member_responses or []:
        name = getattr(member, "agent_name", None) or "Member"
        for tool in getattr(member, "tools", None) or []:
            steps.append({"kind": "tool", "agent": name, "tool": tool.tool_name, "args": tool.tool_args or {}, "detail": _short(tool.result)})
    return steps


def ask_shopassist(customer_id, message):
    started = time.perf_counter()
    person  = customer(customer_id)
    try:
        result = shop_team.run(
                               message,
                               user_id      = customer_id,
                               session_id   = session_for(customer_id),
                               dependencies = {"signed_in_customer": person["name"] + " (" + customer_id + ")"},
                              )
    except Exception as error:
        traceback.print_exc()
        return {"status": "error", "answer": "Sorry, ShopAssist could not answer right now (" + type(error).__name__ + "). Please try again.", "agents": [], "steps": [], "pages": [], "seconds": round(time.perf_counter() - started, 1)}
    answer = result.content if isinstance(result.content, str) else str(result.content or "")
    steps  = _steps(result)
    agents = []
    for step in steps:
        name = step["to"] if step["kind"] == "delegate" else step["agent"]
        if name and name not in agents:
            agents.append(name)
    pages  = sorted({int(p) for p in re.findall(r"Page (\d+)", answer)})
    return {"status": "ok", "answer": answer, "agents": agents or ["ShopAssist"], "steps": steps, "pages": pages, "seconds": round(time.perf_counter() - started, 1)}


def clear_memory(customer_id):
    shop_team.delete_session(session_id=session_for(customer_id))
