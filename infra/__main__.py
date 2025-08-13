import pulumi
import pulumi_gcp as gcp

# --------------------
# Minimal VPC Network
# --------------------
network = gcp.compute.Network(
    "vpc-network",
    auto_create_subnetworks=False,
    description="Minimal VPC network for Cloud Run",
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
gcp.cloudrun.IamMember(
    "public-access",
    service=cloud_run_service.name,
    location=cloud_run_service.location,
    role="roles/run.invoker",
    member="allUsers",
)

# --------------------
# Outputs
# --------------------
pulumi.export("bucket_url", bucket.url)
pulumi.export("cloud_run_url", cloud_run_service.statuses[0].url)
