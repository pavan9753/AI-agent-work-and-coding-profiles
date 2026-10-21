"""Google ADK ATM agent. Start with `adk web` from this repository directory."""
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from . import banking

async def login_customer(customer_id: str, pin: str, tool_context: ToolContext) -> dict[str,str]:
    """Sign in to the demo ATM using the customer ID and four-digit PIN."""
    result=banking.authenticate(customer_id,pin)
    if result["status"] == "success":
        tool_context.state["customer_id"]=result["customer_id"]
        tool_context.state["customer_name"]=result["name"]
    return result

async def check_balance(tool_context: ToolContext) -> dict[str,str]:
    """Show the signed-in customer's available demo account balance."""
    cid=tool_context.state.get("customer_id")
    return banking.balance(cid) if cid else {"status":"error","message":"Please sign in first."}

async def deposit_cash(amount: float, tool_context: ToolContext) -> dict[str,str]:
    """Deposit a positive amount of simulated cash in INR into the signed-in account."""
    cid=tool_context.state.get("customer_id")
    if not cid: return {"status":"error","message":"Please sign in first."}
    try: return banking.deposit(cid,amount)
    except ValueError as exc: return {"status":"error","message":str(exc)}

async def withdraw_cash(amount: float, tool_context: ToolContext) -> dict[str,str]:
    """Withdraw a positive amount of simulated cash in INR from the signed-in account."""
    cid=tool_context.state.get("customer_id")
    if not cid: return {"status":"error","message":"Please sign in first."}
    try: return banking.withdraw(cid,amount)
    except ValueError as exc: return {"status":"error","message":str(exc)}

async def transfer_money(recipient_customer_id: str, amount: float, tool_context: ToolContext) -> dict[str,str]:
    """Transfer simulated INR to another customer; confirm recipient and amount before calling."""
    cid=tool_context.state.get("customer_id")
    if not cid: return {"status":"error","message":"Please sign in first."}
    try: return banking.transfer(cid,recipient_customer_id,amount)
    except ValueError as exc: return {"status":"error","message":str(exc)}

async def get_transaction_history(tool_context: ToolContext, limit: int=10) -> dict[str,object]:
    """Show up to 20 recent transactions for the signed-in customer (default 10)."""
    cid=tool_context.state.get("customer_id")
    return banking.history(cid,limit) if cid else {"status":"error","message":"Please sign in first."}

async def update_pin(current_pin: str, new_pin: str, tool_context: ToolContext) -> dict[str,str]:
    """Change the signed-in customer's demo ATM PIN after verifying the current PIN."""
    cid=tool_context.state.get("customer_id")
    return banking.change_pin(cid,current_pin,new_pin) if cid else {"status":"error","message":"Please sign in first."}

async def logout_customer(tool_context: ToolContext) -> dict[str,str]:
    """Sign out and clear the current demo ATM session."""
    tool_context.state.pop("customer_id",None); tool_context.state.pop("customer_name",None)
    return {"status":"success","message":"You have been signed out."}

banking.seed_demo_account()
root_agent=Agent(
    name="atm_agent", model="gemini-2.5-flash",
    description="Conversational demo ATM agent for simulated INR banking.",
    instruction="""You are a careful ATM assistant for a LOCAL DEMO with fictional INR accounts.
Support sign in, balance, simulated deposits and withdrawals, transfers, transaction history, PIN changes, and sign out.
Always require a successful login before account operations. Never claim success without a successful tool result.
Before a withdrawal or transfer, restate the amount and (for transfers) recipient and get explicit user confirmation in this conversation before calling the tool. Never guess account IDs, PINs, amounts, or recipients.
Never ask for or suggest using a real bank PIN. Do not imply connection to a real bank or ATM. Deposits are simulated and do not represent real cash acceptance. Report validation errors plainly; never expose internal implementation details.""",
    tools=[login_customer,check_balance,deposit_cash,withdraw_cash,transfer_money,get_transaction_history,update_pin,logout_customer],
)
