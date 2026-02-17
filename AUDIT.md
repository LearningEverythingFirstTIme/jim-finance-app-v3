# Jim's Finance Tracker - Audit Report (Supabase Version)

**Date:** 2026-02-17  
**Auditor:** OpenClaw Agent  
**File:** `streamlit_app.py`  
**App Type:** Streamlit Personal Finance Web App  
**Database:** Supabase (refactored from SQLite)

---

## Executive Summary

The app has been refactored to use Supabase which is great for cloud deployment. However, there are **critical security vulnerabilities** (hardcoded credentials), **no error handling**, and several **performance issues**. The core functionality works but production deployment would expose the database and crash on any API error.

**Overall Assessment:** ⭐⭐⭐ (3/5) - Functional but needs security & reliability fixes

---

## 1. Critical Security Issues

### C1: Hardcoded Supabase Credentials (CRITICAL)
**Location:** Lines 21-28

```python
SUPABASE_URL = "https://qqwnnvoahcsrffacafig.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxd25udm9haGNzcmZmYWNhZmlnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEzNTMyNjMsImV4cCI6MjA4NjkyOTI2M30.7OfMaGSLbvMNFOoT2fGB1DhiojKWO6R1Uoo1N8PTAIE"
APP_PASSWORD = "jim123"
```

**Problem:** 
- Anyone with repo access can see the Supabase project URL and anon key
- The anon key is exposed in client-side JavaScript (Streamlit sends it to browser)
- Password is plaintext in source code

**Impact:** 
- Database can be accessed by anyone with the URL/key
- Attacker can read/write/delete all data
- Unauthorized access to the app

**Fix:**
```python
# Use Streamlit secrets (st.secrets.toml in .streamlit folder)
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")
APP_PASSWORD = st.secrets.get("app_password", "jim123")  # fallback for dev
```

---

### C2: Password Validation Timing Attack
**Location:** Line 46

```python
if password == APP_PASSWORD:
```

**Problem:** Direct string comparison is vulnerable to timing attacks. While unlikely to be exploited here, it's bad practice.

**Fix:**
```python
import hmac
if hmac.compare_digest(password, APP_PASSWORD):
```

---

## 2. Error Handling Gaps (HIGH PRIORITY)

### E1: No Try/Except on Any Supabase Calls
**Location:** All helper functions (lines 134-240)

**Problem:** Every database call can fail:
- Network connectivity issues
- Supabase service outages  
- Invalid data causing constraint violations
- Rate limiting

When errors occur, users see ugly Python tracebacks.

**Example of current code (no error handling):**
```python
def get_categories(transaction_type=None):
    if transaction_type:
        if transaction_type == 'income':
            result = supabase.table('categories').select('*').eq('is_income', 1).execute()
        else:
            result = supabase.table('categories').select('*').eq('is_income', 0).execute()
    else:
        result = supabase.table('categories').select('*').execute()
    return pd.DataFrame(result.data)  # Crashes if result.data is None
```

**Fix:**
```python
def get_categories(transaction_type=None):
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
```

---

### E2: No Input Validation
**Location:** `add_transaction()`, `add_recurring_bill()`, `add_savings_goal()`

**Problem:**
- No validation that amount is positive
- No validation on date ranges
- No validation on required fields

---

### E3: Missing Null Checks After Joins
**Location:** Lines 157-160, 175-178

```python
df = df.merge(cats_df, left_on='category_id', right_on='id', how='left', suffixes=('', '_cat'))
df = df.rename(columns={'name': 'category', 'icon': 'category_icon'})
```

**Problem:** If `category_id` references a deleted category, the merge produces null values. Code doesn't handle this gracefully.

---

## 3. Performance Issues

### P1: Redundant Category Queries
**Location:** Multiple functions query categories separately

- `get_transactions()` - queries categories (lines 157)
- `get_recurring_bills()` - queries categories (line 175)  
- `get_category_breakdown()` - queries categories (line 217)
- `get_categories()` - queries categories

Every function call fetches categories again. While cached, this adds latency.

**Fix:** Create a single cached category lookup:
```python
@st.cache_data(ttl=300)
def get_category_lookup():
    """Get all categories as a lookup dict for O(1) access"""
    result = supabase.table('categories').select('id, name, icon').execute()
    if not result.data:
        return {}
    df = pd.DataFrame(result.data)
    return df.set_index('id').to_dict('index')
```

---

### P2: Inefficient JOIN Pattern
**Location:** `get_transactions()` (lines 151-162)

```python
# Current: Two separate queries + pandas merge
result = supabase.table('transactions').select(...).execute()
df = pd.DataFrame(result.data)
cats = supabase.table('categories').select('id, name, icon').execute()
cats_df = pd.DataFrame(cats.data)
df = df.merge(cats_df, left_on='category_id', right_on='id', how='left')
```

**Better:** Use Supabase's `select()` with foreign table or do a single query:
```python
# Supabase can do this with proper foreign key setup
result = supabase.table('transactions').select('*, categories(name, icon)').execute()
```

---

### P3: No Connection Pooling
**Location:** Line 35

```python
supabase = get_supabase_client()
```

The client is created once but could benefit from explicit pooling configuration for high traffic.

---

### P4: LIKE Query for Date Filtering
**Location:** Lines 193-197, 207-212

```python
month_str = f"{year}-{month:02d}%"
result = supabase.table('transactions').select(...).like('date', month_str).execute()
```

**Problem:** Using `LIKE` on a date column can't use indexes efficiently. Better to use explicit range:
```python
start_date = f"{year}-{month:02d}-01"
if month == 12:
    end_date = f"{year+1}-01-01"
else:
    end_date = f"{year}-{month+1:02d}-01"
result = supabase.table('transactions').select(...).gte('date', start_date).lt('date', end_date).execute()
```

