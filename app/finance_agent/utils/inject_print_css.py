"""
Helper utility to inject print CSS into HTML content for PDF generation.
"""

# --- Print CSS injected into every HTML before PDF ---
PRINT_CSS = """
@page {
  size: A4;
  margin: 10mm;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  margin: 0;
  padding: 0;
  background: #fff;
  color: #0f172a;
  font: 14px/1.6 "Inter", "Noto Sans TC", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.container {
  max-width: 100%;
  margin: 0;
  padding: 0 0 5mm 0;
}

.card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0;
  box-shadow: none;
  overflow: visible;
  margin-bottom: 5mm;
}

.header {
  padding: 20px 20px 8px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: nowrap;
}

.brand { display: flex; flex-direction: column; gap: 4px; max-width: 400px; }
.brand h1 { margin: 0; font-size: 16px; letter-spacing: 0.8px; font-weight: 700; }
.brand .en { font-weight: 600; font-size: 10px; color: #64748b; letter-spacing: 0.4px; white-space: nowrap; }

.meta { display: grid; gap: 3px; font-size: 12px; min-width: 280px; }
.meta div { display: flex; justify-content: space-between; gap: 8px; }

.pill {
  display: inline-block;
  border: 1px solid #e5e7eb;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  color: #64748b;
  width: max-content;
}

.title {
  padding: 14px 20px 0;
  font-size: 24px;
  font-weight: 800;
  text-align: center;
  letter-spacing: 1px;
}

.subtitle {
  text-align: center;
  color: #64748b;
  margin-top: 0;
  margin-bottom: 12px;
  font-size: 12px;
}

.section { padding: 16px 20px; }

.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.kv { display: grid; gap: 4px; }
.kv .label { color: #64748b; font-size: 12px; }

.badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #111827;
  color: #fff;
  border-radius: 999px;
  padding: 6px 12px;
  font-weight: 700;
  letter-spacing: 0.5px;
  font-size: 12px;
}
.badge .sub { opacity: 0.9; font-weight: 600; }

/* Table */
.table-wrap {
  max-width: 100%;
  margin: 0 auto;
  padding: 0 20px;
}

table {
  width: 100%;
  table-layout: fixed;
  border-collapse: separate;
  border-spacing: 0;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

thead th {
  background: #fafafa;
  color: #64748b;
  font-weight: 700;
  text-align: left;
  font-size: 12px;
  padding: 10px;
  border-bottom: 1px solid #e5e7eb;
}

tbody td {
  padding: 10px;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: middle;
  font-size: 13px;
}

tbody tr:last-child td { border-bottom: none; }

.num {
  text-align: center;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

.right {
  text-align: right;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

.muted { color: #64748b; }

/* Hide interactive elements */
.btns { display: none !important; }
.btn { display: none !important; }
.remove-btn { display: none !important; }
button { display: none !important; }
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button { display: none; }
select { appearance: none; border: none; background: transparent; }

/* Make inputs look like text */
.cell-input {
  width: 100%;
  border: none;
  background: transparent;
  font-family: inherit;
  font-size: inherit;
  pointer-events: none;
}
.cell-input.num { text-align: center; }
.cell-input.price { text-align: right; }

/* Total section */
.total {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px 0;
}

.total-card {
  min-width: 340px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

.total-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 16px;
  font-weight: 600;
  border-bottom: 1px solid #e5e7eb;
}

.total-row:last-child {
  border-bottom: none;
  background: #fafafa;
  font-size: 18px;
}

.footer {
  padding: 16px 20px 20px;
  color: #64748b;
  font-size: 12px;
  line-height: 1.6;
}

/* Column widths for quotation table */
table colgroup col:nth-child(1) { width: 50px; }   /* 序號 */
table colgroup col:nth-child(2) { width: auto; }   /* 內容 */
table colgroup col:nth-child(3) { width: 68px; }   /* 數量 */
table colgroup col:nth-child(4) { width: 68px; }   /* 單位 */
table colgroup col:nth-child(5) { width: 120px; }  /* 單價 */
table colgroup col:nth-child(6) { width: 120px; }  /* 小計 */
table colgroup col:nth-child(7) { width: 0; display: none; }  /* 操作 - hide */

/* Avoid page breaks */
.card, .header, .section, table, .total-card {
  page-break-inside: avoid;
}
"""


def inject_print_css(html_text: str, css_text: str = PRINT_CSS) -> str:
    """
    Inject <style>CSS</style> into <head>. If there is no head, prepend to beginning.

    Args:
        html_text: The HTML content to inject CSS into
        css_text: The CSS to inject (defaults to PRINT_CSS)

    Returns:
        HTML content with injected CSS
    """
    style_block = f"<style>{css_text}</style>"

    if "</head>" in html_text:
        return html_text.replace("</head>", f"{style_block}</head>")

    # best-effort: try after <html> or at very beginning
    if "<html" in html_text:
        # insert after the first '>'
        idx = html_text.find(">")
        return html_text[:idx+1] + style_block + html_text[idx+1:]

    return style_block + html_text
