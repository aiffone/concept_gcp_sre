import copy
import yaml
import pulumi
import pulumi_gcp as gcp

# --- Config ---
cfg = pulumi.Config("gcp")
project = cfg.require("project")
region = cfg.get("region") or "us-central1"

# --- VPC (custom subnets recommended in real setups) ---
network = gcp.compute.Network(
    "vpc-network",
    auto_create_subnetworks=False,
    description="Minimal VPC network for API Gateway and Cloud Run",
)

# --- Storage bucket for OpenAPI (and general app artifacts) ---
bucket = gcp.storage.Bucket(
    "openapi-bucket",
    location="US",
    force_destroy=True,
    uniform_bucket_level_access=True,
    public_access_prevention="enforced",
)

# --- Cloud Run service (public 'hello' image) ---
cloud_run_service = gcp.cloudrun.Service(
    "hello-world-service",
    location=region,
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

# Allow public invoke on the Cloud Run service
gcp.cloudrun.IamMember(
    "public-access",
    service=cloud_run_service.name,
    location=cloud_run_service.location,
    role="roles/run.invoker",
    member="allUsers",
)

# --- Prepare OpenAPI: read local file & inject Cloud Run URL into servers[] ---
with open("openapi.yaml", "r") as f:
    base_spec = yaml.safe_load(f)

def synthesize_openapi(run_url: str) -> str:
    spec = copy.deepcopy(base_spec) if base_spec else {}
    # Ensure 'servers' points at the Cloud Run URL
    spec["servers"] = [{"url": run_url}]
    return yaml.safe_dump(spec, sort_keys=False)

openapi_content = cloud_run_service.statuses[0].url.apply(synthesize_openapi)

# Upload the generated OpenAPI to GCS as a single object
openapi_asset = openapi_content.apply(lambda s: pulumi.asset.StringAsset(s))
openapi_object = gcp.storage.BucketObject(
    "openapi-spec",
    bucket=bucket.name,
    content_type="application/yaml",
    source=openapi_asset,  # Output[StringAsset] is fine
)

# --- API Gateway ---
api = gcp.apigateway.Api(
    "api-gateway-api",
    api_id="hello-api",
    display_name="Hello API",
    project=project,
)

api_config = gcp.apigateway.ApiConfig(
    "concept-gcp-sre-api-config",
    api=api.name,
    # Point to the GCS object we just uploaded
    openapi_documents=[{
        "document": {
            "path": pulumi.Output.concat("gs://", bucket.name, "/", openapi_object.name)
        }
    }],
    project=project,
)

gateway = gcp.apigateway.Gateway(
    "api-gateway-gateway",
    api_config=api_config.id,
    gateway_id="hello-gateway",
    display_name="Hello Gateway",
    region=region,
    project=project,
)

# --- Outputs ---
pulumi.export("project", project)
pulumi.export("region", region)
pulumi.export("cloud_run_url", cloud_run_service.statuses[0].url)
pulumi.export("api_gateway_hostname", gateway.default_hostname)
pulumi.export("openapi_gcs_uri", pulumi.Output.concat("gs://", bucket.name, "/", openapi_object.name))
