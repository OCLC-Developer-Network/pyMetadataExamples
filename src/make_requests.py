from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
import pandas as pd  
import json
import requests
import pymarc
from pymarc import Record, Field, Subfield
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
        r = oauth_session.get(config.get('metadata_service_url') + "/bibs/current?oclcNumbers=" + oclcnumber, headers={"Accept":"application/json"})
        r.raise_for_status
        try:
            result = r.json()
            currentOCLCNumber = result['controlNumbers'][0]['current']
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
        r = oauth_session.get(config.get('metadata_service_url') +"/bibs/" + str(oclcnumber), headers={"Accept":'application/atom+xml;content="application/vnd.oclc.marc21+xml"'})
        r.raise_for_status
        try:
            marcRecords = pymarc.parse_xml_to_array(StringIO(r.text))
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
        r = oauth_session.post(config.get('metadata_service_url') + "/institution/holdings/" + oclcnumber + "/set", headers={"Accept":"application/json"})
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
        r = oauth_session.post(config.get('metadata_service_url') + "/institution/holdings/" + oclcnumber + "/unset", headers={"Accept":"application/json"})
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
                Subfield(code='a', value= note)
            ]),
        Field(
            indicators = [' ', ' '],
            tag = '935',
            subfields = [
                Subfield(code='a', value= str(time.time()))
            ]),
        Field(
            indicators = [' ', ' '],
            tag = '940',
            subfields = [
                Subfield(code='a', value= config.get('oclcSymbol'))
            ])
        )
    input = pymarc.record_to_xml(record).decode("utf-8")
    
    try:
        r = oauth_session.post(config.get('metadata_service_url') + "/lbds", data=input, headers={"Accept":'application/atom+xml;content="application/vnd.oclc.marc21+xml"', "Content-Type": "application/vnd.oclc.marc21+xml"})
        r.raise_for_status
        try:
            marcRecords = pymarc.parse_xml_to_array(StringIO(r.text))
            # pull out the LBD accession number
            accessionNumber = marcRecords[0]['001'].value()
            status = "success"
        except xml.etree.ElementTree.ParseError  as err:
            accessionNumber = ""
            status = "failed XML parsing issue"
            print(err)
    except requests.exceptions.HTTPError as err:
        status = "failed"
    return pd.Series([oclcnumber, accessionNumber, status])

def addLHR(config, oclcnumber, oclcSymbol, branch, shelfLocation, classPart, itemPart, prefix, suffix, barcode):
    oauth_session = config.get('oauth-session')
    #create the LBD
    record = Record(leader='00000nx  a2200000zi 4500')
    record.add_field(Field(tag='004', data=oclcnumber))
    record.add_field(Field(tag='007', data="zu"))
    record.add_field(
        Field(
            indicators = ['', ''],
            tag = '035',
            subfields = [
                Subfield(code='a', value= '(OCoLC)' + oclcnumber)
            ]
        )
    )
    record.add_field(
        Field(
            indicators = [' ', ' '],
            tag = '852',
            subfields = [
                Subfield(code='a', value= oclcSymbol),
                Subfield(code='b', value= branch),
                Subfield(code='c', value= shelfLocation),
                Subfield(code='h', value= classPart),
                Subfield(code='i', value= itemPart),
                Subfield(code='k', value= prefix),
                Subfield(code='m', value= suffix)
            ]),
        Field(
            indicators = [' ', ' '],
            tag = '876',
            subfields = [
                Subfield(code='p', value= barcode)
            ])
    )
    input = pymarc.record_to_xml(record).decode("utf-8")

    try:
        r = oauth_session.post(config.get('metadata_service_url') + "/lhrs", data=input, headers={"Accept":'application/xml"', "Content-Type": "application/xml"})
        r.raise_for_status
        try:
            marcRecords = pymarc.parse_xml_to_array(StringIO(r.text))
            # pull out the LBD accession number
            accessionNumber = marcRecords[0]['001'].value()
            status = "success"
        except xml.etree.ElementTree.ParseError  as err:
            accessionNumber = ""
            status = "failed XML parsing issue"
            print(err)
    except requests.exceptions.HTTPError as err:
        status = "failed"
    return pd.Series([oclcnumber, accessionNumber, status])

def findBibMatch(config, record):
    oauth_session = config.get('oauth-session')
    try:
        r = oauth_session.post(config.get('metadata_service_url') + "/bibs/match", data=input, headers={"Accept":'application/xml"', "Content-Type": "application/xml"})
        r.raise_for_status
        try:
            result = r.json()
            oclcNumber = result['briefRecords'][0]['oclcNumber']
            status = "success"
        except xml.etree.ElementTree.ParseError  as err:
            oclcNumber = ""
            status = "failed XML parsing issue"
            print(err)
    except requests.exceptions.HTTPError as err:
        status = "failed"
    return pd.Series([oclcNumber, status])

def getLatestEdition(config, oclcNumber):
    oauth_session = config.get('oauth-session')
    requestURL = config.get('metadata_service_url') + "/brief-bibs/" + str(oclcNumber) + "/other-editions?inLanguage=eng&limit=1&orderBy=publicationDateDesc"
    try:
        r = requests.get(requestURL, headers={"Accept":"application/json"})
        r.raise_for_status
        try:
            result = r.json()
            if result.get('briefRecords'):
                if (str(oclcNumber) == result.get('briefRecords')[0].get('oclcNumber')):
                    isLatestEdition = "true"
                elif (result.get('briefRecords')[0].get('mergedOclcNumbers') and str(oclcNumber) in result.get('briefRecords')[0].get('mergedOclcNumbers')):
                    isLatestEdition = "true"
                else:
                    isLatestEdition = "false"
                latestEditionOCN = result.get('briefRecords')[0].get('oclcNumber')
                latestEditionYear = result.get('briefRecords')[0].get('date')
            else:
                isLatestEdition = ""
                latestEditionOCN = ""
                latestEditionYear = ""
        except json.decoder.JSONDecodeError:
            isLatestEdition = ""
            latestEditionOCN = ""
            latestEditionYear = ""
    except requests.exceptions.HTTPError as err:
        status = "failed"

    return pd.Series([isLatestEdition, latestEditionOCN, latestEditionYear, status])
