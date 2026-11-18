---
type: Policy
title: Revenue Recognition Policy (FY2026)
description: Finance policy defining when a customer order counts as revenue. Reviewed every year.
resource: https://wiki.acme.internal/finance/revenue-recognition
tags: [finance, policy, revenue]
generated: { by: human:jsmith@acme, at: 2026-01-05T10:00:00Z }
verified:
  - { by: human:jsmith@acme, at: 2026-06-15T09:00:00Z }
status: stable
stale_after: 2026-12-31T00:00:00Z
---

# Acme Retail Revenue Recognition Policy (FY2026)

**Owner:** VP Finance (jsmith@acme) · **Effective:** 2026-01-01 · **Next review:** 2026-12-31

## 1. When an order counts as revenue

An order counts as revenue only when **both** are true:

- its status is `delivered`, and
- the **30-day return window has closed**: at least 30 days have passed since `delivered_on`.

Shipped, refunded and cancelled orders are never revenue.

## 2. Amount

The amount is `net_amount`, in INR, without tax and shipping.

## 3. Fiscal year

Acme's fiscal year is the **calendar year** (1 January to 31 December), taken from `order_date`. It is **not** the April to March year.

# Used by

- [`metrics/revenue`](../metrics/revenue.md)
- [`computations/revenue-ytd`](../computations/revenue-ytd.md)
- [`tables/orders`](../tables/orders.md)
