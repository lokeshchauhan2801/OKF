---
type: Log
title: Acme Retail bundle history
---

# Bundle history

## 2026-07-01

- **Verified** the whole bundle for OKF v0.2. `human:kliu@acme` checked the `sales.orders` columns against the database.

## 2026-06-30

- **Added** the approved SQL query `computations/revenue-ytd.md` and linked it from `metrics/revenue.md`.

## 2026-01-05

- **Deprecated** the old revenue definition (`metrics/revenue-legacy.md`), which counted orders still inside the return window. The new definition is `metrics/revenue.md`.
