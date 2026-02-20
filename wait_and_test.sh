#!/bin/bash
cd ~/Programs/tapo-c210-monitor
source .venv/bin/activate

echo 'Waiting for rate limit to clear...'
while true; do
    result=$(python3 -c "
import requests, warnings
warnings.filterwarnings('ignore')
resp = requests.post('https://192.168.29.183/stok=/ds', 
    json={'method': 'login', 'params': {'username': 'x', 'password': 'x'}},
    verify=False, timeout=5)
data = resp.json()
if 'data' in data and 'sec_left' in data.get('data', {}):
    print(data['data']['sec_left'])
else:
    print('0')
" 2>/dev/null)
    
    if [ "$result" = "0" ]; then
        echo 'Rate limit cleared! Running test...'
        python3 test_night_vision.py
        exit $?
    else
        mins=$((result / 60))
        secs=$((result % 60))
        echo -ne "\rWaiting: ${mins}m ${secs}s remaining..."
        sleep 30
    fi
done
