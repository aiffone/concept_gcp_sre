from google.cloud import monitoring_v3
import datetime

PROJECT_ID = "concepts-459009"

def generate_slo_report_from_uptime():
    client = monitoring_v3.MetricServiceClient()

    # Metric for uptime checks in Cloud Monitoring
    METRIC_TYPE = "monitoring.googleapis.com/uptime_check/check_passed"

    now = datetime.datetime.utcnow()
    interval = monitoring_v3.TimeInterval(
        end_time={"seconds": int(now.timestamp())},
        start_time={"seconds": int((now - datetime.timedelta(days=30)).timestamp())}
    )

    # Query uptime check pass/fail data
    results = client.list_time_series(
        request={
            "name": f"projects/{PROJECT_ID}",
            "filter": f'metric.type="{METRIC_TYPE}"',
            "interval": interval,
            "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL
        }
    )

    total_points = 0
    passed_points = 0

    for ts in results:
        for point in ts.points:
            value = point.value.bool_value  # True = passed, False = failed
            total_points += 1
            if value:
                passed_points += 1

    if total_points > 0:
        availability = (passed_points / total_points) * 100
        print(f"SLO Report: Availability {availability:.2f}% over last 30 days")
    else:
        print("No uptime check data available.")

if __name__ == "__main__":
    generate_slo_report_from_uptime()
