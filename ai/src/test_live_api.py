import urllib.request
import json
from pathlib import Path

url = 'http://127.0.0.1:8000/predict'
sample_path = Path('C:/Users/sinch/.gemini/antigravity-ide/brain/e71b2c74-a3bb-44b7-b705-fd0702cc3f51/scratch/chatgpt_sep10.png')

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
data = []
data.append(f'--{boundary}'.encode())
data.append(b'Content-Disposition: form-data; name="email"')
data.append(b'')
data.append(b'test@solarsafe.com')
data.append(f'--{boundary}'.encode())
data.append(f'Content-Disposition: form-data; name="image"; filename="{sample_path.name}"'.encode())
data.append(b'Content-Type: image/png')
data.append(b'')
with open(sample_path, 'rb') as f:
    data.append(f.read())
data.append(f'--{boundary}--'.encode())
data.append(b'')

body = b'\r\n'.join(data)

req = urllib.request.Request(url, data=body)
req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print('HTTP Status:', resp.status)
        result = json.loads(resp.read().decode('utf-8'))
        print('\nLive FastAPI /predict Response:')
        print(json.dumps(result, indent=2))
except Exception as e:
    print('Error:', e)
