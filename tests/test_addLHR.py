import pytest
import json
import requests_mock
import pandas
from src import make_requests

with open('tests/mocks/lbd_response.xml', 'r') as myfile:
    data=myfile.read()
    
lbd_response = data    

def test_addLHR(requests_mock, mockOAuthSession, getTestConfig):
    getTestConfig.update({'oauth-session': mockOAuthSession})
    oclcNumber = "2416076"
    note = "fala"
    requests_mock.register_uri('POST', 'https://metadata.api.oclc.org/worldcat/manage/lhrs', status_code=200, text=lbd_response)
    lhr = make_requests.addLHR(getTestConfig, oclcNumber, note);
    assert type(lhr) is pandas.core.series.Series
    assert lhr[0] == '2416076'
    #assert lhr[1] == '1204719824'
    assert lhr[2] == 'success'
    
    