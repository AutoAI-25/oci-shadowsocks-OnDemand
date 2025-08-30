# usage_tracker.py
#
# This module tracks session start and stop times and persists
# the data to a local JSON file for usage reporting.

import json
import os
import datetime

class UsageTracker:
    """
    Tracks and reports on the usage of the Shadowsocks instance.
    """
    def __init__(self, config):
        self.config = config
        self.log_file = "usage_log.json"
        self.session_data = self._load_log()
    
    def _load_log(self):
        """
        Loads the usage log from a JSON file. Creates a new file if it doesn't exist.
        """
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return []

    def _save_log(self):
        """
        Saves the current session data to the JSON log file.
        """
        with open(self.log_file, 'w') as f:
            json.dump(self.session_data, f, indent=4)

    def log_start(self, instance_id):
        """
        Logs the start time of a new session.
        """
        new_session = {
            "instance_id": instance_id,
            "start_time": datetime.datetime.now().isoformat(),
            "end_time": None
        }
        self.session_data.append(new_session)
        self._save_log()
        print(f"Session started at {new_session['start_time']}")

    def log_stop(self):
        """
        Logs the stop time for the last open session.
        """
        if not self.session_data:
            print("No active session to stop.")
            return

        last_session = self.session_data[-1]
        if last_session["end_time"] is None:
            last_session["end_time"] = datetime.datetime.now().isoformat()
            self._save_log()
            print(f"Session stopped at {last_session['end_time']}")
        else:
            print("No active session to stop.")

    def generate_report(self):
        """
        Generates a summary report of all sessions.
        """
        total_duration = datetime.timedelta(0)
        report_lines = ["--- Usage Report ---"]
        
        for session in self.session_data:
            start_time = datetime.datetime.fromisoformat(session['start_time'])
            end_time = datetime.datetime.fromisoformat(session['end_time']) if session['end_time'] else datetime.datetime.now()
            
            duration = end_time - start_time
            total_duration += duration
            
            report_lines.append(f"Session ID: {session['instance_id']}")
            report_lines.append(f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append(f"End: {end_time.strftime('%Y-%m-%d %H:%M:%S') if session['end_time'] else 'Active'}")
            report_lines.append(f"Duration: {duration}")
            report_lines.append("-" * 20)
            
        report_lines.append(f"Total OCI Usage: {total_duration}")
        return "\n".join(report_lines)
