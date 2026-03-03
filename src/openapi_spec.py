# Minimal OpenAPI spec shared across the app
OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "ForexFactoryScrapper API",
        "version": "1.0.0",
        "description": "OpenAPI spec with schemas for the scraping API",
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
                                    "$ref": "#/components/schemas/PaginatedRecords"
                                },
                                "examples": {
                                    "example": {
                                        "summary": "Sample response",
                                        "value": {
                                            "total": 1,
                                            "offset": 0,
                                            "limit": None,
                                            "results": [
                                                {
                                                    "Time": "01/01/2020 00:00",
                                                    "Currency": "USD",
                                                    "Event": "NFP",
                                                    "Forecast": "100k",
                                                    "Actual": "120k",
                                                    "Previous": "90k",
                                                }
                                            ],
                                        },
                                    }
                                },
                            }
                        },
                    },
                    "400": {"description": "Bad Request - invalid params"},
                },
            }
        },
    },
    "components": {
        "schemas": {
            "Record": {
                "type": "object",
                "properties": {
                    "Time": {
                        "type": "string",
                        "description": "Localized timestamp or formatted time",
                    },
                    "Currency": {"type": "string", "description": "Currency code"},
                    "Event": {"type": "string", "description": "Event name"},
                    "Forecast": {
                        "type": "string",
                        "description": "Forecast value (raw string)",
                    },
                    "Actual": {
                        "type": "string",
                        "description": "Actual value (raw string)",
                    },
                    "Previous": {
                        "type": "string",
                        "description": "Previous value (raw string)",
                    },
                },
                "additionalProperties": True,
            },
            "PaginatedRecords": {
                "type": "object",
                "properties": {
                    "total": {
                        "type": "integer",
                        "description": "Total number of available records",
                    },
                    "offset": {"type": "integer", "description": "Offset applied"},
                    "limit": {
                        "oneOf": [{"type": "integer"}, {"type": "null"}],
                        "description": "Limit applied (null means unlimited)",
                    },
                    "results": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/Record"},
                    },
                },
                "required": ["total", "offset", "limit", "results"],
            },
        }
    },
}
