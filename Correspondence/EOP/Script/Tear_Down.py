import requests
import json
import DataFunctions
import EmailExecutionResults

def return_to_jira():
  #get token
  headers = {"Accept": "application/json"}
  url_auth = "https://xray.cloud.getxray.app/api/v2/authenticate"
  response = requests.request(
     "POST",
     url_auth,
     headers=headers,
     data = { "client_id": Project.Variables.jira_client_id,"client_secret": Project.Variables.jira_client_secret}
  )

  token = json.loads(response.text)

  url = "https://xray.cloud.getxray.app/api/v2/import/execution"

  headers = {
    "Accept": "application/json",
  'Content-Type' : 'application/json',
  "Authorization":"Bearer %s" % token
  }

  contents = open('payload.json', 'rb').read()

  response = requests.request(
     "POST",
     url,
     headers=headers,
      data = contents
  )

  Log.Message(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
  
def delete_failure_folder():
  folder = 'Failure'
  if aqFileSystem.Exists(folder):
    aqFileSystem.DeleteFolder(folder,True)
    
def close_browser():
  while Sys.WaitChild('''Browser("%s")''' % Project.Variables.required_browser,1000).Exists:
    Sys.Browser(Project.Variables.required_browser).Close()
    
def clean_test_data():
  query = "UPDATE %s SET member_id=null, supplier_npi=null,supplier_hcc_id=null,practitioner_npi=null, claim_id=null,claim_status=null,batch_run_id=null,transaction_number=null,job_run_date=null " % (Project.Variables.test_data_table)
  DataFunctions.executeQueryQADB(query, False)
  
def reset_run_status():
  Project.Variables.subscriber_payment_run = False
  Project.Variables.supplier_payment_run = False
  
def email_execution_results():
  exec_result = 'PASSED'
  for res in Project.Variables.execution_results.values():
    if 'failed' in res.lower():
      exec_result = 'FAILED'
      break
  from_email = "noreply@corvesta.com"
  to_email = "AutomationSolutionsTeam@northwindstech.com"

  EmailExecutionResults.email_execution_result(from_email, to_email, 'Correspondence-EOP', exec_result, Project.Variables.client_id, Project.Variables.env,Project.Variables.start_time,test_report = Project.Variables.execution_results)