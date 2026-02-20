<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { addTransaction, getCategories } from '$lib/api';
  import type { Category } from '$lib/types';
  
  let loading = true;
  let saving = false;
  let error = '';
  let success = '';
  
  let date = new Date().toISOString().split('T')[0];
  let amount = '';
  let transactionType: 'income' | 'expense' = 'expense';
  let categoryId: number | null = null;
  let notes = '';
  let categories: Category[] = [];
  let filteredCategories: Category[] = [];
  
  $: filteredCategories = categories.filter(c => 
    transactionType === 'income' ? c.is_income === 1 : c.is_income === 0
  );
  
  $: if (filteredCategories.length > 0 && !categoryId) {
    categoryId = filteredCategories[0].id;
  }
  
  onMount(async () => {
    try {
      categories = await getCategories();
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  });
  
  async function handleSubmit() {
    if (!amount || !categoryId) return;
    
    saving = true;
    error = '';
    success = '';
    
    try {
      await addTransaction(
        date,
        parseFloat(amount),
        categoryId,
        transactionType,
        notes
      );
      
      success = `Added ${transactionType}: $${parseFloat(amount).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
      
      // Reset form
      amount = '';
      notes = '';
      date = new Date().toISOString().split('T')[0];
      
      // Redirect after a short delay
      setTimeout(() => {
        goto('/');
      }, 1500);
    } catch (e: any) {
      error = e.message;
    } finally {
      saving = false;
    }
  }
</script>

<svelte:head>
  <title>Add Transaction - Jim's Finance Tracker</title>
</svelte:head>

<div class="page">
  <h1 class="page-title">➕ Add Transaction</h1>
  
  {#if loading}
    <div class="loading">Loading...⏳</div>
  {:else}
    {#if error}
      <div class="error">{error}</div>
    {/if}
    
    {#if success}
      <div class="success">{success} ✅</div>
    {/if}
    
    <form on:submit|preventDefault={handleSubmit}>
      <div class="form-group">
        <label>Transaction Type</label>
        <div class="type-selector">
          <button
            type="button"
            class="type-btn"
            class:active={transactionType === 'expense'}
            on:click={() => transactionType = 'expense'}
          >
            💸 Expense
          </button>
          <button
            type="button"
            class="type-btn"
            class:active={transactionType === 'income'}
            on:click={() => transactionType = 'income'}
          >
            💵 Income
          </button>
        </div>
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label for="date">Date</label>
          <input
            id="date"
            type="date"
            class="input"
            bind:value={date}
            required
          />
        </div>
        
        <div class="form-group">
          <label for="amount">Amount</label>
          <input
            id="amount"
            type="number"
            class="input"
            bind:value={amount}
            placeholder="0.00"
            step="0.01"
            min="0.01"
            required
          />
        </div>
      </div>
      
      <div class="form-group">
        <label for="category">Category</label>
        <select id="category" class="input" bind:value={categoryId} required>
          {#each filteredCategories as cat}
            <option value={cat.id}>{cat.icon} {cat.name}</option>
          {/each}
        </select>
      </div>
      
      <div class="form-group">
        <label for="notes">Notes (optional)</label>
        <input
          id="notes"
          type="text"
          class="input"
          bind:value={notes}
          placeholder="Add a note..."
        />
      </div>
      
      <button type="submit" class="btn btn-success" disabled={saving || !amount}>
        {saving ? 'Saving...' : '➕ Add Transaction'}
      </button>
    </form>
  {/if}
</div>

<style>
  .type-selector {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
  }
  
  .type-btn {
    padding: 1rem;
    border-radius: 0.5rem;
    border: 2px solid #334155;
    background-color: #0f172a;
    color: #94a3b8;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .type-btn.active {
    border-color: #3b82f6;
    background-color: rgba(59, 130, 246, 0.1);
    color: #f8fafc;
  }
  
  .success {
    background-color: rgba(34, 197, 94, 0.1);
    border: 1px solid #22c55e;
    color: #22c55e;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
  }
  
  button[type="submit"] {
    width: 100%;
    margin-top: 1rem;
  }
</style>
