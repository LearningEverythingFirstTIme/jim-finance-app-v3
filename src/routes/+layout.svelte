<script lang="ts">
  import '../app.css';
  import { page } from '$app/stores';
  
  const navItems = [
    { path: '/', label: 'Home', icon: '📊' },
    { path: '/add', label: 'Add', icon: '➕' },
    { path: '/transactions', label: 'History', icon: '📋' },
    { path: '/bills', label: 'Bills', icon: '🔄' },
    { path: '/import', label: 'Import', icon: '📁' },
    { path: '/reports', label: 'Reports', icon: '📈' }
  ];
</script>

<div class="app">
  <slot />
  
  {#if $page.url.pathname !== '/login'}
    <nav class="bottom-nav">
      {#each navItems as item}
        <a 
          href={item.path} 
          class="nav-item"
          class:active={$page.url.pathname === item.path || (item.path !== '/' && $page.url.pathname.startsWith(item.path))}
        >
          <span class="nav-icon">{item.icon}</span>
          {item.label}
        </a>
      {/each}
    </nav>
  {/if}
</div>
