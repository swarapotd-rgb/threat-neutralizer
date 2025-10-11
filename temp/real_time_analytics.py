import json
import numpy as np
import pandas as pd
import joblib
from datetime import datetime, timedelta
from dual_layer_profiling import InsiderThreatDetector
from user_data_generation import generate_user_data


class RealTimeAnalytics:
    def __init__(self, detector):
        self.detector = detector
        self.active_sessions = {}
        self.threat_threshold = -0.3  # Anomaly Score Threshold
        self.last_risk_scores = {}  # Track last known risk score per user

    def process_activity_log(self, log_entry):

        if isinstance(log_entry, str):
            try:
                log_entry = json.loads(log_entry)
            except json.JSONDecodeError:
                return {"status": "error", "message": "Invalid JSON format"}

        if not isinstance(log_entry, dict):
            return {"status": "error", "message": "log_entry must be dict or JSON string"}

        user = log_entry.get('user')
        action = log_entry.get('action')

        if not user or not action:
            return {"status": "error", "message": "Missing required fields: user, action"}

        timestamp = log_entry.get('timestamp', datetime.now())

        # FIX: Initialize as list, not dict
        if user not in self.active_sessions:
            self.active_sessions[user] = []

        self.active_sessions[user].append({
            'timestamp': timestamp,
            'action': action,
            'session_duration': log_entry.get('duration', 0),
            'files_accessed': log_entry.get('files', 0)
        })

        # check anomalies every 5 events
        if len(self.active_sessions[user]) % 5 == 0:
            return self.evaluate_session(user)

        # Return last known risk score for non-evaluation events
        last_score = self.last_risk_scores.get(user, 0)
        return {'status': 'monitoring', 'risk_score': float(last_score),
                'events_until_eval': 5 - (len(self.active_sessions[user]) % 5)}

    def evaluate_session(self, user):
        # Get recent activity
        recent_activity = self.active_sessions[user][-10:]

        # Check if we have any data
        if not recent_activity:
            return {'status': 'error', 'message': 'No activity data available'}

        # Create DataFrame and add 'user' column required by detector
        activity_df = pd.DataFrame(recent_activity)
        activity_df['user'] = user

        # detect_anomaly returns a dict like: {user: {"Anomaly_Status": bool, "Scores": float}}
        results = self.detector.detect_anomaly(activity_df, 'analyst')

        # Extract the result for this user
        if user in results:
            is_anomaly = results[user]["Anomaly_Status"]
            risk_score = results[user]["Scores"]

            # Store the risk score for tracking
            self.last_risk_scores[user] = risk_score

            if is_anomaly and risk_score < self.threat_threshold:
                return {
                    'status': 'THREAT_DETECTED',
                    'user': user,
                    'risk_score': float(risk_score),
                    'timestamp': datetime.now().isoformat(),
                    'recommended_action': 'TERMINATE_SESSION'
                }

            return {'status': 'normal', 'risk_score': float(risk_score), 'is_anomaly': is_anomaly}

        # Fallback if user not in results
        return {'status': 'error', 'message': 'User not found in detection results'}



