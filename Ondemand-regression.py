import requests
import json
from os import listdir
from os.path import isfile, join
import unittest
import os


# API Proxy details
base_url = 'http://correspondence.service.qa.corvesta.net/correspondence/reports'

# Variables
headers_json = {"keyspring.client.id":'DDVA',"keyspring.tenant.id":'DDVA','content-Type':'application/json'}
file_path = os.getcwd()+'\\Ondemand_jsonpayload\\'
liststepresults1 = []
liststepresults2 = []
list_failed_file = []

#List for  validating of each of request response
content_type_list=['application/pdf','application/vnd.ms-excel','text/plain']

# to get all the files in the folder
onlyfiles = [f for f in listdir(file_path) if isfile(join(file_path, f))]


def ondemand_testing():
  try:
    for i in onlyfiles:
      filename=file_path+i
      with open(filename, 'r') as filehandle:
        filecontent = filehandle.read()
        strResponse = requests.post(base_url, data=filecontent, headers=headers_json,stream=True)
        if strResponse.status_code == 200:
          liststepresults1.append([i,"Passed"])
          if strResponse.headers['Content-Type'] in content_type_list:
            liststepresults2.append([i,"Passed"])
          else:
            liststepresults2.append([i,"Failed"])
        else:
          liststepresults1.append([i,"Failed",strResponse.status_code])

    for i in liststepresults1: # to check whether status code 200 is recieved or not for all documents
      if(i[1] == 'Passed'):
        print('Step1 passed - 200 OK for API request is recieved '+str(i[0]))
        continue
      else:
        print('Step1 failed - '+str(i[2])+' response code recieved for API request instead of 200 for  '+str(i[0]))
        list_failed_file.append(i[0])
        
  
    for j in liststepresults2: # to check whether proper content type is recieved or not for all documents
      if(j[1] == 'Passed'):
        print('Step2 is passed - Recieved Appropriate Content-Type '+str(j[0]))
        continue
      else:
        print('Step2 failed - Received inappropriate Content-Type '+str(j[0]))
        list_failed_file.append(j[0])
    

          
  except Exception as e:
        print("Error while executing test case")
  finally:
    if len(list_failed_file) == 0: # to check whether do we have any failed to generate document
      print("All documents are generated sucessfully") 
      return True
    else:
      print("These documents are failed to generate "+str(list_failed_file)) # print failed documents list
      return False

def test_ondemand():
  assert ondemand_testing() is True
