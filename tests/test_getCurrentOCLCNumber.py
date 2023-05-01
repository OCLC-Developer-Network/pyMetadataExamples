import pytest
import json
import requests_mock
import pandas
from src import make_requests

with open('tests/mocks/getCurrentOCLCNumber.json', 'r') as myfile:
    data=myfile.read()

# parse file
currentOCLCNumberMock = json.loads(data)

def test_getCurrentOCLCNumber(requests_mock, mockOAuthSession, getTestConfig):
    getTestConfig.update({'oauth-session': mockOAuthSession})
    oclcNumber = "2416076"
    requests_mock.register_uri('GET', 'https://metadata.api.oclc.org/worldcat/manage/bibs/current?oclcNumbers' + oclcNumber, status_code=207, json=currentOCLCNumberMock)
    bib = make_requests.getCurrentOCLCNumber(getTestConfig, oclcNumber);
    assert type(bib) is pandas.core.series.Series
    assert bib[0] == '2416076'
    assert bib[1] == '24991049'
    assert bib[2] == 'success'
    
    