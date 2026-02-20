import { supabase } from './supabase';
import type { Transaction, RecurringBill, SavingsGoal, MonthlySummary, CategoryBreakdown } from './types';

// Categories
export async function getCategories(transactionType?: 'income' | 'expense') {
  let query = supabase.from('categories').select('*');
  
  if (transactionType === 'income') {
    query = query.eq('is_income', 1);
  } else if (transactionType === 'expense') {
    query = query.eq('is_income', 0);
  }
  
  const { data, error } = await query;
  if (error) throw error;
  return data || [];
}

// Transactions
export async function getTransactions(limit = 100): Promise<Transaction[]> {
  const { data: transactions, error } = await supabase
    .from('transactions')
    .select('id, date, amount, transaction_type, notes, category_id')
    .order('date', { ascending: false })
    .order('id', { ascending: false })
    .limit(limit);
  
  if (error) throw error;
  if (!transactions) return [];
  
  // Get categories for join
  const { data: cats } = await supabase.from('categories').select('id, name, icon');
  const catsMap = new Map(cats?.map(c => [c.id, c]) || []);
  
  return transactions.map(t => ({
    ...t,
    category: catsMap.get(t.category_id),
    created_at: t.created_at || new Date().toISOString()
  }));
}

export async function addTransaction(
  date: string,
  amount: number,
  categoryId: number,
  transactionType: 'income' | 'expense',
  notes: string
) {
  const { error } = await supabase.from('transactions').insert({
    date,
    amount,
    category_id: categoryId,
    transaction_type: transactionType,
    notes
  });
  if (error) throw error;
}

export async function deleteTransaction(id: number) {
  const { error } = await supabase.from('transactions').delete().eq('id', id);
  if (error) throw error;
}

// Recurring Bills
export async function getRecurringBills(): Promise<RecurringBill[]> {
  const { data: bills, error } = await supabase
    .from('recurring_bills')
    .select('*')
    .order('due_day');
  
  if (error) throw error;
  if (!bills) return [];
  
  const { data: cats } = await supabase.from('categories').select('id, name, icon');
  const catsMap = new Map(cats?.map(c => [c.id, c]) || []);
  
  return bills.map(b => ({
    ...b,
    category: catsMap.get(b.category_id)
  }));
}

export async function addRecurringBill(
  name: string,
  amount: number,
  dueDay: number,
  categoryId: number
) {
  const { error } = await supabase.from('recurring_bills').insert({
    name,
    amount,
    due_day: dueDay,
    category_id: categoryId
  });
  if (error) throw error;
}

export async function toggleRecurringBill(id: number, isActive: boolean) {
  const { error } = await supabase
    .from('recurring_bills')
    .update({ is_active: isActive ? 1 : 0 })
    .eq('id', id);
  if (error) throw error;
}

export async function deleteRecurringBill(id: number) {
  const { error } = await supabase.from('recurring_bills').delete().eq('id', id);
  if (error) throw error;
}

// Monthly Summary
export async function getMonthlySummary(year?: number, month?: number): Promise<MonthlySummary> {
  let query = supabase.from('transactions').select('amount, transaction_type');
  
  if (year && month) {
    const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
    const endDate = month === 12 
      ? `${year + 1}-01-01` 
      : `${year}-${String(month + 1).padStart(2, '0')}-01`;
    query = query.gte('date', startDate).lt('date', endDate);
  }
  
  const { data, error } = await query;
  if (error) throw error;
  
  if (!data || data.length === 0) {
    return { total_income: 0, total_expense: 0 };
  }
  
  const income = data
    .filter(t => t.transaction_type === 'income')
    .reduce((sum, t) => sum + t.amount, 0);
  const expense = data
    .filter(t => t.transaction_type === 'expense')
    .reduce((sum, t) => sum + t.amount, 0);
  
  return { total_income: income, total_expense: expense };
}

