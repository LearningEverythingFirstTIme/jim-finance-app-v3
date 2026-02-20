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
</script>

<svelte:head>
  <title>Recurring Bills - Jim's Finance Tracker</title>
</svelte:head>

<div class="page">
  <h1 class="page-title">🔄 Recurring Bills</h1>
  
  {#if loading}
    <div class="loading">Loading bills...⏳</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else}
    <!-- Add Button -->
    <button class="btn btn-primary add-btn" on:click={() => showAddForm = !showAddForm}>
      {showAddForm ? '✕ Cancel' : '➕ Add New Bill'}
    </button>
    
    <!-- Add Form -->
    {#if showAddForm}
      <div class="card add-form">
        <h3>Add New Bill</h3>
        
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
      <div class="empty-state">No recurring bills yet. Add one above!</div>
    {:else}
      <div class="bills-list">
        {#each bills as bill}
          {@const cat = getCategory(bill.category_id)}
          
          <div class="bill-card" class:inactive={bill.is_active === 0}>
            <div class="bill-header">
              <div class="bill-title">
                <span class="bill-icon">{cat?.icon || '📦'}</span>
                <div>
                  <h4>{bill.name}</h4>
                  <span class="bill-category">{cat?.name || 'Unknown'}</span>
                </div>
              </div>
              
              <div class="bill-amount">
                ${bill.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </div>
            </div>
            
            <div class="bill-footer">
              <span class="due-day">📅 Due on the {bill.due_day}{['st','nd','rd'][((bill.due_day+90)%100-10)%10-1]||'th'}</span>
              
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
    margin-bottom: 1rem;
  }
  
  .add-form {
    margin-bottom: 1.5rem;
  }
  
  .add-form h3 {
    margin-top: 0;
  }
  
  .bills-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .bill-card {
    background-color: #1e293b;
    border-radius: 0.75rem;
    padding: 1rem;
    border-left: 4px solid #3b82f6;
  }
  
  .bill-card.inactive {
    opacity: 0.6;
    border-left-color: #64748b;
  }
  
  .bill-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.75rem;
  }
  
  .bill-title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }
  
  .bill-icon {
    font-size: 1.5rem;
  }
  
  .bill-title h4 {
    margin: 0;
    font-size: 1rem;
  }
  
  .bill-category {
    font-size: 0.8rem;
    color: #94a3b8;
  }
  
  .bill-amount {
    font-size: 1.25rem;
    font-weight: 700;
    color: #ef4444;
  }
  
  .bill-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 0.75rem;
    border-top: 1px solid #334155;
  }
  
  .due-day {
    font-size: 0.875rem;
    color: #94a3b8;
  }
  
  .bill-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .toggle-btn {
    background: none;
    border: 1px solid #334155;
    border-radius: 0.375rem;
    padding: 0.375rem 0.75rem;
    color: #94a3b8;
    cursor: pointer;
    font-size: 0.8rem;
  }
  
  .toggle-btn.active {
    border-color: #22c55e;
    color: #22c55e;
  }
  
  .delete-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.1rem;
    padding: 0.25rem;
    opacity: 0.7;
  }
  
  .delete-confirm {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
  }
  
  .btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
  }
</style>
