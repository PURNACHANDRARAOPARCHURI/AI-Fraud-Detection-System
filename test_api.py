import requests
import json

# Test data
test_data = {
    'account_id': 'test_user_001',
    'amount': 5000.0,
    'type': 0  # PAYMENT
}

print('🚀 Testing API endpoint...')
print(f'Sending: {test_data}')

try:
    response = requests.post('http://127.0.0.1:8000/score', json=test_data, timeout=30)
    
    print(f'\n✅ Status Code: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        print('\n📊 Response Data:')
        print(json.dumps(result, indent=2))
        
        print('\n✅ Transaction successfully processed and stored in NeonTech database!')
        print(f"   - Decision: {result.get('decision')}")
        print(f"   - Fraud Probability: {result.get('fraud_probability'):.2%}")
        print(f"   - Risk Score: {result.get('risk_score'):.2f}")
    else:
        print(f'\n❌ Error: {response.text}')
        
except Exception as e:
    print(f'\n❌ Connection Error: {e}')
