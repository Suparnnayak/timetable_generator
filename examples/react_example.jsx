/**
 * React Example - NEP Timetable Generator API Integration
 * 
 * This example shows how to integrate the Flask API with a React application.
 * 
 * Installation:
 * npm install axios
 * 
 * Or use fetch API (built-in, no installation needed)
 */

import React, { useState } from 'react';
import axios from 'axios'; // npm install axios

// Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
// For production, set REACT_APP_API_URL=https://your-app.onrender.com in .env

/**
 * Custom Hook for Timetable Generation
 */
function useTimetableGenerator() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const generateTimetable = async (inputData) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/generate`, inputData, {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 120000, // 2 minutes
      });

      if (response.data.success) {
        setResult(response.data);
        return response.data;
      } else {
        throw new Error(response.data.error || response.data.message);
      }
    } catch (err) {
      const errorMessage = err.response?.data?.message || 
                        err.response?.data?.error || 
                        err.message || 
                        'Failed to generate timetable';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const validateInput = async (inputData) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/validate`, inputData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      return response.data;
    } catch (err) {
      return {
        valid: false,
        errors: [err.response?.data?.error || err.message || 'Validation failed']
      };
    }
  };

  const checkHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      return response.data;
    } catch (err) {
      return { status: 'unhealthy' };
    }
  };

  return {
    generateTimetable,
    validateInput,
    checkHealth,
    loading,
    error,
    result,
  };
}

/**
 * React Component Example
 */
function TimetableGenerator() {
  const { generateTimetable, validateInput, checkHealth, loading, error, result } = useTimetableGenerator();
  const [inputData, setInputData] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);

  // Check API health on component mount
  React.useEffect(() => {
    checkHealth().then(status => {
      setHealthStatus(status.status === 'healthy' ? 'online' : 'offline');
    });
  }, []);

  const handleGenerate = async () => {
    if (!inputData) {
      alert('Please provide input data');
      return;
    }

    // Validate first
    const validation = await validateInput(inputData);
    if (!validation.valid) {
      alert('Validation failed: ' + validation.errors.join(', '));
      return;
    }

    // Generate timetable
    try {
      await generateTimetable(inputData);
    } catch (err) {
      // Error is already set by the hook
      console.error('Generation failed:', err);
    }
  };

  return (
    <div className="timetable-generator">
      <h1>NEP Timetable Generator</h1>
      
      {/* API Status */}
      <div className="status">
        <p>API Status: 
          <span className={healthStatus === 'online' ? 'online' : 'offline'}>
            {healthStatus || 'checking...'}
          </span>
        </p>
      </div>

      {/* Input Data Editor */}
      <div className="input-section">
        <h2>Input Data</h2>
        <textarea
          placeholder="Paste your JSON input data here..."
          rows={10}
          onChange={(e) => {
            try {
              setInputData(JSON.parse(e.target.value));
            } catch (err) {
              // Invalid JSON, ignore for now
            }
          }}
        />
      </div>

      {/* Generate Button */}
      <button 
        onClick={handleGenerate}
        disabled={loading || !inputData}
        className="generate-button"
      >
        {loading ? 'Generating...' : 'Generate Timetable'}
      </button>

      {/* Error Display */}
      {error && (
        <div className="error">
          <h3>Error</h3>
          <p>{error}</p>
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="results">
          <h2>Results</h2>
          
          {/* Summary */}
          <div className="summary">
            <h3>Summary</h3>
            <ul>
              <li>Time Slots Used: {result.metadata.time_slots_used}</li>
              <li>Students Scheduled: {result.metadata.students_scheduled}</li>
              <li>Faculty Assigned: {result.metadata.faculty_assigned}</li>
              <li>Violations: {result.metadata.violations_count}</li>
            </ul>
          </div>

          {/* Assignments */}
          <div className="assignments">
            <h3>Assignments</h3>
            <pre>{JSON.stringify(result.assignments, null, 2)}</pre>
          </div>

          {/* Student Timetables */}
          <div className="student-timetables">
            <h3>Student Timetables</h3>
            <pre>{JSON.stringify(result.student_timetables, null, 2)}</pre>
          </div>

          {/* Faculty Timetables */}
          <div className="faculty-timetables">
            <h3>Faculty Timetables</h3>
            <pre>{JSON.stringify(result.faculty_timetables, null, 2)}</pre>
          </div>

          {/* Violations */}
          {result.violations.length > 0 && (
            <div className="violations">
              <h3>⚠️ Violations</h3>
              <pre>{JSON.stringify(result.violations, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * Alternative: Using Fetch API (No dependencies)
 */
async function generateTimetableWithFetch(inputData) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(inputData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || errorData.error || 'Request failed');
    }

    const result = await response.json();
    
    if (result.success) {
      return result;
    } else {
      throw new Error(result.error || result.message);
    }
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

export default TimetableGenerator;
export { useTimetableGenerator, generateTimetableWithFetch };

