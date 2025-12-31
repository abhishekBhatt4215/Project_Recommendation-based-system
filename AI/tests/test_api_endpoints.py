import sys
import os

# Add AI folder to path so direct imports work
ai_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ai_folder not in sys.path:
    sys.path.insert(0, ai_folder)

import pytest
from fastapi.testclient import TestClient


class DummyAgent:
    def __init__(self, ask_resp=None, stream_tokens=None, plan_resp=None, refine_resp=None):
        self._ask = ask_resp
        self._stream = stream_tokens or []
        self._plan = plan_resp
        self._refine = refine_resp

    def ask(self, message):
        return self._ask

    def ask_stream(self, message):
        for t in self._stream:
            yield t

    def plan_full_trip(self, **kwargs):
        return self._plan

    def refine_itinerary(self, existing_itinerary, user_request):
        return self._refine


# Import app after path setup
import api

# Replace agent globally in api module before tests run
api.agent = DummyAgent()


def get_client():
    return TestClient(api.app)



def test_health():
    client = get_client()
    r = client.get('/')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'


def test_chat_success():
    client = get_client()
    api.agent._ask = "Hello from agent"
    
    r = client.post('/chat', json={'message': 'hi'})
    assert r.status_code == 200
    assert r.json()['response'] == 'Hello from agent'


def test_chat_llm_error():
    client = get_client()
    api.agent._ask = '[LLM ERROR] model down'
    
    r = client.post('/chat', json={'message': 'hi'})
    assert r.status_code == 503


def test_chat_stream():
    client = get_client()
    api.agent._stream = ['Hello ', 'World', '!']
    
    r = client.post('/chat/stream', json={'message': 'hi'})
    # TestClient returns full response; for streaming check status
    assert r.status_code == 200
    api.agent._plan = {'day1': 'visit museum'}
    
    payload = {
        'origin_city': 'city A',
        'destination_city': 'city b',
        'depart_date': '2026-01-01',
        'return_date': '2026-01-05',
        'passengers': 2,
        'cabin_class': 'economy',
        'interests': 'sightseeing',
        'days': 4
    }

    r = client.post('/trip', json=payload)
    assert r.status_code == 200
    assert 'itinerary' in r.json()


def test_plan_trip_validation_error():
    client = get_client()
    # If agent returns a known '❌' string, API should return 400
    api.agent._plan = '❌ invalid destination'
    
    payload = {
        'origin_city': 'city A',
        'destination_city': 'city b',
        'depart_date': '2026-01-01',
        'return_date': '2026-01-05',
        'passengers': 2,
        'cabin_class': 'economy',
        'interests': 'sightseeing',
        'days': 4
    }

    r = client.post('/trip', json=payload)
    assert r.status_code == 400


def test_refine_trip():
    client = get_client()
    api.agent._refine = 'Updated itinerary'
    
    r = client.post('/refine', json={'itinerary': 'orig', 'user_request': 'add museum'})
    assert r.status_code == 200
    assert r.json()['itinerary'] == 'Updated itinerary'
