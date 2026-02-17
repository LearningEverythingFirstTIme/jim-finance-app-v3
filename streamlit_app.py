"""
Jim's Finance Tracker - A Streamlit App
Built with love for Nick's sponsor
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import os
from pathlib import Path
from supabase import create_client, Client

# Configure page - collapsed sidebar by default for mobile friendliness
st.set_page_config(
    page_title="Jim's Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Supabase configuration - use st.secrets, fallback to env vars or hardcoded for dev
# In production (Streamlit Cloud), add these to Secrets:
# [supabase]
# url = "https://xxxx.supabase.co"
# key = "eyJxxx"
# app_password = "your-secure-password"

try:
    SUPABASE_URL = st.secrets.get("supabase", {}).get("url", "")
    SUPABASE_KEY = st.secrets.get("supabase", {}).get("key", "")
    APP_PASSWORD = st.secrets.get("supabase", {}).get("app_password", "jim123")
except:
    # Fallback for local development
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://qqwnnvoahcsrffacafig.supabase.co")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxd25udm9haGNzcmZmYWNhZmlnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEzNTMyNjMsImV4cCI6MjA4NjkyOTI2M30.7OfMaGSLbvMNFOoT2fGB1DhiojKWO6R1Uoo1N8PTAIE")
    APP_PASSWORD = os.environ.get("APP_PASSWORD", "jim123")

@st.cache_resource
def get_supabase_client() -> Client:
    """Create Supabase client"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Supabase client
supabase = get_supabase_client()

# Password protection
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Simple password check (change this to something more secure in production)

def check_password():
    """Show login screen if not authenticated"""
    if st.session_state.authenticated:
        return True
    
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 50px auto;
            padding: 30px;
            background-color: #262730;
            border-radius: 10px;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🔐 Jim's Finance Tracker")
    st.write("Please enter your password to access the app:")
    
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if password == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")
    
    st.markdown("---")
    st.caption("Contact Nick if you forgot your password")
    return False

if not check_password():
    st.stop()

# Custom dark theme CSS - Mobile responsive
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
    
    /* Mobile: Hide sidebar nav, show top nav instead */
    @media (max-width: 768px) {
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        .stRadio > div {
            flex-direction: row !important;
            flex-wrap: wrap !important;
            justify-content: center;
        }
        div[data-testid="stRadio"] > div > label {
            padding: 8px 12px !important;
            margin: 4px !important;
            font-size: 0.8rem !important;
        }
        div[data-testid="stMetric"] {
            padding: 0.5rem !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
        }
        /* Mobile form improvements - stack properly and larger touch targets */
        .stForm > div[data-testid="stFormRow"] {
            flex-direction: column !important;
            gap: 0.75rem !important;
        }
        .stButton > button {
            min-height: 48px !important;
            font-size: 1rem !important;
            width: 100% !important;
            margin-top: 0.5rem !important;
        }
    }
    /* Quick Add section styling */
    .quick-add-header {
        font-size: 1.1rem;
        font-weight: 600;
    }
    /* Delete confirmation modal */
    .delete-confirm {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #f87171;
    }
