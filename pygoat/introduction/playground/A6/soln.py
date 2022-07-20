import requests

def check_vuln(list_of_modules)->list:
    vulns = []
    for i in list_of_modules:
        k = i.split("==")
        url = f"https://pypi.org/pypi/{k[0]}/{k[1]}/json"
        response = requests.get(url)
        response.raise_for_status()
        info = response.json()
        existing_vuln = info['vulnerabilities']
        if len(existing_vuln) > 0:
            vulns.append(existing_vuln) 
    return vulns