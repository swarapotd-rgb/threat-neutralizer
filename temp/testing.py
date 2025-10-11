from dual_layer_profiling import InsiderThreatDetector
from real_time_analytics import RealTimeAnalytics
import json
import numpy as np
import pandas as pd
import joblib
import os
from datetime import datetime, timedelta


def build_baseline_from_csv(csv_file="baseline_training_data.csv", role_name="analyst", save_model=True):
    """Train a new baseline model from CSV"""
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Training data file '{csv_file}' not found. Please provide baseline data.")

    print(f"Loading training data from {csv_file}...")
    data = pd.read_csv(csv_file)
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    print(f"✓ Loaded {len(data)} training records for role '{role_name}'")

    detector = InsiderThreatDetector()
    detector.train_role_baseline(role_name, data, contamination=0.02)
    print("✓ Model training complete")

    if save_model:
        model_file = f'{role_name}_detector.pkl'
        joblib.dump(detector, model_file)
        print(f"✓ Model saved as {model_file}")

    return detector


def fine_tune_from_csv(detector, csv_file="baseline_training_data.csv", role_name="analyst", save_model=True):
    """Fine-tune an existing model with updated data"""
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Fine-tuning data file '{csv_file}' not found.")

    print(f"\nLoading fine-tuning data from {csv_file}...")
    data = pd.read_csv(csv_file)
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    print(f"✓ Loaded {len(data)} new records for fine-tuning")

    # Define your hyperparameter search grid (lightweight)
    param_grid = {
        'contamination': [0.02, 0.05, 0.1],
        'n_estimators': [200, 300],
        'max_samples': ['auto', 512]
    }

    model, params = detector.fine_tune_role_model(role_name, data, param_grid)
    print(f"✓ Fine-tuning complete with parameters: {params}")

    if save_model:
        model_file = f'{role_name}_detector_finetuned.pkl'
        joblib.dump(detector, model_file)
        print(f"✓ Fine-tuned model saved as {model_file}")

    return detector


def stream_events(rta, role_name="analyst"):
    """Simulate normal and anomalous activity for testing"""
    user = "u3"
    base_ts = datetime.now().replace(second=0, microsecond=0)

    events = [
        # Normal
        {"user": user, "action": "login", "timestamp": base_ts.replace(hour=10), "duration": 35, "files": 5},
        {"user": user, "action": "read", "timestamp": base_ts.replace(hour=10, minute=15), "duration": 40, "files": 6},
        {"user": user, "action": "edit", "timestamp": base_ts.replace(hour=11), "duration": 38, "files": 5},
        {"user": user, "action": "read", "timestamp": base_ts.replace(hour=11, minute=30), "duration": 42, "files": 6},
        {"user": user, "action": "logout", "timestamp": base_ts.replace(hour=12), "duration": 36, "files": 5},

        # Anomalies
        {"user": user, "action": "login", "timestamp": base_ts.replace(hour=14), "duration": 2, "files": 60},
        {"user": user, "action": "read", "timestamp": base_ts.replace(hour=14, minute=5), "duration": 3, "files": 70},
        {"user": user, "action": "logout", "timestamp": base_ts.replace(hour=14, minute=20), "duration": 3, "files": 85},

        {"user": user, "action": "login", "timestamp": base_ts.replace(hour=23), "duration": 5, "files": 90},
        {"user": user, "action": "logout", "timestamp": base_ts.replace(hour=23, minute=40), "duration": 2, "files": 110},
    ]

    print("\n" + "=" * 60)
    print("STREAMING EVENTS - Real-Time Threat Detection")
    print("=" * 60)
    print(f"Baseline: Work hours 9-17, 25-55 min sessions, 2-10 files")
    print(f"Threat threshold: {rta.threat_threshold}")
    print("=" * 60)

    for i, e in enumerate(events, 1):
        result = rta.process_activity_log(e)
        if i % 5 == 0:
            hour = e['timestamp'].hour
            files = e['files']
            duration = e['duration']

            print(f"\n[Event {i}] Evaluation Result:")
            print(f"  Pattern: Hour={hour}, Duration={duration}min, Files={files}")
            print(f"  Status: {result.get('status')}")
            print(f"  Risk Score: {result.get('risk_score', 'N/A'):.4f}")
            if result.get('status') == 'THREAT_DETECTED':
                print(f"  ALERT: {result.get('recommended_action')}")
                print(f"  User: {result.get('user')}")
                print(f"  Timestamp: {result.get('timestamp')}")
            print("-" * 60)


if __name__ == "__main__":
    role_name = "analyst"
    model_file = f"{role_name}_detector.pkl"

    # Load or fine-tune model
    if os.path.exists(model_file):
        print(f"Loading existing model from {model_file}...")
        detector = joblib.load(model_file)
        print("✓ Model loaded successfully")

        # Fine-tune using updated baseline data
        detector = fine_tune_from_csv(detector, csv_file="baseline_training_data.csv", role_name=role_name)
        print("\n✓ Model fine-tuned and ready.\n")

    else:
        print("No existing model found. Training new model from CSV...")
        detector = build_baseline_from_csv(csv_file="baseline_training_data.csv", role_name=role_name)
        print()

    # Initialize real-time analytics
    rta = RealTimeAnalytics(detector)
    rta.threat_threshold = -0.05

    # Run the event simulation
    stream_events(rta, role_name)
