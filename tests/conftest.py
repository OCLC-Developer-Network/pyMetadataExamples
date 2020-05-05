import pytest
import yaml
import json
import requests_mock
import moto
import boto3

from src import make_requests

with open('tests/mocks/access_token.json', 'r') as myfile:
    data=myfile.read()

# parse file
oauth_response = json.loads(data)

bucket = "mock-test-bucket"
key = "test_csv.csv"

@pytest.fixture(scope="function")
def mockOAuthSession(requests_mock, getTestConfig):
    requests_mock.register_uri('POST', getTestConfig.get('token_url') , status_code=200, json=oauth_response)
    oauth_session = make_requests.createOAuthSession(getTestConfig, 'DISCOVERY')    
    return oauth_session

@pytest.fixture(scope="function")
def getTestConfig():
    with open("tests/test_config.yml", 'r') as stream:
        config = yaml.safe_load(stream)
    
    return config

@pytest.fixture
def s3_bucket():
    with moto.mock_s3():
        boto3.client('s3').create_bucket(Bucket=bucket)
        boto3.client('s3').put_object(Bucket=bucket, Key=key, Body="oclcnumber\n2416076\n318877925\n829387251\n55887559\n70775700\n466335791\n713567391\n84838876\n960238778\n893163693")
        yield boto3.resource('s3').Bucket(bucket)

@pytest.fixture
def s3_event_payload():
    def _payload(id):
        s3_key = f'{id}.csv'

        msg = {
            'Records': [
                {
                    's3': {
                        'bucket': {'name': bucket},
                        'object': {'key': s3_key},
                    }
                }
            ]
        }
        
        return msg

    return _payload        

