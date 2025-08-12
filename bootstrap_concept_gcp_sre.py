import os
from pathlib import Path

# Base project path
BASE = Path("concept_gcp_sre")

# Folder structure
folders = [
    BASE / "infra",
    BASE / "automation",
    BASE / ".github" / "workflows"
]

# File templates
files = {
    BASE / "infra" / "__main__.py": """import pulumi
import pulumi_gcp as gcp

# Placeholder Pulumi IaC code
pulumi.export("message", pulumi.Output.secret("Hello from GCP SRE Demo"))
""",

    BASE / "infra" / "requirements.txt": """pulumi
pulumi_gcp
""",

    BASE / "infra" / "Pulumi.yaml": """name: concept-gcp-sre
runtime:
  name: python
  options:
    virtualenv: venv
description: GCP SRE demo with Pulumi & Python automation
""",

    BASE / "automation" / "deploy_app.py": """# Deploy/update Cloud Run service
print("Deploy/update Cloud Run service script placeholder")
""",

    BASE / "automation" / "monitoring.py": """# Create uptime checks, alerts, custom metrics
print("Monitoring automation script placeholder")
""",

    BASE / "automation" / "heal.py": """# Detect failure & restart service
print("Self-healing script placeholder")
""",

    BASE / "automation" / "slo_report.py": """# Query metrics & calculate SLO/error budget
print("SLO report script placeholder")
""",

    BASE / "automation" / "requirements.txt": """google-cloud-run
google-cloud-monitoring
slack_sdk
""",

    BASE / "README.md": """# Concept GCP SRE

This project demonstrates SRE/DevOps practices with Pulumi, Python automation, and GCP services.
""",

    BASE / ".github" / "workflows" / "ci-cd.yml": """name: CI/CD

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Pulumi
        uses: pulumi/actions@v4

      - name: Install Infra Dependencies
        run: |
          cd infra
          pip install -r requirements.txt

      - name: Deploy with Pulumi
        run: |
          cd infra
          pulumi stack init dev || true
          pulumi up --yes
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
          GOOGLE_CLOUD_PROJECT: ${{ secrets.GCP_PROJECT }}
          GOOGLE_CREDENTIALS: ${{ secrets.GCP_CREDENTIALS }}
"""
}

def main():
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)
        print(f"Created folder: {folder}")

    for path, content in files.items():
        path.write_text(content)
        print(f"Created file: {path}")

    print("\n✅ Project skeleton created at:", BASE.resolve())

if __name__ == "__main__":
    main()
