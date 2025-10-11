class DemoScenarios:
    def __init__(self,analytics_engine):
        self.engine = analytics_engine
    
    def simulate_insider_threat(self):
        
        sus_logs = [
            # Unusual login time (3 AM)
            {'user': 'chew', 'action': 'login', 'duration': 120, 'files': 0, 'time': '03:00'},
            # Excessive file access
            {'user': 'tia', 'action': 'file_access', 'duration': 45, 'files': 25, 'time': '03:15'},
            # Unusual data queries
            {'user': 'bose', 'action': 'data_query', 'duration': 90, 'files': 15, 'time': '03:30'},
            # Long session duration
            {'user': 'dk', 'action': 'report_generate', 'duration': 180, 'files': 30, 'time': '04:00'}
        ]
        
        results = []
        for log in sus_logs:
            result = self.analytics_engine.process_activity_log(log)
            results.append(result)
            
        return results
    
    def normal_behavior(self):
        
        normal_logs = [
            {'user': 'chew', 'action': 'login', 'duration': 45, 'files': 0, 'time': '09:00'},
            {'user': 'tia', 'action': 'file_access', 'duration': 30, 'files': 3, 'time': '09:15'},
            {'user': 'bose', 'action': 'data_query', 'duration': 25, 'files': 2, 'time': '10:00'}
        ]
    
        results = []
        for log in normal_logs:
            result = self.analytics_engine.process_activity_log(log)
            results.append(result)
        
        return results
            