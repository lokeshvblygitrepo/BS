import re
import DataFunctions
import DataCreationFunctions
import HEMemberFunctions
import SearchFunctions
import HelperFunctions
import HEAccountFunctions
import CollectExecutionInfo as cei
import requests
import string
import random


Project.Variables.execution_results={}
Project.Variables.start_time = str(aqDateTime.Now())

@beforescenario
def before_test(scenario):
  # Perform some action before running a scenario, for example:
  Log.Message("Before running the " + scenario.Name + "scenario")
  
  #get Jira ticket from scenario.Name
  filter = re.compile("\((.+)\)")
  content = filter.search(scenario.Name)
  test_id = content.group(1)
  Project.Variables.test_case_id = test_id  
  
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
  Log.Message(str(Project.Variables.execution_results))
  
@beforefeature
def someFunc(feature):
  # Perform some action before running a feature file, for example:
  Log.Message("Before running the " + feature.Name + " feature file")
  filter = re.compile("\(Test Plan:(.+)\)")
  if 'Single Account' not in feature.Name: # selecting table to run tests with 2 account types
    Project.Variables.test_data_table = Project.Variables.test_data_table.replace('_2','')
  content = filter.search(feature.Name)
  test_plan_id = content.group(1)  
  Project.Variables.dict_info['description'] += '%s\n' % test_plan_id
  query = "SELECT * FROM %s where bill_id is null order by id asc" % (Project.Variables.test_data_table)
#  query = "SELECT * FROM %s where id>20 order by id asc" % (TABLE)
  test_data = DataFunctions.executeQueryQADB(query, True)
  
  for test_dta in test_data:
    test_case_id = test_dta.test_case_id
    account_type = test_dta.account_type
    age_category = test_dta.age_category
    handicapped = test_dta.handicapped
    correspondence_definition = test_dta.correspondence_definition
    resp_party_email = test_dta.resp_party_email
    resp_party = test_dta.responsibile_party
    member_delivery_preference = test_dta.member_delivery_preference
    subscriber_id = test_dta.subscriber_id
    
    Project.Variables.test_case_id = test_case_id
    
   # Query to get the account id and benefit plan associated with account  
    if account_type == 'ACA Exchange Individual':
      account_name = Project.Variables.account_aca_exchange_indiv
    elif account_type == "Non-Exchange Individual":
      account_name = Project.Variables.account_non_exchange_indiv
    
    query ="select ac.ACCOUNT_HCC_ID,bp.benefit_plan_name,ac.account_name from payor_dw.account ac "
    query += "join PAYOR_DW.ACCOUNT_PLAN_SELECT_FACT ap "
    query += "on ap.account_key=ac.account_key "
    query += "join PAYOR_DW.BENEFIT_PLAN bp "
    query += "on bp.benefit_plan_key=ap.benefit_plan_key "
    query += "where ac.account_name ='{}' and ac.ACCOUNT_LEVEL='2' fetch next 1 row only".format(account_name)
    records = DataFunctions.getDataDW('test',query) 
    for ac in records:
      account_id = ac[0]
      benefit_plan = ac[1]
      account_name = ac[2]
      
    query = "select subscriber_id from %s "  % (Project.Variables.test_data_table)
    test_data = DataFunctions.executeQueryQADB(query, True) 
    lst_subr = []
    for data in test_data:
      if 'None' not in str(data):
        lst_subr.append(data[0])
    subscription = ''
  # DW Query to find the member with matching conditions
    query = HelperFunctions.query_builder(account_type,age_category,handicapped,member_delivery_preference,resp_party,resp_party_email,lst_subr)
    records = DataFunctions.getDataDW('test',query) 
    for ac in records:
        subscription = ac[0]
        account_id = ac[1]
        benefit_plan = ac[2]
        account_name = ac[3]
    
    # If no data found, create a new subscriber and configure the subscriber
    if subscription == '':
      subscription = configure_member(account_id,benefit_plan,age_category,True,member_delivery_preference,resp_party_email,handicapped,resp_party)
    query = "UPDATE %s SET subscriber_id='%s',account_id='%s',account_name='%s' where test_case_id='%s' and account_type = '%s'" % (Project.Variables.test_data_table,subscription,account_id,account_name,test_case_id,account_type)
    DataFunctions.executeQueryQADB(query, False)

    # Running bill from HE
    bill_number = run_bill(subscription)
    if test_case_id not in('KSQA-396','KSQA-397','KSQA-398'):
      query = "UPDATE %s SET bill_id='%s' where test_case_id='%s' and account_type = '%s'" % (Project.Variables.test_data_table,bill_number,test_case_id,account_type)
      DataFunctions.executeQueryQADB(query, False)
     
    # Applying adjustments and payments 
    if test_case_id in('KSQA-396','KSQA-397','KSQA-398'):
      if test_case_id == 'KSQA-396':
        coverage_date = aqConvert.DateTimeToFormatStr(aqDateTime.Now(), "%m/%d/%Y")
        HEAccountFunctions.create_billing_adjustment(benefit_plan = benefit_plan,billing_category='Premium',coverage_date=coverage_date,adjustment_amount='150', adjustment_type='Customer Refund',comment='Automation Test')
      if test_case_id == 'KSQA-397':
        payment_number = str(random.randint(1000000, 9999999))
        receipt_date = payment_date = aqConvert.DateTimeToFormatStr(aqDateTime.Now(), "%m/%d/%Y")
        payment_amount = '45'
        payment_type = 'Check'
        HEAccountFunctions.post_payment_allocation(payment_number,payment_date,receipt_date,payment_amount,payment_type)
      if test_case_id == 'KSQA-398':
        HEAccountFunctions.create_billing_adjustment(benefit_plan = benefit_plan,billing_category='Premium',coverage_date=coverage_date,adjustment_amount='150', adjustment_type='Customer Refund',comment='Automation Test')
        payment_number = str(random.randint(1000000, 9999999))
        receipt_date = payment_date = aqConvert.DateTimeToFormatStr(aqDateTime.Now(), "%m/%d/%Y")
        payment_amount = '45'
        payment_type = 'Check'
        HEAccountFunctions.post_payment_allocation(payment_number,payment_date,receipt_date,payment_amount,payment_type)
      bill_number = run_bill(subscription)
      query = "UPDATE %s SET bill_id='%s' where test_case_id='%s' and account_type = '%s'" % (Project.Variables.test_data_table,bill_number,test_case_id,account_type)
      DataFunctions.executeQueryQADB(query, False)
    
