import requests
from functools import wraps
from flask import session

def report_solve(lab_name):
    """
    The Success Bridge.
    Wraps a Flask route and notifies the Django Gateway on success.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. Run the original lab code
            response = f(*args, **kwargs)
            
            # 2. Notify the Django Gateway
            try:
                # 'web' is the internal Docker name for the Django container
                requests.post(
                    "http://web:8000/api/solve/", 
                    json={
                        "lab_name": lab_name,
                        "user_id": session.get('gateway_user_id', 1) 
                    },
                    timeout=2
                )
            except Exception as e:
                print(f"Sync failed: {e}")
                
            return response
        return decorated_function
    return decorator