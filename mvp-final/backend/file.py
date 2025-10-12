import requests
import json
import pyotp
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest


# ===============================================================
#  STEP 1: Login & Retrieve Logs from API
# ===============================================================

def get_logs_from_server():
    # Generate current TOTP code
    totp = pyotp.TOTP('JBSWY3DPEHPK3PXP')
    current_code = totp.now()
    print(f"Current TOTP code: {current_code}")

    # Login payload
    login_data = {
        "username": "admin",
        "password": "admin123",
        "totp_code": current_code
    }

    try:
        # Login
        login_response = requests.post(
            "http://localhost:8000/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )

        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code}")
            print(login_response.text)
            return None

        token = login_response.json().get("token")
        print(f"\nLogin successful! Token: {token}\n")

        # Retrieve logs
        logs_response = requests.get(
            "http://localhost:8000/logs",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )

        if logs_response.status_code == 200:
            logs = logs_response.json()
            print("Logs retrieved successfully!")
            return logs
        else:
            print(f"Error getting logs: {logs_response.status_code}")
            print(logs_response.text)
            return None

    except Exception as e:
        print(f"Error: {str(e)}")
        return None


# ===============================================================
#  STEP 2: Intent Detector using Isolation Forest Baseline
# ===============================================================

class UserIntentDetector:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.baseline_features = None

    def _extract_features(self, logs):
        """
        Convert raw log events into a numeric feature vector.
        Expect logs as a list of dicts.
        """
        df = pd.DataFrame(logs)
        if "timestamp" not in df or "action" not in df:
            raise ValueError("Logs must contain 'timestamp' and 'action' fields.")

        # Derived metrics
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.hour

        after_hours_ratio = len(df[(df["hour"] < 8) | (df["hour"] > 20)]) / len(df)
        unique_actions = df["action"].nunique()
        total_events = len(df)
        files_accessed = df.get("files_accessed", pd.Series([0]*len(df))).mean()
        avg_session_time = df.get("session_duration", pd.Series([0]*len(df))).mean()

        features = np.array([
            files_accessed,
            unique_actions,
            total_events,
            avg_session_time,
            after_hours_ratio
        ]).reshape(1, -1)
        return features

    def train_baseline(self, logs):
        """
        Build IsolationForest baseline from known logs (assuming mostly normal).
        """
        features = self._extract_features(logs)
        self.scaler = StandardScaler()
        scaled = self.scaler.fit_transform(features)
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.model.fit(scaled)
        self.baseline_features = scaled
        print("✅ Baseline model trained successfully!")

    def infer_intent(self, new_logs):
        """
        Compare new activity logs against baseline and infer intent.
        """
        if self.model is None:
            raise RuntimeError("Baseline not trained yet.")

        features = self._extract_features(new_logs)
        scaled = self.scaler.transform(features)
        score = self.model.decision_function(scaled)[0]  # higher = normal

        # Interpret score into human intent
        if score > 0.2:
            intent = "normal_activity"
        elif -0.2 <= score <= 0.2:
            intent = "reconnaissance"
        elif score < -0.2 and score > -0.5:
            intent = "data_exfiltration"
        else:
            intent = "privilege_escalation"

        return {
            "intent": intent,
            "anomaly_score": round(score, 3),
            "recommended_action": {
                "normal_activity": "NO_ACTION",
                "reconnaissance": "FLAG_FOR_REVIEW",
                "data_exfiltration": "TERMINATE_SESSION",
                "privilege_escalation": "IMMEDIATE_INVESTIGATION"
            }.get(intent, "REVIEW_MANUALLY")
        }


# ===============================================================
#  STEP 3: Orchestrate End-to-End Flow
# ===============================================================

if __name__ == "__main__":
    logs = get_logs_from_server()
    if logs is None:
        exit()

    detector = UserIntentDetector()

    # Assume retrieved logs are baseline (normal)
    detector.train_baseline(logs["logs"])

    # Re-run on same logs for demonstration
    result = detector.infer_intent(logs["logs"])
    print("\n=== Intent Detection Result ===")
    print(json.dumps(result, indent=2))
