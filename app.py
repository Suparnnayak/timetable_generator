"""
Streamlit Web Interface for NEP Timetable Generator
"""
import streamlit as st
import json
import os
from datetime import datetime
from timetable_ai.dual_timetable_manager import DualTimetableManager

# Page configuration
st.set_page_config(
    page_title="NEP Timetable Generator",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'result' not in st.session_state:
    st.session_state.result = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

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
        st.error(f"Error loading default data: {e}")
        return None

def validate_data(data):
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

# Sidebar
with st.sidebar:
    st.title("📅 NEP Timetable Generator")
    st.markdown("---")
    
    st.subheader("Data Source")
    data_mode = st.radio(
        "Choose data source:",
        ["Use Default Data", "Upload Custom Data", "Edit Manually"],
        key="data_mode"
    )
    
    if data_mode == "Use Default Data":
        if st.button("Load Default Data"):
            data = load_default_data()
            if data:
                st.session_state.data = data
                st.session_state.data_loaded = True
                st.success("Default data loaded successfully!")
                st.rerun()
    
    elif data_mode == "Upload Custom Data":
        uploaded_files = {}
        uploaded_files['slots'] = st.file_uploader("Time Slots (slots.json)", type=['json'])
        uploaded_files['courses'] = st.file_uploader("Courses (courses.json)", type=['json'])
        uploaded_files['faculty'] = st.file_uploader("Faculty (faculty.json)", type=['json'])
        uploaded_files['rooms'] = st.file_uploader("Rooms (rooms.json)", type=['json'])
        uploaded_files['groups'] = st.file_uploader("Student Groups (groups.json)", type=['json'])
        
        if st.button("Load Uploaded Data"):
            if all(uploaded_files.values()):
                try:
                    data = {
                        "time_slots": json.load(uploaded_files['slots']),
                        "courses": json.load(uploaded_files['courses']),
                        "faculty": json.load(uploaded_files['faculty']),
                        "rooms": json.load(uploaded_files['rooms']),
                        "student_groups": json.load(uploaded_files['groups'])
                    }
                    valid, message = validate_data(data)
                    if valid:
                        st.session_state.data = data
                        st.session_state.data_loaded = True
                        st.success("Data loaded successfully!")
                        st.rerun()
                    else:
                        st.error(f"Validation error: {message}")
                except Exception as e:
                    st.error(f"Error loading data: {e}")
            else:
                st.warning("Please upload all required files")
    
    st.markdown("---")
    
    if st.session_state.data_loaded:
        st.success("✅ Data loaded")
        st.info(f"""
        - Time Slots: {len(st.session_state.data.get('time_slots', []))}
        - Courses: {len(st.session_state.data.get('courses', []))}
        - Faculty: {len(st.session_state.data.get('faculty', []))}
        - Rooms: {len(st.session_state.data.get('rooms', []))}
        - Student Groups: {len(st.session_state.data.get('student_groups', []))}
        """)

# Main content
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Home", "📝 Data Editor", "🚀 Generate", "📊 Results", "📥 Download"])

# Home Tab
with tab1:
    st.title("Welcome to NEP Timetable Generator")
    st.markdown("""
    This application generates optimized timetables for students and faculty under NEP-like flexible curricula.
    
    ### Features:
    - **Student-centric scheduling**: Optimizes student timetables first
    - **Faculty assignment**: Automatically assigns faculty to courses
    - **Constraint validation**: Ensures all constraints are satisfied
    - **Flexible data input**: Use default data, upload files, or edit manually
    
    ### How to use:
    1. **Load Data**: Use the sidebar to load default data or upload your own JSON files
    2. **Edit Data** (optional): Use the Data Editor tab to modify the data
    3. **Generate**: Go to the Generate tab and click the generate button
    4. **View Results**: Check the Results tab to see the generated timetables
    5. **Download**: Download the results as JSON files from the Download tab
    """)
    
    if st.session_state.data_loaded:
        st.success("✅ Data is loaded and ready!")
        st.subheader("Data Summary")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Time Slots", len(st.session_state.data.get('time_slots', [])))
        with col2:
            st.metric("Courses", len(st.session_state.data.get('courses', [])))
        with col3:
            st.metric("Faculty", len(st.session_state.data.get('faculty', [])))
        with col4:
            st.metric("Rooms", len(st.session_state.data.get('rooms', [])))
        with col5:
            st.metric("Student Groups", len(st.session_state.data.get('student_groups', [])))
    else:
        st.info("👈 Please load data using the sidebar to get started")

# Data Editor Tab
with tab2:
    st.title("Data Editor")
    
    if not st.session_state.data_loaded:
        st.warning("Please load data first using the sidebar")
    else:
        st.subheader("Edit Data")
        
        data_types = {
            "Time Slots": "time_slots",
            "Courses": "courses",
            "Faculty": "faculty",
            "Rooms": "rooms",
            "Student Groups": "student_groups"
        }
        
        selected_type = st.selectbox("Select data type to edit:", list(data_types.keys()))
        data_key = data_types[selected_type]
        
        # Display current data as editable JSON
        current_data = json.dumps(st.session_state.data[data_key], indent=2)
        edited_data = st.text_area(
            f"Edit {selected_type} (JSON format):",
            value=current_data,
            height=400,
            key=f"editor_{data_key}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update Data", key=f"update_{data_key}"):
                try:
                    parsed_data = json.loads(edited_data)
                    st.session_state.data[data_key] = parsed_data
                    st.success(f"{selected_type} updated successfully!")
                    st.rerun()
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON: {e}")
        
        with col2:
            if st.button("Reset to Original", key=f"reset_{data_key}"):
                st.session_state.data[data_key] = json.loads(current_data)
                st.info("Data reset to original")
                st.rerun()
        
        # Validation
        valid, message = validate_data(st.session_state.data)
        if valid:
            st.success("✅ Data structure is valid")
        else:
            st.error(f"❌ Validation error: {message}")

# Generate Tab
with tab3:
    st.title("Generate Timetable")
    
    if not st.session_state.data_loaded:
        st.warning("Please load data first using the sidebar")
    else:
        st.subheader("Generation Settings")
        
        time_limit = st.slider(
            "Solver Time Limit (seconds):",
            min_value=5,
            max_value=60,
            value=10,
            step=5,
            help="Increase for more complex schedules"
        )
        
        if st.button("🚀 Generate Timetable", type="primary", use_container_width=True):
            with st.spinner("Generating timetable... This may take a while."):
                try:
                    # Validate data before generation
                    valid, message = validate_data(st.session_state.data)
                    if not valid:
                        st.error(f"Data validation failed: {message}")
                    else:
                        manager = DualTimetableManager(st.session_state.data)
                        result, error = manager.generate(time_limit=time_limit)
                        
                        if error:
                            st.error(f"Generation failed: {error}")
                        else:
                            st.session_state.result = result
                            st.success("✅ Timetable generated successfully!")
                            
                            # Display summary
                            st.subheader("Generation Summary")
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Time Slots Used", len(result.get('assignments', {})))
                            with col2:
                                st.metric("Students Scheduled", len(result.get('student_timetables', {})))
                            with col3:
                                st.metric("Faculty Assigned", len(result.get('faculty_timetables', {})))
                            with col4:
                                violations_count = len(result.get('violations', []))
                                if violations_count == 0:
                                    st.metric("Violations", violations_count, delta="✅ None")
                                else:
                                    st.metric("Violations", violations_count, delta="⚠️ Found", delta_color="inverse")
                            
                            st.rerun()
                except Exception as e:
                    st.error(f"Error during generation: {str(e)}")
                    st.exception(e)
        
        if st.session_state.result:
            st.info("✅ Timetable has been generated. Check the Results tab to view it.")

# Results Tab
with tab4:
    st.title("Results")
    
    if not st.session_state.result:
        st.info("No results available. Please generate a timetable first.")
    else:
        result = st.session_state.result
        
        view_option = st.selectbox(
            "Select view:",
            ["Assignments", "Student Timetables", "Faculty Timetables", "Violations"]
        )
        
        if view_option == "Assignments":
            st.subheader("Course Assignments by Time Slot")
            assignments = result.get('assignments', {})
            if assignments:
                for slot, courses in assignments.items():
                    with st.expander(f"📅 {slot}"):
                        if courses:
                            for course in courses:
                                st.json(course)
                        else:
                            st.info("No courses assigned to this slot")
            else:
                st.info("No assignments found")
        
        elif view_option == "Student Timetables":
            st.subheader("Student Timetables")
            student_timetables = result.get('student_timetables', {})
            if student_timetables:
                student_id = st.selectbox("Select Student:", list(student_timetables.keys()))
                if student_id:
                    st.json(student_timetables[student_id])
            else:
                st.info("No student timetables found")
        
        elif view_option == "Faculty Timetables":
            st.subheader("Faculty Timetables")
            faculty_timetables = result.get('faculty_timetables', {})
            if faculty_timetables:
                faculty_id = st.selectbox("Select Faculty:", list(faculty_timetables.keys()))
                if faculty_id:
                    st.json(faculty_timetables[faculty_id])
            else:
                st.info("No faculty timetables found")
        
        elif view_option == "Violations":
            st.subheader("Constraint Violations")
            violations = result.get('violations', [])
            if violations:
                st.warning(f"⚠️ Found {len(violations)} violation(s)")
                for i, violation in enumerate(violations, 1):
                    with st.expander(f"Violation {i}"):
                        st.json(violation)
            else:
                st.success("✅ No violations found! All constraints are satisfied.")

# Download Tab
with tab5:
    st.title("Download Results")
    
    if not st.session_state.result:
        st.info("No results available. Please generate a timetable first.")
    else:
        result = st.session_state.result
        
        st.subheader("Download Generated Files")
        
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        
        with col1:
            assignments_json = json.dumps(result.get('assignments', {}), indent=2)
            st.download_button(
                label="📄 Download Assignments",
                data=assignments_json,
                file_name="assignments.json",
                mime="application/json"
            )
        
        with col2:
            students_json = json.dumps(result.get('student_timetables', {}), indent=2)
            st.download_button(
                label="📄 Download Student Timetables",
                data=students_json,
                file_name="student_timetables.json",
                mime="application/json"
            )
        
        with col3:
            faculty_json = json.dumps(result.get('faculty_timetables', {}), indent=2)
            st.download_button(
                label="📄 Download Faculty Timetables",
                data=faculty_json,
                file_name="faculty_timetables.json",
                mime="application/json"
            )
        
        with col4:
            violations_json = json.dumps(result.get('violations', []), indent=2)
            st.download_button(
                label="📄 Download Violations",
                data=violations_json,
                file_name="violations.json",
                mime="application/json"
            )
        
        st.markdown("---")
        st.subheader("Download Complete Results")
        complete_json = json.dumps(result, indent=2)
        st.download_button(
            label="📦 Download All Results",
            data=complete_json,
            file_name=f"timetable_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

