import pulumi
import pulumi_gcp as gcp
import yaml

# --------------------
# Minimal VPC Network
# --------------------
network = gcp.compute.Network(
    "vpc-network",
    auto_create_subnetworks=False,
    description="Minimal VPC network for API Gateway and Cloud Run",
)

# --------------------
# Storage bucket for app data
# --------------------
bucket = gcp.storage.Bucket(
    "storage-bucket",
    location="US",
    force_destroy=True,
    uniform_bucket_level_access=True,
    public_access_prevention="enforced",
)

# --------------------
# Cloud Run Service (hello world)
# --------------------
cloud_run_service = gcp.cloudrun.Service(
    "hello-world-service",
    location="us-central1",
    template=gcp.cloudrun.ServiceTemplateArgs(
        spec=gcp.cloudrun.ServiceTemplateSpecArgs(
            containers=[
                gcp.cloudrun.ServiceTemplateSpecContainerArgs(
                    image="gcr.io/cloudrun/hello"
                )
            ]
        )
    ),
)

# Allow public access
gcp.cloudrun.IamMember(
    "public-access",
    service=cloud_run_service.name,
    location=cloud_run_service.location,
    role="roles/run.invoker",
    member="allUsers",
)

# --------------------
# Generate updated OpenAPI spec locally
# --------------------
def write_openapi_with_url(url):
    with open("openapi.yaml", "r") as f:
        spec = yaml.safe_load(f)

    spec["servers"] = [{"url": url}]

    out_path = "openapi.generated.yaml"
    with open(out_path, "w") as f:
        yaml.safe_dump(spec, f)

    return out_path

openapi_file_path = cloud_run_service.statuses[0].url.apply(write_openapi_with_url)

# --------------------
# API Gateway
# --------------------
api = gcp.apigateway.Api(
    "api-gateway-api",
    api_id="hello-api",
    display_name="Hello API",
)

api_config = gcp.apigateway.ApiConfig(
    "concept-gcp-sre-api-config",
    api=api.name,
    openapi_documents=[{
        "document": {
            # Pass the local file path — not GCS
            "path": openapi_file_path
        }
    }],
)

gateway = gcp.apigateway.Gateway(
    "api-gateway-gateway",
    api_config=api_config.id,
    gateway_id="hello-gateway",
    display_name="Hello Gateway",
    region="us-central1",
)

# --------------------
# Outputs
# --------------------
pulumi.export("cloud_run_url", cloud_run_service.statuses[0].url)
pulumi.export("api_gateway_url", gateway.default_hostname)