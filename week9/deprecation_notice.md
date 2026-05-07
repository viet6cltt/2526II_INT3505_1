# Payment API v1 Deprecation Notice

## Overview

Payment API v1 is deprecated and will be removed in the future.
Developers should migrate to Payment API v2.

---

## Important Dates

| Event         | Date       |
| ------------- | ---------- |
| v2 Release    | 2026-05-01 |
| v1 Deprecated | 2026-08-01 |
| v1 Sunset     | 2026-12-01 |

---

## Deprecated Endpoint

```http
POST /api/v1/payment
```

---

## New Endpoint

```http
POST /api/v2/payment
```

---

## Breaking Changes in v2

| Change                  | Description        |
| ----------------------- | ------------------ |
| amount type changed     | string → integer   |
| currency field required | New required field |
| transaction_id added    | New response field |

---

## Migration Example

### v1 Request

```json
{
  "amount": "1000"
}
```

### v2 Request

```json
{
  "amount": 1000,
  "currency": "USD"
}
```

---

## Recommended Actions

* Update client integrations to use `/api/v2/payment`
* Validate request payloads for v2 compatibility
* Complete migration before 2026-12-01

---

## Contact

For support, contact the API platform team.
