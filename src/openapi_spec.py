# Minimal OpenAPI spec shared across the app
OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "ForexFactoryScrapper API",
        "version": "1.0.0",
        "description": "Minimal OpenAPI spec for the small scraping API",
    },
    "paths": {
        "/api/hello": {
            "get": {
                "summary": "Hello endpoint",
                "responses": {"200": {"description": "OK"}},
            }
        },
        "/api/health": {
            "get": {
                "summary": "Health check",
                "responses": {"200": {"description": "OK"}},
            }
        },
        "/api/forex/daily": {
            "get": {
                "summary": "Get forex calendar for a day",
                "parameters": [
                    {
                        "name": "day",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Day of month",
                    },
                    {
                        "name": "month",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Month (1-12)",
                    },
                    {
                        "name": "year",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "integer"},
                        "description": "Year (e.g. 2020)",
                    },
                    {
                        "name": "limit",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "integer", "minimum": 0},
                        "description": "Max number of results to return",
                    },
                    {
                        "name": "offset",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "integer", "minimum": 0},
                        "description": "Number of records to skip",
                    },
                ],
                "responses": {
                    "200": {
                        "description": "A pagination wrapper with metadata and results",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "total": {
                                            "type": "integer",
                                            "description": "Total number of available records",
                                        },
                                        "offset": {
                                            "type": "integer",
                                            "description": "Offset applied",
                                        },
                                        "limit": {
                                            "oneOf": [
                                                {"type": "integer"},
                                                {"type": "null"},
                                            ],
                                            "description": "Limit applied (null means unlimited)",
                                        },
                                        "results": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "additionalProperties": True,
                                                "description": "A single parsed record (fields depend on scraper)",
                                            },
                                        },
                                    },
                                    "required": ["total", "offset", "limit", "results"],
                                }
                            }
                        },
                    },
                    "400": {"description": "Bad Request - invalid params"},
                },
            }
        },
    },
}
