<script lang="ts">
  import { onMount, tick } from 'svelte';
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
  
  // Chart elements
  let pieChartCanvas: HTMLCanvasElement;
  let barChartCanvas: HTMLCanvasElement;
  let pieChart: Chart | null = null;
  let barChart: Chart | null = null;
  let chartsInitialized = false;
  
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
    upcomingBills = bills.filter(b => b.due_day >= currentDay && b.is_active === 1).slice(0, 3);
    
    // Wait for DOM to update then load charts
    await tick();
    await loadCharts();
  }
  
  async function loadCharts() {
    // Prevent multiple simultaneous chart loads
    if (chartsInitialized) return;
    
    // Make sure canvas elements exist
    if (!pieChartCanvas || !barChartCanvas) {
      console.log('Canvas elements not ready');
      return;
    }
    
    chartsInitialized = true;
    
    // Destroy existing charts
    if (pieChart) {
      pieChart.destroy();
      pieChart = null;
    }
    if (barChart) {
      barChart.destroy();
      barChart = null;
    }
    
    // Pie chart - category breakdown
    const breakdown = await getCategoryBreakdown('expense', currentYear, currentMonth);
    
    if (breakdown.length > 0) {
      const pieCtx = pieChartCanvas.getContext('2d');
      if (pieCtx) {
        pieChart = new Chart(pieCtx, {
          type: 'doughnut',
          data: {
            labels: breakdown.map(b => `${b.icon} ${b.name}`),
            datasets: [{
              data: breakdown.map(b => b.total),
              backgroundColor: [
                '#3b82f6', '#60a5fa', '#93c5fd', '#1d4ed8', '#1e40af',
                '#10b981', '#34d399', '#f59e0b', '#f43f5e', '#8b5cf6'
              ],
              borderWidth: 0,
              hoverOffset: 8
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
              legend: {
                position: 'bottom',
                labels: { 
                  color: '#94a3b8', 
                  font: { size: 11, family: 'Inter' },
                  padding: 16,
                  usePointStyle: true,
                  pointStyle: 'circle'
                }
              },
              tooltip: {
                backgroundColor: '#1e293b',
                titleColor: '#f8fafc',
                bodyColor: '#94a3b8',
                borderColor: '#334155',
                borderWidth: 1,
                padding: 12,
                callbacks: {
                  label: (context) => {
                    const value = context.parsed;
                    const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
                    const percentage = ((value / total) * 100).toFixed(1);
                    return ` $${value.toLocaleString()} (${percentage}%)`;
                  }
                }
              }
            }
          }
        });
      }
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
    
    const barCtx = barChartCanvas.getContext('2d');
    if (barCtx) {
      // Create gradient for bars
      const incomeGradient = barCtx.createLinearGradient(0, 0, 0, 200);
      incomeGradient.addColorStop(0, '#10b981');
      incomeGradient.addColorStop(1, '#059669');
      
      const expenseGradient = barCtx.createLinearGradient(0, 0, 0, 200);
      expenseGradient.addColorStop(0, '#f43f5e');
      expenseGradient.addColorStop(1, '#e11d48');
      
      barChart = new Chart(barCtx, {
        type: 'bar',
        data: {
          labels: monthsData.map(m => m.month),
          datasets: [
            {
              label: 'Income',
              data: monthsData.map(m => m.income),
              backgroundColor: incomeGradient,
              borderRadius: 4,
              borderSkipped: false
            },
            {
              label: 'Expenses',
              data: monthsData.map(m => m.expense),
              backgroundColor: expenseGradient,
              borderRadius: 4,
              borderSkipped: false
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
              align: 'end',
              labels: { 
                color: '#94a3b8', 
                font: { size: 11, family: 'Inter' },
                usePointStyle: true,
                pointStyle: 'circle',
                padding: 16
              }
            },
            tooltip: {
              backgroundColor: '#1e293b',
              titleColor: '#f8fafc',
              bodyColor: '#94a3b8',
              borderColor: '#334155',
              borderWidth: 1,
              padding: 12,
              callbacks: {
                label: (context) => ` ${context.dataset.label}: $${context.parsed.y.toLocaleString()}`
              }
            }
          },
          scales: {
            x: {
              ticks: { 
                color: '#64748b', 
                font: { size: 11, family: 'Inter' }
              },
              grid: { display: false }
            },
            y: {
              ticks: { 
                color: '#64748b', 
                font: { size: 11, family: 'Inter' },
                callback: (value) => `$${(value as number / 1000).toFixed(0)}k`
              },
              grid: { 
                color: '#1f2937',
                drawBorder: false
              }
            }
          }
        }
      });
    }
    
    chartsInitialized = true;
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
  
  function formatCurrency(amount: number): string {
    return amount.toLocaleString('en-US', { 
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  }
</script>

<svelte:head>
  <title>Dashboard - Jim's Finance</title>
</svelte:head>

<div class="page">
  <header class="page-header">
    <h1 class="page-title">Dashboard</h1>
    <p class="page-subtitle">{today.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</p>
  </header>
  
  {#if loading}
    <div class="loading">Loading your finances...</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else}
    <!-- Metrics -->
    <div class="metric-grid animate-fade-in">
      <div class="metric-card">
        <div class="metric-label">Income</div>
        <div class="metric-value income">${formatCurrency(income)}</div>
      </div>
      
      <div class="metric-card">
        <div class="metric-label">Expenses</div>
        <div class="metric-value expense">${formatCurrency(expense)}</div>
      </div>
      
      <div class="metric-card">
        <div class="metric-label">Balance</div>
        <div class="metric-value" class:income={balance >= 0} class:expense={balance < 0}>
          ${formatCurrency(balance)}
        </div>
      </div>
    </div>
    
    <!-- Quick Add -->
    <div class="card animate-fade-in stagger-1">
      <div class="card-header">
        <h3 class="card-title">⚡ Quick Add</h3>
      </div>
      
      <div class="quick-add-form">
        <div class="type-selector">
          <button
            type="button"
            class="type-btn"
            class:active={quickType === 'expense'}
            class:expense-type={quickType === 'expense'}
            on:click={() => quickType = 'expense'}
          >
            💸 Expense
          </button>
          <button
            type="button"
            class="type-btn"
            class:active={quickType === 'income'}
            class:income-type={quickType === 'income'}
            on:click={() => quickType = 'income'}
          >
            💵 Income
          </button>
        </div>
        
        <div class="quick-add-row">
          <div class="form-group" style="margin-bottom: 0;">
            <input
              type="number"
              class="input"
              bind:value={quickAmount}
              placeholder="0.00"
              step="0.01"
              min="0"
            />
          </div>
          <div class="form-group" style="margin-bottom: 0;">
            <select class="input" bind:value={quickCategory}>
              {#each filteredCategories as cat}
                <option value={cat.id}>{cat.icon} {cat.name}</option>
              {/each}
            </select>
          </div>
        </div>
        
        <input
          type="text"
          class="input"
          bind:value={quickNote}
          placeholder="Add a note (optional)"
        />
        
        <button class="btn btn-success" on:click={handleQuickAdd} disabled={!quickAmount}>
          ➕ Add Transaction
        </button>
      </div>
    </div>
    
    {#if !hasTransactions}
      <div class="card welcome-card animate-fade-in stagger-2">
        <div class="welcome-icon">🎉</div>
        <h2>Welcome to Jim's Finance!</h2>
        <p>Track your money with ease. Here's how to get started:</p>
        <ol>
          <li>Use <strong>Quick Add</strong> above for your first transaction</li>
          <li>Set up recurring bills in <strong>Bills</strong></li>
          <li>Import bank data via <strong>Import</strong></li>
        </ol>
        <p class="highlight">Add your first transaction to see your charts!</p>
      </div>
    {/if}
    
    <!-- Charts -->
    <div class="card chart-container animate-fade-in stagger-3">
      <h3 class="card-title">
        <span>💳</span>
        Spending by Category
      </h3>
      <div class="chart-wrapper">
        <canvas bind:this={pieChartCanvas}></canvas>
      </div>
    </div>
    
    <div class="card chart-container animate-fade-in stagger-4">
      <h3 class="card-title">
        <span>📈</span>
        Income vs Expenses
      </h3>
      <div class="chart-wrapper chart-wrapper-lg">
        <canvas bind:this={barChartCanvas}></canvas>
      </div>
    </div>
    
    <!-- Upcoming Bills -->
    {#if upcomingBills.length > 0}
      <div class="card animate-fade-in stagger-5">
        <div class="card-header">
          <h3 class="card-title">📅 Upcoming Bills</h3>
        </div>
        
        {#each upcomingBills as bill}
          <div class="bill-item">
            <div class="bill-item-info">
              <span class="bill-item-icon">🔔</span>
              <span class="bill-item-name">{bill.name}</span>
            </div>
            <div class="bill-item-details">
              <span class="bill-item-amount">-${bill.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
              <span class="bill-item-due">Due {bill.due_day}{['st','nd','rd'][((bill.due_day+90)%100-10)%10-1]||'th'}</span>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</div>

<style>
  .bill-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.875rem 0;
    border-bottom: 1px solid var(--color-border-subtle);
  }
  
  .bill-item:last-child {
    border-bottom: none;
  }
  
  .bill-item-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }
  
  .bill-item-icon {
    font-size: 1.125rem;
  }
  
  .bill-item-name {
    font-weight: 500;
    color: var(--color-text);
  }
  
  .bill-item-details {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.125rem;
  }
  
  .bill-item-amount {
    font-family: var(--font-display);
    font-weight: 700;
    color: var(--color-expense);
    font-size: 0.9375rem;
  }
  
  .bill-item-due {
    font-size: 0.75rem;
    color: var(--color-text-muted);
  }
  
  .welcome-icon {
    font-size: 3rem;
    margin-bottom: 0.75rem;
  }
</style>
