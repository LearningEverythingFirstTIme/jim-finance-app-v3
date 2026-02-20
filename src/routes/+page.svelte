<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import Chart from 'chart.js/auto';
  import { 
    getMonthlySummary, 
    getCategoryBreakdown, 
    getTransactions,
    getRecurringBills,
    addTransaction,
    getCategories
  } from '$lib/api';
  import type { Category } from '$lib/types';
  
  let loading = true;
  let error = '';
  let income = 0;
  let expense = 0;
  let balance = 0;
  let hasTransactions = false;
  let upcomingBills: any[] = [];
  
  // Quick add
  let quickAmount = '';
  let quickType: 'expense' | 'income' = 'expense';
  let quickCategory: number | null = null;
  let quickNote = '';
  let categories: Category[] = [];
  let filteredCategories: Category[] = [];
  
  let pieChartCanvas: HTMLCanvasElement;
  let barChartCanvas: HTMLCanvasElement;
  let pieChart: Chart;
  let barChart: Chart;
  
  const today = new Date();
  const currentYear = today.getFullYear();
  const currentMonth = today.getMonth() + 1;
  
  $: filteredCategories = categories.filter(c => 
    quickType === 'income' ? c.is_income === 1 : c.is_income === 0
  );
  
  $: if (filteredCategories.length > 0 && !quickCategory) {
    quickCategory = filteredCategories[0].id;
  }
  
  onMount(async () => {
    try {
      categories = await getCategories();
      await loadDashboard();
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  });
  
  async function loadDashboard() {
    const summary = await getMonthlySummary(currentYear, currentMonth);
    income = summary.total_income;
    expense = summary.total_expense;
    balance = income - expense;
    
    const transactions = await getTransactions(1);
    hasTransactions = transactions.length > 0;
    
    // Get upcoming bills
    const bills = await getRecurringBills();
    const currentDay = today.getDate();
    upcomingBills = bills.filter(b => b.due_day >= currentDay && b.is_active === 1);
    
    // Load charts
    await loadCharts();
  }
  
  async function loadCharts() {
    // Pie chart - category breakdown
    const breakdown = await getCategoryBreakdown('expense', currentYear, currentMonth);
    
    if (pieChart) pieChart.destroy();
    if (breakdown.length > 0) {
      pieChart = new Chart(pieChartCanvas, {
        type: 'doughnut',
        data: {
          labels: breakdown.map(b => `${b.icon} ${b.name}`),
          datasets: [{
            data: breakdown.map(b => b.total),
            backgroundColor: [
              '#3b82f6', '#ef4444', '#22c55e', '#f59e0b', '#8b5cf6',
              '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16'
            ]
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: '#f8fafc', font: { size: 11 } }
            }
          }
        }
      });
    }
    
    // Bar chart - 6 month trend
    const monthsData = [];
    for (let i = 5; i >= 0; i--) {
      const d = new Date(today.getFullYear(), today.getMonth() - i, 1);
      const s = await getMonthlySummary(d.getFullYear(), d.getMonth() + 1);
      monthsData.push({
        month: d.toLocaleDateString('en-US', { month: 'short' }),
        income: s.total_income,
        expense: s.total_expense
      });
    }
    
    if (barChart) barChart.destroy();
    barChart = new Chart(barChartCanvas, {
      type: 'bar',
      data: {
        labels: monthsData.map(m => m.month),
        datasets: [
          {
            label: 'Income',
            data: monthsData.map(m => m.income),
            backgroundColor: '#22c55e'
          },
          {
            label: 'Expenses',
            data: monthsData.map(m => m.expense),
            backgroundColor: '#ef4444'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: '#f8fafc' }
          }
        },
        scales: {
          x: {
            ticks: { color: '#94a3b8' },
            grid: { color: '#334155' }
          },
          y: {
            ticks: { color: '#94a3b8' },
            grid: { color: '#334155' }
          }
        }
      }
    });
  }
  
  async function handleQuickAdd() {
    if (!quickAmount || !quickCategory) return;
    
    try {
      await addTransaction(
        today.toISOString().split('T')[0],
        parseFloat(quickAmount),
        quickCategory,
        quickType,
        quickNote
      );
      
      // Reset form
      quickAmount = '';
      quickNote = '';
      
      // Reload dashboard
      await loadDashboard();
    } catch (e: any) {
      error = e.message;
    }
  }
