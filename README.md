# Monarch Money MCP Server

A server application built with FastMCP to expose tools for interacting with a Monarch Money account via the [hammem/monarchmoney](https://github.com/hammem/monarchmoney) library.

## Features

This server provides the following tools that can be called via the MCP protocol:

- `get_accounts`: Retrieves a list of all accounts linked to Monarch Money.
- `get_account_holdings`: Retrieves all securities (holdings) in a brokerage or similar type of account.
- `get_account_type_options`: Retrieves all account types and their subtypes available in Monarch Money.
- `get_account_history`: Retrieves the daily account history for a specified account.
- `get_institutions`: Retrieves institutions linked to Monarch Money.
- `get_budgets`: Retrieves all budgets and corresponding actual amounts.
- `get_recurring_transactions`: Retrieves future recurring transactions, including merchant and account details.
- `get_transactions_summary`: Retrieves the transaction summary data from the transactions page.
- `get_transactions`: Retrieves transaction data, defaults to the last 100 transactions, and can be filtered by date range.
- `get_transaction_categories`: Retrieves all categories configured in the account.
- `get_transaction_category_groups`: Retrieves all category groups configured in the account.
- `get_cashflow`: Retrieves cashflow data (by category, category group, merchant, and summary).
- `get_cashflow_summary`: Retrieves the cash flow summary (income, expense, savings rate).

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

This command will typically handle the creation or modification of the necessary configuration files for you.

## Dependencies

- [FastMCP](https://github.com/AutonomousResearchGroup/FastMCP)
- [monarchmoney](https://github.com/hammem/monarchmoney)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [uvicorn](https://www.uvicorn.org/)
- [aiohttp](https://docs.aiohttp.org/en/stable/) (Dependency of monarchmoney)
- [gql](https://gql.readthedocs.io/en/latest/) (Dependency of monarchmoney)
- [oathtool](https://www.nongnu.org/oath-toolkit/oathtool.1.html) (Dependency of monarchmoney)
