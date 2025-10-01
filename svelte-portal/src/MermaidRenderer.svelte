<script>
  import { onMount } from 'svelte';
  import mermaid from 'mermaid';

  export let definition = '';
  export let theme = 'dark';

  let container;
  let rendered = false;

  onMount(async () => {
    if (!container || !definition || rendered) {
      return;
    }

    const trimmed = definition.trim();
    if (!trimmed) {
      return;
    }

    try {
      // Initialize mermaid
      mermaid.initialize({ 
        startOnLoad: false, 
        securityLevel: 'loose', 
        theme,
        fontFamily: 'Inter, system-ui, sans-serif'
      });

      // Generate unique ID
      const id = `mermaid-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
      
      // Render diagram
      const { svg } = await mermaid.render(id, trimmed);
      
      // Insert SVG
      container.innerHTML = svg;
      rendered = true;
      
      console.log('Mermaid rendered successfully');
    } catch (err) {
      console.error('Mermaid render error:', err);
      container.innerHTML = `<pre style="color: red; background: #fff1f0; padding: 1rem; border-radius: 8px; overflow: auto;"><code>Mermaid Error: ${err.message || 'Unknown error'}\n\nDefinition:\n${trimmed}</code></pre>`;
    }
  });
</script>

<div class="mermaid-container" bind:this={container}></div>

<style>
  .mermaid-container {
    margin: 1.25rem 0;
    background: #0f172a;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.25);
    overflow-x: auto;
  }

  .mermaid-container :global(svg) {
    max-width: 100%;
  }
</style>
