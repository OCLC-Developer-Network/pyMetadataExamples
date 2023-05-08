import pytest
import json
import requests_mock
import pandas
from src import make_requests

with open('tests/mocks/bib_match_response.json', 'r') as myfile:
    data=myfile.read()
# parse file
matchResults = json.loads(data)

def test_findBibMatch(requests_mock, mockOAuthSession, getTestConfig):
    getTestConfig.update({'oauth-session': mockOAuthSession})
    with open('tests/mocks/bib_to_match.xml', 'r') as recordFile:
        data=recordFile.read()
    record = data
    requests_mock.register_uri('POST', 'https://metadata.api.oclc.org/worldcat/manage/bibs/match', status_code=200, json=matchResults)
    bib = make_requests.findBibMatch(getTestConfig, record);
    assert type(bib) is pandas.core.series.Series
    assert bib[0] == '311684437'
    assert bib[1] == 'success'
    
    