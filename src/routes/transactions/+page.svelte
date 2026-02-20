<script lang="ts">
  import { onMount } from 'svelte';
  import { getTransactions, deleteTransaction, getCategories } from '$lib/api';
  import type { Transaction, Category } from '$lib/types';
  
  let loading = true;
  let error = '';
  let transactions: Transaction[] = [];
  let filteredTransactions: Transaction[] = [];
  let categories: Category[] = [];
  
  let filterType: 'all' | 'income' | 'expense' = 'all';
  let filterMonth = 'all';
  let deleteConfirmId: number | null = null;
  
  const months = Array.from({ length: 12 }, (_, i) => {
    const d = new Date();
    d.setMonth(d.getMonth() - i);
    return {
      value: d.toISOString().slice(0, 7),
      label: d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    };
  });
  
  $: {
    let filtered = transactions;
    
    if (filterType !== 'all') {
      filtered = filtered.filter(t => t.transaction_type === filterType);
    }
    
    if (filterMonth !== 'all') {
      filtered = filtered.filter(t => t.date.startsWith(filterMonth));
    }
    
    filteredTransactions = filtered;
  }
  
  onMount(async () => {
    try {
      [transactions, categories] = await Promise.all([
        getTransactions(200),
        getCategories()
      ]);
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  });
  
  function getCategory(id: number): Category | undefined {
    return categories.find(c => c.id === id);
  }
  
  async function handleDelete(id: number) {
    try {
      await deleteTransaction(id);
      transactions = transactions.filter(t => t.id !== id);
      deleteConfirmId = null;
    } catch (e: any) {
      error = e.message;
    }
  }
  
  function formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  }
</script>

<svelte:head>
  <title>Transactions - Jim's Finance Tracker</title>
</svelte:head>

<div class="page">
  <h1 class="page-title">📋 Transactions</h1>
  
  {#if loading}
    <div class="loading">Loading transactions...⏳</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else}
    <!-- Filters -->
    <div class="filter-row">
      <select class="input" bind:value={filterType}>
        <option value="all">All Types</option>
        <option value="income">💵 Income</option>
        <option value="expense">💸 Expense</option>
      </select>
      
      <select class="input" bind:value={filterMonth}>
        <option value="all">All Months</option>
        {#each months as month}
          <option value={month.value}>{month.label}</option>
        {/each}
      </select>
    </div>
    
    <!-- Transaction List -->
    {#if filteredTransactions.length === 0}
      <div class="empty-state">
        No transactions found. <a href="/add">Add one</a> to get started!
      </div>
    {:else}
      <div class="transactions-list">
        {#each filteredTransactions as tx}
          {@const cat = getCategory(tx.category_id)}
          <div class="transaction-item">
            <div class="transaction-info">
              <div class="transaction-icon">
                {cat?.icon || '❓'}
              </div>
              <div class="transaction-details">
                <h4>{cat?.name || 'Unknown'}</h4>
                <p>{formatDate(tx.date)}{#if tx.notes} • {tx.notes}{/if}</p>
              </div>
            </div>
            
            <div class="transaction-actions">
              <span 
                class="transaction-amount"
                class:income={tx.transaction_type === 'income'}
                class:expense={tx.transaction_type === 'expense'}
              >
                {tx.transaction_type === 'income' ? '+' : '-'}
                ${tx.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </span>
              
              {#if deleteConfirmId === tx.id}
                <div class="delete-confirm">
                  <button class="btn btn-danger btn-sm" on:click={() => handleDelete(tx.id)}>✓</button>
                  <button class="btn btn-secondary btn-sm" on:click={() => deleteConfirmId = null}>✕</button>
                </div>
              {:else}
                <button class="delete-btn" on:click={() => deleteConfirmId = tx.id}>🗑️</button>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</div>

<style>
  .transactions-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .transaction-actions {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }
  
  .delete-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.25rem;
    padding: 0.25rem;
    opacity: 0.7;
    transition: opacity 0.2s;
  }
  
  .delete-btn:hover {
    opacity: 1;
  }
  
  .delete-confirm {
    display: flex;
    gap: 0.25rem;
  }
  
  .btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.875rem;
  }
  
  .empty-state a {
    color: #3b82f6;
    text-decoration: none;
  }
  
  .empty-state a:hover {
    text-decoration: underline;
  }
</style>
