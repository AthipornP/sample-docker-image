<script>
  import { onDestroy, tick } from 'svelte';
  import { marked } from 'marked';
  import hljs from 'highlight.js';
  import DOMPurify from 'dompurify';
  import MermaidRenderer from './MermaidRenderer.svelte';

  // ตั้งค่า DOMPurify ให้อนุญาต class attributes
  DOMPurify.setConfig({
    ALLOWED_ATTR: ['class', 'href', 'title', 'target', 'rel', 'data-mermaid-index']
  });

  // ใช้ setOptions ของ marked
  marked.setOptions({
    highlight(code, lang) {
      if (lang && hljs.getLanguage(lang)) {
        return hljs.highlight(code, { language: lang }).value;
      }
      return hljs.highlightAuto(code).value;
    },
    langPrefix: 'hljs language-'   // ให้ highlight.js ทำงาน
  });

  export let source = '';
  let html = '';
  let container;
  let mermaidDefinitions = [];
  let mermaidInstances = [];

  const defaultCodeRenderer = marked.Renderer.prototype.code;

  // แปลงทุกครั้งที่ source เปลี่ยน
  $: ({ html, mermaidDefinitions } = renderMarkdown(source));
  $: mountMermaidComponents();

  onDestroy(() => {
    destroyMermaidInstances();
  });

  function renderMarkdown(markdown = '') {
    const definitions = [];
    const renderer = new marked.Renderer();
    renderer.code = function (code, infostring, escaped) {
      const lang = (infostring || '').trim().toLowerCase();
      if (lang === 'mermaid') {
        const index = definitions.length;
        definitions.push(code);
        return `<div class="mermaid-placeholder" data-mermaid-index="${index}"></div>`;
      }
      return defaultCodeRenderer.call(this, code, infostring, escaped);
    };

    const parsed = marked.parse(markdown, { renderer });
    const sanitized = DOMPurify.sanitize(parsed, { USE_PROFILES: { html: true } });
    return { html: sanitized, mermaidDefinitions: definitions };
  }

  function destroyMermaidInstances() {
    if (mermaidInstances && mermaidInstances.length) {
      mermaidInstances.forEach(instance => {
        if (instance && typeof instance.$destroy === 'function') {
          instance.$destroy();
        }
      });
    }
    mermaidInstances = [];
  }

  async function mountMermaidComponents() {
    if (!container) {
      return;
    }

    await tick();
    const placeholders = container.querySelectorAll('[data-mermaid-index]');

    destroyMermaidInstances();

    placeholders.forEach(placeholder => {
      const idx = Number(placeholder.getAttribute('data-mermaid-index'));
      if (Number.isNaN(idx) || !mermaidDefinitions[idx]) {
        return;
      }

      const instance = new MermaidRenderer({
        target: placeholder,
        props: { definition: mermaidDefinitions[idx] }
      });
      mermaidInstances = [...mermaidInstances, instance];
    });
  }
</script>

<div class="markdown-body" bind:this={container}>{@html html}</div>

<style>
  .markdown-body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    line-height: 1.6;
  }

  /* Code block styling - ให้ highlight.js จัดการสี */
  :global(.markdown-body pre) {
    padding: 1rem;
    border-radius: 8px;
    overflow-x: auto;
    margin: 1rem 0;
    /* ลบ background-color และ color ออก */
  }

  :global(.markdown-body code:not([class])) {
    /* แค่ inline code ธรรมดา (ไม่มี class) */
    background-color: #2d3748;
    color: #e2e8f0;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  }

  :global(.markdown-body pre code) {
    /* Code ใน pre block - ให้ highlight.js จัดการทุกอย่าง */
    background-color: transparent;
    padding: 0;
    color: inherit; /* ให้สีตาม highlight.js theme */
  }

  :global(.markdown-body .mermaid) {
    margin: 1.25rem 0;
    background: #0f172a;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.25);
    overflow-x: auto;
  }
</style>