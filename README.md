# Private Wealth AI — Persistent Storage Edition

## Set up Supabase
1. Create a Supabase project at https://supabase.com and save your database password.
2. In Supabase, find **Connect** and copy the PostgreSQL connection string (use Session Pooler if the direct connection does not support your hosting network). Replace the password placeholder with your real password. Use URL encoding if your password has reserved URL characters.
3. Open your app at https://share.streamlit.io, choose **Manage app → Settings → Secrets**, and add:

```toml
DATABASE_URL = "postgresql://YOUR_USER:YOUR_PASSWORD@YOUR_HOST:5432/YOUR_DATABASE"
APP_PASSWORD = "A_LONG_UNIQUE_RANDOM_PASSWORD"
```

Never commit secrets to GitHub. Keep the repository private. Update app.py and requirements.txt on GitHub; Streamlit will redeploy. The app creates its tables automatically after it successfully connects.

## Important
- A PostgreSQL database is persistent across Streamlit redeploys and restarts, but not immune to deletion or provider outages. Enable managed backups/PITR if available, and download periodic CSV exports.
- This version is **single-user** and protected by an app password, not production-grade multiuser authentication. Do not share the site/password. Add managed authentication and stronger access controls before using it for sensitive real-world data.
- No old SQLite records can be recovered unless a copy of the original `wealth.db` still exists. The previous Streamlit deployment may already have discarded it.
- Never upload bank credentials, account numbers, passwords, or API keys to the application.
- Cash and investment holdings should not be counted twice in net worth.
