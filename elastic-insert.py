# elastic test and fileRead helpers
# loading dumped json file and inserting to elastic search
import requests
from elasticsearch import Elasticsearch
import json
import os
r = requests.get('http://localhost:9200')
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
# index id
i = 1
fileLoc = 'pipeline/'
files = []

for r, d, f in os.walk(fileLoc):
    for file in f:
        if '.txt' in file:
            files.append(os.path.join(r, file))

# creating an index Name
# indexName = 'wikipediaarticles'

for file in files:
    fileContent = open(file,'r',encoding='utf8')
    fileText = fileContent.read()
    jsonFile = json.loads(fileText) 
    for key, value in jsonFile.items():
        es.index(index= 'wikiarticles' , doc_type = 'text', id=i, body = value)
        i+=1
