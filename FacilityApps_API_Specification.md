# FacilityApps API Specification

## Overview

This document provides a comprehensive specification for the FacilityApps API, including both REST and GraphQL endpoints for accessing forms, form submissions, and related data.

## Base URLs

- **REST API**: `https://{domain}/api/v1`
- **GraphQL API**: `https://{domain}/api/graphql`

## Authentication

All API requests require Bearer token authentication:

```http
Authorization: Bearer {your_token}
Content-Type: application/json
Accept: application/json
```

---

## 1. REST API Endpoints

### 1.1 Users

#### Get Users
```http
GET /api/v1/user
```

**Response:**
```json
[
  {
    "object": "user",
    "id": "1",
    "user_name": "eric.kok@facilityapps.com",
    "email": "eric.kok@facilityapps.com",
    "links": {
      "contact": "1"
    },
    "metadata": [],
    "created_at": null,
    "updated_at": "2025-06-30T02:28:44+01:00",
    "real_id": 1,
    "deleted_at": null
  }
]
```

**Postman Collection:**
```json
{
  "name": "Get Users",
  "request": {
    "method": "GET",
    "header": [
      {
        "key": "Authorization",
        "value": "Bearer {{token}}",
        "type": "text"
      },
      {
        "key": "Content-Type",
        "value": "application/json",
        "type": "text"
      }
    ],
    "url": {
      "raw": "{{base_url}}/api/v1/user",
      "host": ["{{base_url}}"],
      "path": ["api", "v1", "user"]
    }
  }
}
```

### 1.2 Contacts

#### Get Contacts
```http
GET /api/v1/contact
```

**Response:**
```json
[
  {
    "object": "contact",
    "id": "1",
    "first_name": "Eric",
    "last_name": "Kok",
    "email": "eric.kok@facilityapps.com",
    "phone_number": "+31 299 74 47 77",
    "address_1": "Spinnekop 2",
    "zip_code": "1444 GN",
    "city": "Purmerend",
    "country_code": "NL",
    "links": {
      "user": "1",
      "employee": null,
      "sites": []
    },
    "created_at": null,
    "updated_at": "2025-08-31T21:07:15+00:00",
    "real_id": 1,
    "deleted_at": null
  }
]
```

### 1.3 Employees

#### Get Employees
```http
GET /api/v1/employee
```

**Response:**
```json
[
  {
    "object": "employee",
    "id": "1",
    "name": "Bus Auditor",
    "identifier": "151189001",
    "service_start": "2025-02-19T00:00:00.000000Z",
    "service_end": null,
    "links": {
      "contact": "16",
      "sites": ["829"],
      "positions": [
        {
          "id": "1",
          "valid_from": "2025-02-01",
          "valid_to": null,
          "default": 1
        }
      ]
    },
    "contact": {
      "data": {
        "object": "contact",
        "id": "16",
        "first_name": "Bus",
        "last_name": "Auditor",
        "email": "Matthew.smith5@Icloud.com"
      }
    }
  }
]
```

### 1.4 Sites

#### Get Sites
```http
GET /api/v1/planning/sites
```

**Response:**
```json
[
  {
    "id": "828",
    "name": "Main Office",
    "address": "123 Main Street",
    "city": "London",
    "country": "UK"
  }
]
```

### 1.5 Floors

#### Get Floors
```http
GET /api/v1/planning/floors
```

**Response:**
```json
[
  {
    "id": "2",
    "name": "Ground Floor",
    "site_id": "828",
    "level": 0
  }
]
```

### 1.6 Spaces

#### Get Spaces
```http
GET /api/v1/planning/spaces
```

**Response:**
```json
[
  {
    "id": "6",
    "name": "Reception",
    "floor_id": "2",
    "area": 50.5
  }
]
```

### 1.7 Tasks

#### Get Tasks
```http
GET /api/v1/tasks
```

**Response:**
```json
[
  {
    "object": "Task",
    "id": "1",
    "title": "9626",
    "description": null,
    "date_start": "1970-01-01",
    "date_end": "1970-01-01",
    "hour_start": 0,
    "hour_end": 0,
    "minute_start": 1,
    "minute_end": 1,
    "state": "template",
    "real_id": 1
  }
]
```

---

## 2. GraphQL API Endpoints

### 2.1 Forms

#### Get Forms List
```graphql
query {
  forms(first: 50) {
    data {
      id
      name
      type
      isLogbook
      version
      canSubmit
      createdAt
      updatedAt
    }
    paginatorInfo {
      total
      count
      currentPage
      lastPage
    }
  }
}
```

