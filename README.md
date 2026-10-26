# Private Wealth — Groq Advisor Update

## Install
1. Export your accounts, holdings, and transactions CSVs as a precaution.
2. Replace app.py and requirements.txt in your existing GitHub repository with the included files. Commit both files and let Streamlit redeploy.
3. Keep existing DATABASE_URL and APP_PASSWORD secrets. Add the following at the top level of Streamlit Secrets, above any [section] headings:

GROQ_API_KEY = "your-private-groq-key"
GROQ_MODEL = "openai/gpt-oss-20b"

4. Open Advisor Chat. Select Groq AI, type in Your question, and click Ask advisor.

No database migrations, resets, or CSV restores are needed. The app uses your existing PostgreSQL database. Never commit API keys or secrets.toml to GitHub.

## Modes
Groq AI is conversational and sends your question, recent Groq conversation, and the displayed financial summary to Groq. It shares aggregate balances and ticker values, not account nicknames or transaction descriptions. Avoid typing sensitive identifiers in your questions. Preview exactly what is in the snapshot under Financial summary shared with Groq. Configure Zero Data Retention in Groq's console if desired.

Free calculator runs locally in the app with no AI API requests. It also serves as fallback for a missing key, usage limits, service failures, model errors, or empty replies. It handles supported keywords; it is not conversational. Responses show which mode produced them. Chat history is session-only; Clear conversation removes it from that session.

Groq's Free plan is subject to model-specific limits. This app cannot verify your billing plan or prevent charges if you use a paid Groq plan. It makes one request per submitted question with no automatic retries. No external trading or record-changing tools are exposed.

## Try
- How am I doing financially?
- What should I prioritize based on my saved finances?
- Explain the concentration in my portfolio.
- What would saving $20,000 require?

Saved prices are not live. Missing debt rates, taxes, fund contents, or expenses limit analysis. AI answers can make mistakes. The calculator uses recorded monthly surplus and an illustrative reserve target.

## Validation
Python syntax passed. Mocked integration checks passed for a successful Groq response, no-key fallback, and a 429 rate-limit fallback. No live Groq key or PostgreSQL deployment was available here, so live API and deployment behavior remain unverified.
