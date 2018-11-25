import requests
import json

class FirebaseWorker:
    def __init__(self):
        self.secrets = json.load(open("secrets.json"))
        self.base = self.secrets.get("firebase_base")

    def full_url(self, url):
        return self.base + '/' + url + '.json'

    def get(self, url):
        r = requests.get(self.full_url(url))
        return r.json()
    
    def add(self, url, payload):
        str_payload = json.dumps(payload, separators=(',', ':'))
        r = requests.patch(self.full_url(url), data=str_payload)
        return r.json() == payload

    def add_list(self, url, payload):
        str_payload = json.dumps(payload, separators=(',', ':'))
        r = requests.post(self.full_url(url), data=str_payload)
    
    # def update(Self, url, payload):
    #     str_payload = json.dumps(payload, separators=(',', ':'))
    #     r = requests.

if __name__ == "__main__":
    f = FirebaseWorker()

    print(f.get("data/historical"))
    print(f.add("data/historical", {"asdf": 12}))
    for i in range(10):
        f.add_list("data/historical", {"asddf": 12})
    print(f.get("data/historical"))


    
