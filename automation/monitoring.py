from google.cloud import monitoring_v3
from google.api_core.exceptions import GoogleAPICallError, PermissionDenied

PROJECT_ID = "concepts-459009"

def create_uptime_check():
    client = monitoring_v3.UptimeCheckServiceClient()
    parent = f"projects/{PROJECT_ID}"

    config = monitoring_v3.UptimeCheckConfig(
        display_name="API Uptime Check",
        monitored_resource={
            "type": "uptime_url",
            "labels": {
                "host": "jkaconsulting.co.uk"  # No "https://"
            }
        },
        http_check={
            "path": "/",
            "port": 443,
            "use_ssl": True
        },
        timeout={"seconds": 10},
        period={"seconds": 60}
    )

    try:
        response = client.create_uptime_check_config(
            request={
                "parent": parent,
                "uptime_check_config": config
            }
        )
        print("✅ Uptime check created successfully.")
        print(f"Name: {response.name}")
        print(f"Display Name: {response.display_name}")
        print(f"Resource: {response.monitored_resource}")
        print(f"HTTP Check: {response.http_check}")
    except PermissionDenied as e:
        print("❌ Permission denied. Ensure your account or service account has Monitoring Admin role.")
        print(e)
    except GoogleAPICallError as e:
        print("❌ API call error:")
        print(e)
    except Exception as e:
        print("❌ Unexpected error:")
        print(e)

if __name__ == "__main__":
    create_uptime_check()
