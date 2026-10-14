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

export default function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [search, setSearch] = useState('')
  const [type, setType] = useState('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadTransactions = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const data = await apiRequest('/transactions')
      setTransactions(getItems(data))
    } catch (error) {
      setError(
        error.message ||
          'Could not load transactions. Check that the backend is running.',
      )
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadTransactions()
  }, [loadTransactions])

  const filteredTransactions = useMemo(() => {
    const query = search.toLowerCase().trim()

    return transactions.filter((transaction) => {
      const transactionType = String(
        transaction.transaction_type ?? '',
      ).toLowerCase()

      const matchesType = type === 'all' || transactionType === type

      const searchableText = [
        transaction.description,
        transaction.vendor,
        transaction.transaction_type,
        transaction.id,
      ]
        .join(' ')
        .toLowerCase()

      return matchesType && searchableText.includes(query)
    })
  }, [transactions, search, type])

  const revenue = transactions
    .filter(
      (item) =>
        String(item.transaction_type ?? '').toLowerCase() === 'revenue',
    )
    .reduce((sum, item) => sum + Number(item.amount || 0), 0)

  const expenses = transactions
    .filter(
      (item) =>
        String(item.transaction_type ?? '').toLowerCase() === 'expense',
    )
    .reduce((sum, item) => sum + Number(item.amount || 0), 0)

  return (
    <>
      <header className="page-header dashboard-header">
        <div>
          <p className="eyebrow">FINANCIAL ACTIVITY</p>
          <h1>Transactions</h1>
          <p>Search and review your recorded income and expenses.</p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={loadTransactions}
          disabled={loading}
        >
          {loading ? 'Refreshing…' : ' Refresh Data'}
        </button>
      </header>

      {error && (
        <div className="panel" role="alert">
          <h3>Transactions unavailable</h3>
          <p>{error}</p>
          <button
            type="button"
            className="secondary-button"
            onClick={loadTransactions}
            disabled={loading}
          >
            Try again
          </button>
        </div>
      )}

      <section className="dashboard-metrics">
        <article className="metric-card">
          <p>Total Transactions</p>
          <h2>
            {loading && !transactions.length ? '…' : transactions.length}
          </h2>
          <span className="metric-note">All recorded entries</span>
        </article>

        <article className="metric-card">
          <p>Total Revenue</p>
          <h2>
            {loading && !transactions.length ? '…' : money(revenue)}
          </h2>
          <span className="metric-note">Income entries</span>
        </article>

        <article className="metric-card">
          <p>Total Expenses</p>
          <h2>
            {loading && !transactions.length ? '…' : money(expenses)}
          </h2>
          <span className="metric-note">Expense entries</span>
        </article>

        <article className="metric-card">
          <p>Net from Transactions</p>
          <h2>
            {loading && !transactions.length
              ? '…'
              : money(revenue - expenses)}
          </h2>
          <span className="metric-note">Revenue minus expenses</span>
        </article>
      </section>

      <section className="panel">
        <div className="transaction-toolbar">
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search description, vendor, or ID..."
            aria-label="Search transactions"
          />

          <select
            value={type}
            onChange={(event) => setType(event.target.value)}
            aria-label="Filter transaction type"
          >
            <option value="all">All types</option>
            <option value="revenue">Revenue</option>
            <option value="expense">Expense</option>
          </select>

          <button
            type="button"
            className="secondary-button"
            onClick={() => {
              setSearch('')
              setType('all')
            }}
            disabled={!search && type === 'all'}
          >
            Clear filters
          </button>
        </div>

        {loading && <p role="status">Loading transactions…</p>}

        {!loading && !error && filteredTransactions.length === 0 && (
          <p>
            No matching transactions found. Try changing your search or filters.
          </p>
        )}

        {!loading && !error && filteredTransactions.length > 0 && (
          <div className="table-wrapper">
            <table className="finance-table">
              <thead>
                <tr>
                  <th>Description</th>
                  <th>Vendor</th>
                  <th>Type</th>
                  <th>Date</th>
                  <th className="amount-cell">Amount</th>
                </tr>
              </thead>

              <tbody>
                {filteredTransactions.map((transaction, index) => {
                  const isRevenue =
                    String(transaction.transaction_type ?? '').toLowerCase() ===
                    'revenue'

                  return (
                    <tr
                      key={
                        transaction.id ??
                        `${transaction.description}-${transaction.amount}-${index}`
                      }
                    >
                      <td>{transaction.description || '—'}</td>
                      <td>{transaction.vendor || '—'}</td>

                      <td>
                        <span
                          className={`badge ${
                            isRevenue ? 'paid' : 'overdue'
                          }`}
                        >
                          {transaction.transaction_type || 'Unknown'}
                        </span>
                      </td>

                      <td>
                        {transaction.transaction_date
                          ? new Date(
                              transaction.transaction_date,
                            ).toLocaleDateString('en-IN')
                          : '—'}
                      </td>

                      <td
                        className={`amount-cell ${
                          isRevenue ? 'positive' : 'negative'
                        }`}
                      >
                        {isRevenue ? '+' : '−'}
                        {money(transaction.amount)}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}

        <p className="table-count">
          Showing {loading ? '…' : filteredTransactions.length} of{' '}
          {transactions.length} transactions
        </p>
      </section>
    </>
  )
}
