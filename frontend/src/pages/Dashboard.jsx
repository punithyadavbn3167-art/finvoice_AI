import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'
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

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [invoices, setInvoices] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const loadDashboard = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const [summaryData, transactionData, invoiceData] =
        await Promise.all([
          apiRequest('/summary'),
          apiRequest('/transactions'),
          apiRequest('/invoices'),
        ])

      setSummary(summaryData)
      setTransactions(getItems(transactionData))
      setInvoices(getItems(invoiceData))
    } catch (error) {
      setError(
        error.message ||
          'Could not load your dashboard. Make sure the backend is running.',
      )
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadDashboard()
  }, [loadDashboard])

  const outstanding = invoices
    .filter((invoice) =>
      ['pending', 'overdue', 'unpaid'].includes(
        String(invoice.status ?? '').toLowerCase(),
      ),
    )
    .reduce(
      (total, invoice) => total + Number(invoice.amount || 0),
      0,
    )

  const metrics = [
    {
      label: 'Total Revenue',
      value: summary ? money(summary.total_revenue) : '—',
      note: 'Recorded business income',
      icon: '↗',
      kind: 'revenue',
    },
    {
      label: 'Total Expenses',
      value: summary ? money(summary.total_expenses) : '—',
      note: 'Recorded business spending',
      icon: '↘',
      kind: 'expense',
    },
    {
      label: 'Net Balance',
      value: summary ? money(summary.net_balance) : '—',
      note: 'Revenue minus expenses',
      icon: '₹',
      kind: 'balance',
    },
    {
      label: 'Outstanding Invoices',
      value: loading && invoices.length === 0 ? '—' : money(outstanding),
      note: 'Pending and overdue',
      icon: '▤',
      kind: 'invoice',
    },
  ]

  const chartData = [
    {
      name: 'Revenue',
      amount: Number(summary?.total_revenue) || 0,
    },
    {
      name: 'Expenses',
      amount: Number(summary?.total_expenses) || 0,
    },
  ]

  return (
    <>
      <header className="page-header dashboard-header">
        <div>
          <p className="eyebrow">FINANCIAL OVERVIEW</p>
          <h1>Dashboard</h1>
          <p>Your business finances at a glance.</p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={loadDashboard}
          disabled={loading}
        >
          {loading ? '↻ Refreshing…' : '↻ Refresh Data'}
        </button>
      </header>

      {error && (
        <div className="panel" role="alert">
          <h3>Dashboard unavailable</h3>
          <p>{error}</p>

          <button
            type="button"
            className="secondary-button"
            onClick={loadDashboard}
            disabled={loading}
          >
            Try again
          </button>
        </div>
      )}

      <section className="dashboard-metrics">
        {metrics.map((metric) => (
          <article className="metric-card" key={metric.label}>
            <div className="metric-top">
              <p>{metric.label}</p>
              <span className={`metric-icon ${metric.kind}`}>
                {metric.icon}
              </span>
            </div>

            <h2>
              {loading && !summary ? 'Loading…' : metric.value}
            </h2>

            <span className="metric-note">{metric.note}</span>
          </article>
        ))}
      </section>

      {loading && (
        <div className="panel" role="status">
          Loading your latest financial activity…
        </div>
      )}

      {!loading && !error && (
        <>
          <section className="panel finance-chart-panel">
            <div className="panel-heading">
              <div>
                <h3>Income vs Expenses</h3>
                <p>Compare your recorded revenue and spending</p>
              </div>
            </div>

            <div className="finance-chart">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={chartData}
                  margin={{
                    top: 10,
                    right: 20,
                    left: 10,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="var(--border)"
                  />

                  <XAxis
                    dataKey="name"
                    stroke="var(--muted)"
                  />

                  <YAxis
                    stroke="var(--muted)"
                    tickFormatter={(value) =>
                      `₹${Number(value).toLocaleString('en-IN')}`
                    }
                  />

                  <Tooltip
                    formatter={(value) => [money(value), 'Amount']}
                    contentStyle={{
                      background: 'var(--panel)',
                      border: '1px solid var(--border)',
                      borderRadius: 10,
                      color: 'var(--text)',
                    }}
                  />

                  <Legend />

                  <Bar
                    dataKey="amount"
                    name="Amount"
                    fill="#818cf8"
                    radius={[6, 6, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>

          <section className="dashboard-grid">
            <article className="panel">
              <div className="panel-heading">
                <div>
                  <h3>Recent Transactions</h3>
                  <p>Your latest recorded activity</p>
                </div>

                <Link to="/transactions">View all →</Link>
              </div>

              {transactions.length === 0 ? (
                <p>No transactions found.</p>
              ) : (
                transactions.slice(0, 5).map((transaction) => {
                  const isRevenue =
                    String(transaction.transaction_type ?? '')
                      .toLowerCase() === 'revenue'

                  return (
                    <div
                      className="transaction"
                      key={transaction.id}
                    >
                      <div
                        className={`transaction-icon ${
                          isRevenue ? 'revenue' : 'expense'
                        }`}
                      >
                        {isRevenue ? '↙' : '↗'}
                      </div>

                      <div className="transaction-info">
                        <strong>
                          {transaction.description || 'Transaction'}
                        </strong>
                        <p>{transaction.vendor || 'Unknown vendor'}</p>
                      </div>

                      <strong
                        className={isRevenue ? 'positive' : 'negative'}
                      >
                        {isRevenue ? '+' : '−'}
                        {money(transaction.amount)}
                      </strong>
                    </div>
                  )
                })
              )}
            </article>

            <article className="panel">
              <div className="panel-heading">
                <div>
                  <h3>Invoice Overview</h3>
                  <p>Your recent invoices</p>
                </div>

                <Link to="/invoices">View all →</Link>
              </div>

              {invoices.length === 0 ? (
                <p>No invoices found.</p>
              ) : (
                invoices.slice(0, 5).map((invoice) => (
                  <div
                    className="invoice-row"
                    key={invoice.id ?? invoice.invoice_number}
                  >
                    <div>
                      <strong>
                        {invoice.invoice_number || 'Invoice'}
                      </strong>
                      <p>{invoice.customer || 'Customer'}</p>
                    </div>

                    <strong>{money(invoice.amount)}</strong>

                    <span
                      className={`badge ${String(
                        invoice.status ?? 'unknown',
                      ).toLowerCase()}`}
                    >
                      {invoice.status || 'Unknown'}
                    </span>
                  </div>
                ))
              )}
            </article>
          </section>
        </>
      )}

      <footer>
        FinVoice AI · Financial information from your backend
      </footer>
    </>
  )
}
