from flask import Flask, request, jsonify
from dual_layer_profiling import InsiderThreatDetector
from real_time_analytics import RealTimeAnalytics
from demo_scenarios import DemoScenarios
from user_data_generation import generate_user_data
import json
import pandas as pd
app = Flask(__name__)

detector = InsiderThreatDetector()
analytics = RealTimeAnalytics(detector)
demo = DemoScenarios(analytics)

training_data = generate_user_data()
detector.train_role_baseline("analyst", training_data)

@app.route('/analyze_activity', methods = ['POST'])
def analyze_activity():
    '''endpoint for real-time activity analysis'''
    activity_log = request.json
    activity_df = pd.DataFrame(activity_log)
    result = detector.detect_anomaly(activity_df, role_name = "analyst")
    return jsonify(result)

@app.route('/demo/threat', methods = ['GET'])
def demo_threat():
    '''demo for insider threat detection'''
    demo_user_data = generate_user_data()
    demo_user_data.loc[0, 'session_duration'] = 10
    demo_user_data.loc[0, 'files_accessed'] = 25
    demo_user_data.loc[0, 'timestamp'] = demo_user_data.loc[0, 'timestamp'].replace(hour=23)
    results = detector.detect_anomaly(demo_user_data.head(1), role_name = "analyst")

    return jsonify({'scenario': 'insider_threat', 'results': results})

@app.route('/user_profile/<user_id>', methods = ['GET'])
def get_user_profile(user_id):
    '''getting user behavioral profile'''
    profile = {
        'user_id': user_id,
        'avg_session_duration': 45,
        'typical_login_times': ['09:00-17:00'],
        'file_access_pattern': 'moderate',
        'risk_level': 'low'
    }
    
    return jsonify(profile)


if __name__ == '__main__':
    app.run(debug = True, port = 5001)
    