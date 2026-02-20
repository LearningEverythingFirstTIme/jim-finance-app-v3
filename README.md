# Jim's Finance Tracker

A modern personal finance tracking app built with SvelteKit and Supabase.

## Features

- **📊 Dashboard** - Balance, monthly income/expense, spending pie chart, 6-month trend bar chart
- **➕ Add Transaction** - Quick logging with date, amount, category, notes
- **📋 Transactions** - View and delete past transactions with filtering
- **🔄 Recurring Bills** - Track monthly bills with due dates
- **📁 Import CSV** - Upload bank exports, auto-categorize based on description
- **📈 Reports** - Monthly/annual summaries, category breakdowns

## Tech Stack

- **Frontend:** SvelteKit
- **Backend:** Supabase (Auth + Database)
- **Styling:** Tailwind CSS
- **Charts:** Chart.js
- **Deployment:** Vercel

## Prerequisites

- Node.js 18+
- A Supabase project with the following tables:
  - `categories` (id, name, icon, is_income)
  - `transactions` (id, date, amount, category_id, transaction_type, notes, created_at)
  - `recurring_bills` (id, name, amount, due_day, category_id, is_active)
  - `savings_goals` (id, name, target_amount, current_amount, deadline, is_active)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/LearningEverythingFirstTIme/jim-finance-app.git
cd jim-finance-app
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the root directory:
```env
PUBLIC_SUPABASE_URL=your_supabase_url
PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

4. Start the development server:
```bash
npm run dev
```

5. Open [http://localhost:5173](http://localhost:5173) in your browser.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PUBLIC_SUPABASE_URL` | Your Supabase project URL |
| `PUBLIC_SUPABASE_ANON_KEY` | Your Supabase anonymous key |

## Categories

The app uses the following categories:
- Income 💵
- Rent 🏠
- Utilities 💡
- Food 🍔
- Transportation 🚗
- Insurance 🛡️
- Phone 📱
- Entertainment 🎬
- Healthcare 🏥
- Savings 💰
- Other 📦

## Deployment to Vercel

### Option 1: Vercel CLI

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel --prod
```

### Option 2: GitHub Integration

1. Push your code to GitHub
2. Connect your repository to Vercel dashboard
3. Add environment variables in Vercel settings
4. Deploy!

## Database Schema

The app expects these tables in Supabase:

```sql
-- Categories
CREATE TABLE categories (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  icon TEXT,
  is_income INTEGER DEFAULT 0
);

-- Transactions
CREATE TABLE transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL,
  amount REAL NOT NULL,
  category_id INTEGER REFERENCES categories(id),
  transaction_type TEXT NOT NULL,
  notes TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Recurring Bills
CREATE TABLE recurring_bills (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  amount REAL NOT NULL,
  due_day INTEGER NOT NULL,
  category_id INTEGER REFERENCES categories(id),
  is_active INTEGER DEFAULT 1
);

-- Savings Goals
CREATE TABLE savings_goals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  target_amount REAL NOT NULL,
  current_amount REAL DEFAULT 0,
  deadline TEXT,
  is_active INTEGER DEFAULT 1
);

-- Insert default categories
INSERT INTO categories (id, name, icon, is_income) VALUES
(1, 'Income', '💵', 1),
(2, 'Rent', '🏠', 0),
(3, 'Utilities', '💡', 0),
(4, 'Food', '🍔', 0),
(5, 'Transportation', '🚗', 0),
(6, 'Insurance', '🛡️', 0),
(7, 'Phone', '📱', 0),
(8, 'Entertainment', '🎬', 0),
(9, 'Healthcare', '🏥', 0),
(10, 'Savings', '💰', 0),
(11, 'Other', '📦', 0);
```

## Auth Setup

The app uses Supabase Auth with email/password. Make sure to:
1. Enable Email provider in Supabase Auth settings
2. Configure your site URL in Supabase Auth settings

## Mobile-First Design

The app is designed mobile-first with:
- Bottom navigation for easy thumb access
- Touch-friendly buttons (min 48px)
- Responsive charts and tables
- Clean, minimal aesthetic
- Red for expenses, green for income

## License

MIT
