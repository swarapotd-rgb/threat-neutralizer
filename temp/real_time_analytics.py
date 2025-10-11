import json
import numpy as np
import pandas as pd
import joblib
from datetime import datetime


class RealTimeAnalytics:
    def __init__(self, detector):
        self.detector = detector
        self.active_sessions = {}
        self.threat_threshold = -0.3 #Anomaly Score Threshold
        
    def process_activity_log(self, log_entry):
        user = log_entry['user']
        action = log_entry['action']
        timestamp = datetime.now()
        
        if user not in self.active_sessions:
            self.active_sessions[user] = {}
    
        self.active_sessions[user].append({
            'timestamp':timestamp,
            'action': action,
            'session_duration':log_entry.get('duration', 0),
            'files_accessed': log_entry.get('files', 0)})
        
        # check anomalies every 5 seconds
        if len(self.active_sessions[user])%5==0:
            return self.evaluate_session(user)
        
        return {'status':'normal', 'risk_score':0}
    
    def evaluate_session(self, user):
        
        recent_activity = pd.DataFrame(self.active_sessions[user][-10:])
        
        is_anomaly, risk_score = self.detector.detect_anomaly(recent_activity)
        
        if is_anomaly and risk_score < self.threat_threshold:
            return {
                'status': 'THREAT_DETECTED',
                'user': user,
                'risk_score': float(risk_score),
                'timestamp': datetime.now().isoformat(),
                'recommended_action': 'TERMINATE_SESSION'
                }
        
        return {'status': 'normal', 'risk_score': float(risk_score)}
    
    