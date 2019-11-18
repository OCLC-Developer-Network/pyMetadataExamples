import pytest
import json
import requests_mock
import pandas
import handler

with open('tests/mocks/getCurrentOCLCNumber.json', 'r') as myfile:
    data=myfile.read()

# parse file
currentOCLCNumberMock = json.loads(data)

def test_getCurrentOCLCNum(requests_mock):
    oclcNumber = "2416076"
    requests_mock.register_uri('GET', 'https://worldcat.org/bib/checkcontrolnumbers?oclcNumbers=' + oclcNumber, status_code=207, json=currentOCLCNumberMock)
    bib = handler.getCurrentOCLCNum(oclcNumber);
    assert type(user) is pandas.core.series.Series
    assert bib[0] == '2416076'
    assert bib[1] == '24991049'
    assert bib[2] == 'success'
    
    