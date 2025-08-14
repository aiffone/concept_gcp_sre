from google.cloud import monitoring_v3

PROJECT_ID = "concepts-459009"

def list_uptime_checks():
    client = monitoring_v3.UptimeCheckServiceClient()
    parent = f"projects/{PROJECT_ID}"
    configs = client.list_uptime_check_configs(request={"parent": parent})

    found = False
    for config in configs:
        found = True
        print(f"Name: {config.name}")
        print(f"Display Name: {config.display_name}")
        print(f"Monitored Resource: {config.monitored_resource}")
        print(f"HTTP Check: {config.http_check}")
        print("-" * 40)

    if not found:
        print("❌ No uptime checks found in this project.")

if __name__ == "__main__":
    list_uptime_checks()
