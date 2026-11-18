---
type: SQL Table
title: Customer Orders
description: The sales.orders table. One row per customer order, with its status, delivery date and amount in INR.
resource: sales.orders
tags: [sales, orders, revenue, sql]
generated: { by: human:kliu@acme, at: 2026-06-30T14:00:00Z }
verified:
  - { by: human:kliu@acme, at: 2026-07-01T16:00:00Z }
status: stable
stale_after: 2026-12-31T00:00:00Z
sources:
  - id: revenue-policy
    resource: policies/revenue-recognition.md
    title: Revenue Recognition Policy (FY2026)
---

# Schema

| Column | Type | Meaning |
|---|---|---|
| `order_id` | INTEGER | Unique order id. One row per order. |
| `order_date` | TEXT (`YYYY-MM-DD`) | The day the customer placed the order. **This date decides the fiscal year.** [^revenue-policy] |
| `order_status` | TEXT | One of `delivered`, `shipped`, `refunded`, `cancelled`. Only `delivered` orders can become revenue. [^revenue-policy] |
| `delivered_on` | TEXT (`YYYY-MM-DD`) | The day the order was delivered. `NULL` if not delivered yet. The 30-day return window starts here. [^revenue-policy] |
| `net_amount` | INTEGER | Order amount in INR, without tax and shipping. This is the amount counted as revenue. [^revenue-policy] |

# Notes for SQL users

- Do not write your own revenue query. Use the approved query in [`computations/revenue-ytd.md`](../computations/revenue-ytd.md).
- A `delivered` order is **not** revenue yet while it is inside the 30-day return window.

[^revenue-policy]: Revenue Recognition Policy (FY2026)
