import json
import base64
from datetime import datetime, timezone, timedelta

def collect_start_info():
  dict_info = {}
  dict_info.update({"summary":"Individual Risk Bill Regression Tests Execution"})
  dict_info.update({"description": "This execution was automatically created when importing execution results from TestComplete run for the following regression test plan:\n"})
  dict_info.update({"project": "KSQA"})
  dict_info.update({"startDate":get_now()})
  dict_info.update({"finishDate":""})
  
  Project.Variables.dict_info = dict_info
  Project.Variables.list_tests = []

def collect_finish_info():
  Project.Variables.dict_info.update({"finishDate":get_now()})
  
  
def generate_payload_file():
  dict = {"info":Project.Variables.dict_info}
  dict.update({"tests":Project.Variables.list_tests})
  
  jsonString = json.dumps(dict, indent=4)
  jsonFile = open("payload.json", "w")
  jsonFile.write(jsonString)
  jsonFile.close()
  
def get_now():
  tzinfo = datetime.now(timezone.utc).astimezone().tzinfo
  return datetime.now(tzinfo).isoformat(sep='T',timespec='seconds')
  
def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')
        
def get_evidences(test_id):
  list_evidence = []
  
  folder = "Failure\\"+test_id
  folder_info = aqFileSystem.GetFolderInfo(folder)
  
  files = folder_info.Files

  while files.HasNext():
    dict_evidence = {}
    file = files.Next()
    dict_evidence.update({"filename":file.Name})
    dict_evidence.update({"contentType":"image/jpeg"})
    dict_evidence.update({"data":get_base64_encoded_image('%s\\%s' % (folder,file.Name))})
    
    list_evidence.append(dict_evidence)
    
  return list_evidence
    

def add_failure_evident_OnLogError(Sender, LogParams):
  try:
    folder = 'Failure\\%s' % Project.Variables.test_case_id #Project.Variables.dict_test['testKey']

    if not aqFileSystem.Exists(folder):
      aqFileSystem.CreateFolder(folder)
  
    Sys.Desktop.Picture().SaveToFile('%s\\%s.jpg' % (folder,str(get_now()).replace(":","")))
    
  except Exception as e:
    pass