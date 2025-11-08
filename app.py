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
# Enable CORS for cross-origin requests (allows all origins for frontend integration)
CORS(app, resources={
    r"/api/*": {"origins": "*"},
    r"/health": {"origins": "*"},
    r"/": {"origins": "*"}
})

# Configuration
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Base path for dummy data
BASE = os.path.join(os.path.dirname(__file__), 'timetable_ai', 'dummy_data')

def load_default_data():
    """Load default data from dummy_data directory"""
    try:
        return {
            "time_slots": json.load(open(os.path.join(BASE, 'slots.json'))),
            "courses": json.load(open(os.path.join(BASE, 'courses.json'))),
            "faculty": json.load(open(os.path.join(BASE, 'faculty.json'))),
            "rooms": json.load(open(os.path.join(BASE, 'rooms.json'))),
            "student_groups": json.load(open(os.path.join(BASE, 'groups.json')))
        }
    except Exception as e:
        return None

def validate_data_structure(data):
    """Validate data structure"""
    required_fields = ['time_slots', 'courses', 'faculty', 'rooms', 'student_groups']
    missing = [field for field in required_fields if field not in data]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    if not isinstance(data.get('time_slots'), list):
        return False, "time_slots must be a list"
    if not isinstance(data.get('courses'), list):
        return False, "courses must be a list"
    if not isinstance(data.get('faculty'), list):
        return False, "faculty must be a list"
    if not isinstance(data.get('rooms'), list):
        return False, "rooms must be a list"
    if not isinstance(data.get('student_groups'), list):
        return False, "student_groups must be a list"
    
    return True, "Data structure is valid"

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    """Root endpoint - API information"""
    return jsonify({
        'service': 'NEP Timetable Generator API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'GET /': 'This endpoint (API information)',
            'GET /health': 'Health check',
            'GET /api/info': 'Detailed API information and schema',
            'GET /api/data/default': 'Get default sample data',
            'POST /api/data/summary': 'Get data summary',
            'POST /api/data/update': 'Update specific data section',
            'POST /api/validate': 'Validate input JSON structure',
            'POST /api/generate': 'Generate timetable from JSON input',
            'POST /api/results/assignments': 'Get assignments from result',
            'POST /api/results/students': 'Get student timetables from result',
            'POST /api/results/faculty': 'Get faculty timetables from result',
            'POST /api/results/violations': 'Get violations from result'
        },
        'documentation': 'See /api/info for detailed API documentation',
        'timestamp': datetime.now().isoformat()
    }), 200

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
        if DualTimetableManager is None:
            return jsonify({
                'success': False,
                'error': 'Timetable manager not available',
                'message': 'The timetable generation module could not be loaded'
            }), 500
        
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

# Get default data endpoint
@app.route('/api/data/default', methods=['GET'])
def get_default_data():
    """
    Get default sample data from dummy_data directory
    
    Returns:
    {
        "success": true,
        "data": {
            "time_slots": [...],
            "courses": [...],
            "faculty": [...],
            "rooms": [...],
            "student_groups": [...]
        },
        "message": "..."
    }
    """
    try:
        data = load_default_data()
        if data is None:
            return jsonify({
                'success': False,
                'error': 'Could not load default data',
                'message': 'Default data files not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': data,
            'message': 'Default data loaded successfully',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error loading default data',
            'timestamp': datetime.now().isoformat()
        }), 500

