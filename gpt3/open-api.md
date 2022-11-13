# Generating OpenAPI specifications using GPT-3

I wanted to start playing around with [OpenAPI](https://www.openapis.org/). I decided to see if I could get GPT-3 to generate the first version of a specification for me.

I used this prompt:
```
Write an OpenAPI JSON specification for the following APIs:

GET /data/docs.json

Returns:

{
  "database": "data",
  "table": "docs",
  "rows": [
    {
      "id": 1,
      "title": "A title"
    },
    {
      "id": 2,
      "title": "Another doc"
    }
  ]
}

POST /data/-/create
{
  "table": "my_new_table",
  "columns": [
    {
      "name": "id",
      "type": "integer"
    },
    {
      "name": "age",
      "type": "float"
    },
    {
      "name": "title",
      "type": "text"
    }
  ],
  "pk": "id"
}

Output:

{
  "ok": true,
  "database": "data",
  "table": "my_new_table",
  "table_url": "http://127.0.0.1:8001/data/my_new_table"
}
```
I had to hit the button in the Playground a few times due to the length, but the eventual output looked like this:
```json
{
  "swagger": "2.0",
  "info": {
    "version": "1.0.0",
    "title": "Data API"
  },
  "paths": {
    "/data/docs.json": {
      "get": {
        "tags": [
          "data"
        ],
        "summary": "Get data from docs.json",
        "operationId": "getData",
        "produces": [
          "application/json"
        ],
        "parameters": [],
        "responses": {
          "200": {
            "description": "Successful response",
            "schema": {
              "type": "object",
              "properties": {
                "database": {
                  "type": "string"
                },
                "table": {
                  "type": "string"
                },
                "rows": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "id": {
                        "type": "integer"
                      },
                      "title": {
                        "type": "string"
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "/data/{id}": {
      "post": {
        "tags": [
          "data"
        ],
        "summary": "Create a new table",
        "operationId": "createTable",
        "produces": [
          "application/json"
        ],
        "parameters": [
          {
            "name": "table",
            "in": "path",
            "required": true,
            "type": "string"
          },
          {
            "name": "columns",
            "in": "body",
            "required": true,
            "schema": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "name": {
                    "type": "string"
                  },
                  "type": {
                    "type": "string"
                  }
                }
              }
            }
          },
          {
            "name": "pk",
            "in": "body",
            "required": true,
            "type": "string"
          }
        ],
        "responses": {
          "200": {
            "description": "Successful response",
            "schema": {
              "type": "object",
              "properties": {
                "ok": {
                  "type": "boolean"
                },
                "database": {
                  "type": "string"
                },
                "table": {
                  "type": "string"
                },
                "table_url": {
                  "type": "string"
                }
              }
            }
          }
        }
      }
    }
  }
}
```
