# faculty_optimizer.py
# Assign faculty to course-slot-room assignments and balance faculty load.
# Simple heuristic: prefer possible_faculty, then expertise and availability; balance loads by greedy assignment.

from collections import defaultdict
import copy

class FacultyOptimizer:
    def __init__(self, data):
        self.faculty = {f['faculty_id']: dict(f) for f in data['faculty']}
        self.courses = {c['course_code']: dict(c) for c in data['courses']}
        self.slots = data['time_slots']
        self.rooms = {r['room_id']: r for r in data['rooms']}

    def assign_faculty(self, baseline_assignments):
        """
        baseline_assignments: dict slot -> list of {course_code, room_id}
        Returns: faculty_timetable (faculty_id->slot->course), updated assignments with faculty_id
        """
        # prepare faculty load counts
        load = {fid: 0 for fid in self.faculty}
        # prepare faculty assigned timetable
        faculty_tt = {fid: {} for fid in self.faculty}
        # result: same structure with faculty_id attached
        assignments = {}
        for s, assigns in baseline_assignments.items():
            assignments[s] = []
            for a in assigns:
                code = a['course_code']
                rid = a['room_id']
                # candidate faculty list: course.possible_faculty then those with expertise
                course_obj = self.courses.get(code, {})
                candidates = list(course_obj.get('possible_faculty', []))
                # add those who have expertise but not already listed
                for fid, fobj in self.faculty.items():
                    if code in fobj.get('expertise', []) and fid not in candidates:
                        candidates.append(fid)
                # filter by availability in slot and room compatibility
                chosen = None
                best_load = None
                for fid in candidates:
                    fobj = self.faculty[fid]
                    if s not in fobj.get('available_slots', []):
                        continue
                    # check faculty not already teaching in this slot
                    if s in faculty_tt[fid]:
                        continue
                    # check max hours
                    if load[fid] >= fobj.get('max_hours_per_week', 40):
                        continue
                    # choose least loaded candidate
                    if best_load is None or load[fid] < best_load:
                        chosen = fid
                        best_load = load[fid]
                # fallback: pick any available faculty
                if chosen is None:
                    for fid, fobj in self.faculty.items():
                        if s in fobj.get('available_slots', []) and s not in faculty_tt[fid] and load[fid] < fobj.get('max_hours_per_week', 40):
                            chosen = fid
                            break
                assignment_entry = dict(a)
                assignment_entry["faculty_id"] = chosen
                assignments[s].append(assignment_entry)
                if chosen:
                    faculty_tt[chosen][s] = code
                    load[chosen] += 1
        return assignments, faculty_tt
