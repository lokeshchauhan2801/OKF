---
type: Metric
title: Revenue
description: Recognized revenue for a fiscal year, per Acme's FY2026 revenue recognition policy.
tags: [finance, revenue, headline-metric]
generated: { by: human:jsmith@acme, at: 2026-06-30T14:00:00Z }
verified:
  - { by: human:jsmith@acme, at: 2026-07-01T09:00:00Z }
status: stable
stale_after: 2026-12-31T00:00:00Z
sources:
  - id: revenue-policy
    resource: policies/revenue-recognition.md
    title: Revenue Recognition Policy (FY2026)
---

# Definition

Revenue for a fiscal year is the sum of `net_amount` over orders in [`sales.orders`](../tables/orders.md) that:

1. have `order_status = 'delivered'`,
2. were delivered at least **30 days ago** (the return window has closed), and
3. were placed in that fiscal year. **The fiscal year is the calendar year** (1 January to 31 December) of `order_date`.

[^revenue-policy]

# How to calculate it

Run the approved SQL query [`computations/revenue-ytd.md`](../computations/revenue-ytd.md). Do not compose your own query.

The old definition, which counted every delivered order, is deprecated: see [`metrics/revenue-legacy.md`](./revenue-legacy.md).

[^revenue-policy]: Revenue Recognition Policy (FY2026)
