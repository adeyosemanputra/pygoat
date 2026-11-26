import os

# Injected at runtime from the Kubernetes Secret "aws-credentials",
# stored encrypted in secrets/aws-credentials.enc.yaml (SOPS + age).
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")