# Monarch Money MCP Server

A server application built with FastMCP to expose tools for interacting with a Monarch Money account via the [hammem/monarchmoney](https://github.com/hammem/monarchmoney) library.

## Features

This server provides the following tools that can be called via the MCP protocol:

- [x] `get_accounts` — gets all the accounts linked to Monarch Money
- [x] `get_account_holdings` — gets all of the securities in a brokerage or similar type of account
- [x] `get_account_type_options` — all account types and their subtypes available in Monarch Money
- [x] `get_account_history` — gets all daily account history for the specified account
- [x] `get_institutions` — gets institutions linked to Monarch Money
- [x] `get_budgets` — all the budgets and the corresponding actual amounts
- [ ] `get_subscription_details` — gets the Monarch Money account's status (e.g., paid or trial)
- [x] `get_recurring_transactions` — gets the future recurring transactions, including merchant and account details
- [x] `get_transactions_summary` — gets the transaction summary data from the transactions page
- [x] `get_transactions` — gets transaction data, defaults to returning the last 100 transactions; can also be searched by date range
- [x] `get_transaction_categories` — gets all of the categories configured in the account
- [x] `get_transaction_category_groups` — all category groups configured in the account
- [ ] `get_transaction_details` — gets detailed transaction data for a single transaction
- [ ] `get_transaction_splits` — gets transaction splits for a single transaction
- [ ] `get_transaction_tags` — gets all of the tags configured in the account
- [x] `get_cashflow` — gets cashflow data (by category, category group, merchant, and a summary)
- [x] `get_cashflow_summary` — gets cashflow summary (income, expense, savings, savings rate)
- [ ] `is_accounts_refresh_complete` — gets the status of a running account refresh

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/richardadonnell/monarchmoney-mcp
    cd monarchmoney-mcp
    ```
2.  **Install dependencies:**
    Make sure you have Python 3.x installed. Then, install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

This server requires credentials to access your Monarch Money account. Create a `.env` file in the project root directory with the following variables:

```dotenv
MONARCH_EMAIL=your_email@example.com
MONARCH_PASSWORD=your_monarch_password
# Optional: Only required if your account uses MFA/TOTP. Comment out line below if not needed.
MONARCH_MFA_SECRET=your_mfa_totp_secret_key
```

- Replace the placeholder values with your actual Monarch Money email and password.
- If you use Multi-Factor Authentication (MFA) with an authenticator app (TOTP), you can provide your secret key (`MONARCH_MFA_SECRET`) for non-interactive logins. If this is not provided and MFA is required, the login attempts within the tools will fail.

**Security Note:** Keep your `.env` file secure and do not commit it to version control.

## Running the Server

There are two ways to configure your IDE (like Cursor or Claude Desktop) to use this MCP tool:

### Option 1: Manual Configuration (Cursor)

1.  **Create `mcp.json`:** Create a file named `mcp.json` in the `.cursor` folder within your workspace. **Make sure to replace the absolute path to `main.py` with the correct path on your system.**

    ```json
    {
      "mcpServers": {
        "MonarchMoneyTool": {
          "command": "uv",
          "args": [
            "run",
            "--with",
            "mcp[cli]",
            "mcp",
            "run",
            "C:\\\\example\\\\path\\\\to\\\\project\\\\main.py"
          ]
        }
      }
    }
    ```

### Option 2: Automatic Installation (Claude Desktop / MCP CLI)

If you have the MCP CLI installed, you can automatically configure the tool by running the following command in the root directory of this project:

```bash
mcp install main.py
```

## Dependencies

- [FastMCP](https://github.com/AutonomousResearchGroup/FastMCP)
- [monarchmoney](https://github.com/hammem/monarchmoney)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [uvicorn](https://www.uvicorn.org/)
- [aiohttp](https://docs.aiohttp.org/en/stable/) (Dependency of monarchmoney)
- [gql](https://gql.readthedocs.io/en/latest/) (Dependency of monarchmoney)
- [oathtool](https://www.nongnu.org/oath-toolkit/oathtool.1.html) (Dependency of monarchmoney)
