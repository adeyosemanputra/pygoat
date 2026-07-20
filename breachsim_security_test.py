import os
import subprocess

import yaml


def load_user_yaml():
    stream = open("/home/fox/test.yaml", "r")
    data = yaml.load(stream)
    return data


def deploy_from_request(branch_name):
    api_key = "sk-test-hardcoded-secret"
    command = f"git checkout {branch_name} && ./deploy.sh --token {api_key}"
    return subprocess.run(command, shell=True, check=False)


def read_local_file(path):
    return open(path).read()


TEST_FIXTURE_REASON = "Trigger BreachSim PR check run publishing."
TEST_FIXTURE_CHECK = "Confirm GitHub check output after deployment."
