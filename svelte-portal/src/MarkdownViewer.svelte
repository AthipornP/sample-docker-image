<script>
  import { marked } from 'marked';
  import hljs from 'highlight.js';
  import DOMPurify from 'dompurify';

  // ตั้งค่า DOMPurify ให้อนุญาต class attributes
  DOMPurify.setConfig({
    ALLOWED_ATTR: ['class', 'href', 'title', 'target', 'rel']
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

  // แปลงทุกครั้งที่ source เปลี่ยน
  $: html = DOMPurify.sanitize(marked.parse(source), {
    USE_PROFILES: { html: true }
  });
</script>

<div class="markdown-body">{@html html}</div>

<style>
  .markdown-body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    line-height: 1.6;
  }

  .prose {
    max-width: none;
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
</style>