// Category Breakdown
export async function getCategoryBreakdown(
  transactionType: 'income' | 'expense' = 'expense',
  year?: number,
  month?: number
): Promise<CategoryBreakdown[]> {
  let query = supabase.from('transactions').select('amount, category_id, transaction_type');
  
  if (year && month) {
    const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
    const endDate = month === 12 
      ? `${year + 1}-01-01` 
      : `${year}-${String(month + 1).padStart(2, '0')}-01`;
    query = query.gte('date', startDate).lt('date', endDate);
  } else if (year) {
    query = query.gte('date', `${year}-01-01`).lt('date', `${year + 1}-01-01`);
  }
  
  const { data: transactions, error } = await query;
  if (error) throw error;
  if (!transactions) return [];
  
  const filtered = transactions.filter(t => t.transaction_type === transactionType);
  if (filtered.length === 0) return [];
  
  const { data: cats } = await supabase.from('categories').select('id, name, icon');
  if (!cats) return [];
  
  const totals = new Map<number, number>();
  for (const t of filtered) {
    totals.set(t.category_id, (totals.get(t.category_id) || 0) + t.amount);
  }
  
  const result: CategoryBreakdown[] = [];
  for (const [catId, total] of totals) {
    const cat = cats.find(c => c.id === catId);
    if (cat) {
      result.push({ name: cat.name, icon: cat.icon, total });
    }
  }
  
  return result.sort((a, b) => b.total - a.total);
}

// Savings Goals
export async function getSavingsGoals(): Promise<SavingsGoal[]> {
  const { data, error } = await supabase
    .from('savings_goals')
    .select('*')
    .order('is_active', { ascending: false })
    .order('id', { ascending: false });
  if (error) throw error;
  return data || [];
}

export async function addSavingsGoal(name: string, targetAmount: number, deadline?: string) {
  const { error } = await supabase.from('savings_goals').insert({
    name,
    target_amount: targetAmount,
    deadline: deadline || null
  });
  if (error) throw error;
}

export async function updateSavingsGoalAmount(id: number, amountToAdd: number) {
  const { data: goal } = await supabase
    .from('savings_goals')
    .select('current_amount')
    .eq('id', id)
    .single();
  
  if (!goal) return;
  
  const newAmount = (goal.current_amount || 0) + amountToAdd;
  const { error } = await supabase
    .from('savings_goals')
    .update({ current_amount: newAmount })
    .eq('id', id);
  if (error) throw error;
}

export async function toggleSavingsGoal(id: number, isActive: boolean) {
  const { error } = await supabase
    .from('savings_goals')
    .update({ is_active: isActive ? 1 : 0 })
    .eq('id', id);
  if (error) throw error;
}

export async function deleteSavingsGoal(id: number) {
  const { error } = await supabase.from('savings_goals').delete().eq('id', id);
  if (error) throw error;
}

// CSV Import helper
const categoryKeywords: Record<string, string[]> = {
  'Food': ['grocery', 'restaurant', 'food', 'coffee', 'cafe', 'supermarket'],
  'Transportation': ['gas', 'fuel', 'uber', 'lyft', 'parking', 'transit'],
  'Utilities': ['electric', 'water', 'gas', 'internet', 'phone', 'utility'],
  'Entertainment': ['netflix', 'spotify', 'movie', 'game', 'streaming'],
  'Rent': ['rent', 'lease'],
  'Insurance': ['insurance', 'premium'],
  'Healthcare': ['medical', 'doctor', 'pharmacy', 'health'],
  'Phone': ['mobile', 'cell', 'phone'],
  'Savings': ['savings', 'investment', 'deposit']
};

export function autoCategorize(description: string, categories: { id: number; name: string; is_income: number }[]): number {
  const descLower = description.toLowerCase();
  
  for (const [catName, keywords] of Object.entries(categoryKeywords)) {
    if (keywords.some(kw => descLower.includes(kw))) {
      const match = categories.find(c => c.name === catName);
      if (match) return match.id;
    }
  }
  
  // Default to Other for expenses
  const other = categories.find(c => c.name === 'Other');
  return other?.id || categories[0]?.id;
}
