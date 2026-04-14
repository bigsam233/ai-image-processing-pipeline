# Serverless Image Processing Pipeline (AWS + AI)

# 📌 Overview

This project implements a **fully serverless, event-driven image processing pipeline** on AWS.

When an image is uploaded to Amazon S3, the system automatically:
- Triggers a Lambda function
- Analyzes the image using AI (Amazon Rekognition)
- Stores the processed output
- Sends a notification email with detected labels

This project demonstrates **real-world cloud engineering practices**, including automation, service integration, and debugging in distributed systems.

---

## 🧠 What This Project Demonstrates

- Event-driven architecture using S3 triggers  
- Serverless compute with AWS Lambda  
- AI integration using Amazon Rekognition  
- Secure service interaction via IAM roles  
- Real-time notifications with SNS  
- Debugging using CloudWatch logs  

---

# 🏗️ Architecture

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

# ⚙️ Step-by-Step Implementation

### 🔹 Step 1: Create S3 Buckets

Create two buckets:

- `my-raw-images-in` → Input bucket (trigger source)
- `my-thumbnails-out` → Output bucket (processed images)

**Important:**
- Bucket names must be globally unique
- Keep both buckets in the **same region**

**Why two buckets?**
Using one bucket would create an **infinite loop** (output triggers input again).

##### *Image uploaded to input bucket*
<img width="1362" height="661" alt="Image uploaded to input bucket" src="https://github.com/user-attachments/assets/c391ef4f-4959-4cb7-826d-5a76a880065d" />  

##### *Image uploaded to output bucket*
<img width="1362" height="661" alt="Image uploaded to output bucket" src="https://github.com/user-attachments/assets/746b7c43-b88b-4320-978c-13533506c7fe" />

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

##### *IAM Role for Lambda*
<img width="1652" height="939" alt="IAM Role for Lambda" src="https://github.com/user-attachments/assets/fb408c39-91d6-4741-9f86-05391d162369" />

---

### 🔹 Step 3: Create Lambda Function

1. Go to Lambda → Create Function
2. Runtime: **Python 3.x**
3. Attach the IAM role created above

##### *Creating Lambda Function*
<img width="1652" height="998" alt="Creating Lambda Function" src="https://github.com/user-attachments/assets/1a982c82-6d28-4606-b79f-0cad96fe561d" />

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
##### *Code for Lambda function*
<img width="1652" height="998" alt="code for Lambda function" src="https://github.com/user-attachments/assets/381250d5-8716-4aba-8139-ec10d9ea05f9" />


### 🔹 Step 5: Configure S3 Trigger

1. Open my-raw-images-in
2. Go to Properties → Event Notifications
3. Create event:  
	•	Event type: All object create events
	•	Destination: Lambda function  

##### *Configuring s3 event notification*
<img width="1652" height="908" alt="Configuring s3 event notification" src="https://github.com/user-attachments/assets/9b35be52-f615-4b5d-aba7-ee5fdd56895d" />


--- 

### 🔹 Step 6: Create SNS Topic

1. Go to SNS → Create Topic
2. Select Standard
3. Name: ImageSuccess

##### *SNS topic created*
<img width="1362" height="661" alt="SNS topic created" src="https://github.com/user-attachments/assets/e973bbf0-9b7c-4432-b2cd-1f83789c11d2" />


---

### 🔹 Step 7: Create Subscription

1. Add subscription:
	•	Protocol: Email
	•	Endpoint: Your email
2. Confirm subscription via email

##### *Creating SNS Subscription*
<img width="1652" height="998" alt="Creating SNS Subscription" src="https://github.com/user-attachments/assets/338113d2-843a-4881-8474-7a8bbb4116a9" />


---

### 🔹 Step 8: Connect SNS to Lambda

- Copy the SNS Topic ARN  
- Replace it in your Lambda code:

```python
TOPIC_ARN = "your-actual-arn"
```

---

### 🔹 Step 9: Test the Pipeline

1. Upload image to the input bucket  
2. Verify: 
	•	Lambda runs (CloudWatch logs)
	•	Image appears in output bucket  
    •	Email notification is received

##### *Image uploaded to input bucket*
<img width="1362" height="661" alt="Image uploaded to input bucket" src="https://github.com/user-attachments/assets/29b985a0-a976-4cdc-a9ae-556ae2449017" />

##### *Image uploaded to output bucket*
<img width="1362" height="661" alt="Image uploaded to output bucket" src="https://github.com/user-attachments/assets/e8703afe-c9af-44f9-8f25-ff8154abbe4b" />

---

# ✅ Working Application
##### *AI description of image*
<img width="1284" height="967" alt="AI description of image" src="https://github.com/user-attachments/assets/4f12b8c4-b7a1-4e6b-9784-e950e70a6b3c" />


# ⚠️ Challenges & Solutions
❌ **nvalidImageFormatException**  
**Issue:** Rekognition rejected uploaded files (WEBP) 
**Solution:** Restricted uploads to .jpg, .png


❌ **SNS Notifications Not Sending**  
**Issue:** No email received due to missing IAM permission (sns:Publish)  
**Solution:** Attached the AmazonSNSFullAccess policy to the Lambda role  


## 📬 Contact  
If you’re a recruiter or hiring manager looking for a Cloud/DevOps Engineer, feel free to connect via email at samuel.tfio@gmail.com

## 🔗 Links

[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/samuel-tettey-fio/)


## Authors

- [@bigsam233](https://www.github.com/bigsam233)