</style>
""", unsafe_allow_html=True)

# Database is now Supabase - no local initialization needed
# Tables are created in Supabase Dashboard

# Helper functions using Supabase with error handling
def clear_cache():
    """Clear all cached data after modifications"""
    get_categories.clear()
    get_transactions.clear()
    get_recurring_bills.clear()
    get_savings_goals.clear()
    get_monthly_summary.clear()
    get_category_breakdown.clear()

@st.cache_data(ttl=60)
def get_categories(transaction_type=None):
    """Get categories from Supabase"""
    try:
        query = supabase.table('categories').select('*')
        if transaction_type == 'income':
            query = query.eq('is_income', 1)
        elif transaction_type == 'expense':
            query = query.eq('is_income', 0)
        result = query.execute()
        return pd.DataFrame(result.data) if result.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to load categories: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_transactions(limit=100):
    """Get transactions from Supabase"""
    try:
        result = supabase.table('transactions').select('id, date, amount, transaction_type, notes, category_id').order('date', desc=True).order('id', desc=True).limit(limit).execute()
        df = pd.DataFrame(result.data) if result.data else pd.DataFrame()
        if not df.empty:
            # Join with categories to get category name and icon
            try:
                cats = supabase.table('categories').select('id, name, icon').execute()
                if cats.data:
                    cats_df = pd.DataFrame(cats.data)
                    df = df.merge(cats_df, left_on='category_id', right_on='id', how='left', suffixes=('', '_cat'))
                    df = df.rename(columns={'name': 'category', 'icon': 'category_icon'})
            except Exception:
                df['category'] = 'Unknown'
                df['category_icon'] = '❓'
        return df
    except Exception as e:
        st.error(f"Failed to load transactions: {e}")
        return pd.DataFrame()

def add_transaction(date_val, amount, category_id, transaction_type, notes):
    """Add a new transaction to Supabase"""
    try:
        supabase.table('transactions').insert({
            'date': date_val.strftime('%Y-%m-%d') if isinstance(date_val, (date, datetime)) else str(date_val),
            'amount': amount,
            'category_id': category_id,
            'transaction_type': transaction_type,
            'notes': notes
        }).execute()
        clear_cache()
        return True
    except Exception as e:
        st.error(f"Failed to add transaction: {e}")
        return False

@st.cache_data(ttl=60)
def get_recurring_bills():
    """Get recurring bills from Supabase"""
    try:
        result = supabase.table('recurring_bills').select('*').order('due_day').execute()
        df = pd.DataFrame(result.data) if result.data else pd.DataFrame()
        if not df.empty:
            try:
                cats = supabase.table('categories').select('id, name, icon').execute()
                if cats.data:
                    cats_df = pd.DataFrame(cats.data)
                    df = df.merge(cats_df, left_on='category_id', right_on='id', how='left', suffixes=('', '_cat'))
                    df = df.rename(columns={'name': 'category', 'icon': 'category_icon'})
            except Exception:
                df['category'] = 'Unknown'
                df['category_icon'] = '❓'
        return df
    except Exception as e:
        st.error(f"Failed to load recurring bills: {e}")
        return pd.DataFrame()

def add_recurring_bill(name, amount, due_day, category_id):
    """Add a recurring bill to Supabase"""
    try:
        supabase.table('recurring_bills').insert({
            'name': name,
            'amount': amount,
            'due_day': due_day,
            'category_id': category_id
        }).execute()
        clear_cache()
        return True
    except Exception as e:
        st.error(f"Failed to add recurring bill: {e}")
        return False

def delete_transaction(tx_id):
    """Delete a transaction from Supabase"""
    try:
        supabase.table('transactions').delete().eq('id', tx_id).execute()
        clear_cache()
        return True
    except Exception as e:
        st.error(f"Failed to delete transaction: {e}")
        return False

@st.cache_data(ttl=60)
def get_monthly_summary(year=None, month=None):
    """Get monthly income/expense summary from Supabase"""
    try:
        query = supabase.table('transactions').select('amount, transaction_type')
        if year and month:
            start_date = f"{year}-{month:02d}-01"
            if month == 12:
                end_date = f"{year+1}-01-01"
            else:
                end_date = f"{year}-{month+1:02d}-01"
            query = query.gte('date', start_date).lt('date', end_date)
        result = query.execute()
        df = pd.DataFrame(result.data) if result.data else pd.DataFrame()
        if df.empty:
            return pd.DataFrame([{'total_income': 0, 'total_expense': 0}])
        income = df[df['transaction_type'] == 'income']['amount'].sum()
        expense = df[df['transaction_type'] == 'expense']['amount'].sum()
        return pd.DataFrame([{'total_income': income, 'total_expense': expense}])
    except Exception as e:
        st.error(f"Failed to load monthly summary: {e}")
        return pd.DataFrame([{'total_income': 0, 'total_expense': 0}])

@st.cache_data(ttl=60)
def get_category_breakdown(transaction_type='expense', year=None, month=None):
    """Get spending by category from Supabase"""
    try:
        query = supabase.table('transactions').select('amount, category_id, transaction_type')
        if year and month:
            start_date = f"{year}-{month:02d}-01"
            if month == 12:
                end_date = f"{year+1}-01-01"
            else:
                end_date = f"{year}-{month+1:02d}-01"
            query = query.gte('date', start_date).lt('date', end_date)
        result = query.execute()
        df = pd.DataFrame(result.data) if result.data else pd.DataFrame()
        if df.empty:
            return pd.DataFrame()
        df = df[df['transaction_type'] == transaction_type]
        if df.empty:
            return pd.DataFrame()
        try:
            cats = supabase.table('categories').select('id, name, icon').execute()
            if cats.data:
                cats_df = pd.DataFrame(cats.data)
                df = df.merge(cats_df, left_on='category_id', right_on='id', how='left')
                breakdown = df.groupby(['name', 'icon'])['amount'].sum().reset_index()
                breakdown.columns = ['name', 'icon', 'total']
                return breakdown.sort_values('total', ascending=False)
        except Exception:
            pass
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to load category breakdown: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_savings_goals():
    """Get all savings goals from Supabase"""
    try:
        result = supabase.table('savings_goals').select('*').order('is_active', desc=True).order('id', desc=True).execute()
        return pd.DataFrame(result.data) if result.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to load savings goals: {e}")
        return pd.DataFrame()

def add_savings_goal(name, target_amount, deadline=None):
    """Add a new savings goal to Supabase"""
    try:
        deadline_val = deadline.strftime('%Y-%m-%d') if deadline else None
        supabase.table('savings_goals').insert({
            'name': name,
            'target_amount': target_amount,
            'deadline': deadline_val
        }).execute()
        clear_cache()
        return True
    except Exception as e:
        st.error(f"Failed to add savings goal: {e}")
        return False

def update_savings_goal_amount(goal_id, amount_to_add):
    """Add to a savings goal's current amount in Supabase (atomic update)"""
    try:
        # Use atomic increment to avoid race conditions
        result = supabase.table('savings_goals').select('current_amount').eq('id', goal_id).execute()
        if result.data:
            current = result.data[0]['current_amount'] or 0
            supabase.table('savings_goals').update({'current_amount': current + amount_to_add}).eq('id', goal_id).execute()
            clear_cache()
            return True
        return False
    except Exception as e:
        st.error(f"Failed to update savings goal: {e}")
        return False

