## need to import the relevant files
import argparse
import yaml
from src import handle_files, process_data, make_requests
import sys
import string

with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)
    
def processArgs():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--itemFile', required=True, help='File you want to process')
        parser.add_argument('--operation', required=True, choices=['getCurrentOCLCNumbers', 'retrieveMergedOCLCNumbers', 'setHoldingsbyOCLCNumber', 'deleteHoldingsbyOCLCNumber', 'addLBDs', 'getLatestEdition'], help='Operation to run: getCurrentOCLCNumbers, retrieveMergedOCLCNumbers, setHoldingsbyOCLCNumber, deleteHoldingsbyOCLCNumber, addLBDs')
        parser.add_argument('--outputDir', required=True, help='Directory to save output to')        
    
        args = parser.parse_args()
    except SystemExit:
        raise
    
def process(args):
    item_file = handle_files.readFileFromLocal(args.itemFile) 
    
    operation = args.operation
    output_dir = args.outputDir
    
    # get a token
    scope = ['WorldCatMetadataAPI']
    try:
        oauth_session = make_requests.createOAuthSession(config, scope)
    
        config.update({"oauth-session": oauth_session})
        processConfig = config
        csv_read = handle_files.loadCSV(item_file) 
        
        if operation == "getCurrentOCLCNumbers":
            csv_read = process_data.retrieveCurrentOCLCNumbers(processConfig, csv_read)
        elif operation == "retrieveMergedOCLCNumbers":
            csv_read = process_data.retrieveMergedOCLCNumbers(processConfig, csv_read)    
        elif operation == "setHoldingsbyOCLCNumber":                
            csv_read = process_data.setHoldingsbyOCLCNumber(processConfig, csv_read)   
        elif operation == "deleteHoldingsbyOCLCNumber":
            csv_read = process_data.deleteHoldingsbyOCLCNumber(processConfig, csv_read)
        elif operation == "addLBDs":
            csv_read = process_data.addLBDs(processConfig, csv_read)
        elif operation == "getLatestEdition":
            csv_read = process_data.getLatestEdition(processConfig, csv_read)

        return handle_files.saveFileLocal(csv_read, output_dir)

    except BaseException as err:
        result = 'no access token ' + str(err)
        return result   

if __name__ == '__processSheet__':
    try:
        args = processArgs()
        print(process(args))
    except SystemExit:
        print("Invalid Operation specified")
else:
    try:
        args = processArgs()
        print(process(args))
    except SystemExit:
        print("Invalid Operation specified")
  