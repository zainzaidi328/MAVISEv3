import threading, uvicorn, requests, time, os
from api.main import app

def run_server():
    uvicorn.run(app, host='127.0.0.1', port=8001)

threading.Thread(target=run_server, daemon=True).start()
time.sleep(5)
t=time.time()
if os.path.exists('data/s1_video.zip'):
    print("Testing with real file")
    res=requests.post('http://127.0.0.1:8001/enhance', files={'video': open('data/s1_video.zip', 'rb')})
    print(res.status_code)
    print(res.text[:200])
else:
    print('No video')
print('Time:', time.time()-t)