**Postman Collection:**
```json
{
  "name": "Get Forms (GraphQL)",
  "request": {
    "method": "POST",
    "header": [
      {
        "key": "Authorization",
        "value": "Bearer {{token}}",
        "type": "text"
      },
      {
        "key": "Content-Type",
        "value": "application/json",
        "type": "text"
      }
    ],
    "body": {
      "mode": "raw",
      "raw": "{\n  \"query\": \"query { forms(first: 50) { data { id name type isLogbook version canSubmit createdAt updatedAt } paginatorInfo { total count currentPage lastPage } } }\"\n}",
      "options": {
        "raw": {
          "language": "json"
        }
      }
    },
    "url": {
      "raw": "{{graphql_url}}",
      "host": ["{{graphql_url}}"]
    }
  }
}
```

**Response:**
```json
{
  "data": {
    "forms": {
      "data": [
        {
          "id": "8",
          "name": "Add Logbook / Complaint",
          "type": "SITE",
          "isLogbook": true,
          "version": 1,
          "canSubmit": true,
          "createdAt": "2025-02-20T21:16:10",
          "updatedAt": "2025-05-13T12:43:49"
        }
      ],
      "paginatorInfo": {
        "total": 69,
        "count": 50,
        "currentPage": 1,
        "lastPage": 2
      }
    }
  }
}
```

### 2.2 Form Submissions

#### Get Form Submission by ID
```graphql
query {
  formSubmission(id: 127) {
    id
    submitterName
    form {
      id
      name
      type
    }
    answers {
      id
      answer
      answerProcessed
      question {
        id
        name
        identifier
        type
        options
        settings
        required
        explanation
        order
        defaultValue
        maxChoices
        optionTranslation
        createdAt
        updatedAt
      }
    }
    createdAt
    updatedAt
  }
}
```

**Postman Collection:**
```json
{
  "name": "Get Form Submission (GraphQL)",
  "request": {
    "method": "POST",
    "header": [
      {
        "key": "Authorization",
        "value": "Bearer {{token}}",
        "type": "text"
      },
      {
        "key": "Content-Type",
        "value": "application/json",
        "type": "text"
      }
    ],
    "body": {
      "mode": "raw",
      "raw": "{\n  \"query\": \"query { formSubmission(id: 127) { id submitterName form { id name type } answers { id answer answerProcessed question { id name identifier type options settings required explanation order defaultValue maxChoices optionTranslation createdAt updatedAt } } createdAt updatedAt } }\"\n}",
      "options": {
        "raw": {
          "language": "json"
        }
      }
    },
    "url": {
      "raw": "{{graphql_url}}",
      "host": ["{{graphql_url}}"]
    }
  }
}
```

**Response:**
```json
{
  "data": {
    "formSubmission": {
      "id": "127",
      "submitterName": "No user",
      "form": {
        "id": "92",
        "name": "Deliveries",
        "type": "SITE"
      },
      "answers": [
        {
          "id": "711",
          "answer": "1",
          "answerProcessed": "Yes",
          "question": {
            "id": "2629",
            "name": "Would you like to record a delivery today",
            "identifier": "Q000000",
            "type": "YES_NO",
            "options": null,
            "settings": null,
            "required": false,
            "explanation": null,
            "order": 0,
            "defaultValue": null,
            "maxChoices": null,
            "optionTranslation": "",
            "createdAt": "2025-02-20T21:16:10",
            "updatedAt": "2025-05-13T12:43:49"
          }
        }
      ],
      "createdAt": "2025-05-14 10:27:18",
      "updatedAt": "2025-05-14 10:27:20"
    }
  }
}
```

---

## 3. Data Relationships

### 3.1 Entity Relationships

```
Form (1) ──→ (Many) FormSubmission
  │
  └─── (Many) FormQuestion
           │
           └─── (1) FormSubmissionAnswer
```

### 3.2 Form Question Types

| Type | Description | Example |
|------|-------------|---------|
| `YES_NO` | Boolean questions | "Would you like to record a delivery today" |
| `SINGLE_LINE_TEXT` | Text input | "Supplier Name", "Delivery Note" |
| `NUMERIC` | Number input | "Temp" |
| `OPTIONS` | Multiple choice | "Delivery Issues" |

### 3.3 Answer Processing

The system provides both raw and processed answers:

- **Raw Answer**: Stored value (`"1"`, `""`, etc.)
- **Processed Answer**: Human-readable interpretation (`"Yes"`, `"Quality"`, etc.)

