# validator.py
# Validate conflict-free baseline and faculty assignments

from collections import defaultdict


def _required_sessions(course):
    if 'sessions_per_week' in course:
        return course['sessions_per_week']
    components = course.get('components') or {}
    if components:
        return max(1, sum(components.values()))
    credit_hours = course.get('credit_hours') or course.get('hours_per_week')
    if credit_hours:
        return max(1, int(credit_hours))
    return None

def validate_timetable(timetable, data):
    """
    timetable: dict slot -> list of {course_code, room_id, faculty_id (optional)}
    data: master data dict
    returns: list of violation messages
    """
    violations = []
    rooms = {r['room_id']: r for r in data['rooms']}
    faculty = {f['faculty_id']: f for f in data['faculty']}
    courses = {c['course_code']: c for c in data['courses']}
    groups = {g['group_id']: g for g in data['student_groups']}
    slots = set(data['time_slots'])
    course_tracks = {code: cobj.get('course_track') for code, cobj in courses.items()}
    course_credits = {
        code: cobj.get('credit_hours', cobj.get('sessions_per_week', cobj.get('hours_per_week', 1)))
        for code, cobj in courses.items()
    }
    group_sizes = {g['group_id']: len(g.get('students', [])) for g in data['student_groups']}

    # slot existence
    for s in timetable:
        if s not in slots:
            violations.append(f"Slot {s} is not in master slots")

    # room double-book & availability
    for s, assigns in timetable.items():
        seen_rooms = {}
        for a in assigns:
            rid = a.get('room_id')
            code = a.get('course_code')
            if rid not in rooms:
                violations.append(f"Room {rid} used at {s} not found in master list")
                continue
            if s not in rooms[rid].get('available_slots', []):
                violations.append(f"Room {rid} not available at {s} but scheduled for {code}")
            if rid in seen_rooms:
                violations.append(f"Room {rid} double-booked at {s} for {seen_rooms[rid]} and {code}")
            else:
                seen_rooms[rid] = code
            # capacity check
            groups_for_course = courses.get(code, {}).get('student_groups', [])
            total_students = sum(group_sizes.get(gid, 0) for gid in groups_for_course)
            capacity = rooms[rid].get('capacity')
            if capacity is not None and total_students > capacity:
                violations.append(
                    f"Room {rid} capacity {capacity} insufficient for {code} (needs {total_students})"
                )

    # faculty double-book & availability
    faculty_load = defaultdict(int)
    for s, assigns in timetable.items():
        seen_fac = {}
        for a in assigns:
            fid = a.get('faculty_id')
            code = a.get('course_code')
            if not fid:
                violations.append(f"No faculty assigned for {code} at {s}")
                continue
            if fid not in faculty:
                violations.append(f"Faculty {fid} assigned at {s} not in master list")
                continue
            if s not in faculty[fid].get('available_slots', []):
                violations.append(f"Faculty {fid} not available at {s} but scheduled for {code}")
            if fid in seen_fac:
                violations.append(f"Faculty {fid} double-booked at {s} for {seen_fac[fid]} and {code}")
            else:
                seen_fac[fid] = code
            faculty_load[fid] += 1

    for fid, load in faculty_load.items():
        max_hours = faculty.get(fid, {}).get('max_hours_per_week')
        if max_hours and load > max_hours:
            violations.append(f"Faculty {fid} exceeds weekly load: {load}/{max_hours}")

    # group conflicts
    course_groups = {c['course_code']: c.get('student_groups', []) for c in data['courses']}
    group_course_assignments = defaultdict(set)
    for s, assigns in timetable.items():
        group_seen = {}
        for a in assigns:
            code = a.get('course_code')
            for g in course_groups.get(code, []):
                if g in group_seen:
                    violations.append(f"Group {g} has multiple classes at {s}: {group_seen[g]} and {code}")
                else:
                    group_seen[g] = code
                group_course_assignments[g].add(code)

    # sessions count
    scheduled = defaultdict(int)
    for s, assigns in timetable.items():
        for a in assigns:
            scheduled[a['course_code']] += 1
    for code, cobj in courses.items():
        req = _required_sessions(cobj)
        if req is not None and scheduled.get(code,0) != req:
            violations.append(f"Course {code} requires {req} sessions/week but scheduled {scheduled.get(code,0)}")

    # credit and track compliance per group
    for gid, group in groups.items():
        reqs = group.get('credit_requirements', {})
        if not reqs:
            continue
        totals = defaultdict(int)
        assigned_courses = group_course_assignments.get(gid, set())
        choices = group.get('course_choices', {})
        track_overrides = {}
        if isinstance(choices, dict):
            for track_label, course_list in choices.items():
                for course in course_list:
                    track_overrides[course] = track_label.lower()
        allowed = set()
        if isinstance(choices, dict):
            for course_list in choices.values():
                allowed.update(course_list)
        else:
            allowed.update(choices)
        for course in assigned_courses:
            credit = course_credits.get(course, 0)
            track = track_overrides.get(course)
            if not track:
                track = (course_tracks.get(course) or 'elective').lower()
            totals['total'] += credit
            totals[track] += credit
        if reqs.get('min') and totals['total'] < reqs['min']:
            violations.append(f"Group {gid} total credits {totals['total']} below minimum {reqs['min']}")
        if reqs.get('max') and totals['total'] > reqs['max']:
            violations.append(f"Group {gid} total credits {totals['total']} exceeds maximum {reqs['max']}")
        if reqs.get('major_min') and totals.get('major', 0) < reqs['major_min']:
            violations.append(f"Group {gid} major credits {totals.get('major',0)} below required {reqs['major_min']}")
        if reqs.get('minor_min') and totals.get('minor', 0) < reqs['minor_min']:
            violations.append(f"Group {gid} minor credits {totals.get('minor',0)} below required {reqs['minor_min']}")
        if reqs.get('skill_min') and totals.get('skill', 0) < reqs['skill_min']:
            violations.append(f"Group {gid} skill credits {totals.get('skill',0)} below required {reqs['skill_min']}")

        if allowed:
            for course in assigned_courses:
                if course not in allowed:
                    violations.append(f"Group {gid} assigned to {course} which is outside declared choices")

    # teaching practice window compliance
    practice_windows = data.get('teaching_practice_windows')
    if practice_windows:
        window_slots = {
            key: set(value) for key, value in practice_windows.items()
        }
        for s, assigns in timetable.items():
            for a in assigns:
                code = a.get('course_code')
                course_info = courses.get(code, {})
                if not course_info.get('teaching_practice_required'):
                    continue
                target = course_info.get('student_groups', [])
                for gid in target:
                    allowed_slots = window_slots.get(gid) or window_slots.get(course_info.get('program'))
                    if allowed_slots is None:
                        continue
                    if s not in allowed_slots:
                        violations.append(
                            f"Teaching practice course {code} for {gid} scheduled at {s} outside approved window"
                        )

    return violations
