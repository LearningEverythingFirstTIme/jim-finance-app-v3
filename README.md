# Jim's Finance Tracker

A Streamlit app for tracking personal finances. Built with love for Jim.

## Features

- **📊 Dashboard** - Balance, monthly income/expense, spending pie chart, trend bar chart
- **➕ Add Transaction** - Quick logging with date, amount, category, notes
- **📋 Transactions** - View and delete past transactions with filtering
- **🔄 Recurring Bills** - Track monthly bills with due dates
- **📁 Import CSV** - Upload bank exports, auto-categorize based on description
- **📈 Reports** - Monthly/annual summaries, category breakdowns

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploying to Streamlit Cloud

1. Push to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/jim-finance-app.git
   git push -u origin main
   ```

2. Go to https://share.streamlit.io
3. Connect your GitHub and select this repo
4. Deploy!

## Tech Stack

- Streamlit (UI)
- SQLite (database)
- Plotly (charts)
- Pandas (data)

## Categories

Default categories: Income, Rent, Utilities, Food, Transportation, Insurance, Phone, Entertainment, Healthcare, Savings, Other
