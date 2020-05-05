from io import StringIO
import pandas as pd
import boto3
from botocore.exceptions import ClientError

credentials = boto3.Session().get_credentials()

s3 = boto3.client('s3')

def readFileFromBucket(event):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    # need to get the file from S3
    response = s3.get_object(Bucket=bucket, Key=key)  
    item_file = response['Body'].read().decode('utf-8')
    return item_file    

def loadCSV(item_file, seperator=",", typeArray=None):
    csv_read = pd.read_csv(StringIO(item_file), sep=seperator, dtype=typeArray, index_col=False)
    return csv_read

def saveFileToBucket(bucket, filename, csv_dict):
    csv_buffer = StringIO()    
    csv_dict.to_csv(csv_buffer, sep="|", index=False)

    try:
        write_response = s3.put_object(Bucket=bucket, Key= filename, Body=csv_buffer.getvalue())
        return "success"
    except ClientError as err:
        error_message = "Operation complete - output write failed"
        if err.response['Error']['Code']:
            error_message += err.response['Error']['Code']
        return error_message 

def readFileFromLocal(pathToFile):
    file = open(pathToFile, "r")
    return file.read()

def saveFileLocal(pandasDataFrame, output_dir):
    pandasDataFrame.to_csv(output_dir, index=False)   
    return "success"