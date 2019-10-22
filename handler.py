import yaml
import json
import pandas as pd  
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
import requests
import pymarc
from pymarc import Record, Field
import os
from io import StringIO
import time
from xml.etree import ElementTree
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# load key/secret config info
# read a configuration file
with open("config.yml", 'r') as stream:
    config = yaml.load(stream)
    
serviceURL = config.get('metadata_service_url')  
institution_symbol = config.get('institution_symbol')  
# get a token
scope = ['WorldCatMetadataAPI']
auth = HTTPBasicAuth(config.get('key'), config.get('secret'))
client = BackendApplicationClient(client_id=config.get('key'), scope=scope)
oauth_session = OAuth2Session(client=client)

try:
    token = oauth_session.fetch_token(token_url=config.get('token_url'), auth=auth)
except BaseException as err:
    print(err)
    
def getCurrentOCLCNum(oclcnumber):
    try:
        r = oauth_session.get(serviceURL + "/bib/checkcontrolnumbers?oclcNumbers=" + oclcnumber, headers={"Accept":"application/json"})
        r.raise_for_status
        try:
            result = r.json()
            new_oclc_number = results['entry'][0]['currentOclcNumber']
            status = "success"
        except json.decoder.JSONDecodeError:
            new_oclc_number = ""
            status = "failed"
    except requests.exceptions.HTTPError as err:
        new_oclc_number = ""
        status = "failed"
    return pd.Series([oclc_number, new_oclc_number, status])

def setHolding(oclcnumber):
    try:
        r = oauth_session.post(serviceURL + "/ih/data?oclcNumber=" + oclcnumber, headers={"Accept":"application/json"})
        r.raise_for_status
        try:
            result = r.json()
            status = "success"
        except json.decoder.JSONDecodeError:
            status = "failed"
    except requests.exceptions.HTTPError as err:
        status = "failed"
    return pd.Series([oclc_number, status])

def deleteHolding(oclcnumber):
    try:
        r = oauth_session.delete(serviceURL + "/ih/data?oclcNumber=" + oclcnumber, headers={"Accept":"application/json"})
        r.raise_for_status
        try:
            result = r.json()
            status = "success"
        except json.decoder.JSONDecodeError:
            status = "failed"
    except requests.exceptions.HTTPError as err:
        status = "failed"
    return pd.Series([oclc_number, status])

def addLBD(oclcnumber, note):
    #create the LBD
    record = Record(leader='00000n   a2200000   4500')
    record.add_field(Field(tag='004', data=oclcnumber))
    record.add_field(
        Field(
            indicators = [' ', ' '],
            tag = '500',
            subfields = [
                'a', note
            ]),
        Field(
            indicators = [' ', ' '],
            tag = '935',
            subfields = [
                'a', str(time.time())
            ]),
        Field(
            indicators = [' ', ' '],
            tag = '940',
            subfields = [
                'a', institution_symbol
            ])
        )
    input = pymarc.record_to_xml(record).decode("utf-8")
    
    try:
        r = oauth_session.post(serviceURL + "/lbd/data", data=input, headers={"Accept":'application/atom+xml;content="application/vnd.oclc.marc21+xml"', "Content-Type": "application/vnd.oclc.marc21+xml"})
        r.raise_for_status
        try:
            result = ElementTree.fromstring(r.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom', 'wc': 'http://worldcat.org/rb'}
            marcNode = result.findall('atom:content/wc:response', ns)[0].getchildren()[0]
            marcData = StringIO(ElementTree.tostring(marcNode, encoding='unicode', method='xml'))
            # need to get this XML section out as a string and into a file like object
            marcRecords = pymarc.parse_xml_to_array(marcData)
            # pull out the LBD accession number
            accessionNumber = marcRecords[0]['001'].value()
            status = "success"
        except json.decoder.JSONDecodeError:
            accessionNumber = ""
            status = "failed"
    except requests.exceptions.HTTPError as err:
        status = "failed"
    return pd.Series([oclc_number, accessionNumber, status])  
    
def getCurrentOCLCNumbers(event, context):  
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    # need to get the file from S3
    response = s3.get_object(Bucket=bucket, Key=key)  
    item_file = response['Body'].read().decode('utf-8')
    csv_read = pd.read_csv(item_file, sep="|", dtype={'Item_Call_Number': 'object'}, index_col=False)
    csv_read[['oclcnumber', 'status']] = csv_read.apply (lambda row: getCurrentOCLCNum(row['oclcNumber']), axis=1)    
     
    #create a new CSV file
    #remove unnecessary fields    
    csv_read.to_csv(path_or_buf='results.txt', sep="|", index=False)
    
    return "success"

def setHoldingsbyOCLCNumber(event, context):  
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    # need to get the file from S3
    response = s3.get_object(Bucket=bucket, Key=key)  
    item_file = response['Body'].read().decode('utf-8')
    csv_read = pd.read_csv(item_file, sep="|", dtype={'Item_Call_Number': 'object'}, index_col=False)
    csv_read[['oclcnumber', 'status']] = csv_read.apply (lambda row: setHolding(row['oclcNumber']), axis=1)    
     
    #create a new CSV file
    #remove unnecessary fields    
    csv_read.to_csv(path_or_buf='results.txt', sep="|", index=False)
    
    return "success"

def deleteHoldingsbyOCLCNumber(event, context):  
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    # need to get the file from S3
    response = s3.get_object(Bucket=bucket, Key=key)  
    item_file = response['Body'].read().decode('utf-8')
    csv_read = pd.read_csv(item_file, sep="|", dtype={'Item_Call_Number': 'object'}, index_col=False)
    csv_read[['oclcnumber', 'status']] = csv_read.apply (lambda row: deleteHolding(oclcnumber)(row['oclcNumber']), axis=1)    
     
    #create a new CSV file
    #remove unnecessary fields    
    csv_read.to_csv(path_or_buf='results.txt', sep="|", index=False)
    
    return "success"

def addLBDs(event, context):  
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    # need to get the file from S3
    response = s3.get_object(Bucket=bucket, Key=key)  
    item_file = response['Body'].read().decode('utf-8')
    csv_read = pd.read_csv(item_file, sep="|", dtype={'Item_Call_Number': 'object'}, index_col=False)
    csv_read[['oclcnumber', 'lbd_number', 'status']] = csv_read.apply (lambda row: addLBD(row['oclcNumber'], row['note']), axis=1)    
     
    #create a new CSV file
    #remove unnecessary fields    
    csv_read.to_csv(path_or_buf='results.txt', sep="|", index=False)
    
    return "success"
  