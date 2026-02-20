export const categories = [
  { id: 1, name: 'Income', icon: '💵', is_income: 1 },
  { id: 2, name: 'Rent', icon: '🏠', is_income: 0 },
  { id: 3, name: 'Utilities', icon: '💡', is_income: 0 },
  { id: 4, name: 'Food', icon: '🍔', is_income: 0 },
  { id: 5, name: 'Transportation', icon: '🚗', is_income: 0 },
  { id: 6, name: 'Insurance', icon: '🛡️', is_income: 0 },
  { id: 7, name: 'Phone', icon: '📱', is_income: 0 },
  { id: 8, name: 'Entertainment', icon: '🎬', is_income: 0 },
  { id: 9, name: 'Healthcare', icon: '🏥', is_income: 0 },
  { id: 10, name: 'Savings', icon: '💰', is_income: 0 },
  { id: 11, name: 'Other', icon: '📦', is_income: 0 }
];

export type Category = typeof categories[0];

export interface Transaction {
  id: number;
  date: string;
  amount: number;
  category_id: number;
  transaction_type: 'income' | 'expense';
  notes: string | null;
  created_at: string;
  category?: Category;
}

export interface RecurringBill {
  id: number;
  name: string;
  amount: number;
  due_day: number;
  category_id: number;
  is_active: number;
  category?: Category;
}

export interface SavingsGoal {
  id: number;
  name: string;
  target_amount: number;
  current_amount: number;
  deadline: string | null;
  is_active: number;
}

export interface MonthlySummary {
  total_income: number;
  total_expense: number;
}

export interface CategoryBreakdown {
  name: string;
  icon: string;
  total: number;
}
