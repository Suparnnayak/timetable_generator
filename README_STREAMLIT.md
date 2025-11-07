# Streamlit Web Interface for NEP Timetable Generator

## Quick Start

1. **Install Streamlit** (if not already installed):
   ```bash
   pip install streamlit
   ```
   Or install all requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

3. **Open your browser**:
   - The app will automatically open at `http://localhost:8501`
   - If not, manually navigate to that URL

## Features

### 🏠 Home Tab
- Overview of the application
- Data summary (number of slots, courses, faculty, groups)

### 📝 Data Editor Tab
- View and edit all data (courses, faculty, rooms, groups, slots)
- Edit JSON directly in the interface
- Real-time updates

### 🚀 Generate Timetable Tab
- Generate optimized timetables with one click
- Adjustable solver time limit (5-60 seconds)
- Real-time progress indicator
- Summary statistics after generation

### 📊 Results Tab
- **Assignments View**: See all course assignments by time slot
- **Student Timetables**: View individual student schedules
- **Faculty Timetables**: View faculty teaching schedules
- **Violations**: Check for any constraint violations

### 📥 Download Tab
- Download individual JSON files:
  - Assignments
  - Student Timetables
  - Faculty Timetables
  - Violations

## Data Modes

1. **Use Default Data**: Loads data from `timetable_ai/dummy_data/`
2. **Upload Custom Data**: Upload your own JSON files
3. **Edit Data Manually**: Edit data directly in the interface

## Usage Tips

- **Solver Time Limit**: Increase for complex schedules (more courses/faculty)
- **Data Editing**: Make sure JSON is valid before updating
- **Results Viewing**: Use the dropdown to switch between different views
- **Download**: All files are in JSON format for easy integration

## Troubleshooting

- **App won't start**: Make sure Streamlit is installed (`pip install streamlit`)
- **Data loading errors**: Check JSON file format is valid
- **Generation fails**: Check console for error messages, verify data constraints
- **Port already in use**: Use `streamlit run app.py --server.port 8502` to use a different port

## Next Steps

- Customize the interface by editing `app.py`
- Add more visualizations (charts, graphs)
- Integrate with database for persistent storage
- Add export to Excel/PDF formats

