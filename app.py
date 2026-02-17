"""
Jim's Finance Tracker - A Streamlit App
Built with love for Nick's sponsor
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import os
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Jim's Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom dark theme CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stSidebar {
        background-color: #262730;
    }
    .stTextInput, .stNumberInput, .stSelectbox, .stDateInput, .stTimeInput {
        background-color: #262730;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    .income {
        color: #4ade80 !important;
    }
    .expense {
        color: #f87171 !important;
    }
    .stButton>button {
        background-color: #4ade80;
        color: #0e1117;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #22c55e;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Database setup
DB_PATH = Path(__file__).parent / "data" / "finance.db"

def init_db():
    """Initialize SQLite database with tables"""
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Categories table
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        icon TEXT DEFAULT '💰',
        is_income INTEGER DEFAULT 0
    )''')
    
    # Transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        amount REAL NOT NULL,
        category_id INTEGER,
        transaction_type TEXT NOT NULL,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )''')
    
    # Recurring bills table
    c.execute('''CREATE TABLE IF NOT EXISTS recurring_bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        amount REAL NOT NULL,
        due_day INTEGER NOT NULL,
        category_id INTEGER,
        is_active INTEGER DEFAULT 1,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )''')
    
    # Insert default categories if empty
    c.execute("SELECT COUNT(*) FROM categories")
    if c.fetchone()[0] == 0:
        default_categories = [
            ('Income', '💵', 1),
            ('Rent', '🏠', 0),
            ('Utilities', '⚡', 0),
            ('Food', '🍔', 0),
            ('Transportation', '🚗', 0),
            ('Insurance', '🛡️', 0),
            ('Phone', '📱', 0),
            ('Entertainment', '🎬', 0),
            ('Healthcare', '🏥', 0),
            ('Savings', '🏦', 0),
            ('Other', '📦', 0),
        ]
        c.executemany("INSERT INTO categories (name, icon, is_income) VALUES (?, ?, ?)", default_categories)
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    import sqlite3
    return sqlite3.connect(DB_PATH)

# Initialize database
if not DB_PATH.exists():
    init_db()
else:
    init_db()

# Helper functions
def get_categories(transaction_type=None):
    """Get categories from database"""
    conn = get_db_connection()
    if transaction_type:
        if transaction_type == 'income':
            df = pd.read_sql("SELECT * FROM categories WHERE is_income = 1", conn)
        else:
            df = pd.read_sql("SELECT * FROM categories WHERE is_income = 0", conn)
    else:
        df = pd.read_sql("SELECT * FROM categories", conn)
    conn.close()
    return df

def get_transactions(limit=100):
    """Get transactions from database"""
    conn = get_db_connection()
    df = pd.read_sql(f"""
        SELECT t.id, t.date, t.amount, t.transaction_type, t.notes, 
               c.name as category, c.icon as category_icon
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        ORDER BY t.date DESC, t.id DESC
        LIMIT {limit}
    """, conn)
    conn.close()
    return df

def add_transaction(date_val, amount, category_id, transaction_type, notes):
    """Add a new transaction"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO transactions (date, amount, category_id, transaction_type, notes) 
                 VALUES (?, ?, ?, ?, ?)""",
              (date_val, amount, category_id, transaction_type, notes))
    conn.commit()
    conn.close()

def get_recurring_bills():
    """Get recurring bills"""
    conn = get_db_connection()
    df = pd.read_sql("""
        SELECT b.id, b.name, b.amount, b.due_day, b.is_active,
               c.name as category, c.icon as category_icon
        FROM recurring_bills b
        LEFT JOIN categories c ON b.category_id = c.id
        ORDER BY b.due_day
    """, conn)
    conn.close()
    return df

def add_recurring_bill(name, amount, due_day, category_id):
    """Add a recurring bill"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO recurring_bills (name, amount, due_day, category_id) 
                 VALUES (?, ?, ?, ?)""", (name, amount, due_day, category_id))
    conn.commit()
    conn.close()

def delete_transaction(tx_id):
    """Delete a transaction"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
    conn.commit()
    conn.close()

