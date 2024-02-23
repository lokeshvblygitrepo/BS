import re
import DataCreationFunctions
import DW_Helper_Functions
import HE_Helper_Functions
import CreateClaim
import DataFunctions
import Collect_Execution_Info as cei
import requests
from ks_web_service.benefits_plan_service import BenifitPlanService

Project.Variables.execution_results={}
Project.Variables.start_time = str(aqDateTime.Now())

TABLE = Project.Variables.test_data_table
ACCOUNT_NAME = 'KS AUTOMATION FOR CORRESPONDENCE'

@beforefeature
def someFunc(feature):
  # Perform some action before running a feature file, for example:
  Log.Message("Before running the " + feature.Name + "feature file")
  filter = re.compile("\(Test Plan:(.+)\)")
  
  content = filter.search(feature.Name)
  test_plan_id = content.group(1)
  
  Project.Variables.dict_info['description'] += '%s\n' % test_plan_id
  
  if 'subscribers' in feature.Name:
    test_type = 'subscriber'
  elif 'suppliers' in feature.Name:
    test_type = 'supplier'
    
  query = "SELECT * FROM %s WHERE claim_id is null and test_type = '%s' ORDER BY id" % (TABLE, test_type)
    
  data_record = DataFunctions.executeQueryQADB(query,True)
  
  for i in data_record:
    id = i.id
    test_type = i.test_type
    test_case_id = i.test_case_id
    payment_type = i.payment_type
    payment = i.payment
    email = i.email
    
    is_retry = True
    while is_retry:
      #get test data - member
      if test_type == 'subscriber':
        member_detail = get_member(True,payment_type,email)
      elif test_type == 'supplier':
        member_detail = get_member(False)
    
      #get provider data - supplier npi and practitioner npi
      if test_type == 'subscriber':
        list_provider_details = get_supplier(False)
      elif test_type == 'supplier':
        list_provider_details = get_supplier(True,payment_type,email)
    
      service_date = aqConvert.DateTimeToFormatStr(aqDateTime.Today(), "%m/%d/%Y")
               
      transaction = "1 - Statement Of Actual Services"
      
      if test_type == "subscriber":
        submitter="Member"
      elif test_type == "supplier":
        submitter="Provider"
      
      for index in range(20): 
        if payment.lower() == 'some':
          fee = '500'
        else:
          fee = '0'
          
#        member_detail = list_member_details[index]
#        type = member_detail['type']
#        if type == 'BLS-Limit Cleanings':
#          list_services=[{'proc_date':service_date,'pos':'11','proc_code':'D1110','fee':fee}] 
#        
#        elif type == 'BLS-Limit AllExams':
#          list_services=[{'proc_date':service_date,'pos':'11','proc_code':'D0140','fee':fee}] 
#          
#        elif type == 'BLS-Limit Crwns':
#          list_services=[{'proc_date':service_date,'pos':'11','tooth_numbers':'13','proc_code':'D2750','fee':fee}]
#          
#        elif type =='BLS-Limit FMPAXrays':
#          list_services=[{'proc_date':service_date,'pos':'11','proc_code':'D0210','fee':fee}]
#          
#        elif type == 'BLS- Limit SurgPlcImplnt':
#          list_services=[{'proc_date':service_date,'pos':'11','tooth_numbers':'13','proc_code':'D6010','fee':fee}] 
        code = member_detail['type']  
        if code in  ['D1110', 'D0140', 'D0210']:
          list_services=[{'proc_date':service_date,'pos':'11','proc_code':code,'fee':fee}] 
        
        elif code in [ 'D2750','D6010']:          
          list_services=[{'proc_date':service_date,'pos':'11','tooth_numbers':'13','proc_code':code,'fee':fee}]

        claim_id = CreateClaim.create_claim(submitter,transaction,member_detail['member_id'],list_provider_details[index],list_services)
        
        is_wait = True
        while is_wait:
          claim_status = get_claim_status(claim_id)
          if claim_status != "":
            is_wait = False
            break
          aqUtils.Delay(5000)
         
        if claim_status == 'Final':
          #proceed to save data into the test data table
          member_id = member_detail['member_id']
          provider_details = list_provider_details[index]
          query = "UPDATE %s SET member_id='%s', supplier_npi='%s', supplier_hcc_id='%s', practitioner_npi='%s', claim_id='%s',claim_status='%s' WHERE id=%s"  % (TABLE,member_id,provider_details['supplier_npi'],provider_details['supplier_hcc_id'],provider_details['practitioner_hcc_id'],claim_id,claim_status,id)
          data_record = DataFunctions.executeQueryQADB(query,False)
        
          is_retry = False
          break
        else:
          Log.Message('The claim %s was created for the test case %s, however it is in %s' % (claim_id, test_case_id,claim_status))


