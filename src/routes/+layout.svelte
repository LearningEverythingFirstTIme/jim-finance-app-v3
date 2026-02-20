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
  
  $: currentPath = $page.url.pathname;
</script>

<div class="app">
  <slot />
  
  <nav class="bottom-nav">
    {#each navItems as item}
      <a 
        href={item.path} 
        class="nav-item"
        class:active={currentPath === item.path || (item.path !== '/' && currentPath.startsWith(item.path))}
      >
        <span class="nav-icon">{item.icon}</span>
        {item.label}
      </a>
    {/each}
  </nav>
</div>
