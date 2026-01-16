import requests
url = 'http://127.0.0.1:5001/login'
response = requests.get(url)
if response.status_code == 200:
    print("it_works")
else:
    print("not works")
