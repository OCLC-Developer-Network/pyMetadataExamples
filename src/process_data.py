from src import handle_files
from src import make_requests

import pandas as pd

def retrieveCurrentOCLCNumbers(processConfig, csv_read):
    csv_read[['oclcNumber', 'currentOCN', 'status']] = csv_read.apply (lambda row: make_requests.getCurrentOCLCNumber(processConfig, row['oclcNumber']), axis=1)    
    return csv_read 

def retrieveMergedOCLCNumbers(processConfig, csv_read):
    csv_read[['oclcNumber', 'mergedOCNs', 'status']] = csv_read.apply (lambda row: make_requests.getMergedOCLCNumbers(processConfig, row['oclcNumber']), axis=1)    
    return csv_read  

def setHoldingsbyOCLCNumber(processConfig, csv_read):      
    csv_read[['oclcnumber', 'status']] = csv_read.apply (lambda row: setHolding(row['oclcNumber']), axis=1)
    return csv_read    

def deleteHoldingsbyOCLCNumber(processConfig, csv_read):  
    csv_read[['oclcnumber', 'status']] = csv_read.apply (lambda row: deleteHolding(row['oclcNumber']), axis=1)    
    return csv_read    

def addLBDs(processConfig, csv_read):  
    csv_read[['oclcnumber', 'lbd_number', 'status']] = csv_read.apply (lambda row: addLBD(row['oclcNumber'], row['note']), axis=1)    
    return csv_read    
        
