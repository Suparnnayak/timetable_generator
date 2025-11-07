# Flask REST API for NEP Timetable Generator

## Overview

This Flask API provides a RESTful interface for generating timetables. It accepts JSON input and returns JSON output, making it perfect for integration with other systems.

## Installation

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python app.py
```

The server will start on `http://localhost:5000` by default.

To change the port:
```bash
PORT=8080 python app.py
```

## API Endpoints

### 1. Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "NEP Timetable Generator API",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 2. API Information
**GET** `/api/info`

Get API information and schema documentation.

### 3. Validate Input
**POST** `/api/validate`

Validate input JSON structure without generating timetable.

**Request Body:**
```json
{
  "time_slots": [...],
  "courses": [...],
  "faculty": [...],
  "rooms": [...],
  "student_groups": [...]
}
```

**Response:**
```json
{
  "valid": true,
  "message": "Input structure is valid",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 4. Generate Timetable
**POST** `/api/generate`

Generate timetable from JSON input.

**Request Body:**
```json
{
  "time_slots": ["Mon_09", "Mon_10", ...],
  "courses": [
    {
      "course_code": "DSA",
      "name": "Data Structures & Algorithms",
      "credit_hours": 4,
      "course_track": "Major",
      "components": {"theory": 3, "lab": 1},
      "student_groups": ["G1"],
      "possible_faculty": ["F001"],
      "lab_required": true
    }
  ],
  "faculty": [
    {
      "faculty_id": "F001",
      "name": "Dr. Alpha",
      "expertise": ["DSA"],
      "available_slots": ["Mon_09", "Mon_10", ...],
      "max_hours_per_week": 10
    }
  ],
  "rooms": [
    {
      "room_id": "R101",
      "type": "theory",
      "capacity": 60,
      "available_slots": ["Mon_09", ...]
    }
  ],
  "student_groups": [
    {
      "group_id": "G1",
      "program": "B.Tech CS",
      "semester": 3,
      "credit_requirements": {"min": 11, "max": 20},
      "students": ["S001", "S002"],
      "course_choices": {
        "major": ["DSA"],
        "minor": ["ML"]
      }
    }
  ],
  "time_limit": 10
}
```

**Response (Success):**
```json
{
  "success": true,
  "assignments": {
    "Mon_09": [
      {
        "course_code": "DSA",
        "course_name": "Data Structures & Algorithms",
        "room_id": "R101",
        "faculty_id": "F001",
        "course_track": "Major",
        "credit_hours": 4,
        "components": {"theory": 3, "lab": 1}
      }
    ]
  },
  "student_timetables": {
    "S001": {
      "Mon_09": "DSA",
      "Tue_10": "OS"
    }
  },
  "faculty_timetables": {
    "F001": {
      "Mon_09": "DSA"
    }
  },
  "violations": [],
  "metadata": {
    "time_slots_used": 14,
    "students_scheduled": 4,
    "faculty_assigned": 5,
    "violations_count": 0,
    "time_limit_used": 10
  },
  "message": "Timetable generated successfully",
  "timestamp": "2024-01-01T12:00:00"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Error message",
  "message": "Human-readable message",
  "timestamp": "2024-01-01T12:00:00"
}
```

## Usage Examples

### Using cURL

```bash
# Health check
curl http://localhost:5000/health

# Generate timetable
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d @example_request.json

# Validate input
curl -X POST http://localhost:5000/api/validate \
  -H "Content-Type: application/json" \
  -d @example_request.json
```

### Using Python requests

```python
import requests
import json

# Load data
with open('example_request.json') as f:
    data = json.load(f)

# Generate timetable
response = requests.post(
    'http://localhost:5000/api/generate',
    json=data,
    headers={'Content-Type': 'application/json'}
)

result = response.json()
if result['success']:
    print("Timetable generated!")
    print(f"Violations: {result['metadata']['violations_count']}")
    # Save output
    with open('output.json', 'w') as f:
        json.dump(result, f, indent=2)
else:
    print(f"Error: {result['error']}")
```

### Using test script

```bash
# Start the server first
python app.py

# In another terminal, run tests
python test_api.py
```

## Input Schema

### Required Fields

- `time_slots`: List of time slot identifiers (strings)
- `courses`: List of course objects
- `faculty`: List of faculty objects
- `rooms`: List of room objects
- `student_groups`: List of student group objects

### Optional Fields

- `time_limit`: Integer (default: 10) - Solver time limit in seconds

## Output Schema

- `success`: Boolean indicating success/failure
- `assignments`: Dictionary mapping time slots to course assignments
- `student_timetables`: Dictionary mapping student IDs to their timetables
- `faculty_timetables`: Dictionary mapping faculty IDs to their teaching schedules
- `violations`: List of constraint violations (empty if all satisfied)
- `metadata`: Generation statistics
- `message`: Human-readable message
- `timestamp`: ISO format timestamp

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid input, missing fields)
- `404`: Not Found (invalid endpoint)
- `405`: Method Not Allowed
- `500`: Internal Server Error

## CORS

CORS is enabled by default, allowing cross-origin requests from web applications.

## Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Or use uWSGI:

```bash
pip install uwsgi
uwsgi --http :5000 --wsgi-file app.py --callable app
```

## Environment Variables

- `PORT`: Server port (default: 5000)
- `FLASK_DEBUG`: Enable debug mode (default: False)

## Integration Examples

See `example_request.json` for a complete input example and `test_api.py` for Python integration examples.

