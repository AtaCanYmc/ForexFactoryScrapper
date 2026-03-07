# Minimal OpenAPI spec shared across the app
OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "ForexFactoryScrapper API",
        "version": "1.0.0",
        "description": "OpenAPI spec with schemas for the scraping API",
        "contact": {"name": "Repo maintainer", "email": "atacanymc@gmail.com"},
        "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    },
    # Helpful servers entry for local development
    "servers": [{"url": "http://localhost:5000", "description": "Local dev server"}],
    "tags": [
        {"name": "health", "description": "Health and misc endpoints"},
        {"name": "forex", "description": "ForexFactory scraping endpoints"},
        {"name": "cryptocraft", "description": "CryptoCraft scraping endpoints"},
        {"name": "metals", "description": "MetalsMine scraping endpoints"},
        {"name": "energy", "description": "EnergyExch scraping endpoints"},
    ],
    "paths": {
        "/": {
            "get": {
                "summary": "Root welcome page",
                "tags": ["health"],
                "responses": {"200": {"description": "HTML welcome page"}},
            }
        },
        "/api/hello": {
            "get": {
                "summary": "Hello endpoint",
                "tags": ["health"],
                "responses": {"200": {"description": "OK"}},
            }
        },
        "/api/health": {
            "get": {
                "summary": "Health check",
                "tags": ["health"],
                "responses": {"200": {"description": "OK"}},
            }
        },
        "/api/forex/daily": {
            "get": {
                "summary": "Get forex calendar for a day",
                "tags": ["forex"],
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
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Bad Request - invalid params",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                },
            }
        },
        "/api/cryptocraft/daily": {
            "get": {
                "summary": "Get cryptocraft events for a day",
                "tags": ["cryptocraft"],
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
                        "description": "A pagination wrapper with cryptocraft records",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/PaginatedCryptoRecords"
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Bad Request - invalid params",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                },
            }
        },
        "/api/metalsmine/daily": {
            "get": {
                "summary": "Get MetalsMine events for a day",
                "tags": ["metals"],
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
                        "description": "A pagination wrapper with metalsmine records",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/PaginatedRecords"
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Bad Request - invalid params",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                },
            }
        },
        "/api/energyexch/daily": {
            "get": {
                "summary": "Get EnergyExch events for a day",
                "tags": ["energy"],
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
                        "description": "A pagination wrapper with energyexch records",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/PaginatedRecords"
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Bad Request - invalid params",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
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
            "CryptoRecord": {
                "type": "object",
                "properties": {
                    "Time": {
                        "type": "string",
                        "description": "Localized timestamp or formatted time",
                    },
                    "Impact": {
                        "type": "string",
                        "description": "Impact level (e.g. low, medium, high)",
                    },
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
            "PaginatedCryptoRecords": {
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
                        "items": {"$ref": "#/components/schemas/CryptoRecord"},
                    },
                },
                "required": ["total", "offset", "limit", "results"],
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "description": "Error message"}
                },
                "required": ["error"],
            },
        }
    },
}
