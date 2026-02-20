<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    getRecurringBills, 
    addRecurringBill, 
    toggleRecurringBill, 
    deleteRecurringBill,
    getCategories 
  } from '$lib/api';
  import type { RecurringBill, Category } from '$lib/types';
  
  let loading = true;
  let error = '';
  let bills: RecurringBill[] = [];
  let categories: Category[] = [];
  let showAddForm = false;
  let deleteConfirmId: number | null = null;
  
  // Form fields
  let newName = '';
  let newAmount = '';
  let newDueDay = 1;
  let newCategoryId: number | null = null;
  
  onMount(async () => {
    try {
      [bills, categories] = await Promise.all([
        getRecurringBills(),
        getCategories()
      ]);
      const expenseCats = categories.filter(c => c.is_income === 0);
      if (expenseCats.length > 0) {
        newCategoryId = expenseCats[0].id;
      }
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  });
  
  function getCategory(id: number): Category | undefined {
    return categories.find(c => c.id === id);
  }
  
  async function handleAdd() {
    if (!newName || !newAmount || !newCategoryId) return;
    
    try {
      await addRecurringBill(
        newName,
        parseFloat(newAmount),
        newDueDay,
        newCategoryId
      );
      
      // Reset form
      newName = '';
      newAmount = '';
      newDueDay = 1;
      showAddForm = false;
      
      // Reload bills
      bills = await getRecurringBills();
    } catch (e: any) {
      error = e.message;
    }
  }
  
  async function handleToggle(bill: RecurringBill) {
    try {
      await toggleRecurringBill(bill.id, bill.is_active === 0);
      bills = bills.map(b => 
        b.id === bill.id ? { ...b, is_active: b.is_active === 0 ? 1 : 0 } : b
      );
    } catch (e: any) {
      error = e.message;
    }
  }
  
  async function handleDelete(id: number) {
    try {
      await deleteRecurringBill(id);
      bills = bills.filter(b => b.id !== id);
      deleteConfirmId = null;
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
  <title>Recurring Bills - Jim's Finance</title>
</svelte:head>

<div class="page">
  <header class="page-header">
    <h1 class="page-title">Recurring Bills</h1>
    <p class="page-subtitle">Track your monthly subscriptions & bills</p>
  </header>
  
  {#if loading}
    <div class="loading">Loading bills...</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else}
    <!-- Add Button -->
    <button 
      class="btn {showAddForm ? 'btn-secondary' : 'btn-primary'} add-btn animate-fade-in" 
      on:click={() => showAddForm = !showAddForm}
    >
      {showAddForm ? '✕ Cancel' : '➕ Add New Bill'}
    </button>
    
    <!-- Add Form -->
    {#if showAddForm}
      <div class="card add-form animate-fade-in">
        <div class="card-header">
          <h3 class="card-title">New Recurring Bill</h3>
        </div>
        
        <div class="form-group">
          <label>Bill Name</label>
          <input
            type="text"
            class="input"
            bind:value={newName}
            placeholder="e.g., Rent, Netflix"
          />
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>Amount</label>
            <input
              type="number"
              class="input"
              bind:value={newAmount}
              placeholder="0.00"
              step="0.01"
              min="0.01"
            />
          </div>
          
          <div class="form-group">
            <label>Due Day (1-28)</label>
            <input
              type="number"
              class="input"
              bind:value={newDueDay}
              min="1"
              max="28"
            />
          </div>
        </div>
        
        <div class="form-group">
          <label>Category</label>
          <select class="input" bind:value={newCategoryId}>
            {#each categories.filter(c => c.is_income === 0) as cat}
              <option value={cat.id}>{cat.icon} {cat.name}</option>
            {/each}
          </select>
        </div>
        
        <button class="btn btn-success" on:click={handleAdd} disabled={!newName || !newAmount}>
          Save Bill
        </button>
      </div>
    {/if}
    
    <!-- Bills List -->
    {#if bills.length === 0}
      <div class="empty-state animate-fade-in">
        <div class="empty-state-icon">🔄</div>
        <p>No recurring bills yet.</p>
        <p style="color: var(--color-text-muted); font-size: 0.875rem;">Add your subscriptions and monthly bills to track them.</p>
      </div>
    {:else}
      <div class="bills-list">
        {#each bills as bill, i}
          {@const cat = getCategory(bill.category_id)}
          
          <div class="bill-card" class:inactive={bill.is_active === 0} style="animation-delay: {i * 0.05}s">
            <div class="bill-header">
              <div class="bill-title">
                <div class="bill-icon">{cat?.icon || '📦'}</div>
                <div>
                  <h4>{bill.name}</h4>
                  <span class="bill-category">{cat?.name || 'Unknown'}</span>
                </div>
              </div>
              
              <div class="bill-amount">
                ${formatCurrency(bill.amount)}
              </div>
            </div>
            
            <div class="bill-footer">
              <span class="due-day">
                📅 Due on the {bill.due_day}{['st','nd','rd'][((bill.due_day+90)%100-10)%10-1]||'th'}
              </span>
              
              <div class="bill-actions">
                <button 
                  class="toggle-btn"
                  class:active={bill.is_active === 1}
                  on:click={() => handleToggle(bill)}
                >
                  {bill.is_active === 1 ? '⏸️ Pause' : '▶️ Resume'}
                </button>
                
                {#if deleteConfirmId === bill.id}
                  <div class="delete-confirm">
                    <span>Delete?</span>
                    <button class="btn btn-danger btn-sm" on:click={() => handleDelete(bill.id)}>Yes</button>
                    <button class="btn btn-secondary btn-sm" on:click={() => deleteConfirmId = null}>No</button>
                  </div>
                {:else}
                  <button class="delete-btn" on:click={() => deleteConfirmId = bill.id}>🗑️</button>
                {/if}
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</div>

<style>
  .add-btn {
    width: 100%;
    margin-bottom: var(--space-md);
  }
  
  .add-form {
    margin-bottom: var(--space-lg);
  }
  
  .bills-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .delete-confirm {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
  }
  
  .delete-confirm span {
    color: var(--color-text-muted);
  }
</style>
