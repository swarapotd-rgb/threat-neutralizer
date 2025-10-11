import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_user_data():
    users = ['chew', 'tia', 'bose', 'dk']
    roles = ['analyst']*4
    actions = ['login', 'file_access', 'data_query', 'report_generate', 'logout']
    
    normal_data = []
    
    for i,user in enumerate(users):
        for day in range(30):
            daily_actions = np.random.poisson(15)
            
            for _ in range(daily_actions):
                timestamp = datetime.now() - timedelta(days=day) + timedelta(hours = np.random.uniform(8,18))
                action = np.random.choice(actions, p = [0.1,0.4,0.3,0.1,0.1])
                normal_data.append({
                    'user': user, 'role' : roles[i], 'timestamp': timestamp, 'action': action,
                    'session_duration': np.random.normal(45, 15),  # minutes
                    'files_accessed': np.random.poisson(3),
                    'anomaly': False
                })

    return pd.DataFrame(normal_data)
