<script lang="ts">
  import { onMount, tick } from 'svelte';
  import Chart from 'chart.js/auto';
  import { getMonthlySummary, getCategoryBreakdown } from '$lib/api';
  
  let loading = true;
  let error = '';
  let selectedYear = new Date().getFullYear();
  
  let monthlyData: any[] = [];
  let categoryData: any[] = [];
  
  let barChartCanvas: HTMLCanvasElement;
  let categoryChartCanvas: HTMLCanvasElement;
  let barChart: Chart | null = null;
  let categoryChart: Chart | null = null;
  
  const years = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i);
  
  onMount(async () => {
    await loadData();
  });
  
  async function loadData() {
    loading = true;
    error = '';
    
    try {
      // Load monthly data
      monthlyData = [];
      for (let m = 1; m <= 12; m++) {
        if (selectedYear === new Date().getFullYear() && m > new Date().getMonth() + 1) {
          break;
        }
        const summary = await getMonthlySummary(selectedYear, m);
        monthlyData.push({
          month: new Date(selectedYear, m - 1).toLocaleDateString('en-US', { month: 'short' }),
          income: summary.total_income,
          expense: summary.total_expense,
          net: summary.total_income - summary.total_expense
        });
      }
      
      // Load category breakdown
      categoryData = await getCategoryBreakdown('expense', selectedYear);
      
      // Wait for DOM then render charts
      await tick();
      await renderCharts();
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
  
  async function renderCharts() {
    if (!barChartCanvas || !categoryChartCanvas) {
      setTimeout(renderCharts, 100);
      return;
    }
    
    // Destroy existing charts
    if (barChart) {
      barChart.destroy();
      barChart = null;
    }
    if (categoryChart) {
      categoryChart.destroy();
      categoryChart = null;
    }
    
    const barCtx = barChartCanvas.getContext('2d');
    if (barCtx) {
      // Create gradients
      const incomeGradient = barCtx.createLinearGradient(0, 0, 0, 300);
      incomeGradient.addColorStop(0, '#3b82f6');
      incomeGradient.addColorStop(1, '#1d4ed8');
      
      const expenseGradient = barCtx.createLinearGradient(0, 0, 0, 300);
      expenseGradient.addColorStop(0, '#f43f5e');
      expenseGradient.addColorStop(1, '#e11d48');
      
      barChart = new Chart(barCtx, {
        type: 'bar',
        data: {
          labels: monthlyData.map(d => d.month),
          datasets: [
            {
              label: 'Income',
              data: monthlyData.map(d => d.income),
              backgroundColor: incomeGradient,
              borderRadius: 6,
              borderSkipped: false
            },
            {
              label: 'Expenses',
              data: monthlyData.map(d => d.expense),
              backgroundColor: expenseGradient,
              borderRadius: 6,
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
                font: { size: 12, family: 'Inter' },
                usePointStyle: true,
                pointStyle: 'circle',
                padding: 20
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
                font: { size: 12, family: 'Inter' }
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
    
    // Category breakdown chart
    const catCtx = categoryChartCanvas.getContext('2d');
    if (catCtx && categoryData.length > 0) {
      const catGradient = catCtx.createLinearGradient(0, 0, 300, 0);
      catGradient.addColorStop(0, '#3b82f6');
      catGradient.addColorStop(1, '#60a5fa');
      
      categoryChart = new Chart(catCtx, {
        type: 'bar',
        data: {
          labels: categoryData.slice(0, 10).map(d => `${d.icon} ${d.name}`),
          datasets: [{
            label: 'Spending',
            data: categoryData.slice(0, 10).map(d => d.total),
            backgroundColor: catGradient,
            borderRadius: 4,
            borderSkipped: false
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: '#1e293b',
              titleColor: '#f8fafc',
              bodyColor: '#94a3b8',
              borderColor: '#334155',
              borderWidth: 1,
              padding: 12,
              callbacks: {
                label: (context) => ` $${context.parsed.x.toLocaleString()}`
              }
            }
          },
          scales: {
            x: {
              ticks: { 
                color: '#64748b', 
                font: { size: 11, family: 'Inter' },
                callback: (value) => `$${(value as number / 1000).toFixed(0)}k`
              },
              grid: { 
                color: '#1f2937',
                drawBorder: false
              }
            },
            y: {
              ticks: { 
                color: '#f8fafc',
                font: { size: 12, family: 'Inter' }
              },
              grid: { display: false }
            }
          }
        }
      });
    }
  }
  
  $: totalIncome = monthlyData.reduce((sum, d) => sum + d.income, 0);
  $: totalExpense = monthlyData.reduce((sum, d) => sum + d.expense, 0);
  $: totalNet = totalIncome - totalExpense;
  
  function formatCurrency(amount: number): string {
    return amount.toLocaleString('en-US', { 
      style: 'currency', 
      currency: 'USD',
      maximumFractionDigits: 0
    });
  }
</script>

<svelte:head>
  <title>Reports - Jim's Finance</title>
</svelte:head>

<div class="page">
  <header class="page-header">
    <h1 class="page-title">Reports</h1>
    <p class="page-subtitle">Annual financial overview</p>
  </header>
  
  {#if loading}
    <div class="loading">Loading reports...</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else}
    <!-- Year Selector -->
    <div class="card animate-fade-in">
      <div class="form-group" style="margin-bottom: 0;">
        <label>Select Year</label>
        <select class="input" bind:value={selectedYear} on:change={loadData}>
          {#each years as year}
            <option value={year}>{year}</option>
          {/each}
        </select>
      </div>
    </div>
    
    <!-- Annual Summary -->
    <div class="metric-grid animate-fade-in stagger-1">
      <div class="metric-card">
        <div class="metric-label">Total Income</div>
        <div class="metric-value income">{formatCurrency(totalIncome)}</div>
      </div>
      
      <div class="metric-card">
        <div class="metric-label">Total Expenses</div>
        <div class="metric-value expense">{formatCurrency(totalExpense)}</div>
      </div>
      
      <div class="metric-card">
        <div class="metric-label">Annual Net</div>
        <div class="metric-value" class:income={totalNet >= 0} class:expense={totalNet < 0}>
          {formatCurrency(totalNet)}
        </div>
      </div>
    </div>
    
    <!-- Monthly Trend Chart -->
    <div class="card chart-container animate-fade-in stagger-2">
      <div class="card-header">
        <h3 class="card-title">📈 Monthly Trend</h3>
      </div>
      <div class="chart-wrapper chart-wrapper-lg">
        <canvas bind:this={barChartCanvas}></canvas>
      </div>
    </div>
    
    <!-- Category Breakdown Chart -->
    <div class="card chart-container animate-fade-in stagger-3">
      <div class="card-header">
        <h3 class="card-title">💳 Top Spending Categories</h3>
      </div>
      {#if categoryData.length > 0}
        <div class="chart-wrapper">
          <canvas bind:this={categoryChartCanvas}></canvas>
        </div>
      {:else}
        <div class="empty-state">
          <div class="empty-state-icon">📊</div>
          <p>No expense data for this year</p>
        </div>
      {/if}
    </div>
    
    <!-- Monthly Breakdown Table -->
    <div class="card animate-fade-in stagger-4">
      <div class="card-header">
        <h3 class="card-title">📋 Monthly Summary</h3>
      </div>
      
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Month</th>
              <th>Income</th>
              <th>Expenses</th>
              <th>Net</th>
            </tr>
          </thead>
          <tbody>
            {#each monthlyData as row}
              <tr>
                <td>{row.month}</td>
                <td class="income">{formatCurrency(row.income)}</td>
                <td class="expense">{formatCurrency(row.expense)}</td>
                <td class:income={row.net >= 0} class:expense={row.net < 0}>
                  {formatCurrency(row.net)}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {/if}
</div>

<style>
  td.income {
    color: var(--color-income);
  }
  
  td.expense {
    color: var(--color-expense);
  }
</style>
