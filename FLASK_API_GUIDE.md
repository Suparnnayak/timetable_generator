# Complete Flask API Guide for Node.js/React Integration

Complete REST API for NEP Timetable Generator! All functionality is available via JSON endpoints.

## 🎯 Quick Start

```bash
# Start the Flask API
cd ML
python app.py

# API runs on http://localhost:5000
```

## 📋 All Available Endpoints

### 1. **GET** `/api/data/default` - Get Default Sample Data
Load default sample data to get started quickly.

**Request:**
```http
GET /api/data/default
```

**Response:**
```json
{
  "success": true,
  "data": {
    "time_slots": [...],
    "courses": [...],
    "faculty": [...],
    "rooms": [...],
    "student_groups": [...]
  },
  "message": "Default data loaded successfully"
}
```

**Node.js/React Example:**
```javascript
const response = await fetch('http://localhost:5000/api/data/default');
const { data } = await response.json();
// Use data to populate your form
```

---

### 2. **POST** `/api/data/summary` - Get Data Summary
Get statistics about your input data.

**Request:**
```http
POST /api/data/summary
Content-Type: application/json

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
  "success": true,
  "summary": {
    "time_slots_count": 20,
    "courses_count": 5,
    "faculty_count": 3,
    "rooms_count": 4,
    "student_groups_count": 2
  },
  "valid": true,
  "validation_message": "Data structure is valid"
}
```

---

### 3. **POST** `/api/data/update` - Update Data Section
Update a specific section of your data (like editing in Streamlit).

**Request:**
```http
POST /api/data/update
Content-Type: application/json

{
  "data": {
    "time_slots": [...],
    "courses": [...],
    "faculty": [...],
    "rooms": [...],
    "student_groups": [...]
  },
  "section": "courses",
  "section_data": [
    {
      "course_code": "DSA",
      "credit_hours": 4,
      ...
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    // Updated complete data
  },
  "message": "courses updated successfully"
}
```

---

### 4. **POST** `/api/validate` - Validate Input
Validate your data structure before generating.

**Request:**
```http
POST /api/validate
Content-Type: application/json

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
  "message": "Input structure is valid"
}
```

---

### 5. **POST** `/api/generate` - Generate Timetable ⭐
Main endpoint to generate the timetable.

**Request:**
```http
POST /api/generate
Content-Type: application/json

{
  "time_slots": [...],
  "courses": [...],
  "faculty": [...],
  "rooms": [...],
  "student_groups": [...],
  "time_limit": 10
}
```

**Response:**
```json
{
  "success": true,
  "assignments": {...},
  "student_timetables": {...},
  "faculty_timetables": {...},
  "violations": [],
  "metadata": {
    "time_slots_used": 14,
    "students_scheduled": 4,
    "faculty_assigned": 5,
    "violations_count": 0,
    "time_limit_used": 10
  },
  "message": "Timetable generated successfully"
}
```

---

### 6. **POST** `/api/results/assignments` - Get Assignments
Extract just the assignments from a result.

**Request:**
```http
POST /api/results/assignments
Content-Type: application/json

{
  "result": {
    "assignments": {...},
    "student_timetables": {...},
    ...
  }
}
```

**Response:**
```json
{
  "success": true,
  "assignments": {...},
  "count": 14
}
```

---

### 7. **POST** `/api/results/students` - Get Student Timetables
Get all student timetables or a specific one.

**Request (All Students):**
```http
POST /api/results/students
Content-Type: application/json

{
  "result": {
    "student_timetables": {...},
    ...
  }
}
```

**Request (Specific Student):**
```http
POST /api/results/students
Content-Type: application/json

{
  "result": {
    "student_timetables": {...},
    ...
  },
  "student_id": "S001"
}
```

**Response:**
```json
{
  "success": true,
  "student_id": "S001",
  "timetable": {
    "Mon_09": "DSA",
    "Tue_10": "OS"
  }
}
```

---

### 8. **POST** `/api/results/faculty` - Get Faculty Timetables
Get all faculty timetables or a specific one.

**Request:**
```http
POST /api/results/faculty
Content-Type: application/json

{
  "result": {
    "faculty_timetables": {...},
    ...
  },
  "faculty_id": "F001"  // optional
}
```

---

### 9. **POST** `/api/results/violations` - Get Violations
Check for constraint violations.

**Request:**
```http
POST /api/results/violations
Content-Type: application/json

{
  "result": {
    "violations": [...],
    ...
  }
}
```

**Response:**
```json
{
  "success": true,
  "violations": [],
  "count": 0,
  "has_violations": false
}
```

---

## 🔄 Complete Workflow Example

### React/Node.js Integration

```javascript
// 1. Load default data
const loadDefaultData = async () => {
  const response = await fetch('http://localhost:5000/api/data/default');
  const { data } = await response.json();
  return data;
};

// 2. Get summary
const getSummary = async (data) => {
  const response = await fetch('http://localhost:5000/api/data/summary', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return await response.json();
};

// 3. Update a section
const updateSection = async (data, section, sectionData) => {
  const response = await fetch('http://localhost:5000/api/data/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      data,
      section,
      section_data: sectionData
    })
  });
  return await response.json();
};

// 4. Validate
const validate = async (data) => {
  const response = await fetch('http://localhost:5000/api/validate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return await response.json();
};

// 5. Generate timetable
const generateTimetable = async (data, timeLimit = 10) => {
  const response = await fetch('http://localhost:5000/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...data,
      time_limit: timeLimit
    })
  });
  return await response.json();
};

// 6. Extract specific results
const getStudentTimetable = async (result, studentId) => {
  const response = await fetch('http://localhost:5000/api/results/students', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      result,
      student_id: studentId
    })
  });
  return await response.json();
};
```

## 📊 Available Features

All features are available as REST API endpoints:
- ✅ Load default data
- ✅ Get data summary
- ✅ Update data sections
- ✅ Validate input
- ✅ Generate timetables
- ✅ Extract results (assignments, students, faculty, violations)

## 🚀 Ready for Production

The API is ready to:
- Deploy to Render/Heroku/AWS
- Integrate with Node.js/React frontend
- Handle JSON requests/responses
- Support CORS for cross-origin requests

See `examples/nodejs_example.js` and `examples/react_example.jsx` for complete integration examples!

