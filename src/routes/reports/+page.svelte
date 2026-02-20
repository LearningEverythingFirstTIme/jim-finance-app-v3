<script lang="ts">
  import { onMount } from 'svelte';
  import Chart from 'chart.js/auto';
  import { getMonthlySummary, getCategoryBreakdown } from '$lib/api';
  
  let loading = true;
  let error = '';
  let selectedYear = new Date().getFullYear();
  
  let monthlyData: any[] = [];
  let categoryData: any[] = [];
  
  let barChartCanvas: HTMLCanvasElement;
  let categoryChartCanvas: HTMLCanvasElement;
  let barChart: Chart;
  let categoryChart: Chart;
  
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
      
      renderCharts();
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
  
  function renderCharts() {
    // Monthly trend chart
    if (barChart) barChart.destroy();
    barChart = new Chart(barChartCanvas, {
      type: 'bar',
      data: {
        labels: monthlyData.map(d => d.month),
        datasets: [
          {
            label: 'Income',
            data: monthlyData.map(d => d.income),
            backgroundColor: '#22c55e'
          },
          {
            label: 'Expenses',
            data: monthlyData.map(d => d.expense),
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
    
    // Category breakdown chart
    if (categoryChart) categoryChart.destroy();
    if (categoryData.length > 0) {
      categoryChart = new Chart(categoryChartCanvas, {
        type: 'bar',
        data: {
          labels: categoryData.slice(0, 10).map(d => `${d.icon} ${d.name}`),
          datasets: [{
            label: 'Spending',
            data: categoryData.slice(0, 10).map(d => d.total),
            backgroundColor: '#3b82f6'
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              ticks: { color: '#94a3b8' },
              grid: { color: '#334155' }
            },
            y: {
              ticks: { color: '#f8fafc' },
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
      currency: 'USD' 
    });
  }
</script>

<svelte:head>
  <title>Reports - Jim's Finance Tracker</title>
</svelte:head>

<div class="page">
  <h1 class="page-title">📈 Reports</h1>
  
  {#if loading}
    <div class="loading">Loading reports...⏳</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else}
    <!-- Year Selector -->
    <div class="card">
      <label>Select Year</label>
      <select class="input" bind:value={selectedYear} on:change={loadData}>
        {#each years as year}
          <option value={year}>{year}</option>
        {/each}
      </select>
    </div>
    
    <!-- Annual Summary -->
    <div class="metric-grid">
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
    
    <!-- Monthly Breakdown Table -->
    <div class="card">
      <h3>Monthly Summary for {selectedYear}</h3>
      
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
    
    <!-- Charts -->
    <div class="chart-container">
      <h3>Monthly Trend</h3>
      <canvas bind:this={barChartCanvas}></canvas>
    </div>
    
    <div class="chart-container">
      <h3>Top Spending Categories</h3>
      {#if categoryData.length > 0}
        <canvas bind:this={categoryChartCanvas}></canvas>
      {:else}
        <p class="empty-state">No expense data for this year</p>
      {/if}
    </div>
  {/if}
</div>

<style>
  .chart-container h3 {
    margin-top: 0;
    margin-bottom: 1rem;
  }
  
  td.income {
    color: #22c55e;
  }
  
  td.expense {
    color: #ef4444;
  }
</style>
