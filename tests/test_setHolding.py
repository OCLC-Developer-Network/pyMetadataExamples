import pytest
import json
import requests_mock
import pandas
from src import make_requests

def test_setHolding(requests_mock, mockOAuthSession, getTestConfig):
    getTestConfig.update({'oauth-session': mockOAuthSession})
    oclcNumber = "2416076"
    requests_mock.register_uri('POST', 'https://metadata.api.oclc.org/worldcat/manage/institution/holdings/' + oclcNumber + '/set', status_code=201, json="")
    holding = make_requests.setHolding(getTestConfig, oclcNumber);
    assert type(holding) is pandas.core.series.Series
    assert holding[0] == '2416076'
    assert holding[1] == 'success'
    
    