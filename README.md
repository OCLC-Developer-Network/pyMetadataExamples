# Metadata examples

Custom application looks for new files in particular folders an S3 bucket and interacts with the Metadata API based on the data in the delimited file

## Use cases

1. Obtained list of current OCLC Numbers based on a given OCLC Number
2. Obtain list of merged OCLC Numbers based on a given OCLC Number 
3. Set Holdings based on a given OCLC Number 
4. Delete Holdings based on a given OCLC Number
5. Add an LBD based on a given OCLC Number and 500 note data  

## Installing Locally

### Step 1: Clone the repository
Clone this repository

```bash
$ git clone {url}
```
or download directly from GitHub.

Change into the application directory

### Step 2: Setup Virtual Environment

```bash
$ python -m venv venv
$ . venv/bin/activate
```

### Step 3: Install python dependencies

```bash
$ pip install -r requirements.txt
```

### Step 4: Run local tests

```bash
$ python -m pytest
```

### Step 5: Run code locally
```bash
usage: processSheet.py [-h] --itemFile ITEMFILE --operation
                  {getCurrentOCLCNumbers, retrieveMergedOCLCNumbers, setHoldingsbyOCLCNumber, deleteHoldingsbyOCLCNumber, addLBDs}
                  --outputDir OUTPUTDIR

optional arguments:
  -h, --help            show this help message and exit
  --itemFile ITEMFILE   File you want to process
  --operation {getCurrentOCLCNumbers, retrieveMergedOCLCNumbers, setHoldingsbyOCLCNumber, deleteHoldingsbyOCLCNumber, addLBDs}
                        Operation to run: getCurrentOCLCNumbers, 
                        retrieveMergedOCLCNumbers, setHoldingsbyOCLCNumber, 
                        deleteHoldingsbyOCLCNumber, addLBDs
  --outputDir OUTPUTDIR
                        Directory to save output to                                                                       
                        
```

#### Example
```bash
$ python processSheet.py --itemFile samples/oclc_numbers.csv --operation getCurrentOCLCNumbers --outputDir samples/getCurrentOCLCNumbers.csv

$ python processSheet.py --itemFile samples/oclc_numbers_holdings.csv --operation retrieveMergedOCLCNumbers --outputDir samples/mergedOCLCNumbers.csv

$ python processSheet.py --itemFile samples/sp_holdings.csv --operation setHoldingsbyOCLCNumber --outputDir samples/addedHoldings.csv

$ python processSheet.py --itemFile samples/my_retentions.csv --operation deleteHoldingsbyOCLCNumber --outputDir samples/removedHoldings.csv

$ python processSheet.py --itemFile samples/symbol_retentions.csv --operation addLBDs --outputDir samples/newLBDs.csv
```

## Running in AWS Lambda

### Step 1: Use npm to install dependencies needed to deploy code
Download node and npm and use the `install` command to read the dependencies JSON file 

```bash
$ npm install
```

### Step 2: AWS Setup

1. Install AWS Command line tools
- https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html
I recommend using pip.
2. Create an AWS user in IAM console. Give it appropriate permissions. Copy the key and secret for this user to use in the CLI. 
3. Configure the command line tools - https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html

- Make sure you add 
-- key/secret
-- region
    
### Step 3: Create an S3 Bucket for the files
1. Use the AWS Console to create a bucket. Note your bucket name!!!
2. Create folder metadata_tasks/
3. Add a sample csv file named getCurrentOCLCNumbers.csv with data to check for current OCLC Numbers
4. Add a sample csv file named getMergedOCLCNumbers.csv with data to check for merged OCLC Numbers
5. Add a sample csv file named addHoldings.csv with data to add holdings by OCLC Number
6. Add a sample csv file named deleteHoldings.csv with data delete holdings by OCLC Number
7. Add a sample csv file named LBDsToAdd.csv with data to add LBD records to OCLC Numbers


### Step 4: Test application locally
1. Alter s3-getCurrentOCLCNumbers.json to point to your bucket and your sample txt file.

2. Use serverless to test locally

```bash
$ serverless invoke local --function getCurrentOCLCNumbers --path s-getCurrentOCLCNumbers.json
```

3. Alter s3-getMergedOCLCNumbers.json to point to your bucket and your sample csv file.

4. Use serverless to test locally

```bash
$ serverless invoke local --function getMergedOCLCNumbers --path s3-getMergedOCLCNumbers.json
```

5. Alter s3-addHoldings.json to point to your bucket and your sample csv file.

6. Use serverless to test locally

```bash
$ serverless invoke local --function addHoldings --path s3-addHoldings.json
```

7. Alter s3-deleteHoldings.json to point to your bucket and your sample csv file.

8. Use serverless to test locally

```bash
$ serverless invoke local --function deleteHoldings --path s3-deleteHoldings.json
```

9. Alter s3-addLBDs.json to point to your bucket and your sample csv file.

10. Use serverless to test locally

```bash
$ serverless invoke local --function addLBDs --path s3-addLBDs.json
```

### Step 5: Deploy the code using serverless

```bash
$ serverless deploy
```
