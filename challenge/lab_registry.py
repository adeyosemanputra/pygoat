"""
Lab Registry - Central configuration for all dockerized labs
Loads from labs.json (single source of truth)
"""

import json
import os

LABS_JSON_PATH = os.path.join(os.path.dirname(__file__), 'labs', 'labs.json')

def _load_labs_json():
    """Load labs configuration from JSON file"""
    try:
        with open(LABS_JSON_PATH, 'r') as f:
            data = json.load(f)
            
            registry = {}
            for lab_key, lab_data in data.items():
                normalized_key = lab_key.replace('-', '_')
                
                registry[normalized_key] = {
                    "service_name": lab_data.get("service_name", f"{lab_key}-lab"),
                    "internal_port": lab_data.get("internal_port", 5000),
                    "path_prefix": lab_data.get("url", f"/labs/{lab_key}").rstrip('/'),
                    "container_name": lab_data.get("service_name", f"{lab_key}-lab"),
                    "name": lab_data.get("name", ""),
                    "profile": lab_data.get("profile", lab_key),
                    "url": lab_data.get("url", f"/labs/{lab_key}/")
                }
            
            return registry
    except FileNotFoundError:
        print(f"ERROR: labs.json not found at {LABS_JSON_PATH}")
        return {}
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in labs.json: {e}")
        return {}


LAB_REGISTRY = _load_labs_json()


def get_lab_url(lab_name):
    """Get the public URL path for a lab"""
    lab = LAB_REGISTRY.get(lab_name)
    if lab:
        return lab['path_prefix']
    return None


def get_lab_internal_url(lab_name):
    """Get the internal Docker network URL for a lab"""
    lab = LAB_REGISTRY.get(lab_name)
    if lab:
        return f"http://{lab['service_name']}:{lab['internal_port']}"
    return None


def list_all_labs():
    """Return list of all available labs"""
    return list(LAB_REGISTRY.keys())


def get_lab_service_name(lab_name):
    """Get Docker service name for a lab"""
    lab = LAB_REGISTRY.get(lab_name)
    if lab:
        return lab.get('service_name')
    return None


def get_lab_internal_port(lab_name):
    """Get internal port for a lab"""
    lab = LAB_REGISTRY.get(lab_name)
    if lab:
        return lab.get('internal_port', 5000)
    return 5000