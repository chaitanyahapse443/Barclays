import requests
import json

# Read sample case
with open('../sample_data/suspicious_case_1.json') as f:
    case = json.load(f)

print("Testing create case API...")
print(f"Payload: {json.dumps(case, indent=2)}")

# Test create case
resp = requests.post('http://localhost:8001/cases/create', json=case)
print(f'\nStatus: {resp.status_code}')
print(f'Response: {resp.text}')

if resp.status_code == 200:
    print("\n✅ Create case successful!")
else:
    print("\n❌ Create case failed!")