def get_monthly_summary(year=None, month=None):
    """Get monthly income/expense summary"""
    conn = get_db_connection()
    if year and month:
        filter_str = f"WHERE strftime('%Y', date) = '{year}' AND strftime('%m', date) = '{month:02d}'"
    else:
        filter_str = ""
    
    df = pd.read_sql(f"""
        SELECT 
            SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END) as total_expense
        FROM transactions
        {filter_str}
    """, conn)
    conn.close()
    return df

def get_category_breakdown(transaction_type='expense', year=None, month=None):
    """Get spending by category"""
    conn = get_db_connection()
    if year and month:
        filter_str = f"AND strftime('%Y', t.date) = '{year}' AND strftime('%m', t.date) = '{month:02d}'"
    else:
        filter_str = ""
    
    df = pd.read_sql(f"""
        SELECT c.name, c.icon, SUM(t.amount) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.transaction_type = '{transaction_type}' {filter_str}
        GROUP BY c.id
        ORDER BY total DESC
    """, conn)
    conn.close()
    return df

# Sidebar navigation
st.sidebar.title("💰 Jim's Finance Tracker")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["📊 Dashboard", "➕ Add Transaction", "📋 Transactions", "🔄 Recurring Bills", "📁 Import CSV", "📈 Reports"]
)

# Get current month/year for defaults
today = date.today()
current_year = today.year
current_month = today.month

