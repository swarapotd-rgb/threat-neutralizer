# Helper function for formatting operation details
def format_operation_details(op, user_role):
    start_date = datetime.strptime(op[5], '%Y-%m-%d %H:%M:%S')
    
    base_timeline = [
        {
            'date': op[5],
            'event': 'Operation Initiated',
            'details': 'Initial briefing and team assembly',
            'location': 'Command Center Alpha',
            'participants': ['Mission Director', 'Field Team Lead', 'Intelligence Officer']
        },
        {
            'date': (start_date + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'event': 'Phase 1 - Intelligence Gathering',
            'details': 'Deployment of surveillance assets and initial reconnaissance',
            'location': 'Field Operation Zone',
            'participants': ['Surveillance Team', 'Intelligence Analysts']
        },
        {
            'date': (start_date + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S'),
            'event': 'Phase 2 - Operation Execution',
            'details': 'Main operation phase with coordinated team actions',
            'location': 'Target Zone',
            'participants': ['Strike Team', 'Support Units', 'Medical Team']
        }
    ]
    
    basic_resources = {
        'equipment': {
            'surveillance': ['Basic surveillance equipment'],
            'communication': ['Standard communication devices'],
            'tactical': ['Standard issue gear'],
            'medical': ['Basic medical supplies']
        },
        'vehicles': {
            'ground': ['Standard vehicles'],
            'air': ['Basic surveillance drones'],
            'special': ['As needed']
        }
    }
    
    detailed_resources = {
        'equipment': {
            'surveillance': ['Thermal imaging', 'Drone units', 'Signal interceptors'],
            'communication': ['Encrypted radios', 'Satellite uplinks', 'Emergency beacons'],
            'tactical': ['Advanced tactical gear', 'Special operation equipment'],
            'medical': ['Full field medical kits', 'Emergency response equipment']
        },
        'vehicles': {
            'ground': ['Tactical vehicles', 'Support vehicles', 'Emergency response units'],
            'air': ['Surveillance drones', 'Emergency evacuation units'],
            'special': ['Mission-specific vehicles']
        }
    }
    
    basic_security = {
        'protocols': [
            'Standard security procedures',
            'Basic communication protocols',
            'Emergency procedures'
        ]
    }
    
    detailed_security = {
        'communication': [
            'Encrypted channels only',
            'Regular frequency changes',
            'Emergency silence protocols'
        ],
        'information_handling': [
            'Need-to-know basis',
            'Compartmentalized information distribution',
            'Secure data disposal procedures'
        ],
        'personnel': [
            'Regular security clearance verification',
            'Real-time location tracking',
            'Emergency extraction procedures'
        ]
    }
    
    # Return different levels of detail based on user role
    if user_role == 'admin':
        return {
            'timeline': base_timeline,
            'risk_assessment': {
                'threat_level': calculate_threat_level(op[4]),
                'environmental_risks': [
                    'Weather conditions affecting visibility',
                    'Urban environment complications',
                    'Civilian presence in operation zone'
                ],
                'countermeasures': [
                    'Advanced surveillance systems',
                    'Secure communication channels',
                    'Emergency extraction protocols',
                    'Medical evacuation routes'
                ],
                'contingency_plans': [
                    'Plan B: Alternative approach vectors',
                    'Plan C: Emergency extraction procedures',
                    'Communication failure protocols'
                ]
            },
            'resources': detailed_resources,
            'security_protocols': detailed_security,
            'success_metrics': {
                'primary_objectives': [
                    'Mission completion within timeframe',
                    'Minimal security breaches',
                    'Asset protection maintained'
                ],
                'secondary_objectives': [
                    'Intelligence gathering goals',
                    'Resource efficiency targets',
                    'Operational security maintenance'
                ],
                'performance_indicators': [
                    'Response time metrics',
                    'Resource utilization efficiency',
                    'Communication effectiveness'
                ]
            }
        }
    else:
        # Limited information for non-admin roles
        return {
            'timeline': [base_timeline[0]],  # Only show initiation
            'risk_assessment': {
                'threat_level': calculate_threat_level(op[4]),
                'environmental_risks': ['Standard operational risks'],
                'countermeasures': ['Standard security protocols']
            },
            'resources': basic_resources,
            'security_protocols': basic_security,
            'success_metrics': {
                'primary_objectives': ['Mission completion within timeframe'],
                'secondary_objectives': ['Standard operational goals']
            }
        }