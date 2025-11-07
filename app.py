"""
Flask REST API for NEP Timetable Generator
Accepts JSON input and returns JSON output
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from timetable_ai.dual_timetable_manager import DualTimetableManager

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Configuration
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'NEP Timetable Generator API',
        'timestamp': datetime.now().isoformat()
    }), 200

# Generate timetable endpoint
@app.route('/api/generate', methods=['POST'])
def generate_timetable():
    """
    Generate timetable from JSON input
    
    Expected JSON structure:
    {
        "time_slots": [...],
        "courses": [...],
        "faculty": [...],
        "rooms": [...],
        "student_groups": [...],
        "time_limit": 10  // optional, default 10
    }
    
    Returns:
    {
        "success": true/false,
        "assignments": {...},
        "student_timetables": {...},
        "faculty_timetables": {...},
        "violations": [...],
        "message": "...",
        "timestamp": "..."
    }
    """
    try:
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json',
                'message': 'Please send JSON data'
            }), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Empty request body',
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['time_slots', 'courses', 'faculty', 'rooms', 'student_groups']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': 'Missing required fields',
                'missing_fields': missing_fields,
                'message': f'Required fields: {", ".join(required_fields)}'
            }), 400
        
        # Extract time limit (optional, default 10)
        time_limit = data.get('time_limit', 10)
        if not isinstance(time_limit, int) or time_limit < 1:
            time_limit = 10
        
        # Prepare input data
        input_data = {
            'time_slots': data['time_slots'],
            'courses': data['courses'],
            'faculty': data['faculty'],
            'rooms': data['rooms'],
            'student_groups': data['student_groups']
        }
        
        # Generate timetable
        manager = DualTimetableManager(input_data)
        result, error = manager.generate(time_limit=time_limit)
        
        if error:
            return jsonify({
                'success': False,
                'error': error,
                'message': 'Timetable generation failed',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Prepare response
        response = {
            'success': True,
            'assignments': result['assignments'],
            'student_timetables': result['student_timetables'],
            'faculty_timetables': result['faculty_timetables'],
            'violations': result['violations'],
            'message': 'Timetable generated successfully',
            'metadata': {
                'time_slots_used': len(result['assignments']),
                'students_scheduled': len(result['student_timetables']),
                'faculty_assigned': len(result['faculty_timetables']),
                'violations_count': len(result['violations']),
                'time_limit_used': time_limit
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except json.JSONDecodeError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid JSON format',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Validate input endpoint
@app.route('/api/validate', methods=['POST'])
def validate_input():
    """
    Validate input JSON structure without generating timetable
    
    Returns validation results
    """
    try:
        if not request.is_json:
            return jsonify({
                'valid': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'valid': False,
                'error': 'Empty request body'
            }), 400
        
        # Validate required fields
        required_fields = ['time_slots', 'courses', 'faculty', 'rooms', 'student_groups']
        missing_fields = [field for field in required_fields if field not in data]
        
        validation_errors = []
        
        if missing_fields:
            validation_errors.append(f'Missing required fields: {", ".join(missing_fields)}')
        
        # Validate data types
        if 'time_slots' in data and not isinstance(data['time_slots'], list):
            validation_errors.append('time_slots must be a list')
        
        if 'courses' in data and not isinstance(data['courses'], list):
            validation_errors.append('courses must be a list')
        
        if 'faculty' in data and not isinstance(data['faculty'], list):
            validation_errors.append('faculty must be a list')
        
        if 'rooms' in data and not isinstance(data['rooms'], list):
            validation_errors.append('rooms must be a list')
        
        if 'student_groups' in data and not isinstance(data['student_groups'], list):
            validation_errors.append('student_groups must be a list')
        
        if validation_errors:
            return jsonify({
                'valid': False,
                'errors': validation_errors,
                'timestamp': datetime.now().isoformat()
            }), 400
        
        return jsonify({
            'valid': True,
            'message': 'Input structure is valid',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Get API info endpoint
@app.route('/api/info', methods=['GET'])
def api_info():
    """Get API information and schema"""
    return jsonify({
        'service': 'NEP Timetable Generator API',
        'version': '1.0.0',
        'endpoints': {
            'POST /api/generate': 'Generate timetable from JSON input',
            'POST /api/validate': 'Validate input JSON structure',
            'GET /api/info': 'Get API information',
            'GET /health': 'Health check'
        },
        'input_schema': {
            'time_slots': 'List of time slot identifiers (e.g., ["Mon_09", "Mon_10", ...])',
            'courses': 'List of course objects with course_code, credit_hours, course_track, etc.',
            'faculty': 'List of faculty objects with faculty_id, expertise, available_slots, etc.',
            'rooms': 'List of room objects with room_id, type, capacity, available_slots, etc.',
            'student_groups': 'List of student group objects with group_id, students, course_choices, etc.',
            'time_limit': 'Optional integer (default: 10) - solver time limit in seconds'
        },
        'output_schema': {
            'success': 'Boolean indicating success/failure',
            'assignments': 'Dictionary mapping time slots to course assignments',
            'student_timetables': 'Dictionary mapping student IDs to their timetables',
            'faculty_timetables': 'Dictionary mapping faculty IDs to their teaching schedules',
            'violations': 'List of constraint violations (empty if all constraints satisfied)',
            'metadata': 'Generation metadata (counts, time used, etc.)',
            'message': 'Human-readable message',
            'timestamp': 'ISO format timestamp'
        },
        'timestamp': datetime.now().isoformat()
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': ['/health', '/api/generate', '/api/validate', '/api/info']
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Method not allowed',
        'message': 'The HTTP method is not allowed for this endpoint'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║     NEP Timetable Generator API - Flask Server           ║
    ╠══════════════════════════════════════════════════════════╣
    ║  Server running on: http://localhost:{port}                ║
    ║  Health check: http://localhost:{port}/health              ║
    ║  API info: http://localhost:{port}/api/info                ║
    ║  Generate: POST http://localhost:{port}/api/generate       ║
    ║  Validate: POST http://localhost:{port}/api/validate       ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # For production, use gunicorn instead
    # gunicorn app:app --bind 0.0.0.0:PORT
    app.run(host='0.0.0.0', port=port, debug=debug)
