import { useCallback, useEffect, useMemo, useState } from 'react'
import { Activity, AlertTriangle, ArrowDownRight, ArrowUpRight, Box, Check, ChevronDown, CircleHelp, Command, Download, LayoutDashboard, LoaderCircle, Package, Plus, Search, Settings2, Sparkles, Trash2, X } from 'lucide-react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8080/api'
const emptyForm = { name: '', sku: '', category: 'Accessories', unitPrice: '', quantity: '', reorderThreshold: '' }
const money = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })

async function request(path, options) {
  const response = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) }, ...options,
  })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.message || `Request failed (${response.status})`)
  }
  return response.status === 204 ? null : response.json()
}

function App() {
  const [items, setItems] = useState([])
  const [dashboard, setDashboard] = useState(null)
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('All categories')
  const [stockFilter, setStockFilter] = useState('all')
  const [busy, setBusy] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [dialog, setDialog] = useState(null)
  const [saving, setSaving] = useState(false)

  const refresh = useCallback(async (search = query) => {
    setBusy(true)
    try {
      const [list, summary] = await Promise.all([
        request(`/items${search.trim() ? `?q=${encodeURIComponent(search.trim())}` : ''}`),
        request('/dashboard'),
      ])
      setItems(list)
      setDashboard(summary)
      setError('')
    } catch (cause) {
      setError(`${cause.message}. Is the Spring Boot API running on port 8080?`)
    } finally { setBusy(false) }
  }, [query])

  useEffect(() => { refresh('') }, []) // initial snapshot
  useEffect(() => {
    const timer = setTimeout(() => refresh(query), 220)
    return () => clearTimeout(timer)
  }, [query, refresh])

  const categories = useMemo(() => ['All categories', ...new Set(items.map(item => item.category))], [items])
  const visibleItems = items.filter(item => {
    const matchesCategory = category === 'All categories' || item.category === category
    const matchesStock = stockFilter === 'all' || (stockFilter === 'low' ? item.lowStock : !item.lowStock)
    return matchesCategory && matchesStock
  })

  function openCreate() { setDialog({ kind: 'create', item: null, form: emptyForm, formError: '' }) }
  function openEdit(item) { setDialog({ kind: 'edit', item, form: { name: item.name, sku: item.sku, category: item.category, unitPrice: item.unitPrice, quantity: item.quantity, reorderThreshold: item.reorderThreshold }, formError: '' }) }
  function updateForm(key, value) { setDialog(current => ({ ...current, form: { ...current.form, [key]: value }, formError: '' })) }

  async function saveItem(event) {
    event.preventDefault()
    setSaving(true)
    try {
      const payload = { ...dialog.form, unitPrice: Number(dialog.form.unitPrice), quantity: Number(dialog.form.quantity), reorderThreshold: Number(dialog.form.reorderThreshold) }
      await request(dialog.kind === 'edit' ? `/items/${dialog.item.id}` : '/items', { method: dialog.kind === 'edit' ? 'PUT' : 'POST', body: JSON.stringify(payload) })
      setDialog(null)
      setNotice(dialog.kind === 'edit' ? 'Product updated' : 'Product added to inventory')
      await refresh()
    } catch (cause) { setDialog(current => ({ ...current, formError: cause.message })) }
    finally { setSaving(false) }
  }

  async function deleteItem(item) {
    if (!window.confirm(`Remove ${item.name} (${item.sku}) from this demo inventory?`)) return
    try {
      await request(`/items/${item.id}`, { method: 'DELETE' })
      setNotice(`${item.name} removed`)
      await refresh()
    } catch (cause) { setError(cause.message) }
  }

  useEffect(() => {
    if (!notice) return undefined
    const timer = setTimeout(() => setNotice(''), 2800)
    return () => clearTimeout(timer)
  }, [notice])

  function downloadCsv() {
    const rows = [['Name', 'SKU', 'Category', 'Unit price', 'Quantity', 'Reorder threshold'], ...visibleItems.map(item => [item.name, item.sku, item.category, item.unitPrice, item.quantity, item.reorderThreshold])]
    const csv = rows.map(row => row.map(cell => `"${String(cell).replaceAll('"', '""')}"`).join(',')).join('\n')
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }))
    const link = document.createElement('a')
    link.href = url
    link.download = 'stockroom-inventory.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  return <div className="app-shell">
    <aside className="sidebar">
      <a className="brand" href="#top"><span className="brand-mark"><Box size={19} strokeWidth={2.5} /></span><span>stockroom<span className="brand-dot">.</span></span></a>
      <div className="workspace-label">WORKSPACE</div>
      <button className="workspace-switch"><span className="workspace-avatar">N</span><span className="workspace-text"><strong>Northstar Supply</strong><small>Free workspace</small></span><ChevronDown size={15} /></button>
      <div className="nav-caption">OVERVIEW</div>
      <nav className="main-nav"><a className="nav-link active" href="#inventory"><LayoutDashboard size={17} /><span>Inventory</span><span className="nav-pill">01</span></a><a className="nav-link" href="#inventory" onClick={() => setStockFilter('low')}><AlertTriangle size={17} /><span>Low stock</span>{dashboard?.lowStockCount > 0 && <span className="nav-count">{dashboard.lowStockCount}</span>}</a><a className="nav-link" href="#activity"><Activity size={17} /><span>Activity log</span><span className="soon">SOON</span></a></nav>
      <div className="sidebar-bottom"><div className="help-card"><div className="help-icon"><CircleHelp size={17} /></div><strong>Need a hand?</strong><p>Explore the API-backed inventory demo and its project notes.</p><a href="https://github.com/pavan9753/AI-agent-work-and-coding-profiles/tree/main/frontend_react/FullStack_Inventory_Platform" target="_blank" rel="noreferrer">View project <ArrowUpRight size={13} /></a></div><button className="profile-button"><span className="profile-avatar">PR</span><span className="profile-info"><strong>Pavan R</strong><small>Developer</small></span><Settings2 size={16} /></button></div>
    </aside>

    <main className="main-content" id="top">
      <header className="topbar"><div className="breadcrumb"><span>Workspace</span><span className="crumb-slash">/</span><strong>Inventory</strong></div><div className="topbar-right"><span className="api-status"><span className={`status-dot ${error ? 'down' : ''}`}></span>{error ? 'API offline' : 'API connected'}</span><button className="icon-button" aria-label="Project shortcuts"><Command size={16} /></button><span className="top-avatar">P</span></div></header>
      <div className="page-content">
        <section className="intro-row"><div><div className="eyebrow"><span className="eyebrow-dot"></span>OPERATIONS / 2026</div><h1>Inventory</h1><p className="subtitle">Keep every product, unit, and reorder point in view.</p></div><div className="intro-actions"><button className="button button-quiet" onClick={downloadCsv}><Download size={16} /> Export CSV</button><button className="button button-primary" onClick={openCreate}><Plus size={17} /> Add product</button></div></section>

        {error && <div className="error-banner"><AlertTriangle size={17} /><span>{error}</span><button onClick={() => refresh()} className="retry-button">Retry</button></div>}
        {notice && <div className="toast"><Check size={16} />{notice}</div>}

        <section className="metrics-grid" aria-label="Inventory metrics">
          <Metric label="PRODUCTS" value={dashboard?.productCount ?? '—'} detail="Active catalog" icon={<Package size={17} />} tone="blue" />
          <Metric label="TOTAL UNITS" value={dashboard?.unitsInStock?.toLocaleString() ?? '—'} detail="Across all products" icon={<Box size={17} />} tone="lavender" />
          <Metric label="INVENTORY VALUE" value={dashboard ? money.format(dashboard.inventoryValue) : '—'} detail="At current unit cost" icon={<Sparkles size={17} />} tone="mint" />
          <Metric label="NEEDS REORDER" value={dashboard?.lowStockCount ?? '—'} detail={dashboard?.lowStockCount ? 'Review low stock items' : 'All stock levels look good'} icon={<AlertTriangle size={17} />} tone="amber" warning={dashboard?.lowStockCount > 0} />
        </section>

        <section className="panel" id="inventory">
          <div className="panel-heading"><div><h2>Product catalog <span className="table-count">{dashboard?.productCount ?? 0}</span></h2><p>Manage quantities and keep the catalog current.</p></div><div className="table-actions"><div className="search-field"><Search size={16} /><input aria-label="Search products" value={query} onChange={event => setQuery(event.target.value)} placeholder="Search product or SKU" /><kbd>⌘ K</kbd></div><label className="select-wrap"><select aria-label="Filter category" value={category} onChange={event => setCategory(event.target.value)}>{categories.map(option => <option key={option}>{option}</option>)}</select><ChevronDown size={14} /></label></div></div>
          <div className="filter-strip"><button className={stockFilter === 'all' ? 'filter-chip selected' : 'filter-chip'} onClick={() => setStockFilter('all')}>All products</button><button className={stockFilter === 'low' ? 'filter-chip selected' : 'filter-chip'} onClick={() => setStockFilter('low')}><span className="chip-alert"></span>Low stock {dashboard?.lowStockCount > 0 && <span className="filter-total">{dashboard.lowStockCount}</span>}</button><button className={stockFilter === 'healthy' ? 'filter-chip selected' : 'filter-chip'} onClick={() => setStockFilter('healthy')}>Healthy stock</button><div className="filter-right"><span className="live-sync"><span></span> Live data</span><button className="refresh-button" onClick={() => refresh()} aria-label="Refresh inventory"><LoaderCircle size={15} className={busy ? 'spinning' : ''} /></button></div></div>
          <div className="table-scroll"><table><thead><tr><th className="check-cell"><input type="checkbox" aria-label="Select all products" /></th><th>PRODUCT</th><th>SKU</th><th>CATEGORY</th><th>UNIT PRICE</th><th>IN STOCK</th><th>STATUS</th><th></th></tr></thead><tbody>
            {busy && items.length === 0 ? <tr><td className="empty-state" colSpan="8"><LoaderCircle className="spinning" size={21} />Loading catalog…</td></tr> : visibleItems.length === 0 ? <tr><td className="empty-state" colSpan="8"><Search size={19} />No products match these filters.</td></tr> : visibleItems.map((item, index) => <tr key={item.id} className="product-row"><td className="check-cell"><input type="checkbox" aria-label={`Select ${item.name}`} /></td><td><div className="product-cell"><span className={`product-icon product-icon-${index % 5}`}><Package size={17} /></span><div><strong>{item.name}</strong><small>Updated {new Date(item.updatedAt).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}</small></div></div></td><td><code className="sku">{item.sku}</code></td><td><span className="category-pill">{item.category}</span></td><td className="price-cell">{money.format(item.unitPrice)}</td><td><div className="stock-cell"><strong>{item.quantity}</strong><span>units</span></div></td><td><span className={`status-pill ${item.lowStock ? 'status-low' : 'status-ok'}`}><span></span>{item.lowStock ? 'Low stock' : 'In stock'}</span></td><td><div className="row-actions"><button onClick={() => openEdit(item)} title={`Edit ${item.name}`} aria-label={`Edit ${item.name}`}><Settings2 size={15} /></button><button onClick={() => deleteItem(item)} title={`Delete ${item.name}`} aria-label={`Delete ${item.name}`}><Trash2 size={15} /></button></div></td></tr>)}
          </tbody></table></div>
          <div className="table-footer"><span>Showing <strong>{visibleItems.length}</strong> of <strong>{items.length}</strong> matching products</span><span className="updated-indicator"><span></span> Synced just now</span></div>
        </section>

        <footer className="page-footer"><span>Stockroom <span className="footer-dot">·</span> Inventory operations demo</span><span><span className="footer-build">SPRING BOOT + REACT</span><a href="https://github.com/pavan9753/AI-agent-work-and-coding-profiles/tree/main/frontend_react/FullStack_Inventory_Platform" target="_blank" rel="noreferrer">Source code <ArrowUpRight size={12} /></a></span></footer>
      </div>
    </main>

    {dialog && <div className="modal-backdrop" role="presentation" onMouseDown={event => { if (event.target === event.currentTarget) setDialog(null) }}><section className="modal" role="dialog" aria-modal="true" aria-labelledby="dialog-title"><header className="modal-header"><div><span className="modal-eyebrow">PRODUCT CATALOG</span><h2 id="dialog-title">{dialog.kind === 'edit' ? 'Edit product' : 'Add a product'}</h2><p>Product details are saved to the Spring Boot API.</p></div><button className="icon-button" aria-label="Close dialog" onClick={() => setDialog(null)}><X size={18} /></button></header><form onSubmit={saveItem}><div className="form-grid"><label className="field full"><span>Product name</span><input autoFocus required maxLength="120" value={dialog.form.name} onChange={event => updateForm('name', event.target.value)} placeholder="e.g. Wireless keyboard" /></label><label className="field"><span>SKU</span><input required maxLength="40" value={dialog.form.sku} onChange={event => updateForm('sku', event.target.value)} placeholder="ACC-104" /></label><label className="field"><span>Category</span><input required maxLength="60" value={dialog.form.category} onChange={event => updateForm('category', event.target.value)} placeholder="Accessories" /></label><label className="field"><span>Unit price (USD)</span><input type="number" required min="0" step="0.01" value={dialog.form.unitPrice} onChange={event => updateForm('unitPrice', event.target.value)} placeholder="49.00" /></label><label className="field"><span>Quantity in stock</span><input type="number" required min="0" step="1" value={dialog.form.quantity} onChange={event => updateForm('quantity', event.target.value)} placeholder="0" /></label><label className="field full"><span>Reorder threshold</span><input type="number" required min="0" step="1" value={dialog.form.reorderThreshold} onChange={event => updateForm('reorderThreshold', event.target.value)} placeholder="5" /><small>Products at or below this quantity appear in the low stock view.</small></label></div>{dialog.formError && <div className="form-error"><AlertTriangle size={15} />{dialog.formError}</div>}<div className="modal-actions"><button type="button" className="button button-quiet" onClick={() => setDialog(null)}>Cancel</button><button type="submit" className="button button-primary" disabled={saving}>{saving && <LoaderCircle className="spinning" size={15} />}{dialog.kind === 'edit' ? 'Save changes' : 'Add product'}</button></div></form></section></div>}
  </div>
}

function Metric({ label, value, detail, icon, tone, warning }) {
  return <article className="metric-card"><div className="metric-top"><span>{label}</span><span className={`metric-icon ${tone}`}>{icon}</span></div><div className="metric-value">{value}</div><div className={`metric-detail ${warning ? 'metric-warning' : ''}`}>{warning ? <ArrowDownRight size={14} /> : <ArrowUpRight size={14} />}<span>{detail}</span></div></article>
}

export default App
