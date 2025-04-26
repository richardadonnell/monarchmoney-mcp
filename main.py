import asyncio
import logging
import os

import uvicorn
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from monarchmoney import MonarchMoney, RequireMFAException

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
MONARCH_EMAIL = os.getenv("MONARCH_EMAIL")
MONARCH_PASSWORD = os.getenv("MONARCH_PASSWORD")
MONARCH_MFA_SECRET = os.getenv("MONARCH_MFA_SECRET") # Optional

# --- MCP Server Setup ---
mcp = FastMCP("MonarchMoneyTool", description="MCP Tool to interact with Monarch Money.")

# --- Tools ---
@mcp.tool()
async def get_monarch_accounts() -> list[dict]:
    """
    Retrieves a list of all accounts linked to the configured Monarch Money account.
    Returns a list of account dictionaries or an error dictionary.
    """
    # --- Monarch Money Client & Login (Encapsulated within the tool) ---
    if not MONARCH_EMAIL or not MONARCH_PASSWORD:
        logger.error("Cannot proceed: Email or password not configured in .env.")
        return [{"error": "Monarch Money email or password not configured on the server."}]

    mm_client = MonarchMoney()
    logger.info("Attempting to log in to Monarch Money...")
    try:
        await mm_client.login(
            email=MONARCH_EMAIL,
            password=MONARCH_PASSWORD,
            mfa_secret_key=MONARCH_MFA_SECRET, # Will be None if not set, library handles it
        )
        logger.info("Monarch Money login successful.")
    except RequireMFAException:
        logger.error("Monarch Money login failed: MFA is required. "
                     "Provide MONARCH_MFA_SECRET in .env for non-interactive login.")
        # Return an error structure recognizable by the client/LLM
        return [{"error": "Failed to log in to Monarch Money: MFA Required. Check server logs and .env configuration."}]
    except Exception as e:
        logger.error(f"Monarch Money login failed: {e}")
        # Return an error structure recognizable by the client/LLM
        return [{"error": f"Failed to log in to Monarch Money: {e}. Check server logs."}]

    # --- Fetch Accounts ---
    logger.info("Fetching Monarch Money accounts...")
    try:
        # The get_accounts() method returns a dict like {'accounts': [...]}
        result = await mm_client.get_accounts()
        # FastMCP handles serialization of basic types and Pydantic models
        accounts_list = result.get('accounts', [])
        logger.info(f"Successfully fetched {len(accounts_list)} accounts.")
        return accounts_list
    except Exception as e:
        logger.error(f"Error fetching Monarch accounts: {e}")
        # Return an error structure recognizable by the client/LLM
        return [{"error": f"An error occurred while fetching accounts: {e}"}]

@mcp.tool()
async def get_transactions(start_date: str | None = None, end_date: str | None = None, limit: int = 100) -> list[dict]:
    """
    Retrieves transactions from Monarch Money, optionally filtered by date range.
    Defaults to the last 100 transactions if no date range or limit is provided.
    Args:
        start_date: Optional. Start date in 'YYYY-MM-DD' format.
        end_date: Optional. End date in 'YYYY-MM-DD' format.
        limit: Optional. Maximum number of transactions to return. Defaults to 100.
    Returns:
        A list of transaction dictionaries or an error dictionary.
    """
    # --- Monarch Money Client & Login ---
    if not MONARCH_EMAIL or not MONARCH_PASSWORD:
        logger.error("Cannot proceed: Email or password not configured in .env.")
        return [{"error": "Monarch Money email or password not configured on the server."}]

    mm_client = MonarchMoney()
    logger.info(f"Attempting to log in to Monarch Money for get_transactions...")
    try:
        await mm_client.login(
            email=MONARCH_EMAIL,
            password=MONARCH_PASSWORD,
            mfa_secret_key=MONARCH_MFA_SECRET,
        )
        logger.info("Monarch Money login successful for get_transactions.")
    except RequireMFAException:
        logger.error("Monarch Money login failed: MFA required.")
        return [{"error": "Failed to log in to Monarch Money: MFA Required. Check server logs and .env configuration."}]
    except Exception as e:
        logger.error(f"Monarch Money login failed: {e}")
        return [{"error": f"Failed to log in to Monarch Money: {e}. Check server logs."}]

    # --- Fetch Transactions ---
    logger.info(f"Fetching Monarch Money transactions (limit: {limit}, start: {start_date}, end: {end_date})...")
    try:
        # Note: The underlying library might have slightly different parameter names or expect datetime objects.
        # Adjustments may be needed based on testing or more detailed library docs.
        # Common parameters might include `offset`, `is_pending`, etc. which are omitted for simplicity here.
        logger.info("Attempting to call mm_client.get_transactions...")
        result = await mm_client.get_transactions(
            limit=limit,
            start_date=start_date, # Assuming library accepts 'YYYY-MM-DD' strings
            end_date=end_date      # Assuming library accepts 'YYYY-MM-DD' strings
        )
        logger.info(f"Successfully received result from mm_client.get_transactions. Type: {type(result)}")
        logger.info(f"Raw result dict from library: {result}")
        # The actual key for the list might differ, consult library source or test response if needed
        # Accessing the structure based on direct library output: result -> allTransactions -> results
        all_transactions_data = result.get('allTransactions', {})
        transactions_list = all_transactions_data.get('results', [])
        logger.info(f"Successfully fetched {len(transactions_list)} transactions using key path 'allTransactions.results'.")
        return transactions_list
    except Exception as e:
        # Log the specific exception type and message
        logger.error(f"Error during Monarch transactions fetch: {type(e).__name__} - {e}", exc_info=True)
        return [{"error": f"An error occurred while fetching transactions: {type(e).__name__} - {e}"}]

