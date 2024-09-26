"Lambda function 1: Serialize Image Data"
import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    key = event['s3_key']
    bucket = event['s3_bucket']

    # Download the data from s3 to /tmp/image.png
    s3.download_file(bucket, key, "/tmp/image.png")

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }




"Lambda function 2: C;assify Image"
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




"Lambda function 3: Filter Inference"
import json

THRESHOLD = .70

def lambda_handler(event, context):

    # Grab the inferences from the event
    inferences = event["inferences"]

    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = any(prob > THRESHOLD for prob in inferences)

    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise ValueError("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }