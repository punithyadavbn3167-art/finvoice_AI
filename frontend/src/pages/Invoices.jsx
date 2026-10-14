import { useCallback, useEffect, useMemo, useState } from 'react'
import { apiRequest } from '../services/api.js'

const money = (amount) =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
  }).format(Number(amount) || 0)

const getItems = (data) => {
  if (Array.isArray(data)) return data
  if (Array.isArray(data?.value)) return data.value
  if (Array.isArray(data?.items)) return data.items
  return []
}

const formatDate = (value) => {
  if (!value) return '—'

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value

  return date.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

export default function Invoices() {
  const [invoices, setInvoices] = useState([])
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadInvoices = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const data = await apiRequest('/invoices')
      setInvoices(getItems(data))
    } catch (error) {
      setError(
        error.message ||
          'Could not load invoices. Make sure the backend is running.',
      )
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadInvoices()
  }, [loadInvoices])

  const totals = useMemo(() => {
    const totalAmount = invoices.reduce(
      (sum, invoice) => sum + Number(invoice.amount || 0),
      0,
    )

    const paidAmount = invoices
      .filter(
        (invoice) =>
          String(invoice.status ?? '').toLowerCase() === 'paid',
      )
      .reduce((sum, invoice) => sum + Number(invoice.amount || 0), 0)

    const outstandingInvoices = invoices.filter((invoice) =>
      ['pending', 'overdue', 'unpaid'].includes(
        String(invoice.status ?? '').toLowerCase(),
      ),
    )

    const outstanding = outstandingInvoices.reduce(
      (sum, invoice) => sum + Number(invoice.amount || 0),
      0,
    )

    const overdueCount = invoices.filter(
      (invoice) =>
        String(invoice.status ?? '').toLowerCase() === 'overdue',
    ).length

    return {
      count: invoices.length,
      totalAmount,
      paidAmount,
      outstanding,
      outstandingCount: outstandingInvoices.length,
      overdueCount,
    }
  }, [invoices])

  const filteredInvoices = useMemo(() => {
    const query = search.trim().toLowerCase()

    return invoices.filter((invoice) => {
      const searchableFields = [
        invoice.invoice_number,
        invoice.customer,
        invoice.status,
        invoice.id,
      ]

      const matchesSearch = searchableFields.some((value) =>
        String(value ?? '').toLowerCase().includes(query),
      )

      const status = String(invoice.status ?? '').toLowerCase()
      const matchesStatus =
        statusFilter === 'all' || status === statusFilter

      return matchesSearch && matchesStatus
    })
  }, [invoices, search, statusFilter])

  const metrics = [
    {
      label: 'Total Invoices',
      value: totals.count,
      note: 'All recorded invoices',
    },
    {
      label: 'Total Invoiced',
      value: money(totals.totalAmount),
      note: 'Combined invoice value',
    },
    {
      label: 'Paid Amount',
      value: money(totals.paidAmount),
      note: 'Payments recorded',
    },
    {
      label: 'Outstanding',
      value: money(totals.outstanding),
      note: `${totals.outstandingCount} unpaid invoice(s)`,
    },
  ]

  return (
    <>
      <header className="page-header dashboard-header">
        <div>
          <p className="eyebrow">FINANCIAL MANAGEMENT</p>
          <h1>Invoices</h1>
          <p>Track customer invoices, due dates, and payment status.</p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={loadInvoices}
          disabled={loading}
        >
          {loading ? '↻ Refreshing…' : '↻ Refresh Data'}
        </button>
      </header>

      {error && (
        <div className="panel" role="alert">
          <h3>Invoices unavailable</h3>
          <p>{error}</p>

          <button
            type="button"
            className="secondary-button"
            onClick={loadInvoices}
            disabled={loading}
          >
            Try again
          </button>
        </div>
      )}

      <section className="dashboard-metrics">
        {metrics.map((metric) => (
          <article className="metric-card" key={metric.label}>
            <p>{metric.label}</p>
            <h2>
              {loading && !invoices.length ? 'Loading…' : metric.value}
            </h2>
            <span className="metric-note">{metric.note}</span>
          </article>
        ))}
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h3>All Invoices</h3>
            <p>Search and filter your invoice records.</p>
          </div>
        </div>

        <div className="transaction-toolbar">
          <input
            type="search"
            placeholder="Search invoice, customer, or ID..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            aria-label="Search invoices"
          />

          <select
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
            aria-label="Filter invoices by status"
          >
            <option value="all">All statuses</option>
            <option value="paid">Paid</option>
            <option value="pending">Pending</option>
            <option value="overdue">Overdue</option>
            <option value="unpaid">Unpaid</option>
          </select>

          <button
            type="button"
            className="secondary-button"
            onClick={() => {
              setSearch('')
              setStatusFilter('all')
            }}
            disabled={!search && statusFilter === 'all'}
          >
            Clear filters
          </button>
        </div>

        {loading && <p role="status">Loading invoices…</p>}

        {!loading && !error && (
          <div className="table-wrapper">
            <table className="finance-table">
              <thead>
                <tr>
                  <th>Invoice</th>
                  <th>Customer</th>
                  <th>Due Date</th>
                  <th className="amount-cell">Amount</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {filteredInvoices.map((invoice, index) => {
                  const status = String(
                    invoice.status ?? 'unknown',
                  ).toLowerCase()

                  return (
                    <tr
                      key={
                        invoice.id ??
                        invoice.invoice_number ??
                        `${invoice.customer}-${index}`
                      }
                    >
                      <td>{invoice.invoice_number || '—'}</td>
                      <td>{invoice.customer || '—'}</td>
                      <td>{formatDate(invoice.due_date)}</td>

                      <td className="amount-cell">
                        {money(invoice.amount)}
                      </td>

                      <td>
                        <span className={`badge ${status}`}>
                          {invoice.status || 'Unknown'}
                        </span>
                      </td>
                    </tr>
                  )
                })}

                {filteredInvoices.length === 0 && (
                  <tr>
                    <td colSpan={5}>
                      No matching invoices found. Try changing your search
                      or filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        <p className="table-count">
          Showing {loading ? '…' : filteredInvoices.length} of{' '}
          {invoices.length} invoices
        </p>

        {!loading && !error && totals.overdueCount > 0 && (
          <p className="invoice-warning">
            {totals.overdueCount} invoice(s) are overdue. Outstanding amounts
            are based on invoice statuses returned by the backend.
          </p>
        )}
      </section>
    </>
  )
}