@beforescenario
def before_test(scenario):
  # Perform some action before running a scenario, for example:
  Log.Message("Before running the " + scenario.Name + "scenario")
  
  #get Jira ticket from scenario.Name
  filter = re.compile("\((.+)\)")
  content = filter.search(scenario.Name)
  test_id = content.group(1)
  
  Project.Variables.test_case_id=test_id   
  
  #update the test id in dict_test
  dict_test = {}
  dict_test.update({"testKey": test_id})
  dict_test.update({"start":cei.get_now()})
  
  Project.Variables.dict_test = dict_test
  
  Project.Variables.current_errors_cnt = Log.ErrCount
  
@afterscenario
def after_test(scenario):
  Project.Variables.dict_test.update({"finish":cei.get_now()})

  if Log.ErrCount > Project.Variables.current_errors_cnt:
    Project.Variables.dict_test.update({"status":"FAILED"})
    Project.Variables.execution_results.update({Project.Variables.test_case_id:'FAILED'+':'+scenario.name.split('(')[0]})
    #adding evidences
    list_evidences = cei.get_evidences(Project.Variables.dict_test['testKey'])
    Project.Variables.dict_test.update({"evidences":list_evidences})
    
  else:
    Project.Variables.dict_test.update({"status":"PASSED"})
    Project.Variables.execution_results.update({Project.Variables.test_case_id:'PASSED'+':'+scenario.name.split('(')[0]})
    
  Project.Variables.list_tests.append(Project.Variables.dict_test)
  
def get_available_service2(member_id,lstServices):
  for service in lstServices:
    is_to_use = is_eligible(service,'9999002',member_id)
    if is_to_use:
      return service
      
  return None
      
def get_member(is_test, payment_type='', email=''):
  
  #get the currently used members for the tests
  if is_test:
    query = "SELECT * FROM %s WHERE test_type='subscriber' and member_id is not null " % TABLE
    data_record = DataFunctions.executeQueryQADB(query, True)
    
    list_subr = []
    for i in data_record:
      list_subr.append(i.member_id.split('-')[0])

    list_member_id = DW_Helper_Functions.get_member(is_test,ACCOUNT_NAME,payment_type,email, list_subr)

  else:
    list_member_id = DW_Helper_Functions.get_member(is_test,ACCOUNT_NAME)
    
  service = None
  is_found = False
#  lstServices = ['BLS-Limit AllExams','BLS-Limit Crwns'] #'BLS- Limit SurgPlcImplnt', 
  lstServices = ['D1110', 'D0140', 'D2750', 'D0210','D6010']
  
  for member_id in list_member_id:
    service = get_available_service2(member_id, lstServices)
    
    if service is not None:
      break
  
  if service is None:   
    member_creation(is_test,payment_type,email)  #time to call function create new subscriber
    
  else:    
    return {'member_id':member_id, 'type':service}
  
def member_creation(is_test, payment_type='', email=''):
  is_member_found = False
  while not is_member_found:
    for itr in range(0,1):
      DataCreationFunctions.createSubscriptionUpdated('00000009999-0000000001','KS AUTOMATION BP/BASIC','01/01/2022',True,'ACH') #With email payment ACH