@mcp.tool()
async def get_cashflow_summary() -> dict:
    """
    Retrieves the cash flow summary (income, expenses, savings rate) from Monarch Money.
    Returns:
        A dictionary containing the cash flow summary or an error dictionary.
    """
    # --- Monarch Money Client & Login ---
    if not MONARCH_EMAIL or not MONARCH_PASSWORD:
        logger.error("Cannot proceed: Email or password not configured in .env.")
        return {"error": "Monarch Money email or password not configured on the server."}

    mm_client = MonarchMoney()
    logger.info(f"Attempting to log in to Monarch Money for get_cashflow_summary...")
    try:
        await mm_client.login(
            email=MONARCH_EMAIL,
            password=MONARCH_PASSWORD,
            mfa_secret_key=MONARCH_MFA_SECRET,
        )
        logger.info("Monarch Money login successful for get_cashflow_summary.")
    except RequireMFAException:
        logger.error("Monarch Money login failed: MFA required.")
        return {"error": "Failed to log in to Monarch Money: MFA Required. Check server logs and .env configuration."}
    except Exception as e:
        logger.error(f"Monarch Money login failed: {e}")
        return {"error": f"Failed to log in to Monarch Money: {e}. Check server logs."}

    # --- Fetch Cashflow Summary ---
    logger.info(f"Fetching Monarch Money cash flow summary...")
    try:
        summary_data = await mm_client.get_cashflow_summary()
        # Assuming the library returns the dictionary directly
        logger.info(f"Successfully fetched cash flow summary.")
        return summary_data
    except Exception as e:
        logger.error(f"Error fetching Monarch cash flow summary: {e}")
        return {"error": f"An error occurred while fetching the cash flow summary: {e}"}

@mcp.tool()
async def get_account_history(account_id: int) -> list[dict]:
    """
    Retrieves the daily balance history for a specific account.
    Args:
        account_id: The ID of the account to fetch history for.
    Returns:
        A list of history dictionaries or an error dictionary.
    """
    # --- Monarch Money Client & Login ---
    if not MONARCH_EMAIL or not MONARCH_PASSWORD:
        logger.error("Cannot proceed: Email or password not configured in .env.")
        # Return list with error dict to match expected return type hint
        return [{"error": "Monarch Money email or password not configured on the server."}]

    mm_client = MonarchMoney()
    logger.info(f"Attempting to log in to Monarch Money for get_account_history (account: {account_id})...")
    try:
        await mm_client.login(
            email=MONARCH_EMAIL,
            password=MONARCH_PASSWORD,
            mfa_secret_key=MONARCH_MFA_SECRET,
        )
        logger.info("Monarch Money login successful for get_account_history.")
    except RequireMFAException:
        logger.error("Monarch Money login failed: MFA required.")
        return [{"error": "Failed to log in to Monarch Money: MFA Required. Check server logs and .env configuration."}]
    except Exception as e:
        logger.error(f"Monarch Money login failed: {e}")
        return [{"error": f"Failed to log in to Monarch Money: {e}. Check server logs."}]

    # --- Fetch Account History ---
    logger.info(f"Fetching Monarch Money account history for account ID: {account_id}...")
    try:
        # Pass the account_id to the library function
        history_data = await mm_client.get_account_history(account_id=account_id)
        # Assuming the library returns a list of history entries directly or within a known structure
        # Example: history_data might be {'accountHistory': [...]} - adjust .get() key if necessary
        history_list = history_data.get('accountHistory', []) # Adjust key if needed
        logger.info(f"Successfully fetched {len(history_list)} history entries for account {account_id}.")
        return history_list
    except Exception as e:
        logger.error(f"Error fetching Monarch account history for account {account_id}: {e}")
        return [{"error": f"An error occurred while fetching account history: {e}"}]

