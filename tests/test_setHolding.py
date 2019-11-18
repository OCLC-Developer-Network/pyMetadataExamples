import pytest
import json
import requests_mock
import pandas
import handler

with open('tests/mocks/setHoldings.json', 'r') as myfile:
    data=myfile.read()

# parse file
setHolding = json.loads(data)

def test_getCurrentOCLCNum(requests_mock):
    oclcNumber = "2416076"
    requests_mock.register_uri('POST', 'https://worldcat.org/ih/data?oclcNumber=' + oclcNumber, status_code=201, json=setHolding)
    holding = handler.setHolding(oclcNumber);
    assert type(holding) is pandas.core.series.Series
    assert holding[0] == '2416076'
    assert holding[1] == 'success'
    
    