import pulumi
import pulumi_gcp as gcp
import os

# Read OpenAPI spec from local file
with open("openapi.yaml", "r") as f:
    openapi_spec = f.read()

# Minimal VPC Network (custom subnets recommended)
network = gcp.compute.Network("vpc-network",
    auto_create_subnetworks=False,
    description="Minimal VPC network for API Gateway and Cloud Run"
)

# Minimal Storage Bucket
bucket = gcp.storage.Bucket("storage-bucket",
    location="US",
    force_destroy=True,
    uniform_bucket_level_access=True,
    public_access_prevention="enforced"
)

# Basic Cloud Run Service (hello world)
cloud_run_service = gcp.cloudrun.Service("hello-world-service",
    location="us-central1",
    template=gcp.cloudrun.ServiceTemplateArgs(
        spec=gcp.cloudrun.ServiceTemplateSpecArgs(
            containers=[
                gcp.cloudrun.ServiceTemplateSpecContainerArgs(
                    image="gcr.io/cloudrun/hello"
                )
            ]
        )
    )
)

# Allow public access to Cloud Run
cloud_run_iam = gcp.cloudrun.IamMember("public-access",
    service=cloud_run_service.name,
    location=cloud_run_service.location,
    role="roles/run.invoker",
    member="allUsers"
)

# API Gateway API
api = gcp.apigateway.Api("api-gateway-api",
    api_id="hello-api",
    display_name="Hello API"
)

# API Gateway API Config with OpenAPI contents read inline
api_config = gcp.apigateway.ApiConfig("concept-gcp-sre-api-config",
    api=api.name,
    openapi_documents=[{
        "document": {
            "contents": openapi_spec,
        }
    }]
)

# API Gateway Gateway
gateway = gcp.apigateway.Gateway("api-gateway-gateway",
    api_config=api_config.id,
    gateway_id="hello-gateway",
    display_name="Hello Gateway",
    region="us-central1"
)

# Export URLs
pulumi.export("bucket_url", bucket.url)
pulumi.export("cloud_run_url", cloud_run_service.statuses[0].url)
pulumi.export("api_gateway_url", gateway.default_hostname)
