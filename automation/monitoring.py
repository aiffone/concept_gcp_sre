from google.cloud import monitoring_v3

PROJECT_ID = "concepts-459009"

def create_uptime_check():
    client = monitoring_v3.UptimeCheckServiceClient()
    config = monitoring_v3.UptimeCheckConfig(
        display_name="API Uptime Check",
        monitored_resource={"type": "uptime_url", "labels": {"host": "https://jkaconsulting.co.uk/"}},
        http_check={"path": "/", "port": 443, "use_ssl": True},
        timeout={"seconds": 10},
        period={"seconds": 60}
    )
    client.create_uptime_check_config(
        parent=f"projects/{PROJECT_ID}",
        uptime_check_config=config
    )
    print("Uptime check created.")

def push_custom_metric():
    metric_client = monitoring_v3.MetricServiceClient()
    series = monitoring_v3.TimeSeries()
    series.metric.type = "custom.googleapis.com/availability"
    series.resource.type = "global"
    point = monitoring_v3.Point()
    point.value.double_value = 99.9
    point.interval.end_time.GetCurrentTime()
    series.points.append(point)
    metric_client.create_time_series(name=f"projects/{PROJECT_ID}", time_series=[series])
    print("Custom metric pushed.")

create_uptime_check()
push_custom_metric()
