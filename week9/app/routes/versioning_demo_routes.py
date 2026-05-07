from datetime import datetime, timezone

from flask import Blueprint, jsonify, make_response, request


versioning_demo_bp = Blueprint("versioning_demo", __name__)

V1_DEPRECATION_DATE = "2026-08-01"
V1_SUNSET_DATE = "2026-12-01"


BOOKS = [
    {
        "id": 1,
        "title": "Clean Architecture",
        "isbn": "9780134494166",
        "authors": ["Robert C. Martin"],
        "publishedYear": 2017,
    },
    {
        "id": 2,
        "title": "Designing Data-Intensive Applications",
        "isbn": "9781449373320",
        "authors": ["Martin Kleppmann"],
        "publishedYear": 2017,
    },
]


def add_deprecation_headers(response):
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = V1_SUNSET_DATE
    response.headers["Link"] = (
        '</api/docs/v2-migration>; rel="deprecation"; type="text/html"'
    )
    response.headers["Warning"] = (
        '299 - "API v1 is deprecated. '
        f'Please migrate to API v2 before {V1_SUNSET_DATE}"'
    )

    return response


def serialize_books(version):
    if version == "1":
        return [
            {
                "id": book["id"],
                "name": book["title"],
            }
            for book in BOOKS
        ]

    if version == "2":
        return [
            {
                "id": book["id"],
                "title": book["title"],
                "isbn": book["isbn"],
                "authors": book["authors"],
                "publishedYear": book["publishedYear"],
                "links": {
                    "self": f"/api/v2/versioning/books/{book['id']}",
                },
            }
            for book in BOOKS
        ]

    return None


def versioned_response(strategy, version):
    data = serialize_books(version)
    if data is None:
        return (
            jsonify(
                {
                    "error": "Unsupported API version",
                    "supportedVersions": ["1", "2"],
                }
            ),
            400,
        )

    response = make_response(jsonify(
        {
            "versioningStrategy": strategy,
            "apiVersion": version,
            "data": data,
        }
    ))

    if version == "1":
        response = add_deprecation_headers(response)

    return response


@versioning_demo_bp.route("/api/versioning", methods=["GET"])
def versioning_index():
    return jsonify(
        {
            "message": "Demo 3 API versioning strategies",
            "examples": {
                "url": [
                    "GET /api/v1/versioning/books",
                    "GET /api/v2/versioning/books",
                ],
                "queryParam": [
                    "GET /api/versioning/books/query?version=1",
                    "GET /api/versioning/books/query?version=2",
                ],
                "header": [
                    "GET /api/versioning/books/header -H 'X-API-Version: 1'",
                    "GET /api/versioning/books/header -H 'X-API-Version: 2'",
                ],
                "deprecationAndMigration": [
                    "POST /api/v1/payment",
                    "POST /api/v2/payment",
                    "GET /api/docs/v2-migration",
                ],
            },
        }
    )


@versioning_demo_bp.route("/api/v1/versioning/books", methods=["GET"])
def get_books_by_url_v1():
    return versioned_response("URL path", "1")


@versioning_demo_bp.route("/api/v2/versioning/books", methods=["GET"])
def get_books_by_url_v2():
    return versioned_response("URL path", "2")


@versioning_demo_bp.route("/api/versioning/books/query", methods=["GET"])
def get_books_by_query_param():
    version = request.args.get("version", "1")
    return versioned_response("Query parameter", version)


@versioning_demo_bp.route("/api/versioning/books/header", methods=["GET"])
def get_books_by_header():
    version = request.headers.get("X-API-Version", "1")
    return versioned_response("Custom header", version)


@versioning_demo_bp.route("/api/v1/payment", methods=["POST"])
def payment_v1():
    data = request.get_json(silent=True) or {}

    response = make_response(
        jsonify(
            {
                "version": "v1",
                "status": "success",
                "message": "Payment processed",
                "deprecated": True,
                "deprecation_notice": {
                    "deprecated_since": V1_DEPRECATION_DATE,
                    "sunset_date": V1_SUNSET_DATE,
                    "migration_guide": "/api/docs/v2-migration",
                },
                "received": {
                    "amount": data.get("amount"),
                },
            }
        )
    )

    return add_deprecation_headers(response)


@versioning_demo_bp.route("/api/v2/payment", methods=["POST"])
def payment_v2():
    data = request.get_json(silent=True) or {}
    missing_fields = [
        field for field in ("amount", "currency") if data.get(field) is None
    ]

    if missing_fields:
        return (
            jsonify(
                {
                    "version": "v2",
                    "status": "error",
                    "message": "Missing required fields",
                    "missingFields": missing_fields,
                }
            ),
            400,
        )

    if not isinstance(data.get("amount"), int):
        return (
            jsonify(
                {
                    "version": "v2",
                    "status": "error",
                    "message": "amount must be an integer in v2",
                }
            ),
            400,
        )

    return jsonify(
        {
            "version": "v2",
            "status": "success",
            "transaction_id": "TXN-123456",
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "message": "Payment processed successfully",
            "amount": data["amount"],
            "currency": data["currency"],
        }
    )


@versioning_demo_bp.route("/api/docs/v2-migration", methods=["GET"])
def migration_guide():
    return jsonify(
        {
            "title": "Migration Guide v1 -> v2",
            "timeline": {
                "v1_deprecated_since": V1_DEPRECATION_DATE,
                "v1_sunset_date": V1_SUNSET_DATE,
                "recommended_action": "Move all clients from /api/v1/payment to /api/v2/payment before the sunset date.",
            },
            "request_changes": [
                {
                    "field": "amount",
                    "v1": "optional; often sent as string",
                    "v2": "required integer",
                },
                {
                    "field": "currency",
                    "v1": "not required",
                    "v2": "required ISO currency code, for example USD or VND",
                },
            ],
            "response_changes": [
                {
                    "field": "transaction_id",
                    "change": "new response field in v2",
                },
                {
                    "field": "processed_at",
                    "change": "new UTC timestamp in v2",
                },
                {
                    "field": "deprecated",
                    "change": "removed from v2 because v2 is the current version",
                },
            ],
            "example_v1_request": {
                "amount": "1000",
            },
            "example_v2_request": {
                "amount": 1000,
                "currency": "USD",
            },
        }
    )
