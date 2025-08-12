from google.cloud import monitoring_v3
import datetime

PROJECT_ID = "your-gcp-project"
METRIC_TYPE = "custom.googleapis.com/availability"

def generate_slo_report():
    client = monitoring_v3.MetricServiceClient()
    now = datetime.datetime.utcnow()
    interval = monitoring_v3.TimeInterval(
        end_time={"seconds": int(now.timestamp())},
        start_time={"seconds": int((now - datetime.timedelta(days=30)).timestamp())}
    )
    results = client.list_time_series(
        request={
            "name": f"projects/{PROJECT_ID}",
            "filter": f'metric.type="{METRIC_TYPE}"',
            "interval": interval,
            "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL
        }
    )
    values = [point.value.double_value for ts in results for point in ts.points]
    if values:
        avg = sum(values) / len(values)
        print(f"SLO Report: Availability {avg:.2f}% over last 30 days")
    else:
        print("No data for SLO report.")

generate_slo_report()
