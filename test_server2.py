import threading, uvicorn, requests, time, os
from api.main import app

def run_server():
    uvicorn.run(app, host='127.0.0.1', port=8001, log_level='critical')

threading.Thread(target=run_server, daemon=True).start()
time.sleep(5)
t=time.time()
print("starting request")
res=requests.post('http://127.0.0.1:8001/enhance', files={'video': open('data/s1/bbaf2n.mpg', 'rb')})
print(res.status_code)
print(res.content[:200])
print('Time:', time.time()-t)