def delete_savings_goal(goal_id):
    """Delete a savings goal from Supabase"""
    try:
        supabase.table('savings_goals').delete().eq('id', goal_id).execute()
        clear_cache()
        return True
    except Exception as e:
        st.error(f"Failed to delete savings goal: {e}")
        return False

def toggle_savings_goal(goal_id):
    """Toggle a savings goal active status in Supabase"""
    try:
        result = supabase.table('savings_goals').select('is_active').eq('id', goal_id).execute()
        if result.data:
            current = result.data[0]['is_active'] or 0
            supabase.table('savings_goals').update({'is_active': 0 if current else 1}).eq('id', goal_id).execute()
            clear_cache()
            return True
        return False
    except Exception as e:
        st.error(f"Failed to toggle savings goal: {e}")
        return False

# Navigation - top for mobile, sidebar for desktop
pages = ["📊 Dashboard", "➕ Add Transaction", "📋 Transactions", "🔄 Recurring Bills", "🎯 Savings Goals", "📁 Import CSV", "📈 Reports"]

# Use tabs for mobile-friendly navigation
st.title("💰 Jim's Finance Tracker")

# Create a tab-like interface using radio buttons at the top
page = st.radio(
    "Navigate",
    pages + ["🔒 Logout"],
    horizontal=True,
    label_visibility="collapsed"
)

# Handle logout
if page == "🔒 Logout":
    st.session_state.authenticated = False
    st.rerun()

# Get current month/year for defaults
today = date.today()
current_year = today.year
current_month = today.month