# Get data summary endpoint
@app.route('/api/data/summary', methods=['POST'])
def get_data_summary():
    """
    Get summary statistics of input data
    
    Request Body:
    {
        "time_slots": [...],
        "courses": [...],
        "faculty": [...],
        "rooms": [...],
        "student_groups": [...]
    }
    
    Returns:
    {
        "success": true,
        "summary": {
            "time_slots_count": 20,
            "courses_count": 5,
            "faculty_count": 3,
            "rooms_count": 4,
            "student_groups_count": 2
        },
        "valid": true/false
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Empty request body'
            }), 400
        
        # Validate structure
        valid, message = validate_data_structure(data)
        
        summary = {
            'time_slots_count': len(data.get('time_slots', [])),
            'courses_count': len(data.get('courses', [])),
            'faculty_count': len(data.get('faculty', [])),
            'rooms_count': len(data.get('rooms', [])),
            'student_groups_count': len(data.get('student_groups', []))
        }
        
        return jsonify({
            'success': True,
            'summary': summary,
            'valid': valid,
            'validation_message': message,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Update data section endpoint
@app.route('/api/data/update', methods=['POST'])
def update_data_section():
    """
    Update a specific section of the data
    
    Request Body:
    {
        "data": {
            "time_slots": [...],
            "courses": [...],
            ...
        },
        "section": "courses",  // "time_slots", "courses", "faculty", "rooms", "student_groups"
        "section_data": [...]  // New data for the section
    }
    
    Returns:
    {
        "success": true,
        "data": {...},  // Updated data
        "message": "..."
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        request_data = request.get_json()
        if not request_data:
            return jsonify({
                'success': False,
                'error': 'Empty request body'
            }), 400
        
        data = request_data.get('data')
        section = request_data.get('section')
        section_data = request_data.get('section_data')
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Missing "data" field'
            }), 400
        
        if not section:
            return jsonify({
                'success': False,
                'error': 'Missing "section" field'
            }), 400
        
        if section_data is None:
            return jsonify({
                'success': False,
                'error': 'Missing "section_data" field'
            }), 400
        
        valid_sections = ['time_slots', 'courses', 'faculty', 'rooms', 'student_groups']
        if section not in valid_sections:
            return jsonify({
                'success': False,
                'error': f'Invalid section. Must be one of: {", ".join(valid_sections)}'
            }), 400
        
        # Update the section
        data[section] = section_data
        
        # Validate updated data
        valid, message = validate_data_structure(data)
        if not valid:
            return jsonify({
                'success': False,
                'error': message,
                'message': 'Updated data is invalid'
            }), 400
        
        return jsonify({
            'success': True,
            'data': data,
            'message': f'{section} updated successfully',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Get assignments from result
@app.route('/api/results/assignments', methods=['POST'])
def get_assignments():
    """
    Extract assignments from generation result
    
    Request Body:
    {
        "result": {
            "assignments": {...},
            ...
        }
    }
    
    Returns:
    {
        "success": true,
        "assignments": {...}
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        request_data = request.get_json()
        if not request_data or 'result' not in request_data:
            return jsonify({
                'success': False,
                'error': 'Missing "result" field'
            }), 400
        
        result = request_data['result']
        assignments = result.get('assignments', {})
        
        return jsonify({
            'success': True,
            'assignments': assignments,
            'count': len(assignments),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Get student timetables from result
@app.route('/api/results/students', methods=['POST'])
def get_student_timetables():
    """
    Extract student timetables from generation result
    
    Request Body:
    {
        "result": {
            "student_timetables": {...},
            ...
        },
        "student_id": "S001"  // optional, to get specific student
    }
    
    Returns:
    {
        "success": true,
        "student_timetables": {...} or single timetable if student_id provided
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        request_data = request.get_json()
        if not request_data or 'result' not in request_data:
            return jsonify({
                'success': False,
                'error': 'Missing "result" field'
            }), 400
        
        result = request_data['result']
        student_timetables = result.get('student_timetables', {})
        student_id = request_data.get('student_id')
        
        if student_id:
            if student_id in student_timetables:
                return jsonify({
                    'success': True,
                    'student_id': student_id,
                    'timetable': student_timetables[student_id],
                    'timestamp': datetime.now().isoformat()
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': f'Student {student_id} not found',
                    'available_students': list(student_timetables.keys())
                }), 404
        
        return jsonify({
            'success': True,
            'student_timetables': student_timetables,
            'count': len(student_timetables),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Get faculty timetables from result
@app.route('/api/results/faculty', methods=['POST'])
def get_faculty_timetables():
    """
    Extract faculty timetables from generation result
    
    Request Body:
    {
        "result": {
            "faculty_timetables": {...},
            ...
        },
        "faculty_id": "F001"  // optional, to get specific faculty
    }
    
    Returns:
    {
        "success": true,
        "faculty_timetables": {...} or single timetable if faculty_id provided
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        request_data = request.get_json()
        if not request_data or 'result' not in request_data:
            return jsonify({
                'success': False,
                'error': 'Missing "result" field'
            }), 400
        
        result = request_data['result']
        faculty_timetables = result.get('faculty_timetables', {})
        faculty_id = request_data.get('faculty_id')
        
        if faculty_id:
            if faculty_id in faculty_timetables:
                return jsonify({
                    'success': True,
                    'faculty_id': faculty_id,
                    'timetable': faculty_timetables[faculty_id],
                    'timestamp': datetime.now().isoformat()
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': f'Faculty {faculty_id} not found',
                    'available_faculty': list(faculty_timetables.keys())
                }), 404
        
        return jsonify({
            'success': True,
            'faculty_timetables': faculty_timetables,
            'count': len(faculty_timetables),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Get violations from result
@app.route('/api/results/violations', methods=['POST'])
def get_violations():
    """
    Extract violations from generation result
    
    Request Body:
    {
        "result": {
            "violations": [...],
            ...
        }
    }
    
    Returns:
    {
        "success": true,
        "violations": [...],
        "count": 0
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        request_data = request.get_json()
        if not request_data or 'result' not in request_data:
            return jsonify({
                'success': False,
                'error': 'Missing "result" field'
            }), 400
        
        result = request_data['result']
        violations = result.get('violations', [])
        
        return jsonify({
            'success': True,
            'violations': violations,
            'count': len(violations),
            'has_violations': len(violations) > 0,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
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
            'GET /': 'API information',
            'GET /health': 'Health check',
            'GET /api/info': 'Detailed API information',
            'GET /api/data/default': 'Get default sample data',
            'POST /api/data/summary': 'Get data summary statistics',
            'POST /api/data/update': 'Update specific data section',
            'POST /api/validate': 'Validate input JSON structure',
            'POST /api/generate': 'Generate timetable from JSON input',
            'POST /api/results/assignments': 'Extract assignments from result',
            'POST /api/results/students': 'Extract student timetables from result',
            'POST /api/results/faculty': 'Extract faculty timetables from result',
            'POST /api/results/violations': 'Extract violations from result'
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
        'available_endpoints': [
            '/', '/health', '/api/info',
            '/api/data/default', '/api/data/summary', '/api/data/update',
            '/api/validate', '/api/generate',
            '/api/results/assignments', '/api/results/students',
            '/api/results/faculty', '/api/results/violations'
        ]
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
