import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Create a LARGE baseline dataset with realistic patterns
base_ts = datetime.now().replace(minute=0, second=0, microsecond=0)

users = []
roles = []
timestamps = []
durations = []
files = []
actions = []

# Generate 500+ normal work sessions across 50 users over 10 days
num_users = 50
num_days = 10
role_name = "analyst"

for day in range(num_days):
    for user_idx in range(num_users):
        user = f"user_{user_idx:03d}"

        # Each user has 1-2 sessions per day during work hours
        num_sessions = np.random.choice([1, 2], p=[0.7, 0.3])

        for session in range(num_sessions):
            # Work hours: 9 AM - 5 PM (with some variation)
            session_start_hour = np.random.randint(9, 17)
            session_start_minute = np.random.randint(0, 60)

            # Normal session duration: 25-55 minutes (mean ~40)
            session_duration = int(np.random.normal(40, 8))
            session_duration = max(25, min(55, session_duration))  # Clip to range

            # Normal files accessed: 2-10 files (mean ~5-6)
            files_accessed = int(np.random.normal(6, 2))
            files_accessed = max(2, min(10, files_accessed))  # Clip to range

            # Number of activities in this session (3-8)
            num_activities = np.random.randint(3, 9)

            session_timestamp = (base_ts + timedelta(days=day)).replace(
                hour=session_start_hour,
                minute=session_start_minute
            )

            for activity_idx in range(num_activities):
                # Determine action type
                if activity_idx == 0:
                    action = "login"
                elif activity_idx == num_activities - 1:
                    action = "logout"
                else:
                    action = np.random.choice(["read", "edit", "open", "download"],
                                              p=[0.4, 0.3, 0.2, 0.1])

                # Add some variance to each activity
                activity_duration = session_duration + np.random.randint(-5, 6)
                activity_duration = max(20, activity_duration)

                activity_files = files_accessed + np.random.randint(-2, 3)
                activity_files = max(1, activity_files)

                activity_timestamp = session_timestamp + timedelta(minutes=activity_idx * 5)

                users.append(user)
                roles.append(role_name)
                timestamps.append(activity_timestamp)
                durations.append(activity_duration)
                files.append(activity_files)
                actions.append(action)

# Add some edge cases within normal behavior (early birds, late workers)
# 5% of sessions at 8 AM
for _ in range(int(len(users) * 0.05)):
    user = f"user_{np.random.randint(0, num_users):03d}"
    early_ts = (base_ts + timedelta(days=np.random.randint(0, num_days))).replace(hour=8)

    users.append(user)
    roles.append(role_name)
    timestamps.append(early_ts)
    durations.append(int(np.random.normal(40, 8)))
    files.append(int(np.random.normal(6, 2)))
    actions.append("login")

# 5% of sessions at 6 PM
for _ in range(int(len(users) * 0.05)):
    user = f"user_{np.random.randint(0, num_users):03d}"
    late_ts = (base_ts + timedelta(days=np.random.randint(0, num_days))).replace(hour=18)

    users.append(user)
    roles.append(role_name)
    timestamps.append(late_ts)
    durations.append(int(np.random.normal(40, 8)))
    files.append(int(np.random.normal(6, 2)))
    actions.append("login")

# Create DataFrame
data = pd.DataFrame({
    "user": users,
    "role": roles,
    "timestamp": timestamps,
    "session_duration": durations,
    "files_accessed": files,
    "action": actions,
})

# Save to CSV
csv_filename = "baseline_training_data.csv"
data.to_csv(csv_filename, index=False)

print(f"✓ Generated {len(data)} training records")
print(f"✓ {data['user'].nunique()} unique users")
print(
    f"✓ Duration: {data['session_duration'].min()}-{data['session_duration'].max()} min (mean: {data['session_duration'].mean():.1f})")
print(
    f"✓ Files: {data['files_accessed'].min()}-{data['files_accessed'].max()} (mean: {data['files_accessed'].mean():.1f})")
print(f"✓ Saved to: {csv_filename}")