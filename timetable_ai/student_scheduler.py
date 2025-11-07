
# student_scheduler.py
# Baseline student-centric scheduler using OR-Tools CP-SAT.
# Produces student timetables and course-slot-room assignments.

import json
from ortools.sat.python import cp_model
from collections import defaultdict, OrderedDict

class StudentScheduler:
    def __init__(self, data):
        """
        data dict must contain:
          - time_slots: list of slot ids
          - courses: list of course dicts (course_code, sessions_per_week, student_groups, possible_faculty optional)
          - rooms: list of rooms (room_id, type, capacity, available_slots)
          - student_groups: group definitions (group_id, students, course_choices)
          - faculty: faculty list for availability (used later)
        """
        self.slots = data['time_slots']
        self.courses = data['courses']
        self.rooms = data['rooms']
        self.groups = data['student_groups']
        self.faculty = data.get('faculty', [])
        self.model = cp_model.CpModel()
        self.vars = {}  # (course, slot, room) -> BoolVar
        self.course_map = {c['course_code']: c for c in self.courses}
        self.group_requirements = {
            g['group_id']: g.get('credit_requirements', {}) for g in self.groups
        }

    def _sessions_required(self, course):
        if 'sessions_per_week' in course:
            return course['sessions_per_week']
        components = course.get('components') or {}
        if components:
            return max(1, sum(components.values()))
        credit_hours = course.get('credit_hours') or course.get('hours_per_week')
        if credit_hours:
            return max(1, int(credit_hours))
        return 1

    def build_vars(self):
        for c in self.courses:
            code = c['course_code']
            components = c.get('components') or {}
            requires_lab = c.get('lab_required', False)
            if not requires_lab:
                practicum_hours = components.get('practicum', 0) + components.get('lab', 0)
                requires_lab = practicum_hours > 0
            for s in self.slots:
                for r in self.rooms:
                    # Quick room suitability: if course needs lab and room isn't lab, skip if productively desired.
                    if requires_lab and r.get('type','theory') != 'lab':
                        continue
                    self.vars[(code, s, r['room_id'])] = self.model.NewBoolVar(f"x_{code}_{s}_{r['room_id']}")

    def add_hard_constraints(self):
        # sessions per week
        for c in self.courses:
            code = c['course_code']
            needed = self._sessions_required(c)
            self.model.Add(sum(self.vars[k] for k in self.vars if k[0]==code) == needed)

        # room occupancy: at most 1 course per room per slot
        for r in self.rooms:
            rid = r['room_id']
            avail = set(r.get('available_slots', []))
            for s in self.slots:
                # if room not available this slot -> no assignment
                if s not in avail:
                    for k in list(self.vars):
                        if k[1]==s and k[2]==rid:
                            self.model.Add(self.vars[k] == 0)
                else:
                    self.model.Add(sum(self.vars[k] for k in self.vars if k[1]==s and k[2]==rid) <= 1)

        # group conflicts: group cannot have >1 course at same slot
        for g in self.groups:
            gid = g['group_id']
            group_courses = [c['course_code'] for c in self.courses if gid in c.get('student_groups', [])]
            for s in self.slots:
                self.model.Add(sum(self.vars[k] for k in self.vars if k[0] in group_courses and k[1]==s) <= 1)
        
        # HARD CONSTRAINT: Same course cannot be scheduled in consecutive time slots on same day
        # (e.g., DSA at Mon_09 and Mon_10 is not allowed)
        for course_code in self.course_map.keys():
            course_vars = [(k, v) for k, v in self.vars.items() if k[0] == course_code]
            if len(course_vars) < 2:
                continue
            
            # Group by day and time
            day_slots = {}
            for (code, slot, room), var in course_vars:
                day = slot.split('_')[0]
                time = int(slot.split('_')[1])
                if day not in day_slots:
                    day_slots[day] = {}
                if time not in day_slots[day]:
                    day_slots[day][time] = []
                day_slots[day][time].append(var)
            
            # For each day, prevent consecutive time slots
            for day, time_slots in day_slots.items():
                times = sorted(time_slots.keys())
                for i in range(len(times) - 1):
                    if times[i+1] - times[i] == 1:  # Consecutive hours (e.g., 09 and 10)
                        # At most one of these consecutive slots can be used
                        slot1_vars = time_slots[times[i]]
                        slot2_vars = time_slots[times[i+1]]
                        self.model.Add(sum(slot1_vars) + sum(slot2_vars) <= 1)

        # fixed events (if any)
        for c in self.courses:
            # optionally you can add fixed-slot blocking here per course
            pass

    def add_soft_objective(self):
        # Multi-objective: prefer consecutive DAYS, avoid same subject consecutively
        # 1. Avoid late slots
        late_slots = [s for s in self.slots if '17' in s or '18' in s or '19' in s]
        late_penalties = []
        for k, v in self.vars.items():
            if k[1] in late_slots:
                late_penalties.append(v)
        
        # 2. PENALIZE same subject scheduled consecutively (e.g., DSA at Mon_09 and Mon_10)
        slot_to_idx = {s: i for i, s in enumerate(self.slots)}
        consecutive_subject_penalties = []
        
        for course_code in self.course_map.keys():
            course_vars = [(k, v) for k, v in self.vars.items() if k[0] == course_code]
            if len(course_vars) < 2:
                continue
            
            # Group vars by slot
            slot_vars = {}
            for (code, slot, room), var in course_vars:
                if slot not in slot_vars:
                    slot_vars[slot] = []
                slot_vars[slot].append(var)
            
            # Check for consecutive slots (same day, adjacent times)
            slot_list = sorted(slot_vars.keys(), key=lambda s: slot_to_idx.get(s, 999))
            for i, s1 in enumerate(slot_list):
                slot_idx1 = slot_to_idx.get(s1, 999)
                day1 = s1.split('_')[0]  # Extract day (Mon, Tue, etc.)
                time1 = int(s1.split('_')[1])  # Extract time (09, 10, etc.)
                
                # Check if next slot is consecutive (same day, next hour)
                for s2 in slot_list[i+1:]:
                    slot_idx2 = slot_to_idx.get(s2, 999)
                    day2 = s2.split('_')[0]
                    time2 = int(s2.split('_')[1])
                    
                    # If same day and consecutive time slots (e.g., 09 and 10), penalize heavily
                    if day1 == day2 and (time2 - time1) == 1:
                        # Both slots used for same course = bad
                        both_used = self.model.NewBoolVar(f"consec_{course_code}_{s1}_{s2}")
                        s1_sum = sum(slot_vars[s1])
                        s2_sum = sum(slot_vars[s2])
                        self.model.Add(both_used >= s1_sum - len(slot_vars[s1]) + 1)
                        self.model.Add(both_used >= s2_sum - len(slot_vars[s2]) + 1)
                        self.model.Add(both_used <= s1_sum)
                        self.model.Add(both_used <= s2_sum)
                        consecutive_subject_penalties.append(50 * both_used)  # Very heavy penalty
        
        # 3. PREFER consecutive DAYS for student groups (spread classes across week)
        day_penalties = []
        day_order = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4}
        
        for group in self.groups:
            gid = group['group_id']
            group_courses = [c['course_code'] for c in self.courses if gid in c.get('student_groups', [])]
            
            # Track which days have classes for this group
            day_usage = {}
            for day in day_order.keys():
                day_vars = []
                for (code, slot, room), var in self.vars.items():
                    if code in group_courses and slot.startswith(day):
                        day_vars.append(var)
                if day_vars:
                    day_used = self.model.NewBoolVar(f"day_{gid}_{day}")
                    self.model.Add(day_used >= sum(day_vars) - len(day_vars) + 1)
                    self.model.Add(day_used <= sum(day_vars))
                    day_usage[day] = day_used
            
            # Prefer consecutive days: reward Mon-Tue-Wed pattern, penalize scattered
            # Penalize if days are far apart (e.g., Mon and Fri but nothing in between)
            day_list = sorted([d for d in day_usage.keys()], key=lambda d: day_order.get(d, 99))
            for i, d1 in enumerate(day_list):
                for d2 in day_list[i+1:]:
                    gap = day_order.get(d2, 99) - day_order.get(d1, 0)
                    if gap > 2:  # Penalize large gaps between days
                        both_days = self.model.NewBoolVar(f"days_{gid}_{d1}_{d2}")
                        self.model.Add(both_days >= day_usage[d1] + day_usage[d2] - 1)
                        self.model.Add(both_days <= day_usage[d1])
                        self.model.Add(both_days <= day_usage[d2])
                        day_penalties.append(gap * both_days)
        
        # 4. Minimize total penalties
        all_penalties = late_penalties + consecutive_subject_penalties + day_penalties
        
        if all_penalties:
            self.model.Minimize(sum(all_penalties))
        else:
            self.model.Minimize(0)

    def solve(self, time_limit=10):
        self.build_vars()
        self.add_hard_constraints()
        self.add_soft_objective()
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit
        solver.parameters.num_search_workers = 8
        status = solver.Solve(self.model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None, "No feasible student timetable found."

        # Build course assignments (slot-> assignments)
        assignments = defaultdict(list)
        for (code, s, rid), var in self.vars.items():
            if solver.Value(var)==1:
                course_obj = self.course_map.get(code, {})
                assignments[s].append({
                    "course_code": code,
                    "course_name": course_obj.get('name'),
                    "room_id": rid,
                    "course_track": course_obj.get('course_track'),
                    "credit_hours": course_obj.get('credit_hours'),
                    "components": course_obj.get('components')
                })

        # Build student timetables (per student id)
        student_tt = defaultdict(dict)
        # map course -> groups
        course_groups = {c['course_code']: c.get('student_groups', []) for c in self.courses}
        slot_order = {s: i for i, s in enumerate(self.slots)}
        ordered_assignments = OrderedDict()
        for slot in sorted(assignments.keys(), key=lambda x: slot_order.get(x, len(self.slots))):
            ordered_assignments[slot] = sorted(
                assignments[slot],
                key=lambda x: x.get('course_code', '')
            )
        for s, assigns in ordered_assignments.items():
            for a in assigns:
                code = a['course_code']
                for g in course_groups.get(code, []):
                    # each group's students get course in slot s
                    # group students may be many; we assign per student id
                    group_obj = next((x for x in self.groups if x['group_id']==g), None)
                    if group_obj:
                        for stu in group_obj.get('students', []):
                            student_tt[stu][s] = code

        return {"assignments": dict(ordered_assignments), "student_timetables": dict(student_tt)}, None
