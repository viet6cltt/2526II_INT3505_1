# API Versioning Demo

Chay server:

```bash
cd week9
venv/bin/python -m app.app
```

Base URL:

```text
http://127.0.0.1:5001
```

## 1. URL versioning

Version nam truc tiep trong path cua API.

```bash
curl -i http://127.0.0.1:5001/api/v1/versioning/books
curl http://127.0.0.1:5001/api/v2/versioning/books
```

V1 tra ve response don gian:

```json
{
  "apiVersion": "1",
  "versioningStrategy": "URL path",
  "data": [
    {
      "id": 1,
      "name": "Clean Architecture"
    }
  ]
}
```

V1 dang deprecated, nen response co them headers:

```http
Deprecation: true
Sunset: 2026-12-01
Link: </api/docs/v2-migration>; rel="deprecation"; type="text/html"
Warning: 299 - "API v1 is deprecated. Please migrate to API v2 before 2026-12-01"
```

V2 mo rong schema:

```json
{
  "apiVersion": "2",
  "versioningStrategy": "URL path",
  "data": [
    {
      "id": 1,
      "title": "Clean Architecture",
      "isbn": "9780134494166",
      "authors": ["Robert C. Martin"],
      "publishedYear": 2017,
      "links": {
        "self": "/api/v2/versioning/books/1"
      }
    }
  ]
}
```

## 2. Header versioning

URL khong doi, client gui version qua header.

```bash
curl -H "X-API-Version: 1" http://127.0.0.1:5001/api/versioning/books/header
curl -H "X-API-Version: 2" http://127.0.0.1:5001/api/versioning/books/header
```

## 3. Query parameter versioning

URL khong doi, client gui version qua query string.

```bash
curl "http://127.0.0.1:5001/api/versioning/books/query?version=1"
curl "http://127.0.0.1:5001/api/versioning/books/query?version=2"
```

## Endpoint index

```bash
curl http://127.0.0.1:5001/api/versioning
```

Neu request version khong ho tro, API tra ve `400`:

```bash
curl "http://127.0.0.1:5001/api/versioning/books/query?version=3"
```

## 4. Deprecation va migration plan

V1 payment van xu ly request, nhung tra them deprecation headers va notice trong body.

```bash
curl -i -X POST http://127.0.0.1:5001/api/v1/payment \
  -H "Content-Type: application/json" \
  -d '{"amount": "1000"}'
```

V2 payment yeu cau schema moi: `amount` la integer va `currency` la bat buoc.

```bash
curl -X POST http://127.0.0.1:5001/api/v2/payment \
  -H "Content-Type: application/json" \
  -d '{"amount": 1000, "currency": "USD"}'
```

Migration guide cho client:

```bash
curl http://127.0.0.1:5001/api/docs/v2-migration
```

Noi dung can nhan manh khi day:

- `Deprecation: true`: bao client biet API version nay da bi deprecated.
- `Sunset: 2026-12-01`: ngay du kien dung ho tro v1.
- `Link`: tro den tai lieu migration.
- `Warning`: canh bao ro rang cho client/log/monitoring.
- Migration guide nen co timeline, request changes, response changes va example request moi.