### 3.4 Question Configuration Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | ID | Unique question identifier |
| `name` | String | Question text |
| `identifier` | String | Question code (e.g., "Q000000") |
| `type` | FormQuestionType | Question type enum |
| `options` | String | Options reference ID |
| `settings` | String | JSON settings configuration |
| `required` | Boolean | Whether question is required |
| `explanation` | String | Help text or explanation |
| `order` | Int | Display order |
| `defaultValue` | String | Default answer value |
| `maxChoices` | Int | Maximum selections (for multi-choice) |
| `optionTranslation` | String | Human-readable option labels |

---

## 4. Postman Environment Variables

Create a Postman environment with these variables:

```json
{
  "id": "facilityapps-env",
  "name": "FacilityApps Environment",
  "values": [
    {
      "key": "base_url",
      "value": "https://demouk.facilityapps.com/api/v1",
      "enabled": true
    },
    {
      "key": "graphql_url",
      "value": "https://demouk.facilityapps.com/api/graphql",
      "enabled": true
    },
    {
      "key": "token",
      "value": "your_bearer_token_here",
      "enabled": true
    }
  ]
}
```

---

## 5. Complete Postman Collection

```json
{
  "info": {
    "name": "FacilityApps API",
    "description": "Complete API collection for FacilityApps REST and GraphQL endpoints",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "REST API",
      "item": [
        {
          "name": "Users",
          "item": [
            {
              "name": "Get Users",
              "request": {
                "method": "GET",
                "header": [
                  {
                    "key": "Authorization",
                    "value": "Bearer {{token}}",
                    "type": "text"
                  }
                ],
                "url": {
                  "raw": "{{base_url}}/user",
                  "host": ["{{base_url}}"],
                  "path": ["user"]
                }
              }
            }
          ]
        },
        {
          "name": "Contacts",
          "item": [
            {
              "name": "Get Contacts",
              "request": {
                "method": "GET",
                "header": [
                  {
                    "key": "Authorization",
                    "value": "Bearer {{token}}",
                    "type": "text"
                  }
                ],
                "url": {
                  "raw": "{{base_url}}/contact",
                  "host": ["{{base_url}}"],
                  "path": ["contact"]
                }
              }
            }
          ]
        },
        {
          "name": "Employees",
          "item": [
            {
              "name": "Get Employees",
              "request": {
                "method": "GET",
                "header": [
                  {
                    "key": "Authorization",
                    "value": "Bearer {{token}}",
                    "type": "text"
                  }
                ],
                "url": {
                  "raw": "{{base_url}}/employee",
                  "host": ["{{base_url}}"],
                  "path": ["employee"]
                }
              }
            }
          ]
        },
        {
          "name": "Sites",
          "item": [
            {
              "name": "Get Sites",
              "request": {
                "method": "GET",
                "header": [
                  {
                    "key": "Authorization",
                    "value": "Bearer {{token}}",
                    "type": "text"
                  }
                ],
                "url": {
                  "raw": "{{base_url}}/planning/sites",
                  "host": ["{{base_url}}"],
                  "path": ["planning", "sites"]
                }
              }
            }
          ]
        },
        {
          "name": "Floors",
          "item": [
            {
              "name": "Get Floors",
              "request": {
                "method": "GET",
                "header": [
                  {
                    "key": "Authorization",
                    "value": "Bearer {{token}}",
                    "type": "text"
                  }
                ],
                "url": {
                  "raw": "{{base_url}}/planning/floors",
                  "host": ["{{base_url}}"],
                  "path": ["planning", "floors"]
                }
              }
            }
          ]
        },
        {
          "name": "Spaces",
          "item": [
            {
              "name": "Get Spaces",
              "request": {
                "method": "GET",
                "header": [
                  {
                    "key": "Authorization",
                    "value": "Bearer {{token}}",
                    "type": "text"
                  }
                ],
                "url": {
                  "raw": "{{base_url}}/planning/spaces",
                  "host": ["{{base_url}}"],
                  "path": ["planning", "spaces"]
                }
              }
            }
          ]
        },
        {
          "name": "Tasks",
          "item": [
            {
              "name": "Get Tasks",
              "request": {
                "method": "GET",
                "header": [
                  {
                    "key": "Authorization",
                    "value": "Bearer {{token}}",
                    "type": "text"
                  }
                ],
                "url": {
                  "raw": "{{base_url}}/tasks",
                  "host": ["{{base_url}}"],
                  "path": ["tasks"]
                }
              }
            }
          ]
        }
      ]
    },
    {
      "name": "GraphQL API",
      "item": [
        {
          "name": "Forms",
          "item": [
            {
              "name": "Get Forms List",
              "request": {
                "method": "POST",
                "header": [
                  {
                    "key": "Authorization",
                    "value": "Bearer {{token}}",
                    "type": "text"
                  },
                  {
                    "key": "Content-Type",
                    "value": "application/json",
                    "type": "text"
                  }
                ],
                "body": {
                  "mode": "raw",
                  "raw": "{\n  \"query\": \"query { forms(first: 50) { data { id name type isLogbook version canSubmit createdAt updatedAt } paginatorInfo { total count currentPage lastPage } } }\"\n}",
                  "options": {
                    "raw": {
                      "language": "json"
                    }
                  }
                },
                "url": {
                  "raw": "{{graphql_url}}",
                  "host": ["{{graphql_url}}"]
                }
              }
            }
          ]
        },
        {
          "name": "Form Submissions",
          "item": [
            {
              "name": "Get Form Submission by ID",
              "request": {
                "method": "POST",
                "header": [
                  {
                    "key": "Authorization",
                    "value": "Bearer {{token}}",
                    "type": "text"
                  },
                  {
                    "key": "Content-Type",
                    "value": "application/json",
                    "type": "text"
                  }
                ],
                "body": {
                  "mode": "raw",
                  "raw": "{\n  \"query\": \"query { formSubmission(id: 127) { id submitterName form { id name type } answers { id answer answerProcessed question { id name identifier type options settings required explanation order defaultValue maxChoices optionTranslation createdAt updatedAt } } createdAt updatedAt } }\"\n}",
                  "options": {
                    "raw": {
                      "language": "json"
                    }
                  }
                },
                "url": {
                  "raw": "{{graphql_url}}",
                  "host": ["{{graphql_url}}"]
                }
              }
            }
          ]
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "https://demouk.facilityapps.com/api/v1"
    },
    {
      "key": "graphql_url",
      "value": "https://demouk.facilityapps.com/api/graphql"
    }
  ]
}
```

