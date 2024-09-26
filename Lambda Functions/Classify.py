import json
import base64
import boto3

runtime_client = boto3.client('sagemaker-runtime')                   

ENDPOINT = "image-classification-2024-09-25-12-06-15-944"


def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['image_data'])    

    # Response after invoking a deployed endpoint via SageMaker Runtime 
    response = runtime_client.invoke_endpoint(
                                        EndpointName=ENDPOINT,
                                        Body=image,
                                        ContentType='image/png'
                                    )
                                    
    
    # Make a prediction: Unpack reponse
    inferences = json.loads(response['Body'].read().decode('utf-8'))
  
    # Creating a structured response
    result = {
        "statusCode": 200,
        "body": {
            "image_data": event['image_data'], 
            "s3_bucket": event['s3_bucket'], 
            "s3_key": event['s3_key'], 
            "inferences": inferences  # List of predictions
        }
    }
    
    return result