from dual_layer_profiling import InsiderThreatDetector
from real_time_analytics import RealTimeAnalytics
import json
import numpy as np
import pandas as pd
import joblib
import os
from datetime import datetime, timedelta


def build_baseline_from_csv(csv_file="baseline_training_data.csv", role_name="analyst", save_model=True):
    """Load baseline training data from CSV and train the model"""

    if not os.path.exists(csv_file):
        raise FileNotFoundError(
            f"Training data file '{csv_file}' not found. Please run generate_baseline_csv.py first.")

    # Load data from CSV
    print(f"Loading training data from {csv_file}...")
    data = pd.read_csv(csv_file)

    # Convert timestamp column to datetime
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    print(f"✓ Loaded {len(data)} training records")
    print(f"✓ {data['user'].nunique()} unique users")
    print(
        f"✓ Duration: {data['session_duration'].min()}-{data['session_duration'].max()} min (mean: {data['session_duration'].mean():.1f})")
    print(
        f"✓ Files: {data['files_accessed'].min()}-{data['files_accessed'].max()} (mean: {data['files_accessed'].mean():.1f})")
    print(f"✓ Time range: {data['timestamp'].min()} to {data['timestamp'].max()}")

    # Train the detector
    print(f"\nTraining InsiderThreatDetector for role '{role_name}'...")
    detector = InsiderThreatDetector()
    detector.train_role_baseline(role_name, data, contamination=0.02)
    print("✓ Model training complete")

    # Save the trained model
    if save_model:
        model_file = f'{role_name}_detector.pkl'
        joblib.dump(detector, model_file)
        print(f"✓ Model saved as {model_file}")

    return detector


def stream_events(rta, role_name="analyst"):
    """Simulate normal and anomalous activity for testing"""
    user = "u3"
    base_ts = datetime.now().replace(second=0, microsecond=0)

    # Normal baseline from CSV: 9-17 hours, 25-55 min sessions, 2-10 files
    events = [
        # Normal activity during work hours
        {"user": user, "action": "login", "timestamp": base_ts.replace(hour=10), "duration": 35, "files": 5},
        {"user": user, "action": "read", "timestamp": base_ts.replace(hour=10, minute=15), "duration": 40, "files": 6},
        {"user": user, "action": "edit", "timestamp": base_ts.replace(hour=11), "duration": 38, "files": 5},
        {"user": user, "action": "read", "timestamp": base_ts.replace(hour=11, minute=30), "duration": 42, "files": 6},
        {"user": user, "action": "logout", "timestamp": base_ts.replace(hour=12), "duration": 36, "files": 5},
        # 5th -> evaluation (NORMAL)

        # ANOMALY 1: Very short sessions (2-5 min) with MANY files (60-85) during work hours
        {"user": user, "action": "login", "timestamp": base_ts.replace(hour=14), "duration": 2, "files": 60},
        {"user": user, "action": "read", "timestamp": base_ts.replace(hour=14, minute=5), "duration": 3, "files": 70},
        {"user": user, "action": "read", "timestamp": base_ts.replace(hour=14, minute=10), "duration": 2, "files": 75},
        {"user": user, "action": "read", "timestamp": base_ts.replace(hour=14, minute=15), "duration": 4, "files": 80},
        {"user": user, "action": "logout", "timestamp": base_ts.replace(hour=14, minute=20), "duration": 3,
         "files": 85},  # 10th -> evaluation (ANOMALY)

        # ANOMALY 2: Late night (23:00) with excessive files and very short sessions
        {"user": user, "action": "login", "timestamp": base_ts.replace(hour=23), "duration": 5, "files": 90},
        {"user": user, "action": "read", "timestamp": base_ts.replace(hour=23, minute=10), "duration": 4, "files": 95},
        {"user": user, "action": "read", "timestamp": base_ts.replace(hour=23, minute=20), "duration": 3, "files": 100},
        {"user": user, "action": "read", "timestamp": base_ts.replace(hour=23, minute=30), "duration": 4, "files": 105},
        {"user": user, "action": "logout", "timestamp": base_ts.replace(hour=23, minute=40), "duration": 2,
         "files": 110},  # 15th -> evaluation (ANOMALY)

        # ANOMALY 3: Early morning (2 AM) suspicious activity with many files
        {"user": user, "action": "login", "timestamp": base_ts.replace(hour=2), "duration": 3, "files": 95},
        {"user": user, "action": "read", "timestamp": base_ts.replace(hour=2, minute=15), "duration": 2, "files": 100},
        {"user": user, "action": "edit", "timestamp": base_ts.replace(hour=2, minute=30), "duration": 4, "files": 98},
        {"user": user, "action": "read", "timestamp": base_ts.replace(hour=2, minute=45), "duration": 3, "files": 102},
        {"user": user, "action": "logout", "timestamp": base_ts.replace(hour=3), "duration": 2, "files": 105},
        # 20th -> evaluation (ANOMALY)
    ]

    print("\n" + "=" * 60)
    print("STREAMING EVENTS - Real-Time Threat Detection")
    print("=" * 60)
    print(f"Baseline: Work hours 9-17, 25-55 min sessions, 2-10 files")
    print(f"Threat threshold: {rta.threat_threshold}")
    print("=" * 60)

    for i, e in enumerate(events, 1):
        result = rta.process_activity_log(e)
        # Print every evaluation
        if i % 5 == 0:
            hour = e['timestamp'].hour
            files = e['files']
            duration = e['duration']

            print(f"\n[Event {i}] Evaluation Result:")
            print(f"  Pattern: Hour={hour}, Duration={duration}min, Files={files}")
            print(f"  Status: {result.get('status')}")
            print(f"  Risk Score: {result.get('risk_score', 'N/A'):.4f}")
            print(f"  Model Anomaly Flag: {result.get('is_anomaly', result.get('model_anomaly_flag', 'N/A'))}")
            if result.get('status') == 'THREAT_DETECTED':
                print(f"  🚨 ALERT: {result.get('recommended_action')}")
                print(f"  User: {result.get('user')}")
                print(f"  Timestamp: {result.get('timestamp')}")
            print("-" * 60)


if __name__ == "__main__":
    # Check if model exists, otherwise train from CSV
    model_file = "analyst_detector.pkl"

    if os.path.exists(model_file):
        print(f"Loading existing model from {model_file}...")
        detector = joblib.load(model_file)
        print("✓ Model loaded successfully\n")
    else:
        print("No existing model found. Training new model from CSV...")
        detector = build_baseline_from_csv(
            csv_file="baseline_training_data.csv",
            role_name="analyst",
            save_model=True
        )
        print()

    # Initialize real-time analytics
    rta = RealTimeAnalytics(detector)

    # Set threshold - IsolationForest scores: positive = normal, negative = anomaly
    # More negative = more anomalous. Typical range: -0.05 to -0.15
    rta.threat_threshold = -0.05

    # Run the streaming event simulation
    stream_events(rta, "analyst")