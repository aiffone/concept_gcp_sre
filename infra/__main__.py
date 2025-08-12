import pulumi
import pulumi_gcp as gcp

import base64

with open("openapi.yaml", "rb") as f:
    openapi_b64 = base64.b64encode(f.read())

# 1. Create VPC
network = gcp.compute.Network(
    "private-vpc",
    auto_create_subnetworks=False
)

# 2. Create private subnet with Private Google Access enabled
subnet = gcp.compute.Subnetwork(
    "private-subnet",
    ip_cidr_range="10.10.0.0/24",
    network=network.id,
    region="us-central1",
    private_ip_google_access=True
)

# 3. GCS bucket
bucket = gcp.storage.Bucket(
    "concept-gcp-sre-bucket",
    location="US",
    uniform_bucket_level_access=True
)

# 4. Cloud Run service
service = gcp.cloudrun.Service(
    "concept-gcp-sre-service",
    location="us-central1",
    template=gcp.cloudrun.ServiceTemplateArgs(
        spec=gcp.cloudrun.ServiceTemplateSpecArgs(
            containers=[
                gcp.cloudrun.ServiceTemplateSpecContainerArgs(
                    image="us-docker.pkg.dev/cloudrun/container/hello"
                )
            ]
        )
    )
)

# 5. API Gateway
api = gcp.apigateway.Api(
    "concept-gcp-sre-api",
    api_id="concept-gcp-sre-api"
)

api_config = gcp.apigateway.ApiConfig(
    "concept-gcp-sre-api-config",
    api=api.name,
    openapi_documents=[{
        "document": {
            "path": "openapi.yaml"        }
    }],
    project=pulumi.Config("gcp").require("project")
)

gateway = gcp.apigateway.Gateway(
    "concept-gcp-sre-gateway",
    api=api.name,
    api_config=api_config.id,
    location="us-central1"
)

pulumi.export("bucket_name", bucket.url)
pulumi.export("cloud_run_url", service.statuses[0].url)
pulumi.export("api_gateway_url", gateway.default_hostname)
