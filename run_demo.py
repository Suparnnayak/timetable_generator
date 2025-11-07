# run_demo.py
import json
import os
from timetable_ai.dual_timetable_manager import DualTimetableManager
from timetable_ai.rl_agent import TimetableEnv
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

BASE = os.path.join(os.path.dirname(__file__), 'timetable_ai', 'dummy_data')
data = {
    "time_slots": json.load(open(os.path.join(BASE, 'slots.json'))),
    "courses": json.load(open(os.path.join(BASE, 'courses.json'))),
    "faculty": json.load(open(os.path.join(BASE, 'faculty.json'))),
    "rooms": json.load(open(os.path.join(BASE, 'rooms.json'))),
    "student_groups": json.load(open(os.path.join(BASE, 'groups.json'))),
}

print("Running baseline generation...")
manager = DualTimetableManager(data)
result, err = manager.generate(time_limit=10)
if err:
    print("Error:", err)
else:
    print("Violations:", result['violations'])
    # Save baseline
    out_pref = os.path.join(os.path.dirname(__file__), 'out', 'demo_baseline')
    os.makedirs(os.path.dirname(out_pref), exist_ok=True)
    manager.save_json(result, out_pref)
    print("Saved baseline assignments and timetables under out/")

    # Launch a simple RL training on baseline assignments if available
    baseline_assignments = result['assignments']
    print("Starting a short RL fine-tuning (demo only, 2000 timesteps)...")
    env_data = dict(data)
    env_data['baseline_assignments'] = baseline_assignments
    env = DummyVecEnv([lambda: TimetableEnv(env_data, baseline_assignments)])
    model = PPO('MlpPolicy', env, verbose=1)
    model.learn(total_timesteps=2000)
    model.save(os.path.join(os.path.dirname(__file__), 'out', 'ppo_timetable_demo.zip'))
    print("RL model saved to out/ppo_timetable_demo.zip")
