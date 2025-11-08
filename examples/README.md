# Frontend Integration Examples

This directory contains example code for integrating the NEP Timetable Generator API with Node.js and React applications.

## Files

- `nodejs_example.js` - Node.js integration example (works with Express, Next.js, etc.)
- `react_example.jsx` - React component example with custom hook

## Quick Start

### Node.js

1. Install dependencies:
```bash
npm install axios
```

2. Use the example:
```javascript
const { generateTimetable, validateInput } = require('./examples/nodejs_example');

// Generate timetable
const result = await generateTimetable(inputData);
```

### React

1. Install dependencies:
```bash
npm install axios
```

2. Copy the component or hook to your React app:
```jsx
import { useTimetableGenerator } from './examples/react_example';

function MyComponent() {
  const { generateTimetable, loading, error, result } = useTimetableGenerator();
  // Use the hook...
}
```

## API Configuration

Set the API base URL:

**Node.js:**
```javascript
process.env.API_URL = 'https://your-app.onrender.com';
```

**React:**
Create a `.env` file:
```
REACT_APP_API_URL=https://your-app.onrender.com
```

**Local Development:**
Default is `http://localhost:5000`

## API Endpoints

- `POST /api/generate` - Generate timetable
- `POST /api/validate` - Validate input
- `GET /health` - Health check
- `GET /api/info` - API documentation

## Example Request

```javascript
const inputData = {
  time_slots: ["Mon_09", "Mon_10", "Tue_09"],
  courses: [
    {
      course_code: "DSA",
      credit_hours: 4,
      course_track: "Major",
      components: { theory: 3, lab: 1 },
      student_groups: ["G1"],
      possible_faculty: ["F001"]
    }
  ],
  faculty: [
    {
      faculty_id: "F001",
      expertise: ["DSA"],
      available_slots: ["Mon_09", "Mon_10"],
      max_hours_per_week: 10
    }
  ],
  rooms: [
    {
      room_id: "R101",
      type: "theory",
      capacity: 60,
      available_slots: ["Mon_09", "Mon_10"]
    }
  ],
  student_groups: [
    {
      group_id: "G1",
      students: ["S001", "S002"],
      course_choices: { major: ["DSA"] }
    }
  ],
  time_limit: 10
};
```

## Response Structure

```javascript
{
  success: true,
  assignments: { /* time slot -> courses */ },
  student_timetables: { /* student -> timetable */ },
  faculty_timetables: { /* faculty -> timetable */ },
  violations: [],
  metadata: {
    time_slots_used: 14,
    students_scheduled: 4,
    faculty_assigned: 5,
    violations_count: 0,
    time_limit_used: 10
  },
  message: "Timetable generated successfully",
  timestamp: "2024-11-07T19:30:00"
}
```

## Error Handling

Always check for errors:

```javascript
try {
  const result = await generateTimetable(inputData);
  // Use result...
} catch (error) {
  console.error('Error:', error.message);
  // Handle error...
}
```

## Timeout

Generation can take 10-60 seconds. Set appropriate timeouts:

- **Axios**: `timeout: 120000` (2 minutes)
- **Fetch**: Use `AbortController` for timeout control

## CORS

The API has CORS enabled, so you can call it from any frontend domain.

## More Examples

See `FRONTEND_API_GUIDE.md` in the root directory for complete documentation.

