import requests
url = 'http://0.0.0.0:8080/home'
response = requests.get(url)
if response.status_code == 200:
    print("it_works")
else:
    print("not works")