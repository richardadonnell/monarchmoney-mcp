import asyncio
import calendar
import logging
import os
from datetime import datetime, timedelta

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
@mcp.tool(name="get_accounts")
async def get_accounts() -> list[dict]:
    """
    Retrieves a list of all accounts linked to the configured Monarch Money account.
    Corresponds to the get_accounts method in the hammem/monarchmoney library.
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
            save_session=False, # Explicitly disable saving session
            use_saved_session=False # Explicitly disable using saved session
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
            save_session=False, # Explicitly disable saving session
            use_saved_session=False # Explicitly disable using saved session
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
            save_session=False, # Explicitly disable saving session
            use_saved_session=False # Explicitly disable using saved session
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
            save_session=False, # Explicitly disable saving session
            use_saved_session=False # Explicitly disable using saved session
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
            save_session=False, # Explicitly disable saving session
            use_saved_session=False # Explicitly disable using saved session
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
            save_session=False, # Explicitly disable saving session
            use_saved_session=False # Explicitly disable using saved session
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

@mcp.tool()
async def get_account_type_options() -> dict:
    """
    Retrieves all account types and their subtypes available in Monarch Money.
    Corresponds to the get_account_type_options method in the hammem/monarchmoney library.
    Returns:
        A dictionary containing account types and subtypes or an error dictionary.
    """
    # --- Monarch Money Client & Login ---
    if not MONARCH_EMAIL or not MONARCH_PASSWORD:
        logger.error("Cannot proceed: Email or password not configured in .env.")
        return {"error": "Monarch Money email or password not configured on the server."}

    mm_client = MonarchMoney()
    logger.info(f"Attempting to log in to Monarch Money for get_account_type_options...")
    try:
        await mm_client.login(
            email=MONARCH_EMAIL,
            password=MONARCH_PASSWORD,
            mfa_secret_key=MONARCH_MFA_SECRET,
            save_session=False, # Explicitly disable saving session
            use_saved_session=False # Explicitly disable using saved session
        )
        logger.info("Monarch Money login successful for get_account_type_options.")
    except RequireMFAException:
        logger.error("Monarch Money login failed: MFA required.")
        return {"error": "Failed to log in to Monarch Money: MFA Required. Check server logs and .env configuration."}
    except Exception as e:
        logger.error(f"Monarch Money login failed: {e}")
        return {"error": f"Failed to log in to Monarch Money: {e}. Check server logs."}

    # --- Fetch Account Type Options ---
    logger.info(f"Fetching Monarch Money account type options...")
    try:
        options_data = await mm_client.get_account_type_options()
        # Assuming the library returns the dictionary directly
        logger.info(f"Successfully fetched account type options.")
        return options_data
    except Exception as e:
        logger.error(f"Error fetching Monarch account type options: {e}")
        return {"error": f"An error occurred while fetching account type options: {e}"}

@mcp.tool()
async def get_institutions() -> list[dict]:
    """
    Retrieves institutions linked to Monarch Money.
    Corresponds to the get_institutions method in the hammem/monarchmoney library.
    Returns:
        A list of institution dictionaries or an error dictionary.
    """
    # --- Monarch Money Client & Login ---
    if not MONARCH_EMAIL or not MONARCH_PASSWORD:
        logger.error("Cannot proceed: Email or password not configured in .env.")
        return [{"error": "Monarch Money email or password not configured on the server."}]

    mm_client = MonarchMoney()
    logger.info(f"Attempting to log in to Monarch Money for get_institutions...")
    # Add logging to verify loaded credentials
    logger.info(f"Using Email: {MONARCH_EMAIL}")
    logger.info(f"Password loaded: {'Yes' if MONARCH_PASSWORD else 'No'}")
    logger.info(f"MFA Secret loaded: {'Yes' if MONARCH_MFA_SECRET else 'No'}")
    try:
        await mm_client.login(
            email=MONARCH_EMAIL,
            password=MONARCH_PASSWORD,
            mfa_secret_key=MONARCH_MFA_SECRET,
            save_session=False, # Explicitly disable saving session
            use_saved_session=False # Explicitly disable using saved session
        )
        logger.info("Monarch Money login successful for get_institutions.")
    except RequireMFAException:
        logger.error("Monarch Money login failed: MFA required.")
        return [{"error": "Failed to log in to Monarch Money: MFA Required. Check server logs and .env configuration."}]
    except Exception as e:
        logger.error(f"Monarch Money login failed: {e}")
        return [{"error": f"Failed to log in to Monarch Money: {e}. Check server logs."}]

    # --- Fetch Institutions ---
    logger.info(f"Fetching Monarch Money institutions...")
    try:
        # The library function likely returns the raw GraphQL response
        response_data = await mm_client.get_institutions()
        # Extract institutions from the 'credentials' list in the response data
        credentials = response_data.get('credentials', [])
        institutions_set = set() # Use a set to store unique institution IDs
        institutions_list = []
        for cred in credentials:
            inst = cred.get('institution')
            if inst and inst.get('id') not in institutions_set:
                institutions_set.add(inst.get('id'))
                institutions_list.append(inst)

        logger.info(f"Successfully extracted {len(institutions_list)} unique institutions.")
        return institutions_list
    except Exception as e:
        logger.error(f"Error fetching/parsing Monarch institutions: {e}", exc_info=True) # Add exc_info for better debugging
        return [{"error": f"An error occurred while fetching institutions: {e}"}]

@mcp.tool()
async def get_budgets(start_date: str | None = None, end_date: str | None = None) -> dict:
    """
    Retrieves budgets and corresponding actual amounts from Monarch Money for a given period.
    Defaults to the period covering the previous month, current month, and next month if no dates are provided.
    Corresponds to the get_budgets method in the hammem/monarchmoney library.
    Args:
        start_date: Optional. The earliest date to get budget data, in "YYYY-MM-DD" format.
        end_date: Optional. The latest date to get budget data, in "YYYY-MM-DD" format.
    Returns:
        A dictionary containing budget data or an error dictionary.
    """
    # --- Monarch Money Client & Login ---
    if not MONARCH_EMAIL or not MONARCH_PASSWORD:
        logger.error("Cannot proceed: Email or password not configured in .env.")
        return {"error": "Monarch Money email or password not configured on the server."}

    # --- Date Handling (matching reference.py logic) ---
    if bool(start_date) != bool(end_date):
        logger.error("Both start_date and end_date must be provided, or neither.")
        return {"error": "Invalid date parameters: Provide both start_date and end_date, or neither."}

    if not start_date: # If start_date is None, end_date must also be None
        today = datetime.today()
        # Get the first day of last month
        first_day_current_month = today.replace(day=1)
        last_day_last_month = first_day_current_month - timedelta(days=1)
        start_date = last_day_last_month.replace(day=1).strftime("%Y-%m-%d")

        # Get the last day of next month
        # Move to the first day of the current month, add 2 months, then subtract 1 day
        # This handles year rollovers correctly
        first_day_next_next_month = (first_day_current_month.replace(year=today.year + (today.month + 1) // 13, 
                                                                    month=(today.month + 1) % 12 + 1))
        end_date = (first_day_next_next_month - timedelta(days=1)).strftime("%Y-%m-%d")
        logger.info(f"No dates provided, defaulting to start_date={start_date}, end_date={end_date}")


    mm_client = MonarchMoney()
    logger.info(f"Attempting to log in to Monarch Money for get_budgets...")
    # Add logging to verify loaded credentials
    logger.info(f"Using Email: {MONARCH_EMAIL}")
    logger.info(f"Password loaded: {'Yes' if MONARCH_PASSWORD else 'No'}")
    logger.info(f"MFA Secret loaded: {'Yes' if MONARCH_MFA_SECRET else 'No'}")
    try:
        await mm_client.login(
            email=MONARCH_EMAIL,
            password=MONARCH_PASSWORD,
            mfa_secret_key=MONARCH_MFA_SECRET,
            save_session=False, # Explicitly disable saving session
            use_saved_session=False # Explicitly disable using saved session
        )
        logger.info("Monarch Money login successful for get_budgets.")
    except RequireMFAException:
        logger.error("Monarch Money login failed: MFA required.")
        return {"error": "Failed to log in to Monarch Money: MFA Required. Check server logs and .env configuration."}
    except Exception as e:
        logger.error(f"Monarch Money login failed: {e}")
        return {"error": f"Failed to log in to Monarch Money: {e}. Check server logs."}

    # --- Fetch Budgets ---
    logger.info(f"Fetching Monarch Money budgets (start={start_date}, end={end_date})...")
    try:
        # Call the library function with potentially defaulted dates
        # Do NOT pass useLegacyGoals or useV2Goals based on reference.py
        budgets_data = await mm_client.get_budgets(start_date=start_date, end_date=end_date)
        logger.info(f"Successfully fetched budgets data. Type: {type(budgets_data)}")
        # logger.info(f"Budgets data sample: {str(budgets_data)[:500]}") # Log snippet if needed
        return budgets_data
    except Exception as e:
        logger.error(f"Error fetching Monarch budgets: {e}", exc_info=True)
        return {"error": f"An error occurred while fetching budgets: {e}"}

@mcp.tool()
async def get_subscription_details() -> dict:
    """
    Retrieves subscription details for the Monarch Money account.
    Corresponds to the get_subscription_details method in the hammem/monarchmoney library.
    Returns:
        A dictionary containing subscription details or an error dictionary.
    """
    # --- Monarch Money Client & Login ---
    if not MONARCH_EMAIL or not MONARCH_PASSWORD:
        logger.error("Cannot proceed: Email or password not configured in .env.")
        return {"error": "Monarch Money email or password not configured on the server."}

    mm_client = MonarchMoney()
    logger.info(f"Attempting to log in to Monarch Money for get_subscription_details...")
    # Add logging to verify loaded credentials
    logger.info(f"Using Email: {MONARCH_EMAIL}")
    logger.info(f"Password loaded: {'Yes' if MONARCH_PASSWORD else 'No'}")
    logger.info(f"MFA Secret loaded: {'Yes' if MONARCH_MFA_SECRET else 'No'}")
    try:
        await mm_client.login(
            email=MONARCH_EMAIL,
            password=MONARCH_PASSWORD,
            mfa_secret_key=MONARCH_MFA_SECRET,
            save_session=False, # Explicitly disable saving session
            use_saved_session=False # Explicitly disable using saved session
        )
        logger.info("Monarch Money login successful for get_subscription_details.")
    except RequireMFAException:
        logger.error("Monarch Money login failed: MFA required.")
        return {"error": "Failed to log in to Monarch Money: MFA Required. Check server logs and .env configuration."}
    except Exception as e:
        logger.error(f"Monarch Money login failed: {e}")
        return {"error": f"Failed to log in to Monarch Money: {e}. Check server logs."}

    # --- Fetch Subscription Details ---
    logger.info(f"Fetching Monarch Money subscription details...")
    try:
        # Call the library function
        subscription_data = await mm_client.get_subscription_details()
        logger.info(f"Successfully fetched subscription details. Type: {type(subscription_data)}")
        # The library likely returns a dict like {'subscription': {...}}
        # Extract the inner 'subscription' dict or return the whole thing if preferred
        subscription_info = subscription_data.get('subscription', {})
        if not subscription_info and subscription_data: # Handle case where outer key might be missing but data exists
             subscription_info = subscription_data
        logger.info(f"Returning subscription info: {subscription_info}")
        return subscription_info
    except Exception as e:
        logger.error(f"Error fetching Monarch subscription details: {e}", exc_info=True)
        return {"error": f"An error occurred while fetching subscription details: {e}"}

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