def clean_test_data():
  query = "UPDATE correspondence.tbl_individual_bill_test_data SET account_id=null,subscriber_id=null,bill_id=null,batch_run_id=null,job_run_date=null,account_name=null"
  DataFunctions.executeQueryQADB(query, False)
  query = "UPDATE correspondence.tbl_individual_bill_test_data_2 SET account_id=null,subscriber_id=null,bill_id=null,batch_run_id=null,job_run_date=null,account_name=null"
  DataFunctions.executeQueryQADB(query, False)
  
def configure_member(account_id,benefit_plan,age_category,is_email,member_delivery_preference,resp_party_email,handicapped,responsile_party):
  current_year = aqDateTime.GetYear(aqDateTime.Now())
  if age_category == 'child':
    birth_date = '01/01/{}'.format(int(current_year)-8)
  else:
    birth_date = '01/01/{}'.format(int(current_year)-23)
  if handicapped =='handicapped':
    is_handicapped = True
  else:
    is_handicapped = False
  subscription = DataCreationFunctions.createSubscriptionUpdated(account_id,benefit_plan,'01/01/{}'.format(current_year), birth_date,Project.Variables.client_id,is_email,'',isHandicap=is_handicapped)
  subscriber = subscription +'-01'
  if member_delivery_preference.lower() != 'nothing':
    HEMemberFunctions.update_member_doc_delivery(subscriber,member_delivery_preference)
  if responsile_party!='':
    if resp_party_email =='with':
      email = 'mail'+''.join(random.choices(string.ascii_letters, k=7))+'@automationtest.com'
    else:
      email=''
    address = address = {'address1_value': "5515 Airport Road", 'city': "Roanoke", 'state': "Virginia",'country':'UNITED STATES','zip':"24019"}
    first_name ='First'+ ''.join(random.choices(string.ascii_letters, k=7))
    last_name ='Last'+ ''.join(random.choices(string.ascii_letters, k=7))
    HEMemberFunctions.enter_personal_representative_details('Legal Guardian',subscriber,first_name,last_name,address,email=email)
  return subscription
  
  
