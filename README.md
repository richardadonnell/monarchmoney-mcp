# Monarch Money MCP Server

A server application built with FastMCP to expose tools for interacting with a Monarch Money account via the [hammem/monarchmoney](https://github.com/hammem/monarchmoney) library.

## Features

This server provides the following tools that can be called via the MCP protocol:

- `get_accounts`: Retrieves a list of all linked Monarch Money accounts.
- `get_transactions`: Retrieves transactions, optionally filtered by date range and limit.
- `get_cashflow_summary`: Retrieves the cash flow summary (income, expenses, savings rate).
- `get_account_history`: Retrieves the daily balance history for a specific account.
- `get_account_holdings`: Retrieves all securities (holdings) in an investment account.
- `get_transactions_summary`: Retrieves the transaction summary data.
- `get_account_type_options`: Retrieves available account types and subtypes.
- `get_institutions`: Retrieves linked institutions.
- `get_budgets`: Retrieves budgets and actual spending for a given period.
- `get_subscription_details`: Retrieves subscription details for the Monarch Money account.

_(More tools can be added by extending `main.py`)_

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

1.  **Create `mcp.json`:** Create a file named `mcp.json` in the `.cursor` folder. **Make sure to replace the absolute path to `main.py` with the correct path on your system.**

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
            "C:\\example\\path\\to\\project\\main.py"
          ]
        }
      }
    }
    ```

## Dependencies

- [FastMCP](https://github.com/AutonomousResearchGroup/FastMCP)
- [monarchmoney](https://github.com/hammem/monarchmoney)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [uvicorn](https://www.uvicorn.org/)
- [aiohttp](https://docs.aiohttp.org/en/stable/) (Dependency of monarchmoney)
- [gql](https://gql.readthedocs.io/en/latest/) (Dependency of monarchmoney)
- [oathtool](https://www.nongnu.org/oath-toolkit/oathtool.1.html) (Dependency of monarchmoney)
