---
type: SQL Query
title: Revenue for a fiscal year
description: The approved SQL query that returns the orders counted as revenue for a fiscal year, per the FY2026 Revenue Recognition Policy.
tags: [finance, revenue, sql]
parameters:
  - { name: year, type: integer, required: true }
generated: { by: human:jsmith@acme, at: 2026-06-30T14:00:00Z }
verified:
  - { by: human:jsmith@acme, at: 2026-07-01T09:00:00Z }
status: stable
stale_after: 2026-12-31T00:00:00Z
sources:
  - id: revenue-policy
    resource: policies/revenue-recognition.md
    title: Revenue Recognition Policy (FY2026)
  - id: orders-table
    resource: tables/orders.md
    title: Customer Orders (sales.orders)
---

# SQL (SQLite)

```sql
SELECT order_id, net_amount
FROM sales.orders
WHERE order_status = 'delivered'
  AND julianday('now') - julianday(delivered_on) >= 30
  AND CAST(strftime('%Y', order_date) AS INTEGER) = :year
```

Revenue is the sum of `net_amount` over the rows this query returns.

# Which rule each line implements

| SQL line | Policy rule [^revenue-policy] |
|---|---|
| `order_status = 'delivered'` | Only delivered orders count. |
| `julianday('now') - julianday(delivered_on) >= 30` | The 30-day return window has closed. Replace `'now'` with today's date if it is given. |
| `CAST(strftime('%Y', order_date) AS INTEGER) = :year` | Fiscal year = calendar year of `order_date`. |

Reads the table [`tables/orders.md`](../tables/orders.md).

[^revenue-policy]: Revenue Recognition Policy (FY2026)
