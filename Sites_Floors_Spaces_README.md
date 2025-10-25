# FacilityApps - Sites, Floors & Spaces API

This directory contains Postman collections and environment files for testing the FacilityApps Sites, Floors, and Spaces API endpoints.

## Files

- `Sites_Floors_Spaces_Postman.json` - Postman collection with all three API endpoints
- `Sites_Floors_Spaces_Environment.json` - Postman environment with variables
- `Sites_Floors_Spaces_README.md` - This documentation file

## API Endpoints

### 1. Sites
- **Endpoint**: `GET /api/v1/planning/sites`
- **Description**: Retrieve all sites from the FacilityApps system
- **Response**: Array of site objects with id, name, address, city, country

### 2. Floors
- **Endpoint**: `GET /api/v1/planning/floors`
- **Description**: Retrieve all floors from the FacilityApps system
- **Response**: Array of floor objects with id, name, siteId, level
- **Note**: Uses `siteId` for site reference

### 3. Spaces
- **Endpoint**: `GET /api/v1/planning/spaces`
- **Description**: Retrieve all spaces from the FacilityApps system
- **Response**: Array of space objects with id, name, floor_Id, area
- **Note**: Uses `floor_Id` (capital I) for floor reference

## How to Use

### Option 1: Import into Postman

1. Open Postman
2. Click "Import" button
3. Select `Sites_Floors_Spaces_Postman.json`
4. Select `Sites_Floors_Spaces_Environment.json`
5. Set the environment to "FacilityApps - Sites, Floors & Spaces Environment"
6. Update the `token` variable with your actual Bearer token
7. Run the requests

### Option 2: cURL Commands

#### Get Sites
```bash
curl -X GET "https://demouk.facilityapps.com/api/v1/planning/sites" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json"
```

#### Get Floors
```bash
curl -X GET "https://demouk.facilityapps.com/api/v1/planning/floors" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json"
```

#### Get Spaces
```bash
curl -X GET "https://demouk.facilityapps.com/api/v1/planning/spaces" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json"
```

## Data Relationships

- **Site.id** = **Floor.siteId**
- **Floor.id** = **Space.floor_Id** (note capital I)

## Expected Response Structure

### Sites Response
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

### Floors Response
```json
[
  {
    "id": "2",
    "name": "Ground Floor",
    "siteId": "828",
    "level": 0
  }
]
```

### Spaces Response
```json
[
  {
    "id": "6",
    "name": "Reception",
    "floor_Id": "2",
    "area": 50.5
  }
]
```

## Troubleshooting

1. **Authentication Error**: Make sure your Bearer token is valid and not expired
2. **No Data**: Check if the API endpoints are accessible and return data
3. **Field Name Issues**: Note that the API uses `siteId` and `floor_Id` (capital I) for relationships
4. **CORS Issues**: If testing from a browser, you may need to disable CORS or use a CORS proxy

## Debugging the App

Use these API calls to:
1. Verify the data structure returned by each endpoint
2. Check the exact field names used for relationships
3. Confirm that sites, floors, and spaces are properly linked
4. Debug why the cascading dropdowns might not be working
