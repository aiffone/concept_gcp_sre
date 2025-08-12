from google.cloud import run_v2
import sys

PROJECT_ID = "concepts-459009"
LOCATION = "us-central1"
SERVICE_NAME = "concept-gcp-sre-service"

def deploy_new_image(image_url):
    client = run_v2.ServicesClient()
    service_path = client.service_path(PROJECT_ID, LOCATION, SERVICE_NAME)
    
    service = client.get_service(name=service_path)
    service.template.containers[0].image = image_url
    operation = client.update_service(service=service)
    print("Deploying new image...")
    operation.result()
    print("Deployment completed.")

if __name__ == "__main__":
    image = sys.argv[1]
    deploy_new_image(image)
