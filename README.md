# Private Wealth — Free Advisor Update

## Install on your existing Streamlit app
1. Download current accounts, holdings, and transactions CSV exports as a precaution.
2. Replace app.py in your existing GitHub repository with app.py from this ZIP.
3. Replace requirements.txt with the included version. Commit the changes.
4. Let Streamlit redeploy; reboot the app if needed.
5. Open Free Advisor Chat and ask “How am I doing?”

Keep your existing DATABASE_URL and APP_PASSWORD in Streamlit Secrets. Use the same database. This update makes no schema changes and does not delete or reset records. No CSV restore is needed for a normal code update. Do not upload secrets to GitHub. OPENAI_API_KEY and OPENAI_MODEL are no longer used and can be removed from Streamlit Secrets.

## Free advisor
No OpenAI API calls, API key, or AI usage charges. Existing hosting or database service charges, if any, are separate. Chat runs inside your Streamlit app using transparent rules and your saved data.

Supported examples:
- How am I doing? / What should I work on?
- What is my net worth?
- Review my cash flow
- How is my emergency fund?
- Review my debt
- Portfolio risk
- Save $20,000 / Save $20k

Each question stands alone; conversation text is session-only and not used as follow-up context. Replies use the latest loaded saved snapshot. Portfolio weights aggregate each ticker across accounts. Savings timelines assume starting the goal at zero and applying all recorded monthly surplus, with no returns. Reserve targets are illustrative. Saved quotes may be stale. The app cannot infer tax treatment, debt rates, fund contents, or unentered expenses. A single ticker can be a diversified fund. Unknown questions receive supported-topic guidance.

Account/portfolio double-counting prevention, CSV exports/restores, and persistent PostgreSQL storage remain in place. Exact investment account nicknames must match holdings account nicknames. Track uninvested brokerage cash separately.

## Verification
Python syntax and nine checks passed for savings calculations, cross-account ticker aggregation, reserve coverage, cash-flow rates, empty data, unsupported questions, deficit handling, and removal of the API-key path. Live Streamlit/PostgreSQL deployment was not available for testing here.