</script>

<svelte:head>
  <title>Dashboard - Jim's Finance Tracker</title>
</svelte:head>

<div class="page">
  <h1 class="page-title">📊 Dashboard</h1>
  
  {#if loading}
    <div class="loading">Loading dashboard...⏳</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else}
    <!-- Quick Add -->
    <div class="card">
      <h3>⚡ Quick Add</h3>
      <div class="quick-add-form">
        <div class="form-row">
          <div class="form-group">
            <input
              type="number"
              class="input"
              bind:value={quickAmount}
              placeholder="Amount"
              step="0.01"
              min="0"
            />
          </div>
          <div class="form-group">
            <select class="input" bind:value={quickType}>
              <option value="expense">💸 Expense</option>
              <option value="income">💵 Income</option>
            </select>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <select class="input" bind:value={quickCategory}>
              {#each filteredCategories as cat}
                <option value={cat.id}>{cat.icon} {cat.name}</option>
              {/each}
            </select>
          </div>
          <div class="form-group">
            <input
              type="text"
              class="input"
              bind:value={quickNote}
              placeholder="Note (optional)"
            />
          </div>
        </div>
        
        <button class="btn btn-success" on:click={handleQuickAdd} disabled={!quickAmount}>
          ➕ Add Transaction
        </button>
      </div>
    </div>
    
    {#if !hasTransactions}
      <div class="card welcome-card">
        <h2>🎉 Welcome to Jim's Finance Tracker!</h2>
        <p>Get started in just a few steps:</p>
        <ol>
          <li>Use <strong>Quick Add</strong> above to add your first transaction</li>
          <li>Set up recurring bills in <strong>Bills</strong></li>
          <li>Import your bank transactions via <strong>Import CSV</strong></li>
        </ol>
        <p class="highlight">Add your first transaction above to get started!</p>
      </div>
    {/if}
    
    <!-- Metrics -->
    <div class="metric-grid">
      <div class="metric-card">
        <div class="metric-label">💵 Monthly Income</div>
        <div class="metric-value income">${income.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
      </div>
      
      <div class="metric-card">
        <div class="metric-label">💸 Monthly Expenses</div>
        <div class="metric-value expense">${expense.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
      </div>
      
      <div class="metric-card">
        <div class="metric-label">📈 Balance</div>
        <div class="metric-value" class:income={balance >= 0} class:expense={balance < 0}>
          ${balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
        </div>
      </div>
    </div>
    
    <!-- Charts -->
    <div class="chart-container">
      <h3>💳 Spending by Category</h3>
      <canvas bind:this={pieChartCanvas}></canvas>
    </div>
    
    <div class="chart-container">
      <h3>📈 Income vs Expenses (6 Months)</h3>
      <canvas bind:this={barChartCanvas}></canvas>
    </div>
    
    <!-- Upcoming Bills -->
    {#if upcomingBills.length > 0}
      <div class="card">
        <h3>📅 Upcoming Bills This Month</h3>
        
        {#each upcomingBills as bill}
          <div class="bill-item">
            <span>🔔 {bill.name}</span>
            <span class="expense">-${bill.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
            <span class="due-date">Due {bill.due_day}{['st','nd','rd'][((bill.due_day+90)%100-10)%10-1]||'th'}</span>
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</div>

<style>
  .quick-add-form {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .welcome-card {
    text-align: center;
    border: 2px solid #22c55e;
  }
  
  .welcome-card h2 {
    color: #22c55e;
    margin-top: 0;
  }
  
  .welcome-card ol {
    text-align: left;
    max-width: 400px;
    margin: 1rem auto;
    color: #94a3b8;
  }
  
  .welcome-card li {
    margin-bottom: 0.5rem;
  }
  
  .highlight {
    color: #22c55e;
    font-weight: 600;
    margin-top: 1rem;
  }
  
  .chart-container h3 {
    margin-top: 0;
    margin-bottom: 1rem;
    font-size: 1rem;
  }
  
  .bill-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 0;
    border-bottom: 1px solid #334155;
  }
  
  .bill-item:last-child {
    border-bottom: none;
  }
  
  .due-date {
    font-size: 0.8rem;
    color: #94a3b8;
  }
</style>
