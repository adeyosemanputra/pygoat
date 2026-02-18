#!/usr/bin/env python3
import json
import re
import sys
import os

if os.path.basename(os.getcwd()) == 'scripts':
    os.chdir('..')

def load_labs():
    try:
        with open('challenge/labs/labs.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: challenge/labs/labs.json not found")
        sys.exit(1)

def generate_service_block(service_name, data):
    profile = data['profile']
    build_ctx = data['build_context']
    
    block = f"  {service_name}:\n"
    block += f"    build:\n"
    block += f"      context: {build_ctx}\n"
    block += f"    container_name: {service_name}\n"
    
    # optional fields (any future extra docker-compose fields)
    
    if 'command' in data:
        block += f"    command: {data['command']}\n"
    
    if 'environment' in data:
        block += f"    environment:\n"
        for key, val in data['environment'].items():
            block += f"      {key}: {val}\n"
    
    if 'volumes' in data:
        block += f"    volumes:\n"
        for vol in data['volumes']:
            block += f"      - {vol}\n"
    
    if 'depends_on' in data:
        block += f"    depends_on:\n"
        for dep in data['depends_on']:
            block += f"      - {dep}\n"
    
    # networks and profiles are standard for all labs
    block += f"    networks:\n"
    block += f"      - my_network\n"
    block += f"    profiles:\n"
    block += f"      - labs\n"
    block += f"      - {profile}\n"
    
    return block

def generate_docker_compose(labs):
    challenge_labs = {}
    dockerized_labs = {}
    
    for lab_id, data in labs.items():
        if 'challenge/labs/' in data.get('build_context', ''):
            challenge_labs[lab_id] = data
        else:
            dockerized_labs[lab_id] = data
    
    output = "services:\n"
    
    if challenge_labs:
        output += "  # Challenge Labs\n"
        for lab_id, data in challenge_labs.items():
            output += generate_service_block(data['service_name'], data)
            output += "\n"
    
    if dockerized_labs:
        output += "  # Dockerized Labs\n"
        for lab_id, data in dockerized_labs.items():
            output += generate_service_block(data['service_name'], data)
            output += "\n"
    
    output += "networks:\n"
    output += "  my_network:\n"
    output += "    external: true\n"
    output += "    name: pygoat_my_network\n"
    
    return output

def update_nginx_map(labs):
    with open('nginx/nginx.conf', 'r') as f:
        content = f.read()
    
    map_entries = []
    for lab_id, data in sorted(labs.items()):
        port = data['internal_port']
        map_entries.append(f"        {lab_id} {port};")
    
    map_block = "    map $lab $lab_port {\n"
    map_block += "        default 5000;\n"
    map_block += '\n'.join(map_entries)
    map_block += "\n    }"
    
    pattern = r'map \$lab \$lab_port \{[^}]+\}'
    new_content = re.sub(pattern, map_block, content, flags=re.DOTALL)
    
    with open('nginx/nginx.conf', 'w') as f:
        f.write(new_content)

def validate_labs(labs):
    required = ['name', 'profile', 'url', 'service_name', 'internal_port', 'build_context']
    missing = []
    
    for lab_id, data in labs.items():
        for field in required:
            if field not in data:
                missing.append(f"  {lab_id}: missing '{field}'")
    
    if missing:
        print("Error: Missing required fields:")
        for m in missing:
            print(m)
        sys.exit(1)

def main():
    print("Generating configs from labs.json...")
    
    labs = load_labs()
    print(f"Found {len(labs)} labs")
    
    validate_labs(labs)
    
    compose_content = generate_docker_compose(labs)
    with open('docker-compose.labs.yml', 'w') as f:
        f.write(compose_content)
    print("Updated docker-compose.labs.yml")
    
    update_nginx_map(labs)
    print("Updated nginx/nginx.conf")
    
    print("\nDone - please review the changes to docker-compose.labs.yml and nginx/nginx.conf")

if __name__ == '__main__':
    main()