#      DataCreationFunctions.createSubscriptionUpdated('00000009999-0000000001','KS AUTOMATION BP/BASIC','01/01/2022',False,'Check')#W/o email payment check
#      DataCreationFunctions.createSubscriptionUpdated('00000009999-0000000001','KS AUTOMATION BP/BASIC','01/01/2022',True,'Check') #With email payment check
#      DataCreationFunctions.createSubscriptionUpdated('00000009999-0000000001','KS AUTOMATION BP/BASIC','01/01/2022',False,'ACH')#W/o email payment ACH
    if is_test:
      list_member_id = DW_Helper_Functions.get_member(is_test,ACCOUNT_NAME,payment_type,email, list_subr)
    else:    
      list_member_id = DW_Helper_Functions.get_member(is_test,ACCOUNT_NAME)
    lstServices = ['D1110', 'D0140', 'D2750', 'D0210','D6010']
    if list_member_id:
      for member_id in list_member_id:
        service = get_available_service2(member_id, lstServices)    
        if service is not None:
          is_member_found = True
          break  
      if service is None:   
        continue    
      else:    
        return {'member_id':member_id, 'type':service}
    else:
      continue
    
    


def get_supplier(is_test, payment_type='', email=''):
    
  #get the currently used suppliers for the tests
  if is_test:
    query = "SELECT * FROM %s WHERE test_type='supplier' and supplier_hcc_id is not null " % TABLE
    data_record = DataFunctions.executeQueryQADB(query, True)
      
    list_supplier = []
    for i in data_record:
      list_supplier.append(i.supplier_hcc_id)
  
    supplier_details = DW_Helper_Functions.get_supplier(is_test,payment_type,email, list_supplier)
  
  else:
    supplier_details = DW_Helper_Functions.get_supplier(is_test)
        
  return supplier_details      
          
def get_claim_status(claim_id):
  
  query = "select c.CLAIM_STATUS from PAYOR_DW.CLAIMS c where c.CLAIM_HCC_ID='{claim_hcc_id}'".format(claim_hcc_id = claim_id)
  records = DataFunctions.getDataDW(Project.Variables.env,query)
  claim_status=''
  for itr in records:
    claim_status = itr[0]
    
  return claim_status
  
def clean_test_data(test_type):
  query = "UPDATE %s SET member_id=null, supplier_npi=null,supplier_hcc_id=null,practitioner_npi=null, claim_id=null,claim_status=null,batch_run_id=null,transaction_number=null,job_run_date=null where test_type='%s'" % (TABLE,test_type)
  DataFunctions.executeQueryQADB(query, False)
  
def reset_run_status():
  Project.Variables.subscriber_payment_run = False
  Project.Variables.supplier_payment_run = False

#def test():
#  import ks_web_service
#  from ks_web_service import benefits_plan_service as bps
#  
#  x=bps.BenifitPlanService('DDVA','DDVA','test')
#  y=x.get_benefits_service_code_details('D0140','9999002','51000000009428-01')
#  x=1
#  

  
def is_eligible(strService, strBPId, strMemberId):
  bps = BenifitPlanService(Project.Variables.client_id,Project.Variables.tenant_id,Project.Variables.ws_env)
  response = bps.get_benefits_service_code_details(strService,strBPId,strMemberId)
  strDate = response.json()['serviceCodeNetworks'][0]['nextEligible']
  if strDate == None:
    return False
  dateDate = aqConvert.StrToDate(strDate.replace('-','/'))
  
  if dateDate <= aqDateTime.Today():
    return True
  else:
    return False

def test_get_member():
  x = get_member(True,'ACH','null')
  Log.Message(str(x))
  
  x = get_member(True,'ACH','not null')
  Log.Message(str(x))
  
  x = get_member(True,'Check','null')
  Log.Message(str(x))
  
  x = get_member(True,'Check','not null')
  Log.Message(str(x))