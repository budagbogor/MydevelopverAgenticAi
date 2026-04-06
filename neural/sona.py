import json
import os
import time
from datetime import datetime

class SonaMemory:
    """
    SONA (Trajectory Tracking Memory)
    Ref: RuFlo v3 Philosophy
    Records the 'trajectory' of an agent's reasoning and execution steps.
    """
    def __init__(self, storage_dir="neural/storage"):
        self.storage_dir = storage_dir
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        self.current_trajectory = []
        self.session_id = f"sona_{int(time.time())}"

    def start_trajectory(self, goal):
        self.current_trajectory = []
        self.goal = goal
        self.start_time = datetime.now().isoformat()
        print(f"🧠 [SONA] Starting trajectory for goal: {goal}")

    def record_step(self, agent_id, action, observation, thought="", status="SUCCESS"):
        step = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_id,
            "action": action,
            "observation": observation,
            "thought": thought,
            "status": status
        }
        self.current_trajectory.append(step)
        print(f"📍 [SONA] Step recorded for {agent_id}: {action[:50]}... Status: {status}")

    def end_trajectory(self, verdict, conclusion):
        """
        Verdict: 'SUCCESS', 'FAILURE', or 'PARTIAL'
        """
        summary = {
            "session_id": self.session_id,
            "goal": self.goal,
            "start_time": self.start_time,
            "end_time": datetime.now().isoformat(),
            "verdict": verdict,
            "conclusion": conclusion,
            "trajectory": self.current_trajectory
        }
        
        filepath = os.path.join(self.storage_dir, f"{self.session_id}.json")
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=4)
            
        print(f"🏁 [SONA] Trajectory ended. Verdict: {verdict}. Saved to {filepath}")
        return filepath

    def get_recent_trajectories(self, limit=5):
        files = sorted([f for f in os.listdir(self.storage_dir) if f.startswith("sona_")], reverse=True)
        results = []
        for file in files[:limit]:
            with open(os.path.join(self.storage_dir, file), 'r') as f:
                results.append(json.load(f))
        return results
