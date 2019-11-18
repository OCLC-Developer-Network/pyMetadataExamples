import pytest
import json
import requests_mock
import pandas
import handler

with open('tests/mocks/lbd_response.json', 'r') as myfile:
    data=myfile.read()

# parse file
lbd_response = json.loads(data)

def test_addLBD(requests_mock):
    oclcNumber = "2416076"
    note = "fala"
    requests_mock.register_uri('POST', 'https://worldcat.org/lbd/', status_code=200, json=currentOCLCNumberMock)
    lbd = handler.addLBD(oclcNumber, note);
    assert type(lbd) is pandas.core.series.Series
    assert lbd[0] == '2416076'
    assert lbd[1] == 'x'
    assert lbd[2] == 'success'
    
    