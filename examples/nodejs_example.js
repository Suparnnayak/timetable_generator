/**
 * Node.js Example - NEP Timetable Generator API Integration
 * 
 * This example shows how to integrate the Flask API with Node.js applications.
 * Works with Express, Next.js, or any Node.js runtime.
 */

const axios = require('axios'); // npm install axios
// Or use fetch (Node.js 18+) or node-fetch

// Configuration
const API_BASE_URL = process.env.API_URL || 'http://localhost:5000';
// For production: 'https://your-app.onrender.com'

/**
 * Generate Timetable
 * @param {Object} inputData - Timetable input data
 * @returns {Promise<Object>} Generated timetable result
 */
async function generateTimetable(inputData) {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/generate`, inputData, {
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 120000, // 2 minutes timeout (generation can take time)
    });

    if (response.data.success) {
      console.log('✅ Timetable generated successfully!');
      console.log(`Time slots used: ${response.data.metadata.time_slots_used}`);
      console.log(`Violations: ${response.data.metadata.violations_count}`);
      return response.data;
    } else {
      throw new Error(response.data.error || response.data.message);
    }
  } catch (error) {
    if (error.response) {
      // API returned an error response
      console.error('API Error:', error.response.data);
      throw new Error(error.response.data.message || error.response.data.error);
    } else if (error.request) {
      // Request made but no response received
      console.error('Network Error: No response from server');
      throw new Error('Network error: Could not reach the API server');
    } else {
      // Something else happened
      console.error('Error:', error.message);
      throw error;
    }
  }
}

/**
 * Validate Input Data
 * @param {Object} inputData - Timetable input data
 * @returns {Promise<Object>} Validation result
 */
async function validateInput(inputData) {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/validate`, inputData, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    return response.data;
  } catch (error) {
    if (error.response) {
      return error.response.data;
    }
    throw error;
  }
}

/**
 * Health Check
 * @returns {Promise<Object>} Health status
 */
async function checkHealth() {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  } catch (error) {
    throw new Error('API is not available');
  }
}

/**
 * Get API Information
 * @returns {Promise<Object>} API documentation
 */
async function getApiInfo() {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/info`);
    return response.data;
  } catch (error) {
    throw error;
  }
}

// Example usage
async function main() {
  // Sample input data
  const sampleData = {
    time_slots: ["Mon_09", "Mon_10", "Tue_09", "Tue_10"],
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
        available_slots: ["Mon_09", "Mon_10", "Tue_09"],
        max_hours_per_week: 10
      }
    ],
    rooms: [
      {
        room_id: "R101",
        type: "theory",
        capacity: 60,
        available_slots: ["Mon_09", "Mon_10", "Tue_09"]
      }
    ],
    student_groups: [
      {
        group_id: "G1",
        students: ["S001", "S002"],
        course_choices: {
          major: ["DSA"]
        }
      }
    ],
    time_limit: 10
  };

  try {
    // 1. Check API health
    console.log('Checking API health...');
    const health = await checkHealth();
    console.log('Health:', health);

    // 2. Validate input
    console.log('\nValidating input...');
    const validation = await validateInput(sampleData);
    if (validation.valid) {
      console.log('✅ Input is valid');
    } else {
      console.error('❌ Validation errors:', validation.errors);
      return;
    }

    // 3. Generate timetable
    console.log('\nGenerating timetable...');
    const result = await generateTimetable(sampleData);

    // 4. Display results
    console.log('\n📊 Results:');
    console.log('Assignments:', JSON.stringify(result.assignments, null, 2));
    console.log('Student Timetables:', JSON.stringify(result.student_timetables, null, 2));
    console.log('Violations:', result.violations);

  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Export functions for use in other modules
module.exports = {
  generateTimetable,
  validateInput,
  checkHealth,
  getApiInfo
};

// Run example if executed directly
if (require.main === module) {
  main();
}

