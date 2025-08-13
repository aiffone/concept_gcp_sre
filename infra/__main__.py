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

# Allow public access to Cloud Run
cloud_run_iam = gcp.cloudrun.IamMember(
    "public-access",
    service=cloud_run_service.name,
    location=cloud_run_service.location,
    role="roles/run.invoker",
    member="allUsers",
)

# --------------------
# Bucket for OpenAPI spec
# --------------------
spec_bucket = gcp.storage.Bucket(
    "openapi-spec-bucket",
    location="US",
    uniform_bucket_level_access=True,
    force_destroy=True,
)

# --------------------
# Generate OpenAPI spec dynamically
# --------------------
def generate_openapi_spec(url):
    with open("openapi.yaml", "r") as f:
        spec = yaml.safe_load(f)

    # Update the 'servers' section with the Cloud Run URL
    spec["servers"] = [{"url": url}]

    temp_path = "openapi.generated.yaml"
    with open(temp_path, "w") as f:
        yaml.safe_dump(spec, f)

    return temp_path

# Create an Output that writes the updated spec
openapi_file = cloud_run_service.statuses[0].url.apply(generate_openapi_spec)

# Upload updated OpenAPI spec to GCS
spec_object = gcp.storage.BucketObject(
    "openapi-spec-object",
    bucket=spec_bucket.name,
    source=openapi_file.apply(lambda path: pulumi.FileAsset(path)),
)

# --------------------
# API Gateway API
# --------------------
api = gcp.apigateway.Api(
    "api-gateway-api",
    api_id="hello-api",
    display_name="Hello API",
)

# --------------------
# API Gateway API Config with GCS path to spec
# --------------------
api_config = gcp.apigateway.ApiConfig(
    "concept-gcp-sre-api-config",
    api=api.name,
    openapi_documents=[{
        "document": {
            "path": pulumi.Output.concat(
                "gs://", spec_bucket.name, "/", spec_object.name
            )
        }
    }],
)

# --------------------
# API Gateway Gateway
# --------------------
gateway = gcp.apigateway.Gateway(
    "api-gateway-gateway",
    api_config=api_config.id,
    gateway_id="hello-gateway",
    display_name="Hello Gateway",
    region="us-central1",
)

# --------------------
# Export URLs
# --------------------
pulumi.export("bucket_url", bucket.url)
pulumi.export("cloud_run_url", cloud_run_service.statuses[0].url)
pulumi.export("api_gateway_url", gateway.default_hostname)
pulumi.export("openapi_spec_gcs_uri", pulumi.Output.concat(
    "gs://", spec_bucket.name, "/", spec_object.name
))
