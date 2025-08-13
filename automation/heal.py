from google.cloud import monitoring_v3
from google.protobuf.duration_pb2 import Duration
from google.protobuf.timestamp_pb2 import Timestamp
import subprocess
import datetime

PROJECT_ID = "concepts-459009"
THRESHOLD = 1  # number of failed checks to trigger redeploy
IMAGE_URL = "gcr.io/project/new-image:latest"

def get_uptime_failures(config_name, minutes=5):
    """
    Query the number of uptime check failures for the last `minutes`.
    """
    client = monitoring_v3.MetricServiceClient()

    now = datetime.datetime.utcnow()
    start_time = now - datetime.timedelta(minutes=minutes)

    interval = monitoring_v3.TimeInterval(
        start_time=Timestamp(seconds=int(start_time.timestamp())),
        end_time=Timestamp(seconds=int(now.timestamp()))
    )

    results = client.list_time_series(
        request={
            "name": f"projects/{PROJECT_ID}",
            "filter": f'metric.type="monitoring.googleapis.com/uptime_check/check_passed" AND resource.label."uptime_check_id"="{config_name}"',
            "interval": interval,
            "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
        }
    )

    failures = 0
    for ts in results:
        # uptime_check returns 1 if passed, 0 if failed
        for point in ts.points:
            if point.value.bool_value == False:
                failures += 1

    return failures


def check_and_restart():
    client = monitoring_v3.UptimeCheckServiceClient()
    configs = list(client.list_uptime_check_configs(parent=f"projects/{PROJECT_ID}"))

    for config in configs:
        failures = get_uptime_failures(config.name, minutes=5)
        print(f"Uptime check '{config.display_name}' failures in last 5 minutes: {failures}")

        if failures >= THRESHOLD:
            print(f"Failures >= {THRESHOLD}, redeploying service...")
            subprocess.run(["python", "deploy_app.py", IMAGE_URL])


if __name__ == "__main__":
    check_and_restart()
