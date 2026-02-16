import json
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

client = TestClient(app)


def test_create_case_and_generate_sar():
    sample = json.loads(open('..\\sample_data\\suspicious_case_1.json').read())
    # Create case
    r = client.post('/cases/create', json=sample)
    assert r.status_code == 200
    data = r.json()
    assert 'case_id' in data
    case_id = data['case_id']

    # Generate SAR (uses stub LLM by default)
    r2 = client.post(f'/sars/generate?case_id={case_id}')
    assert r2.status_code == 200
    d2 = r2.json()
    assert 'sar_draft' in d2