# Page: Dashboard
if page == "📊 Dashboard":
    st.title("📊 Dashboard")
    
    # Monthly summary
    col1, col2, col3 = st.columns(3)
    
    summary = get_monthly_summary(current_year, current_month)
    income = summary['total_income'].iloc[0] or 0
    expense = summary['total_expense'].iloc[0] or 0
    balance = income - expense
    
    with col1:
        st.metric("💵 Monthly Income", f"${income:,.2f}")
    with col2:
        st.metric("💸 Monthly Expenses", f"${expense:,.2f}")
    with col3:
        st.metric("📈 Balance", f"${balance:,.2f}", delta=balance)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💳 Spending by Category")
        cat_breakdown = get_category_breakdown('expense', current_year, current_month)
        if not cat_breakdown.empty:
            fig = px.pie(
                cat_breakdown, 
                values='total', 
                names='name',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                legend=dict(orientation="h", yanchor="bottom", y=-0.2)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expenses recorded this month")
    
    with col2:
        st.subheader("📈 Income vs Expenses")
        # Get last 6 months data
        months_data = []
        for i in range(5, -1, -1):
            from datetime import timedelta
            d = today - timedelta(days=30*i)
            m = d.month
            y = d.year
            s = get_monthly_summary(y, m)
            months_data.append({
                'month': d.strftime('%b %Y'),
                'income': s['total_income'].iloc[0] or 0,
                'expense': s['total_expense'].iloc[0] or 0
            })
        
        df_trend = pd.DataFrame(months_data)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_trend['month'], y=df_trend['income'], name='Income', marker_color='#4ade80'))
        fig.add_trace(go.Bar(x=df_trend['month'], y=df_trend['expense'], name='Expenses', marker_color='#f87171'))
        fig.update_layout(
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            legend=dict(orientation="h", yanchor="bottom", y=-0.2)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Upcoming bills
    st.markdown("---")
    st.subheader("📅 Upcoming Bills This Month")
    
    bills = get_recurring_bills()
    if not bills.empty:
        bills_due = bills[(bills['due_day'] >= today.day) & (bills['is_active'] == 1)]
        if not bills_due.empty:
            for _, bill in bills_due.iterrows():
                st.write(f"🔔 **{bill['name']}** - ${bill['amount']:,.2f} (due on the {bill['due_day']}th)")
        else:
            st.info("No more bills due this month!")
    else:
        st.info("No recurring bills set up")

# Page: Add Transaction
elif page == "➕ Add Transaction":
    st.title("➕ Add Transaction")
    
    with st.form("add_transaction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_type = st.selectbox("Type", ["expense", "income"], format_func=lambda x: "💸 Expense" if x == "expense" else "💵 Income")
            date_val = st.date_input("Date", today)
        
        with col2:
            amount = st.number_input("Amount", min_value=0.01, step=0.01, format="%.2f")
            categories = get_categories(transaction_type)
            category = st.selectbox("Category", categories['id'], format_func=lambda x: categories[categories['id'] == x]['icon'].values[0] + " " + categories[categories['id'] == x]['name'].values[0])
        
        notes = st.text_input("Notes (optional)")
        
        submitted = st.form_submit_button("Add Transaction", use_container_width=True)
        
        if submitted:
            if amount > 0:
                add_transaction(date_val, amount, category, transaction_type, notes)
                st.success(f"Transaction added: {transaction_type} of ${amount:,.2f}")
            else:
                st.error("Please enter a valid amount")

# Page: Transactions
elif page == "📋 Transactions":
    st.title("📋 Transactions")
    
    df = get_transactions(200)
    
    if not df.empty:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            filter_type = st.selectbox("Filter by type", ["all", "income", "expense"], format_func=lambda x: "All" if x == "all" else ("💵 Income" if x == "income" else "💸 Expense"))
        with col2:
            filter_month = st.selectbox("Filter by month", ["all"] + [d.strftime('%Y-%m') for d in pd.date_range(end=today, periods=12, freq='MS')[::-1]])
        
        if filter_type != "all":
            df = df[df['transaction_type'] == filter_type]
        
        if filter_month != "all":
            df = df[df['date'].str.startswith(filter_month)]
        
        # Display
        for _, row in df.iterrows():
            icon = "💵" if row['transaction_type'] == 'income' else "💸"
            color = "#4ade80" if row['transaction_type'] == 'income' else "#f87171"
            with st.expander(f"{icon} {row['date']} - ${row['amount']:,.2f}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Category:** {row['category_icon']} {row['category']}")
                    if row['notes']:
                        st.write(f"**Notes:** {row['notes']}")
                with col2:
                    if st.button("🗑️ Delete", key=f"del_{row['id']}"):
                        delete_transaction(row['id'])
                        st.rerun()
    else:
        st.info("No transactions yet. Add one to get started!")

# Page: Recurring Bills
elif page == "🔄 Recurring Bills":
    st.title("🔄 Recurring Bills")
    
    # Add new bill
    with st.expander("➕ Add New Bill"):
        with st.form("add_bill_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Bill Name")
                amount = st.number_input("Amount", min_value=0.01, step=0.01, format="%.2f")
            with col2:
                due_day = st.number_input("Due Day (1-28)", min_value=1, max_value=28, value=1)
                categories = get_categories('expense')
                category = st.selectbox("Category", categories['id'], format_func=lambda x: categories[categories['id'] == x]['icon'].values[0] + " " + categories[categories['id'] == x]['name'].values[0])
            
            submitted = st.form_submit_button("Add Bill")
            
            if submitted:
                add_recurring_bill(name, amount, due_day, category)
                st.success(f"Bill '{name}' added!")
                st.rerun()
    
    # Display bills
    bills = get_recurring_bills()
    
    if not bills.empty:
        st.subheader("Your Bills")
        
        for _, bill in bills.iterrows():
            status = "✅ Active" if bill['is_active'] else "⏸️ Paused"
            color = "green" if bill['is_active'] else "gray"
            with st.expander(f"{bill['name']} - ${bill['amount']:,.2f} ({status})"):
                st.write(f"**Amount:** ${bill['amount']:,.2f}")
                st.write(f"**Due Day:** {bill['due_day']}th of each month")
                st.write(f"**Category:** {bill['category_icon']} {bill['category']}")
    else:
        st.info("No recurring bills. Add one above!")

# Page: Import CSV
elif page == "📁 Import CSV":
    st.title("📁 Import CSV")
    
    st.markdown("""
    Upload a bank CSV to import transactions. 
    
    **Expected columns:** Date, Amount (positive for income, negative for expense), Description/Memo
    """)
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.write("Preview:")
            st.dataframe(df.head())
            
            st.info("👆 Please map your columns below:")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                date_col = st.selectbox("Date column", df.columns)
            with col2:
                amount_col = st.selectbox("Amount column", df.columns)
            with col3:
                desc_col = st.selectbox("Description column", df.columns)
            
            if st.button("Import Transactions"):
                # Map and clean data
                import_df = df[[date_col, amount_col, desc_col]].copy()
                import_df.columns = ['date', 'amount', 'description']
                
                # Convert date
                import_df['date'] = pd.to_datetime(import_df['date'])
                
                # Determine type and categorize
                categories = get_categories()
                expense_cats = categories[categories['is_income'] == 0]
                income_cats = categories[categories['is_income'] == 1]
                
                added = 0
                for _, row in import_df.iterrows():
                    if row['amount'] > 0:
                        tx_type = 'income'
                        cat_id = income_cats.iloc[0]['id']
                    else:
                        tx_type = 'expense'
                        # Try to auto-categorize based on description
                        desc_lower = row['description'].lower() if pd.notna(row['description']) else ''
                        cat_id = None
                        
                        # Simple keyword matching
                        keywords = {
                            'food': ['grocery', 'restaurant', 'food', 'coffee', 'cafe'],
                            'transportation': ['gas', 'fuel', 'uber', 'lyft', 'parking'],
                            'utilities': ['electric', 'water', 'gas', 'internet', 'phone'],
                            'entertainment': ['netflix', 'spotify', 'movie', 'game'],
                        }
                        
                        for cat_name, words in keywords.items():
                            if any(w in desc_lower for w in words):
                                match = expense_cats[expense_cats['name'].str.lower() == cat_name]
                                if not match.empty:
                                    cat_id = match.iloc[0]['id']
                                    break
                        
                        if cat_id is None:
                            cat_id = expense_cats.iloc[0]['id']
                    
                    add_transaction(
                        row['date'].strftime('%Y-%m-%d'),
                        abs(row['amount']),
                        cat_id,
                        tx_type,
                        row['description']
                    )
                    added += 1
                
                st.success(f"Imported {added} transactions!")
                
        except Exception as e:
            st.error(f"Error: {e}")

# Page: Reports
elif page == "📈 Reports":
    st.title("📈 Reports")
    
    # Year selector
    year = st.selectbox("Select Year", list(range(2023, today.year + 1)), index=list(range(2023, today.year + 1)).index(today.year))
    
    # Monthly breakdown
    st.subheader(f"Monthly Summary for {year}")
    
    months = []
    for m in range(1, 13):
        if year == today.year and m > today.month:
            break
        s = get_monthly_summary(year, m)
        months.append({
            'Month': datetime(year, m, 1).strftime('%B'),
            'Income': s['total_income'].iloc[0] or 0,
            'Expenses': s['total_expense'].iloc[0] or 0,
            'Net': (s['total_income'].iloc[0] or 0) - (s['total_expense'].iloc[0] or 0)
        })
    
    df_report = pd.DataFrame(months)
    
    # Display table
    st.dataframe(
        df_report.style.format({
            'Income': '${:,.2f}',
            'Expenses': '${:,.2f}',
            'Net': '${:,.2f}'
        }).applymap(lambda x: 'color: #4ade80' if x > 0 else 'color: #f87171', subset=['Net']),
        use_container_width=True
    )
    
    # Year totals
    total_income = df_report['Income'].sum()
    total_expenses = df_report['Expenses'].sum()
    total_net = total_income - total_expenses
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Income", f"${total_income:,.2f}")
    with col2:
        st.metric("Total Expenses", f"${total_expenses:,.2f}")
    with col3:
        st.metric("Annual Net", f"${total_net:,.2f}", delta=total_net)
    
    # Category breakdown for year
    st.markdown("---")
    st.subheader(f"Category Breakdown for {year}")
    
    cat_year = get_category_breakdown('expense', year, None)
    if not cat_year.empty:
        fig = px.bar(
            cat_year.head(10), 
            x='total', 
            y='name', 
            orientation='h',
            title='Top Spending Categories',
            color='total',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            yaxis={'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(f"💰 Built with ❤️ for Jim")
st.sidebar.markdown(f"📅 Last updated: {today.strftime('%B %d, %Y')}")
