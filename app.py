import sqlite3
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='Private Wealth AI', page_icon='💼', layout='wide')
DB = Path(__file__).with_name('wealth.db')

def connect():
    con = sqlite3.connect(DB)
    con.execute('CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL, balance REAL NOT NULL)')
    con.execute('CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, description TEXT NOT NULL, kind TEXT NOT NULL, amount REAL NOT NULL)')
    con.execute('CREATE TABLE IF NOT EXISTS holdings (id INTEGER PRIMARY KEY, ticker TEXT NOT NULL, shares REAL NOT NULL, price REAL NOT NULL)')
    cols = [r[1] for r in con.execute('PRAGMA table_info(holdings)')]
    for field, definition in [('account', "TEXT DEFAULT 'Brokerage'"), ('avg_cost', 'REAL DEFAULT 0'), ('updated_at', 'TEXT')]:
        if field not in cols: con.execute(f'ALTER TABLE holdings ADD COLUMN {field} {definition}')
    con.commit()
    return con

con = connect()
st.title('💼 Private Wealth AI')
st.caption('Your personal wealth office • Local-first MVP • Educational decision support, not autonomous trading')
page = st.sidebar.radio('Workspace', ['Overview', 'Accounts', 'Portfolio', 'Cash Flow', 'Financial Planner', 'Advisor'])
accounts = pd.read_sql_query('SELECT * FROM accounts', con)
transactions = pd.read_sql_query('SELECT * FROM transactions', con)
holdings = pd.read_sql_query('SELECT * FROM holdings', con)
assets = accounts.loc[accounts.category != 'Debt', 'balance'].sum() + (holdings.shares * holdings.price).sum() if not holdings.empty else accounts.loc[accounts.category != 'Debt', 'balance'].sum()
debts = accounts.loc[accounts.category == 'Debt', 'balance'].sum()
networth = assets - debts
money = lambda n: f'${n:,.2f}'

if page == 'Overview':
    a,b,c = st.columns(3)
    a.metric('Total assets', money(assets)); b.metric('Total debts', money(debts)); c.metric('Net worth', money(networth))
    st.info('Add your accounts and investments to begin. Do not enter passwords, account numbers, or other secrets.')
    if not accounts.empty:
        st.subheader('Account balances')
        st.bar_chart(accounts.set_index('name')['balance'])
    if not holdings.empty:
        st.subheader('Investments by ticker')
        chart = holdings.assign(value=holdings.shares * holdings.price)
        st.plotly_chart(px.pie(chart, values='value', names='ticker'), use_container_width=True)

elif page == 'Accounts':
    st.subheader('Add or update an account')
    with st.form('account'):
        name = st.text_input('Account nickname (not account number)')
        category = st.selectbox('Type', ['Cash','Investment','Property','Other asset','Debt'])
        balance = st.number_input('Balance ($; enter debt as a positive amount)', min_value=0.0, step=100.0)
        if st.form_submit_button('Save account') and name.strip():
            con.execute('DELETE FROM accounts WHERE name=?', (name.strip(),))
            con.execute('INSERT INTO accounts(name,category,balance) VALUES (?,?,?)',(name.strip(),category,balance))
            con.commit(); st.rerun()
    st.dataframe(accounts, hide_index=True, use_container_width=True)
    if not accounts.empty:
        with st.form('delete_account'):
            item = st.selectbox('Delete account', accounts['name'].tolist())
            if st.form_submit_button('Delete selected'):
                con.execute('DELETE FROM accounts WHERE name=?',(item,)); con.commit(); st.rerun()

elif page == 'Portfolio':
    st.subheader('Your holdings')
    st.caption('Enter positions manually. The app stores them on this Mac in wealth.db. Market quotes are optional and may be delayed or unavailable.')
    with st.form('holding'):
        account = st.text_input('Account nickname', value='Brokerage')
        ticker = st.text_input('Ticker (e.g. VOO)').upper().strip()
        shares = st.number_input('Shares owned', min_value=0.0, step=0.1, format='%.6f')
        avg_cost = st.number_input('Average purchase price per share ($)', min_value=0.0, step=0.01)
        price = st.number_input('Current price per share ($)', min_value=0.0, step=0.01)
        if st.form_submit_button('Save position') and ticker and account.strip() and shares > 0:
            con.execute('DELETE FROM holdings WHERE ticker=? AND account=?', (ticker, account.strip()))
            con.execute('INSERT INTO holdings(ticker,shares,price,account,avg_cost,updated_at) VALUES (?,?,?,?,?,datetime("now"))', (ticker,shares,price,account.strip(),avg_cost))
            con.commit(); st.rerun()
    if st.button('Refresh available market prices (Yahoo Finance)'):
        try:
            import yfinance as yf
            updated=0; failed=[]
            for _,h in holdings.iterrows():
                try:
                    hist=yf.Ticker(h.ticker).history(period='5d', auto_adjust=False)
                    if hist.empty: raise ValueError('No price')
                    latest=float(hist['Close'].dropna().iloc[-1])
                    if latest<=0: raise ValueError('Invalid price')
                    con.execute('UPDATE holdings SET price=?,updated_at=datetime("now") WHERE id=?',(latest,int(h.id)))
                    updated+=1
                except Exception: failed.append(h.ticker)
            con.commit()
            st.success(f'Refreshed {updated} position(s).')
            if failed: st.warning('No valid quote for: '+', '.join(failed))
            st.rerun()
        except ImportError: st.error('Install dependencies from requirements.txt to enable price refresh.')
    if not holdings.empty:
        view=holdings.copy()
        view['market_value']=view.shares*view.price
        view['cost_basis']=view.shares*view.avg_cost
        view['unrealized_gain']=view.market_value-view.cost_basis
        view['gain_pct']=view.apply(lambda r: 100*r.unrealized_gain/r.cost_basis if r.cost_basis>0 else float('nan'),axis=1)
        total=view.market_value.sum()
        view['allocation_pct']=100*view.market_value/total if total else 0
        st.dataframe(view[['account','ticker','shares','avg_cost','price','market_value','unrealized_gain','gain_pct','allocation_pct','updated_at']],hide_index=True,use_container_width=True)
        a,b,c=st.columns(3)
        a.metric('Market value',money(total))
        b.metric('Unrealized gain/loss',money(view.unrealized_gain.sum()))
        c.metric('Largest position',f'{view.allocation_pct.max():.1f}%')
        if view.allocation_pct.max()>30: st.warning('Concentration alert: a single position exceeds 30% of tracked holdings.')
        st.caption('Unrealized gain assumes entered average cost is accurate and excludes fees, taxes, dividends, and prior realized trades.')
        with st.form('delete_holding'):
            item=st.selectbox('Remove position',view.id.tolist(),format_func=lambda i: f"{view.loc[view.id==i,'account'].iloc[0]} — {view.loc[view.id==i,'ticker'].iloc[0]}")
            if st.form_submit_button('Remove selected position'):
                con.execute('DELETE FROM holdings WHERE id=?',(int(item),));con.commit();st.rerun()
    st.warning('Avoid double counting: if you enter individual positions here, do not also enter their combined market value as an account asset.')

