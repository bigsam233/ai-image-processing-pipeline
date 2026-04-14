# Serverless Image Processing Pipeline (AWS + AI)

## 📌 Overview

This project implements a **serverless, event-driven image processing pipeline** on AWS.

When an image is uploaded to an S3 bucket, it automatically triggers a Lambda function that:
- Validates the file
- Uses Amazon Rekognition to detect labels (AI)
- Copies the processed image to an output bucket
- Sends a notification email via SNS with detected labels

This solution demonstrates **real-world cloud architecture principles**, including:
- Event-driven design
- Serverless computing
- AI service integration
- IAM-based security
- Observability with CloudWatch

---

## 🏗️ Architecture

<img width="1536" height="1024" alt=" architecture diagram" src="https://github.com/user-attachments/assets/331a767e-9139-4439-9507-2ca4954a8a1f" />


### 🔄 Request Flow

1. User uploads image to **S3 input bucket (`my-raw-images-in`)**
2. S3 triggers **AWS Lambda function**
3. Lambda:
   - Validates file type
   - Sends image to **Amazon Rekognition**
   - Extracts labels
4. Lambda copies image to **output bucket (`my-thumbnails-out`)**
5. Lambda publishes message to **SNS topic**
6. SNS sends email notification to subscriber

### 🧩 Key Components

| Component | Description |
|----------|------------|
| **Amazon S3 (Input Bucket)** | Stores raw uploaded images and triggers Lambda |
| **AWS Lambda** | Core processing engine (serverless compute) |
| **Amazon Rekognition** | AI service for image label detection |
| **Amazon S3 (Output Bucket)** | Stores processed images |
| **Amazon SNS** | Sends email notifications |
| **IAM Role** | Grants permissions to Lambda |
| **CloudWatch Logs** | Captures logs for debugging and monitoring |

---

## ⚙️ Step-by-Step Implementation

> ⚠️ This section reflects the **actual manual implementation via AWS Console** to build a foundational understanding.

---

### 🔹 Step 1: Create S3 Buckets

Create two buckets:

- `my-raw-images-in` → Input bucket (trigger source)
- `my-thumbnails-out` → Output bucket (processed images)

**Important:**
- Bucket names must be globally unique
- Keep both buckets in the **same region**

**Why two buckets?**
Using one bucket would create an **infinite loop** (output triggers input again).

---

### 🔹 Step 2: Create IAM Role for Lambda

1. Go to IAM → Roles → Create Role
2. Select **Lambda** as trusted entity
3. Attach the following policies:

- `AmazonS3FullAccess`
- `AmazonRekognitionFullAccess`
- `CloudWatchLogsFullAccess`
- `AmazonSNSFullAccess`

**Why this is critical:**
Without permissions:
- Lambda cannot read/write S3
- Cannot call Rekognition
- Cannot send SNS notifications

---

### 🔹 Step 3: Create Lambda Function

1. Go to Lambda → Create Function
2. Runtime: **Python 3.x**
3. Attach the IAM role created above

---

### 🔹 Step 4: Add Lambda Code

```python
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

    # Copy to output bucket
    copy_source = {'Bucket': bucket, 'Key': key}
    s3.copy(copy_source, OUTPUT_BUCKET, 'processed-' + key)

    # Send notification
    sns.publish(
        TopicArn=TOPIC_ARN,
        Message=f"Image '{key}' processed successfully.\nDetected: {', '.join(labels)}",
        Subject="Image Processing Successful"
    )

    return "Job Done!"
```
### 🔹 Step 5: Configure S3 Trigger

1. Open my-raw-images-in
2. Go to Properties → Event Notifications
3. Create event:  
	•	Event type: All object create events
	•	Destination: Lambda function  

--- 

### 🔹 Step 6: Create SNS Topic

1. Go to SNS → Create Topic
2. Select Standard
3. Name: ImageSuccess

---

### 🔹 Step 7: Create Subscription

1. Add subscription:
	•	Protocol: Email
	•	Endpoint: Your email
2. Confirm subscription via email

---

### 🔹 Step 8: Connect SNS to Lambda
	•	Copy SNS Topic ARN
	•	Replace in Lambda:
```
TOPIC_ARN = 'your-actual-arn'
```  

---

### 🔹 Step 9: Test the Pipeline

1. Upload image to the input bucket
2. Verify: 
	•	Lambda runs (CloudWatch logs)
	•	Image appears in output bucket  
   •	Email notification is received


---