---

## 6. Usage Examples

### 6.1 Python Implementation

```python
import requests

class FacilityAppsClient:
    def __init__(self, domain, token):
        self.domain = domain
        self.token = token
        self.base_url = f"https://{domain}/api/v1"
        self.graphql_url = f"https://{domain}/api/graphql"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_forms(self, first=50):
        """Get forms from GraphQL API"""
        query = {
            "query": f"""
            query {{
              forms(first: {first}) {{
                data {{
                  id
                  name
                  type
                  isLogbook
                  version
                  canSubmit
                  createdAt
                  updatedAt
                }}
                paginatorInfo {{
                  total
                  count
                  currentPage
                  lastPage
                }}
              }}
            }}
            """
        }
        
        response = requests.post(self.graphql_url, headers=self.headers, json=query)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'forms' in data['data']:
                return data['forms']['data']
        return []
    
    def get_form_submission(self, submission_id):
        """Get form submission with question configurations"""
        query = {
            "query": f"""
            query {{
              formSubmission(id: {submission_id}) {{
                id
                submitterName
                form {{
                  id
                  name
                  type
                }}
                answers {{
                  id
                  answer
                  answerProcessed
                  question {{
                    id
                    name
                    identifier
                    type
                    options
                    settings
                    required
                    explanation
                    order
                    defaultValue
                    maxChoices
                    optionTranslation
                  }}
                }}
                createdAt
                updatedAt
              }}
            }}
            """
        }
        
        response = requests.post(self.graphql_url, headers=self.headers, json=query)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'formSubmission' in data['data']:
                return data['data']['formSubmission']
        return None
```

---

## 7. Error Handling

### 7.1 Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

### 7.2 GraphQL Error Format

```json
{
  "errors": [
    {
      "message": "Cannot query field 'invalidField' on type 'Form'",
      "locations": [
        {
          "line": 2,
          "column": 3
        }
      ],
      "path": ["form", "invalidField"]
    }
  ]
}
```

---

## 8. Rate Limits and Best Practices

- Use pagination for large datasets (`first: 50` parameter)
- Implement proper error handling for all requests
- Cache frequently accessed data (forms, users)
- Use appropriate timeouts (15-30 seconds)
- Monitor API response times and implement retry logic

---

## 9. Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-25 | Initial API specification with REST and GraphQL endpoints |
