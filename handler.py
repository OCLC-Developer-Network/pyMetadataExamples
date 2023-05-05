import yaml
import os
from src import handle_files, process_data, make_requests
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# load key/secret config info
# read a configuration file
with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)
     
# get a token
scope = ['WorldCatMetadataAPI']
oauth_session = make_requests.createOAuthSession(config, scope)

processConfig = config.update({"oauth-session": oauth_session})

def getCurrentOCLCNumbers(event, context):      
    item_file = handle_files.readFilesFromBucket(event)
    csv_read = handle_files.loadCSV(item_file)
    csv_read = process_data.retrieveCurrentOCLCNumbers(processConfig, csv_read)
    handle_files.saveFileToBucket(fileInfo['bucket'], fileInfo['key'] + "_updated", csv_read)               

def getMergedOCLCNumbers(event, context):
    item_file = handle_files.readFilesFromBucket(event)
    csv_read = handle_files.loadCSV(item_file)
    csv_read = process_data.retrieveMergedOCLCNumbers(processConfig, csv_read)
    handle_files.saveFileToBucket(fileInfo['bucket'], fileInfo['key'] + "_updated", csv_read)

def setHoldingsbyOCLCNumber(event, context):  
    item_file = handle_files.readFilesFromBucket(event)
    csv_read = handle_files.loadCSV(item_file)
    csv_read = process_data.setHoldingsbyOCLCNumber(processConfig, csv_read)
    handle_files.saveFileToBucket(fileInfo['bucket'], fileInfo['key'] + "_updated", csv_read)   
         
    return saveFile(bucket, key + "_updated", csv_read) 

def deleteHoldingsbyOCLCNumber(event, context):  
    item_file = handle_files.readFilesFromBucket(event)
    csv_read = handle_files.loadCSV(item_file)
    csv_read = process_data.deleteHoldingsbyOCLCNumber(processConfig, csv_read)
    handle_files.saveFileToBucket(fileInfo['bucket'], fileInfo['key'] + "_updated", csv_read)   
         
    return saveFile(bucket, key + "_updated", csv_read) 

def addLBDs(event, context):  
    item_file = handle_files.readFilesFromBucket(event)
    csv_read = handle_files.loadCSV(item_file)
    csv_read = process_data.addLBDs(processConfig, csv_read)
    handle_files.saveFileToBucket(fileInfo['bucket'], fileInfo['key'] + "_updated", csv_read)   
         
    return saveFile(bucket, key + "_updated", csv_read) 
  