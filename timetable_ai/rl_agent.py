

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import json
import os
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from collections import defaultdict

class TimetableEnv(gym.Env):
    """
    Environment that receives baseline assignments and attempts to perform slot swaps
    to reduce soft-constraint penalties (faculty stress, student gaps).
    State: flattened vector encoding current assignment indices for N courses
    Action: swap two course assignments (encoded as two indices)
    Reward: negative count of violations (higher is better)
    """
    metadata = {"render.modes": ["human"]}

    def __init__(self, data, baseline_assignments):
        super().__init__()
        self.data = data
        self.courses = [c['course_code'] for c in data['courses']]
        self.slots = data['time_slots']
        # flatten baseline assignments into list of (course, slot, room)
        self.assign_list = []
        for s, assigns in baseline_assignments.items():
            for a in assigns:
                self.assign_list.append((a['course_code'], s, a['room_id']))
        self.n = len(self.assign_list)
        if self.n < 2:
            # trivial environment
            self.action_space = spaces.Discrete(1)
            self.observation_space = spaces.Box(low=0, high=1, shape=(1,), dtype=np.int32)
        else:
            # action: pick index i and j to swap slots -> encode as single integer: i * n + j
            self.action_space = spaces.Discrete(self.n * self.n)
            # observation: for each assignment, encode its slot index
            self.observation_space = spaces.Box(low=0, high=len(self.slots)-1, shape=(self.n,), dtype=np.int32)

        self.reset()

    def step(self, action):
        if self.n < 2:
            return np.array([0]), 0, True, False, {}
        i = action // self.n
        j = action % self.n
        # swap slots between assignments i and j
        self.assign_list[i], self.assign_list[j] = (self.assign_list[i][0], self.assign_list[j][1], self.assign_list[i][2]), (self.assign_list[j][0], self.assign_list[i][1], self.assign_list[j][2])
        obs = self._get_obs()
        reward = self._compute_reward()
        done = False
        info = {}
        return obs, reward, done, False, info

    def reset(self, seed=None, options=None):
        # reinitialize assign_list from baseline
        self.assign_list = []
        baseline = {}
        for s, assigns in self.data.get('baseline_assignments', {}).items():
            baseline[s] = assigns
            for a in assigns:
                self.assign_list.append((a['course_code'], s, a['room_id']))
        # store baseline in case not present
        if not baseline:
            baseline = self.data.get('baseline_assignments', {})
        self.data['baseline_assignments'] = baseline
        return self._get_obs(), {}

    def _get_obs(self):
        # map slot string to index
        slot_to_idx = {s:i for i,s in enumerate(self.slots)}
        return np.array([slot_to_idx[a[1]] for a in self.assign_list], dtype=np.int32)

    def _compute_reward(self):
        # simple negative violation count: conflicts in faculty, group, room etc.
        # Build timetable dict
        timetable = defaultdict(list)
        for course, slot, room in self.assign_list:
            timetable[slot].append({"course_code": course, "room_id": room})
        # compute basic penalties: group overlapping and room double-book
        penalty = 0
        # room double-book
        for s, assigns in timetable.items():
            rooms = [a['room_id'] for a in assigns]
            if len(rooms) != len(set(rooms)):
                penalty += 5
        # group overlaps
        course_groups = {c['course_code']: c.get('student_groups', []) for c in self.data['courses']}
        for s, assigns in timetable.items():
            group_seen = set()
            for a in assigns:
                for g in course_groups.get(a['course_code'], []):
                    if g in group_seen:
                        penalty += 5
                    group_seen.add(g)
        return -penalty

    def render(self, mode="human"):
        print("Assignments:")
        for a in self.assign_list:
            print(a)
