<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { addTransaction, getCategories, autoCategorize } from '$lib/api';
  import type { Category } from '$lib/types';
  
  let loading = false;
  let error = '';
  let success = '';
  let categories: Category[] = [];
  
  let file: File | null = null;
  let csvData: any[] = [];
  let previewData: any[] = [];
  
  // Column mapping
  let dateColumn = '';
  let amountColumn = '';
  let descColumn = '';
  let columns: string[] = [];
  
  onMount(async () => {
    categories = await getCategories();
  });
  
  function handleFileSelect(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      file = input.files[0];
      parseCSV(file);
    }
  }
  
  function parseCSV(file: File) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const lines = text.split('\n').filter(l => l.trim());
      
      if (lines.length < 2) {
        error = 'CSV file is empty or invalid';
        return;
      }
      
      // Parse header
      const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
      columns = headers;
      
      // Auto-detect columns
      dateColumn = headers.find(h => 
        /date|day|time/i.test(h)
      ) || headers[0];
      
      amountColumn = headers.find(h => 
        /amount|sum|value|price|cost/i.test(h)
      ) || headers.find(h => /^-?\$?\d/.test(h)) || headers[1];
      
      descColumn = headers.find(h => 
        /desc|memo|note|payee|name|merchant|transaction/i.test(h)
      ) || headers[2] || headers[headers.length - 1];
      
      // Parse data rows
      csvData = [];
      for (let i = 1; i < lines.length && i <= 100; i++) {
        const values = lines[i].split(',').map(v => v.trim().replace(/^"|"$/g, ''));
        const row: any = {};
        headers.forEach((h, idx) => {
          row[h] = values[idx] || '';
        });
        csvData.push(row);
      }
      
      previewData = csvData.slice(0, 5);
    };
    reader.readAsText(file);
  }
  
  async function handleImport() {
    if (!dateColumn || !amountColumn || !descColumn || csvData.length === 0) {
      error = 'Please map all columns first';
      return;
    }
    
    loading = true;
    error = '';
    
    try {
      let added = 0;
      const expenseCats = categories.filter(c => c.is_income === 0);
      const incomeCats = categories.filter(c => c.is_income === 1);
      
      for (const row of csvData) {
        const dateVal = row[dateColumn];
        const amountVal = parseFloat(row[amountColumn].replace(/[$,]/g, ''));
        const descVal = row[descColumn];
        
        if (isNaN(amountVal)) continue;
        
        // Determine type
        const txType = amountVal > 0 ? 'income' : 'expense';
        const absAmount = Math.abs(amountVal);
        
        // Auto-categorize
        let catId: number;
        if (txType === 'income') {
          catId = incomeCats[0]?.id || categories[0]?.id;
        } else {
          catId = autoCategorize(descVal, categories);
        }
        
        // Parse date
        let dateStr = dateVal;
        if (!/\d{4}-\d{2}-\d{2}/.test(dateVal)) {
          // Try to parse various date formats
          const d = new Date(dateVal);
          if (!isNaN(d.getTime())) {
            dateStr = d.toISOString().split('T')[0];
          }
        }
        
        await addTransaction(dateStr, absAmount, catId, txType, descVal);
        added++;
      }
      
      success = `Successfully imported ${added} transactions!`;
      setTimeout(() => {
        goto('/transactions');
      }, 1500);
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Import CSV - Jim's Finance</title>
</svelte:head>

<div class="page">
  <header class="page-header">
    <h1 class="page-title">Import CSV</h1>
    <p class="page-subtitle">Import transactions from your bank</p>
  </header>
  
  {#if error}
    <div class="error">{error}</div>
  {/if}
  
  {#if success}
    <div class="success">{success}</div>
  {/if}
  
  <div class="card animate-fade-in">
    <p style="color: var(--color-text-secondary); margin-top: 0; margin-bottom: var(--space-md);">
      Upload a bank CSV export. The app will auto-detect columns and categorize based on descriptions.
    </p>
    
    <div class="file-input-wrapper">
      <input
        type="file"
        accept=".csv"
        on:change={handleFileSelect}
        id="csv-file"
      />
      <label for="csv-file" class="file-label">
        <span class="file-label-icon">📁</span>
        <span class="file-label-text">
          {#if file}
            <strong>{file.name}</strong>
          {:else}
            <strong>Click to upload</strong> or drag and drop
          {/if}
        </span>
      </label>
    </div>
  </div>
  
  {#if columns.length > 0}
    <div class="card mapping-card animate-fade-in stagger-1">
      <div class="card-header">
        <h3 class="card-title">📋 Column Mapping</h3>
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label>Date Column</label>
          <select class="input" bind:value={dateColumn}>
            {#each columns as col}
              <option value={col}>{col}</option>
            {/each}
          </select>
        </div>
        
        <div class="form-group">
          <label>Amount Column</label>
          <select class="input" bind:value={amountColumn}>
            {#each columns as col}
              <option value={col}>{col}</option>
            {/each}
          </select>
        </div>
      </div>
      
      <div class="form-group" style="margin-bottom: 0;">
        <label>Description Column</label>
        <select class="input" bind:value={descColumn}>
          {#each columns as col}
            <option value={col}>{col}</option>
          {/each}
        </select>
      </div>
    </div>
    
    {#if previewData.length > 0}
      <div class="card preview-card animate-fade-in stagger-2">
        <div class="card-header">
          <h3 class="card-title">👀 Preview (First 5 rows)</h3>
        </div>
        
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Amount</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {#each previewData as row}
                <tr>
                  <td>{row[dateColumn]}</td>
                  <td class:expense={parseFloat(row[amountColumn]?.replace(/[$,]/g, '') || 0) < 0}>
                    {row[amountColumn]}
                  </td>
                  <td>{row[descColumn]}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    {/if}
    
    <button class="btn btn-success import-btn animate-fade-in stagger-3" on:click={handleImport} disabled={loading}>
      {loading ? 'Importing...' : `📥 Import ${csvData.length} Transactions`}
    </button>
  {/if}
</div>

<style>
  .mapping-card,
  .preview-card {
    margin-bottom: var(--space-lg);
  }
  
  .preview-card td.expense {
    color: var(--color-expense);
  }
  
  .import-btn {
    width: 100%;
  }
</style>
