import pytest
import json
import requests_mock
import pandas

from src import make_requests

with open('tests/mocks/bib_response.xml', 'r') as myfile:
    data=myfile.read()
        
merged_oclcnumbers = data    

def test_getMergedOCLCNumbers(requests_mock, mockOAuthSession, getTestConfig):
    getTestConfig.update({'oauth-session': mockOAuthSession})
    oclcNumber = "311684437"
    requests_mock.register_uri('GET', 'https://worldcat.org/bib/data/' + oclcNumber, status_code=200, text=merged_oclcnumbers)    
    bib = make_requests.getMergedOCLCNumbers(getTestConfig, oclcNumber);
    assert type(bib) is pandas.core.series.Series
    assert bib[0] == '311684437'
    assert len(bib[1].split(',')) == 10
    assert bib[2] == 'success' 