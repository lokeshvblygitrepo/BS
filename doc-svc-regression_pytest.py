import requests
import json
from os import listdir
from os.path import isfile, join
import unittest
import os


# API Proxy details
base_url = 'http://document-svc.service.qa.corvesta.net/documentgenerator/document'

# Variables
headers_json = {"keyspring.client.id":'DDVA',"keyspring.tenant.id":'DDVA','content-Type':'application/json'}
file_path = os.getcwd()+'\\Docsvc_jsonpayload\\'
liststepresults1 = []
liststepresults2 = []
list_failed_file = []

#List for  validating of each of request response
content_type_list=['application/pdf','application/vnd.ms-excel','text/plain']

# to get all the files in the folder
onlyfiles = [f for f in listdir(file_path) if isfile(join(file_path, f))]


def doc_svc():
  try:
    for i in onlyfiles:
      filename=file_path+i
      with open(filename, 'r') as filehandle:
        filecontent = filehandle.read()
        strResponse = requests.post(base_url, data=filecontent, headers=headers_json,stream=True)
        if strResponse.status_code == 200:
          liststepresults1.append([i,"Passed",'Step1 is passed'])
          if strResponse.headers['Content-Type'] in content_type_list:
            liststepresults2.append([i,"Passed",'Step2 is passed'])
          else:
            liststepresults2.append([i,"Failed",'Step2 is passed'])
        else:
          liststepresults1.append([i,"Failed",'Step1 is Failed'])

    for i in liststepresults1: # to check whether status code 200 is recieved or not for all documents
      if(i[1] == 'Passed'):
        print('Step 1 is passed for '+str(i[0]))
        continue
      else:
        print('Step 1 is failed for '+str(i[0]))
        list_failed_file.append(i[0])
        
  
    for j in liststepresults2: # to check whether proper content type is recieved or not for all documents
      if(j[1] == 'Passed'):
        print('Step 2 is passed for '+str(j[0]))
        continue
      else:
        print('Step 2 is failed for '+str(j[0]))
        list_failed_file.append(j[0])
    

          
  except Exception as e:
        print("Error while executing test case")
  finally:
    if len(list_failed_file) == 0: # to check whether do we have any failed to generate document
      return True
    else:
      print("These documents are failed to generate"+str(list_failed_file)) # print failed documents list
      return False

def test_docsvc():
  assert doc_svc() is True
