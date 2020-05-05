import pytest
import json
import requests_mock
import pandas
from src import make_requests

with open('tests/mocks/lbd_response.xml', 'r') as myfile:
    data=myfile.read()
    
lbd_response = data    

def test_addLBD(requests_mock, mockOAuthSession, getTestConfig):
    getTestConfig.update({'oauth-session': mockOAuthSession})
    oclcNumber = "2416076"
    note = "fala"
    requests_mock.register_uri('POST', 'https://worldcat.org/lbd/data', status_code=200, text=lbd_response)
    lbd = make_requests.addLBD(getTestConfig, oclcNumber, note);
    assert type(lbd) is pandas.core.series.Series
    assert lbd[0] == '2416076'
    #assert lbd[1] == '1204719824'
    assert lbd[2] == 'success'
    
    