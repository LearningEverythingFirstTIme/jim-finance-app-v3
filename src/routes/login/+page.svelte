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
  <title>Sign In - Jim's Finance</title>
</svelte:head>

<div class="login-page">
  <div class="login-container">
    <div class="login-header">
      <div class="logo">💰</div>
      <h1>Jim's Finance</h1>
      <p>Enter your password to continue</p>
    </div>
    
    {#if error}
      <div class="error">{error}</div>
    {/if}
    
    <form on:submit|preventDefault={handleLogin} class="login-form">
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
      
      <button type="submit" class="btn btn-primary btn-lg" disabled={loading}>
        {loading ? 'Signing in...' : 'Sign In'}
      </button>
    </form>
  </div>
</div>
