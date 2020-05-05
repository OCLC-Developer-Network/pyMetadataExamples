from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
import pandas as pd  
import json
import requests
import pymarc
from pymarc import Record, Field
from io import StringIO
import xml
from xml.etree import ElementTree
import time

def createOAuthSession(config, scope):    
    auth = HTTPBasicAuth(config.get('key'), config.get('secret'))
    client = BackendApplicationClient(client_id=config.get('key'), scope=scope)
    oauth_session = OAuth2Session(client=client)
    try:
        token = oauth_session.fetch_token(token_url=config.get('token_url'), auth=auth)
        return oauth_session
    except BaseException as err:
        return err

def getCurrentOCLCNumber(config, oclcnumber):
    oauth_session = config.get('oauth-session')
    try:        
        r = oauth_session.get(config.get('metadata_service_url') + "/bib/checkcontrolnumbers?oclcNumbers=" + oclcnumber, headers={"Accept":"application/json"})
        r.raise_for_status
        try:
            result = r.json()
            currentOCLCNumber = result['entry'][0]['currentOclcNumber']
            status = "success"
        except json.decoder.JSONDecodeError:
            currentOCLCNumber = ""
            status = "failed"
    except requests.exceptions.HTTPError as err:
        mergedOCLCNumbers = ""
        status = "failed"
    return pd.Series([oclcnumber, currentOCLCNumber, status])    

def getMergedOCLCNumbers(config, oclcnumber):
    oauth_session = config.get('oauth-session')
    try:
        r = oauth_session.get(config.get('metadata_service_url') +"/bib/data/" + str(oclcnumber), headers={"Accept":'application/atom+xml;content="application/vnd.oclc.marc21+xml"'})
        r.raise_for_status
        try:
            result = ElementTree.fromstring(r.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom', 'wc': 'http://worldcat.org/rb'}
            marcNode = result.findall('atom:content/wc:response', ns)[0].getchildren()[0]
            marcData = StringIO(ElementTree.tostring(marcNode, encoding='unicode', method='xml'))
            # need to get this XML section out as a string and into a file like object
            marcRecords = pymarc.parse_xml_to_array(marcData)
            # pull out the merged OCLC Numbers
            mergedOCNFields = marcRecords[0]['019'].get_subfields('a')
            mergedOCLCNumbers= list(map(lambda field: field, mergedOCNFields))
            
            status = "success"
        except xml.etree.ElementTree.ParseError as err:
            mergedOCLCNumbers = ""
            status = "failed XML parsing failed"
            print(err)
    except requests.exceptions.HTTPError as err:
        mergedOCLCNumbers = ""
        status = "failed"
    return pd.Series([oclcnumber, ",".join(mergedOCLCNumbers), status])

def setHolding(config, oclcnumber):
    oauth_session = config.get('oauth-session')
    try:
        r = oauth_session.post(config.get('metadata_service_url') + "/ih/data?oclcNumber=" + oclcnumber, headers={"Accept":"application/json"})
        r.raise_for_status
        try:
            result = r.json()
            status = "success"
        except json.decoder.JSONDecodeError:
            status = "failed"
    except requests.exceptions.HTTPError as err:
        status = "failed"
    return pd.Series([oclcnumber, status])

def deleteHolding(config, oclcnumber):
    oauth_session = config.get('oauth-session')
    try:
        r = oauth_session.delete(config.get('metadata_service_url') + "/ih/data?oclcNumber=" + oclcnumber, headers={"Accept":"application/json"})
        r.raise_for_status
        try:
            result = r.json()
            status = "success"
        except json.decoder.JSONDecodeError:
            status = "failed"
    except requests.exceptions.HTTPError as err:
        status = "failed"
    return pd.Series([oclcnumber, status])

def addLBD(config, oclcnumber, note):
    oauth_session = config.get('oauth-session')
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
                'a', config.get('oclcSymbol')
            ])
        )
    input = pymarc.record_to_xml(record).decode("utf-8")
    
    try:
        r = oauth_session.post(config.get('metadata_service_url') + "/lbd/data", data=input, headers={"Accept":'application/atom+xml;content="application/vnd.oclc.marc21+xml"', "Content-Type": "application/vnd.oclc.marc21+xml"})
        r.raise_for_status
        try:
            result = ElementTree.fromstring(r.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom', 'wc': 'http://worldcat.org/rb'}
            marcNode = result.findall('atom:content/wc:response', ns)[0].getchildren()[0]
            marcData = StringIO(ElementTree.tostring(marcNode, encoding='unicode', method='xml'))
            # need to get this XML section out as a string and into a file like object
            marcRecords = pymarc.parse_xml_to_array(marcData)
            # pull out the LBD accession number
            print(marcRecords)
            accessionNumber = marcRecords[0]['001'].value()
            status = "success"
        except xml.etree.ElementTree.ParseError  as err:
            accessionNumber = ""
            status = "failed XML parsing issue"
            print(err)
    except requests.exceptions.HTTPError as err:
        status = "failed"
    return pd.Series([oclcnumber, accessionNumber, status])