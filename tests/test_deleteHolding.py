import pytest
import json
import requests_mock
import pandas
from src import make_requests

def test_deleteHolding(requests_mock, mockOAuthSession, getTestConfig):
    getTestConfig.update({'oauth-session': mockOAuthSession})
    oclcNumber = "2416076"
    requests_mock.register_uri('DELETE', 'https://metadata.api.oclc.org/worldcat/manage/holdings' + oclcNumber, status_code=200, json="")
    holding = make_requests.deleteHolding(getTestConfig, oclcNumber);
    assert type(holding) is pandas.core.series.Series
    assert holding[0] == '2416076'
    assert holding[1] == 'success'
    
    