def run_bill(subscription_id):
  subscription =  HEMemberFunctions.get_subscription()
  if subscription!=None:
    selected_subr =subscription["subscription id"] 
  else:
    selected_subr=''
  if selected_subr!=subscription_id:
    SearchFunctions.searchTask('Manager',"Members","subscription", [{"name":"Member ID", "value":subscription_id+'-01' }],True)
  query = "select max(b.BILL_PERIOD_TO) from PAYOR_DW.BILLING b where b.SUBSCRIPTION_HCC_ID='{}' ".format(subscription_id)
  records = DataFunctions.getDataDW('test',query)
  
  for dt in records:
    latest_date=dt[0]
  if latest_date!=None:
    due_date = aqDateTime.AddMonths(latest_date,1)
    run_date_temp = latest_date
  else:
    run_date_mth = aqDateTime.GetMonth( aqConvert.DateTimeToFormatStr(aqDateTime.Now(), "%m/%d/%Y"))
    run_date_year = aqDateTime.GetYear(aqConvert.DateTimeToFormatStr(aqDateTime.Now(), "%m/%d/%Y"))
    mm= run_date_mth+1
    if mm>12:
      mm=1
      run_date_year = run_date_year+1
    run_date_temp = aqConvert.StrToDate(str("{:02d}".format(mm))+'/01/'+str(run_date_year))
    due_date = aqDateTime.AddMonths(run_date_temp,1)
  due_date = aqConvert.DateTimeToFormatStr(due_date, "%m/%d/%Y")
  run_date = aqConvert.DateTimeToFormatStr(HelperFunctions.get_nth_buisiness_day(aqConvert.DateTimeToFormatStr(run_date_temp, "%m/%d/%Y"),7),"%m/%d/%Y")
  bill_details = HEAccountFunctions.run_bill(due_date, run_date, subscription_id)
  # Checking Bill is created successfully in correspondence bill_run_event table
  query = "select * from reports.bill_run_event br where br.bill_id='{}'".format(str(bill_details['bill_number']).replace('.0',''))
  query+= " and br.account_id='{}'".format(subscription_id+'-01')
  for itr in range(40):
    data_record = DataFunctions.executeQueryPostgresql('{client_id}.db.{env}.corvesta.net'.format(client_id = Project.Variables.client_id.lower(),env=Project.Variables.env) ,'5432','correspondence',Project.Variables.keyspring_db_user_name,Project.Variables.keyspring_db_pwd,query, True)
    if len(data_record)!=0:
      Log.Message("Succsessfully created a bill")
      break
    else:
      aqUtils.Delay(10000)
  return str(bill_details['bill_number']).replace('.0','')
  

  
  
def create_sbscriptions():
  for ct in range(0,10):
    query = "SELECT * FROM %s order by id desc" % (Project.Variables.test_data_table)
  #  query = "SELECT * FROM %s where id>20 order by id asc" % (TABLE)
    test_data = DataFunctions.executeQueryQADB(query, True)
  
    for test_dta in test_data:
      test_case_id = test_dta.test_case_id
      account_type = test_dta.account_type
      age_category = test_dta.age_category
      handicapped = test_dta.handicapped
      correspondence_definition = test_dta.correspondence_definition
      resp_party_email = test_dta.resp_party_email
      resp_party = test_dta.responsibile_party
      member_delivery_preference = test_dta.member_delivery_preference
      subscriber_id = test_dta.subscriber_id
    
     # Query to get the account id and benefit plan associated with account  
      if account_type == 'ACA Exchange Individual':
        account_name = Project.Variables.account_aca_exchange_indiv
      elif account_type == "Non-Exchange Individual":
        account_name = Project.Variables.account_non_exchange_indiv
    
      query ="select ac.ACCOUNT_HCC_ID,bp.benefit_plan_name,ac.account_name from payor_dw.account ac "
      query += "join PAYOR_DW.ACCOUNT_PLAN_SELECT_FACT ap "
      query += "on ap.account_key=ac.account_key "
      query += "join PAYOR_DW.BENEFIT_PLAN bp "
      query += "on bp.benefit_plan_key=ap.benefit_plan_key "
      query += "where ac.account_name ='{}' and ac.ACCOUNT_LEVEL='2' fetch next 1 row only".format(account_name)
      records = DataFunctions.getDataDW('test',query) 
      for ac in records:
        account_id = ac[0]
        benefit_plan = ac[1]
        account_name = ac[2]
      subscription = ''
    
      # If no data found, create a new subscriber and configure the subscriber
      if subscription == '':
        subscription = configure_member(account_id,benefit_plan,age_category,True,member_delivery_preference,resp_party_email,handicapped,resp_party)