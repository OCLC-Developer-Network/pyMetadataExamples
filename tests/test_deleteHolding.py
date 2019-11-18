import pytest
import json
import requests_mock
import pandas
import handler

with open('tests/mocks/deleteHolding.json', 'r') as myfile:
    data=myfile.read()

# parse file
deleteHolding = json.loads(data)

def test_deleteHolding(requests_mock):
    oclcNumber = "2416076"
    requests_mock.register_uri('DELETE', 'https://worldcat.org//ih/data?oclcNumber=' + oclcNumber, status_code=200, json=deleteHolding)
    holding = handler.deleteHolding(oclcNumber);
    assert type(holding) is pandas.core.series.Series
    assert holding[0] == '2416076'
    assert holding[1] == 'success'
    
    