# Page: Dashboard
if page == "📊 Dashboard":
    st.title("📊 Dashboard")
    
    # Check for empty state - onboarding
    transactions_check = get_transactions(1)
    is_empty = transactions_check.empty
    
    # Quick Add Section (expandable)
    with st.expander("⚡ Quick Add Transaction", expanded=not is_empty):
        # Use session state to preserve form values
        if 'quick_type' not in st.session_state:
            st.session_state.quick_type = 'expense'
        
        col1, col2, col3, col4 = st.columns([2, 2, 1.5, 1.5], gap="small")
        
        with col1:
            quick_amount = st.number_input("Amount", min_value=0.01, step=0.01, format="%.2f", key="quick_amount", label_visibility="collapsed", placeholder="0.00")
        with col2:
            quick_categories = get_categories()
            quick_category = st.selectbox("Category", quick_categories['id'], format_func=lambda x: quick_categories[quick_categories['id'] == x]['icon'].values[0] + " " + quick_categories[quick_categories['id'] == x]['name'].values[0], key="quick_category", label_visibility="collapsed")
        with col3:
            quick_type = st.selectbox("Type", ["expense", "income"], format_func=lambda x: "💸 Expense" if x == "expense" else "💵 Income", key="quick_type", label_visibility="visible")
        with col4:
            quick_submit = st.button("➕ Add", key="quick_add_btn", use_container_width=True)
        
        quick_note = st.text_input("Note (optional)", key="quick_note", placeholder="Add a note...")
        
        if quick_submit:
            if quick_amount > 0:
                add_transaction(today, quick_amount, quick_category, quick_type, quick_note)
                st.success(f"✅ Added: {quick_type} - ${quick_amount:,.2f}")
                st.rerun()
            else:
                st.error("Please enter an amount")
    
    # Onboarding message for empty state
    if is_empty:
        st.markdown("""
        <div style="background-color: #262730; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
            <h2 style="color: #4ade80; margin-bottom: 10px;">🎉 Welcome to Jim's Finance Tracker!</h2>
            <p style="color: #fafafa; margin-bottom: 15px;">Get started in just a few steps:</p>
            <ol style="color: #fafafa; text-align: left; max-width: 400px; margin: 0 auto;">
                <li style="margin-bottom: 8px;">Use <strong>Quick Add</strong> above to add your first transaction</li>
                <li style="margin-bottom: 8px;">Set up recurring bills in <strong>Recurring Bills</strong></li>
                <li style="margin-bottom: 8px;">Create savings goals in <strong>Savings Goals</strong></li>
                <li style="margin-bottom: 8px;">Import your bank transactions via <strong>Import CSV</strong></li>
            </ol>
            <p style="color: #4ade80; margin-top: 15px; font-weight: bold;">Add your first transaction above to get started!</p>
        </div>
        """, unsafe_allow_html=True)
    
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
            st.plotly_chart(fig, width='stretch')
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
        st.plotly_chart(fig, width='stretch')
    
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
    
    # Use session state to preserve form values
    if 'add_tx_type' not in st.session_state:
        st.session_state.add_tx_type = 'expense'
    
    col1, col2 = st.columns(2)
    
    with col1:
        transaction_type = st.selectbox("Type", ["expense", "income"], format_func=lambda x: "💸 Expense" if x == "expense" else "💵 Income", key="add_tx_type")
        date_val = st.date_input("Date", today)
    
    with col2:
        amount = st.number_input("Amount", min_value=0.01, step=0.01, format="%.2f")
        categories = get_categories(st.session_state.add_tx_type)
        category = st.selectbox("Category", categories['id'], format_func=lambda x: categories[categories['id'] == x]['icon'].values[0] + " " + categories[categories['id'] == x]['name'].values[0])
    
    notes = st.text_input("Notes (optional)")
    
    if st.button("Add Transaction", width='stretch'):
        if amount > 0:
            add_transaction(date_val, amount, category, st.session_state.add_tx_type, notes)
            st.success(f"Transaction added: {st.session_state.add_tx_type} of ${amount:,.2f}")
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
                    # Delete confirmation
                    confirm_key = f"confirm_del_{row['id']}"
                    if confirm_key not in st.session_state:
                        st.session_state[confirm_key] = False
                    
                    if not st.session_state[confirm_key]:
                        if st.button("🗑️ Delete", key=f"del_{row['id']}"):
                            st.session_state[confirm_key] = True
                            st.rerun()
                    else:
                        st.warning("Confirm?")
                        col_confirm1, col_confirm2 = st.columns(2)
                        with col_confirm1:
                            if st.button("✅ Yes", key=f"yes_{row['id']}"):
                                delete_transaction(row['id'])
                                st.session_state[confirm_key] = False
                                st.rerun()
                        with col_confirm2:
                            if st.button("❌ No", key=f"no_{row['id']}"):
                                st.session_state[confirm_key] = False
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