@mcp.tool()
async def get_account_holdings(account_id: int) -> list[dict]:
    """
    Retrieves all securities (holdings) in a brokerage or similar investment account.
    Args:
        account_id: The ID of the investment account.
    Returns:
        A list of holding dictionaries or an error dictionary.
    """
    # --- Monarch Money Client & Login ---
    if not MONARCH_EMAIL or not MONARCH_PASSWORD:
        logger.error("Cannot proceed: Email or password not configured in .env.")
        return [{"error": "Monarch Money email or password not configured on the server."}]

    mm_client = MonarchMoney()
    logger.info(f"Attempting to log in to Monarch Money for get_account_holdings (account: {account_id})...")
    try:
        await mm_client.login(
            email=MONARCH_EMAIL,
            password=MONARCH_PASSWORD,
            mfa_secret_key=MONARCH_MFA_SECRET,
        )
        logger.info("Monarch Money login successful for get_account_holdings.")
    except RequireMFAException:
        logger.error("Monarch Money login failed: MFA required.")
        return [{"error": "Failed to log in to Monarch Money: MFA Required. Check server logs and .env configuration."}]
    except Exception as e:
        logger.error(f"Monarch Money login failed: {e}")
        return [{"error": f"Failed to log in to Monarch Money: {e}. Check server logs."}]

    # --- Fetch Account Holdings ---
    logger.info(f"Fetching Monarch Money account holdings for account ID: {account_id}...")
    try:
        # Pass the account_id to the library function
        holdings_data = await mm_client.get_account_holdings(account_id=account_id)
        # Assuming the library returns a structure like {'holdings': [...]} - adjust key if needed
        holdings_list = holdings_data.get('holdings', []) # Adjust key if needed
        logger.info(f"Successfully fetched {len(holdings_list)} holdings for account {account_id}.")
        return holdings_list
    except Exception as e:
        logger.error(f"Error fetching Monarch account holdings for account {account_id}: {e}")
        return [{"error": f"An error occurred while fetching account holdings: {e}"}]

@mcp.tool()
async def get_transactions_summary() -> dict:
    """
    Retrieves the transaction summary data (e.g., totals for a period) from Monarch Money.
    Returns:
        A dictionary containing the transaction summary or an error dictionary.
    """
    # --- Monarch Money Client & Login ---
    if not MONARCH_EMAIL or not MONARCH_PASSWORD:
        logger.error("Cannot proceed: Email or password not configured in .env.")
        return {"error": "Monarch Money email or password not configured on the server."}

    mm_client = MonarchMoney()
    logger.info(f"Attempting to log in to Monarch Money for get_transactions_summary...")
    try:
        await mm_client.login(
            email=MONARCH_EMAIL,
            password=MONARCH_PASSWORD,
            mfa_secret_key=MONARCH_MFA_SECRET,
        )
        logger.info("Monarch Money login successful for get_transactions_summary.")
    except RequireMFAException:
        logger.error("Monarch Money login failed: MFA required.")
        return {"error": "Failed to log in to Monarch Money: MFA Required. Check server logs and .env configuration."}
    except Exception as e:
        logger.error(f"Monarch Money login failed: {e}")
        return {"error": f"Failed to log in to Monarch Money: {e}. Check server logs."}

    # --- Fetch Transactions Summary ---
    logger.info(f"Fetching Monarch Money transactions summary...")
    try:
        summary_data = await mm_client.get_transactions_summary()
        # Assuming the library returns the summary dictionary directly
        logger.info(f"Successfully fetched transactions summary.")
        return summary_data
    except Exception as e:
        logger.error(f"Error fetching Monarch transactions summary: {e}")
        return {"error": f"An error occurred while fetching the transactions summary: {e}"}

# Add more tools here later...
# e.g.
# @mcp.tool()
# async def get_transactions(...) -> ... :
#    # Similar login and API call logic
#    pass

# --- Uvicorn Entry Point ---
if __name__ == "__main__":
    # Check for essential config before starting server
    if not MONARCH_EMAIL or not MONARCH_PASSWORD:
        logger.error("MONARCH_EMAIL and MONARCH_PASSWORD environment variables are required in .env file.")
        logger.error("Server cannot start without credentials.")
        # Exit or prevent uvicorn.run if essential config is missing
        exit(1) # Or raise ConfigurationError("Credentials missing")

    logger.info("Starting Uvicorn server...")
    # Run the server using uvicorn directly
    # Pass the actual ASGI app provided by FastMCP via sse_app()
    uvicorn.run(mcp.sse_app(), host="127.0.0.1", port=8000, log_level="info") 