<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { supabase } from '$lib/supabase';
  
  // Hardcoded email for Jim - only password is needed
  const JIM_EMAIL = 'jim@finance.app';
  
  let password = '';
  let loading = false;
  let error = '';
  
  onMount(async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (session) {
      goto('/');
    }
  });
  
  async function handleLogin() {
    loading = true;
    error = '';
    
    const { error: authError } = await supabase.auth.signInWithPassword({
      email: JIM_EMAIL,
      password
    });
    
    if (authError) {
      error = authError.message;
    } else {
      goto('/');
    }
    
    loading = false;
  }
</script>

<svelte:head>
  <title>Login - Jim's Finance Tracker</title>
</svelte:head>

<div class="login-page">
  <div class="login-container">
    <div class="login-header">
      <div class="logo">💰</div>
      <h1>Jim's Finance Tracker</h1>
      <p>Enter your password to access your finances</p>
    </div>
    
    {#if error}
      <div class="error">{error}</div>
    {/if}
    
    <form on:submit|preventDefault={handleLogin}>
      <div class="form-group">
        <label for="password">Password</label>
        <input
          id="password"
          type="password"
          class="input"
          bind:value={password}
          placeholder="••••••••"
          required
        />
      </div>
      
      <button type="submit" class="btn btn-primary" disabled={loading}>
        {loading ? 'Signing in...' : 'Sign In'}
      </button>
    </form>
  </div>
</div>

<style>
  .login-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  }
  
  .login-container {
    width: 100%;
    max-width: 360px;
    background-color: #1e293b;
    border-radius: 1rem;
    padding: 2rem;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  }
  
  .login-header {
    text-align: center;
    margin-bottom: 2rem;
  }
  
  .logo {
    font-size: 3rem;
    margin-bottom: 0.5rem;
  }
  
  .login-header h1 {
    margin: 0 0 0.5rem 0;
    font-size: 1.5rem;
  }
  
  .login-header p {
    margin: 0;
    color: #94a3b8;
    font-size: 0.9rem;
  }
  
  form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  button {
    margin-top: 0.5rem;
  }
  
  button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
</style>
