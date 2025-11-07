# dual_timetable_manager.py
# Orchestrator that runs student scheduler -> faculty optimizer -> validator
import json
from .student_scheduler import StudentScheduler
from .faculty_optimizer import FacultyOptimizer
from .validator import validate_timetable

class DualTimetableManager:
    def __init__(self, data):
        self.data = data

    def generate(self, time_limit=10):
        # Step 1: student-centric baseline
        ss = StudentScheduler(self.data)
        baseline, err = ss.solve(time_limit=time_limit)
        if err:
            return None, f"StudentScheduler error: {err}"

        baseline_assignments = baseline['assignments']  # slot -> [{course_code, room_id}]
        # Step 2: assign faculty and balance load
        fo = FacultyOptimizer(self.data)
        assigned, faculty_tt = fo.assign_faculty(baseline_assignments)

        # Step 3: validate
        violations = validate_timetable(assigned, self.data)
        result = {
            "assignments": assigned,
            "student_timetables": baseline['student_timetables'],
            "faculty_timetables": faculty_tt,
            "violations": violations
        }
        return result, None

    def save_json(self, result, out_path_prefix):
        with open(out_path_prefix + "_assignments.json", "w") as f:
            json.dump(result['assignments'], f, indent=2)
        with open(out_path_prefix + "_students.json", "w") as f:
            json.dump(result['student_timetables'], f, indent=2)
        with open(out_path_prefix + "_faculty.json", "w") as f:
            json.dump(result['faculty_timetables'], f, indent=2)
        with open(out_path_prefix + "_violations.json", "w") as f:
            json.dump(result['violations'], f, indent=2)
