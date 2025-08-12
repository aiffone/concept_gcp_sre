import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";
import * as fs from "fs";

// Minimal VPC Network (custom subnets recommended)
const network = new gcp.compute.Network("vpc-network", {
    autoCreateSubnetworks: false,
    description: "Minimal VPC network for API Gateway and Cloud Run",
});

// Minimal Storage Bucket
const bucket = new gcp.storage.Bucket("storage-bucket", {
    location: "US",
    forceDestroy: true,
    uniformBucketLevelAccess: true,
    publicAccessPrevention: "enforced",
});

// Basic Cloud Run Service (hello world)
const cloudRunService = new gcp.cloudrun.Service("hello-world-service", {
    location: "us-central1",
    template: {
        spec: {
            containers: [{
                image: "gcr.io/cloudrun/hello",
            }],
        },
    },
});

// Allow public access to Cloud Run
new gcp.cloudrun.IamMember("public-access", {
    service: cloudRunService.name,
    location: cloudRunService.location,
    role: "roles/run.invoker",
    member: "allUsers",
});

// API Gateway API
const api = new gcp.apigateway.Api("api-gateway-api", {
    apiId: "hello-api",
    displayName: "Hello API",
});

// API Gateway API Config with OpenAPI contents read inline
const apiConfig = new gcp.apigateway.ApiConfig("concept-gcp-sre-api-config", {
    api: api.name,
    openapiDocuments: [{
        document: {
            contents: fs.readFileSync("openapi.yaml", "utf8"),
        },
    }],
});

// API Gateway Gateway
const gateway = new gcp.apigateway.Gateway("api-gateway-gateway", {
    apiConfig: apiConfig.id,
    gatewayId: "hello-gateway",
    displayName: "Hello Gateway",
    region: "us-central1",
});

// Export URLs
export const bucketUrl = bucket.url;
export const cloudRunUrl = cloudRunService.statuses.apply(s => s[0]?.url);
export const apiGatewayUrl = gateway.defaultHostname;
