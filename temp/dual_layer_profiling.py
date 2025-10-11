from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

import pandas as pd
import numpy as np

class InsiderThreatDetector:
    def __init__(self):
        self.role_models = {}
        self.role_scalers = {}
        
    def extract_features(self, user_data):
        features = []
        user_ids = []
        
        for user in user_data['user'].unique():
            user_df = user_data[user_data['user']==user]
            
            avg_session_time = user_df['session_duration'].mean()
            files_per_session = user_df['files_accessed'].mean()
            login_frequency = len(user_df[user_df['action']=='login'])
            
            hours = pd.to_datetime(user_df['timestamp']).dt.hour
            work_hour_ratio = len(hours[(hours>=9) & (hours<=17)])/len(hours)
            
            features.append([avg_session_time, files_per_session, login_frequency, work_hour_ratio])
            user_ids.append(user)
            
        return np.array(features), user_ids

    def train_role_baseline(self, role_name, role_data, contamination=0.1):
        features, _ = self.extract_features(role_data)
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        model = IsolationForest(contamination = 0.1, random_state = 42, n_estimators = 200, max_samples='auto')
        model.fit(features_scaled)
        
        self.role_models[role_name] = model
        self.role_scalers[role_name] = scaler
        
        return model
    
    def detect_anomaly(self, user_activity, role_name):
        
        if role_name not in self.role_models:
            raise ValueError(f"No trained model found for role '{role_name}'")
        
        features, user_ids = self.extract_features(user_activity)
        scaler = self.role_scalers[role_name]
        model = self.role_models[role_name]
        
        features_scaled = scaler.transform(features)
        predictions = model.predict(features_scaled)
        scores = model.decision_function(features_scaled)
      
        results = {}
        for i, user in enumerate(user_ids):
            anomaly = (predictions[i]==-1)
            results[user] = {
                "Anomaly_Status": anomaly,
                "Scores": scores[i]
            }
        
        return results
  
'''
if __name__ == "__main__":
    data = pd.DataFrame({
        'user': ['u1', 'u1', 'u2', 'u2', 'u3', 'u3'],
        'role': ['analyst'] * 6,
        'timestamp': [
            '2025-10-11 10:00:00', '2025-10-11 14:00:00',
            '2025-10-11 11:00:00', '2025-10-11 12:00:00',
            '2025-10-11 23:00:00', '2025-10-11 02:00:00'
        ],
        'session_duration': [30, 45, 40, 42, 10, 15],
        'files_accessed': [5, 6, 4, 5, 20, 22],
        'action': ['login', 'logout', 'login', 'logout', 'login', 'logout']
    })

    detector = InsiderThreatDetector()
    detector.train_role_baseline("analyst", data)

    # Detect anomalies on new user activity
    new_data = pd.DataFrame({
        'user': ['u3'],
        'role': ['analyst'],
        'timestamp': ['2025-10-11 23:30:00'],
        'session_duration': [10],
        'files_accessed': [25],
        'action': ['login']
        })
    
    results = detector.detect_anomaly(new_data, "analyst")
    print(results)
'''