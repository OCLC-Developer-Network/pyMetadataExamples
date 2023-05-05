import pytest
import json
import requests_mock
import pandas
from src import make_requests

def test_deleteHolding(requests_mock, mockOAuthSession, getTestConfig):
    getTestConfig.update({'oauth-session': mockOAuthSession})
    oclcNumber = "2416076"
    requests_mock.register_uri('POST', 'https://metadata.api.oclc.org/worldcat/manage/institution/holdings/' + oclcNumber + '/unset', status_code=200, json="")
    holding = make_requests.deleteHolding(getTestConfig, oclcNumber);
    assert type(holding) is pandas.core.series.Series
    assert holding[0] == '2416076'
    assert holding[1] == 'success'
    
    