# Page: Savings Goals
elif page == "🎯 Savings Goals":
    st.title("🎯 Savings Goals")
    
    # Add new goal
    with st.expander("➕ Add New Savings Goal"):
        with st.form("add_goal_form"):
            col1, col2 = st.columns(2)
            with col1:
                goal_name = st.text_input("Goal Name", placeholder="e.g., Emergency Fund")
                target_amount = st.number_input("Target Amount", min_value=1.0, step=1.0, format="%.2f")
            with col2:
                deadline = st.date_input("Deadline (optional)", value=None)
            
            submitted = st.form_submit_button("Create Goal")
            
            if submitted:
                if goal_name and target_amount > 0:
                    add_savings_goal(goal_name, target_amount, deadline if deadline else None)
                    st.success(f"Goal '{goal_name}' created with target of ${target_amount:,.2f}!")
                    st.rerun()
                else:
                    st.error("Please enter a goal name and target amount")
    
    # Display goals
    goals = get_savings_goals()
    
    if not goals.empty:
        # Summary cards
        active_goals = goals[goals['is_active'] == 1]
        total_saved = active_goals['current_amount'].sum()
        total_target = active_goals['target_amount'].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Active Goals", len(active_goals))
        with col2:
            st.metric("Total Saved", f"${total_saved:,.2f}")
        with col3:
            remaining = max(0, total_target - total_saved)
            st.metric("Total Remaining", f"${remaining:,.2f}")
        
        st.markdown("---")
        
        for _, goal in goals.iterrows():
            progress = min(goal['current_amount'] / goal['target_amount'], 1.0) if goal['target_amount'] > 0 else 0
            percent = progress * 100
            remaining_amount = max(0, goal['target_amount'] - goal['current_amount'])
            
            status_icon = "✅" if goal['is_active'] else "⏸️"
            deadline_text = f" (Due: {goal['deadline']})" if goal['deadline'] else ""
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader(f"{status_icon} {goal['name']}")
                    st.progress(progress)
                    st.write(f"**${goal['current_amount']:,.2f}** / ${goal['target_amount']:,.2f} ({percent:.1f}%)")
                    if remaining_amount > 0:
                        st.caption(f"💰 ${remaining_amount:,.2f} remaining{deadline_text}")
                    else:
                        st.caption("🎉 Goal reached!")
                
                with col2:
                    # Action buttons
                    with st.form(f"add_to_goal_{goal['id']}"):
                        add_amount = st.number_input("Add amount", min_value=0.01, step=1.0, format="%.2f", key=f"amount_{goal['id']}")
                        if st.form_submit_button("➕ Add", use_container_width=True):
                            if add_amount > 0:
                                update_savings_goal_amount(goal['id'], add_amount)
                                st.success(f"Added ${add_amount:,.2f}!")
                                st.rerun()
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("⏸️", key=f"toggle_{goal['id']}", help="Pause/Resume"):
                            toggle_savings_goal(goal['id'])
                            st.rerun()
                    with col_btn2:
                        # Delete confirmation
                        confirm_key = f"confirm_goal_{goal['id']}"
                        if confirm_key not in st.session_state:
                            st.session_state[confirm_key] = False
                        
                        if not st.session_state[confirm_key]:
                            if st.button("🗑️", key=f"del_goal_{goal['id']}", help="Delete"):
                                st.session_state[confirm_key] = True
                                st.rerun()
                        else:
                            col_confirm1, col_confirm2 = st.columns(2)
                            with col_confirm1:
                                if st.button("✅", key=f"yes_goal_{goal['id']}"):
                                    delete_savings_goal(goal['id'])
                                    st.session_state[confirm_key] = False
                                    st.rerun()
                            with col_confirm2:
                                if st.button("❌", key=f"no_goal_{goal['id']}"):
                                    st.session_state[confirm_key] = False
                                    st.rerun()
                
                st.markdown("---")
    else:
        st.info("No savings goals yet. Create one above to start saving!")

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
        width='stretch'
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
        st.plotly_chart(fig, width='stretch')

# Footer
st.markdown("---")
st.markdown(f"💰 Built with ❤️ for Jim | 📅 {today.strftime('%B %d, %Y')}")
