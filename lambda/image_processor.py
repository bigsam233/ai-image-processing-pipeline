import boto3

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
sns = boto3.client('sns')

TOPIC_ARN = 'YOUR_SNS_TOPIC_ARN'
OUTPUT_BUCKET = 'my-thumbnails-out'

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Validate file type
    if not key.lower().endswith(('.jpg', '.jpeg', '.png')):
        print("Unsupported file format")
        return "Skipped"

    print(f"Processing file: {key}")

    # Detect labels
    response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        MaxLabels=5
    )

    labels = [label['Name'] for label in response['Labels']]
    print(f"Detected labels: {labels}")

    # Copy file to output bucket
    copy_source = {'Bucket': bucket, 'Key': key}
    s3.copy(copy_source, OUTPUT_BUCKET, 'processed-' + key)

    print("File copied successfully")

    # Send notification
    try:
        sns.publish(
            TopicArn=TOPIC_ARN,
            Message=f"Image '{key}' processed successfully.\nDetected: {', '.join(labels)}",
            Subject="Image Processing Successful"
        )
        print("SNS notification sent successfully")
    except Exception as e:
        print(f"SNS ERROR: {str(e)}")

    return "Job Done!"