---

## 4. Race Conditions & Data Inconsistencies

### R1: Read-Then-Write on Savings Goals
**Location:** Lines 198-203

```python
def update_savings_goal_amount(goal_id, amount_to_add):
    # Get current amount
    result = supabase.table('savings_goals').select('current_amount').eq('id', goal_id).execute()
    if result.data:
        current = result.data[0]['current_amount'] or 0
        supabase.table('savings_goals').update({'current_amount': current + amount_to_add}).eq('id', goal_id).execute()
```

**Problem:** Classic race condition. If two users update simultaneously:
1. User A reads current = 100
2. User B reads current = 100  
3. User A writes 100 + 50 = 150
4. User B writes 100 + 75 = 175
5. Final value: 175 (should be 225)

**Fix:** Use Supabase RPC or atomic increment:
```python
# In Supabase, use RPC or database function
supabase.rpc('increment_savings_goal', {'goal_id': goal_id, 'amount': amount_to_add}).execute()

# Or use atomic update
supabase.table('savings_goals').update({'current_amount': supabase.raw('current_amount + ' + str(amount_to_add))}).eq('id', goal_id).execute()
```

---

### R2: No Transaction for Multi-Operation Changes
**Location:** CSV Import (lines 450-490)

If import fails halfway, you have partial data with no rollback.

---

## 5. Missing Features & Edge Cases

### F1: No Data Export
Users can't export their data for backup or to switch apps.

### F2: No Transaction Search
With 200 transactions, finding a specific one is tedious.

### F3: No Edit Transaction
Users can only delete, not edit existing transactions.

### F4: Category Deletion Not Handled
If a category is deleted from Supabase, transactions still reference it. No fallback display.

### F5: Empty State Edge Cases
- `get_monthly_summary` returns DataFrame with zeros but no income/expense columns if no data (line 188)
- Division by zero in savings goal progress if target_amount is 0

### F6: CSV Import Issues
- No validation of date formats
- Very basic auto-categorization (only 4 keyword categories)
- No preview before import
- No rollback capability

---

## 6. UX Improvements

| Issue | Description | Recommendation |
|-------|-------------|----------------|
| U1 | Delete confirmation is session-state heavy | Use Streamlit's `st.dialog()` (newer feature) |
| U2 | Progress bars in savings goals could show more info | Add days remaining, estimated completion date |
| U3 | Recurring bills show no summary total | Add total monthly bills metric at top |
| U4 | No way to mark bill as "paid" | Add paid status tracking |
| U5 | Date filtering uses LIKE instead of proper range | Fix for performance + correctness |

---

## 7. Supabase Schema Expectations

The code expects these tables with these columns:

| Table | Columns | Notes |
|-------|---------|-------|
| `categories` | id, name, icon, is_income | ✅ `is_income` is integer (0/1) |
| `transactions` | id, date, amount, category_id, transaction_type, notes | ✅ |
| `recurring_bills` | id, name, amount, due_day, category_id, is_active | ✅ |
| `savings_goals` | id, name, target_amount, current_amount, deadline, is_active | ✅ |

**Potential Issue:** `is_income` being integer (0/1) works but boolean would be cleaner. Ensure Supabase schema matches.

---

## Priority Action Items

### 🔴 MUST FIX (Before Production)

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| 1 | Move Supabase credentials to `st.secrets` | 10 min | Critical security |
| 2 | Move app password to `st.secrets` | 5 min | Critical security |
| 3 | Add try/except to all DB functions | 30 min | App stability |
| 4 | Add null checks after joins | 10 min | Crash prevention |
| 5 | Fix race condition in savings goals | 15 min | Data integrity |

### 🟡 SHOULD FIX (Before Daily Use)

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| 6 | Add CSV export functionality | 20 min | High |
| 7 | Add transaction search | 20 min | High |
| 8 | Fix date filtering (LIKE → range) | 15 min | Performance |
| 9 | Add category lookup cache | 15 min | Performance |
| 10 | Input validation on forms | 20 min | Data quality |

### 🟢 NICE TO HAVE

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| 11 | Add edit transaction | 30 min | Medium |
| 12 | Recurring bills summary | 10 min | Medium |
| 13 | Better delete confirmation UI | 15 min | Medium |
| 14 | Budget limits per category | 45 min | Low |

---

## Quick Wins (Can Fix Today)

### Fix 1: Security - Use st.secrets
```python
# At top of file
import streamlit as st

# Replace hardcoded values with:
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "") or "https://qqwnnvoahcsrffacafig.supabase.co"
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
APP_PASSWORD = st.secrets.get("app_password", "jim123")

# Create .streamlit/secrets.toml with:
# SUPABASE_URL = "your-url"
# SUPABASE_KEY = "your-key"  
# app_password = "secure-password"
```

### Fix 2: Error Handling Wrapper
```python
def safe_supabase_call(func, *args, **kwargs):
    """Wrapper for all Supabase calls"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return pd.DataFrame()  # Return empty on error
```

### Fix 3: Atomic Savings Update
```python
def update_savings_goal_amount(goal_id, amount_to_add):
    # Use RPC if available, otherwise this is a known limitation
    supabase.table('savings_goals').update({
        'current_amount': supabase.raw(f'current_amount + {amount_to_add}')
    }).eq('id', goal_id).execute()
    clear_cache()
```

---

## Summary

The refactor to Supabase was a good move for cloud deployment, but the app needs:

1. **Immediate security fixes** - credentials shouldn't be in code
2. **Error handling** - any network failure crashes the app  
3. **Data integrity** - race conditions can corrupt savings data
4. **Performance tuning** - reduce redundant queries

With these fixes, the app would be production-ready for daily use.