elif page == 'Cash Flow':
    st.subheader('Monthly cash flow entries')
    with st.form('cashflow'):
        description=st.text_input('Description')
        kind=st.selectbox('Kind',['Income','Expense'])
        amount=st.number_input('Monthly amount ($)',min_value=0.0,step=50.0)
        if st.form_submit_button('Add entry') and description.strip():
            con.execute('INSERT INTO transactions(description,kind,amount) VALUES (?,?,?)',(description.strip(),kind,amount))
            con.commit(); st.rerun()
    income=transactions.loc[transactions.kind=='Income','amount'].sum() if not transactions.empty else 0
    expenses=transactions.loc[transactions.kind=='Expense','amount'].sum() if not transactions.empty else 0
    x,y,z=st.columns(3)
    x.metric('Monthly income',money(income)); y.metric('Monthly expenses',money(expenses)); z.metric('Monthly surplus',money(income-expenses))
    st.dataframe(transactions,hide_index=True,use_container_width=True)
    if not transactions.empty:
        with st.form('delete_cashflow'):
            entry=st.selectbox('Delete entry',transactions.id.tolist(),format_func=lambda i: f'{i}: '+transactions.loc[transactions.id==i,'description'].iloc[0])
            if st.form_submit_button('Delete entry'):
                con.execute('DELETE FROM transactions WHERE id=?',(entry,)); con.commit(); st.rerun()

elif page == 'Financial Planner':
    st.subheader('Long-term investment scenario')
    initial=st.number_input('Starting invested amount ($)',min_value=0.0,value=5000.0,step=500.0)
    monthly=st.number_input('Monthly contributions ($)',min_value=0.0,value=1000.0,step=100.0)
    annual=st.slider('Assumed annual nominal return (%)',-10.0,15.0,7.0,0.5)
    years=st.slider('Years',1,40,10)
    values=[initial]
    for _ in range(years*12): values.append(values[-1]*(1+annual/100/12)+monthly)
    st.metric('Projected balance',money(values[-1]))
    st.line_chart(pd.DataFrame({'Portfolio value':values},index=[i/12 for i in range(len(values))]),x_label='Years')
    st.caption('Illustrative constant-return projection, not a forecast. Excludes taxes, fees, inflation, and market volatility.')

elif page == 'Advisor':
    st.subheader('Wealth Office — Rule-Based Advisor')
    st.caption('This free MVP uses transparent rules, not an external LLM. AI model integration is a later upgrade.')
    income=transactions.loc[transactions.kind=='Income','amount'].sum() if not transactions.empty else 0
    expenses=transactions.loc[transactions.kind=='Expense','amount'].sum() if not transactions.empty else 0
    cash=accounts.loc[accounts.category=='Cash','balance'].sum() if not accounts.empty else 0
    st.write(f'**Your estimated net worth:** {money(networth)}')
    if expenses>0:
        months=cash/expenses
        st.write(f'**Cash reserve:** {months:.1f} months of recorded expenses.')
        if months<3: st.warning('Consider prioritizing an emergency reserve of 3–6 months of essential expenses.')
        else: st.success('Your recorded cash covers at least three months of recorded expenses.')
    else: st.info('Enter monthly expenses to calculate emergency-fund coverage.')
    if income>0:
        rate=(income-expenses)/income
        st.write(f'**Monthly savings rate (before unrecorded items):** {rate:.1%}')
        if rate<0: st.warning('Recorded monthly expenses exceed income.')
    if debts>0: st.write('**Debt review:** Compare each debt’s interest rate before choosing accelerated payoff versus investing.')
    if not holdings.empty and (holdings.shares*holdings.price).sum()>0:
        weights=holdings.shares*holdings.price
        if weights.max()/weights.sum()>0.3: st.warning('Portfolio concentration: review diversification before adding to the largest position.')
    st.write('**Next step:** Build a written investment policy with your goals, horizon, liquidity needs, and acceptable drawdown.')

con.close()
