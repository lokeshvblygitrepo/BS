import DataFunctions
import SearchFunctions
import HEAccountFunctions
import HEMemberFunctions
import CommonFunctions
import DataCreationFunctions
import HelperFunctions
from HelperFunctions import CheckDigitCalculation
from BillsPage import Bills_Page
from CorrespondencePortalFunctions import Home_Page
import LoginPage
import random
import re

@when("I Generate {arg}")
def step_impl(param1):
  if Project.Variables.generate_indiv_risk_bills == False:
    LoginPage.login()  
    bills_page = Bills_Page()
    bills_page.generate_bills('Individual Group Risk',['{} Individual Group Risk'.format(Project.Variables.client_id.upper())])
    Project.Variables.generate_indiv_risk_bills = True

@then("batch status should be {arg}")
def step_impl(param1):
  LoginPage.login()
  query = "SELECT * FROM %s where test_case_id='%s' and account_type='%s'" % (Project.Variables.test_data_table,Project.Variables.test_case_id,Project.Variables.account_type)
  test_data = DataFunctions.executeQueryQADB(query, True)
  
  for test_dta in test_data:
    bill_id = test_dta.bill_id
    
  query = "select batch_run_id from reports.bill_run_event br where br.bill_id='{}'".format(bill_id)
  for itr in range(15):
    data_record = DataFunctions.executeQueryPostgresql('{client_id}.db.{env}.corvesta.net'.format(client_id = Project.Variables.client_id.lower(),env=Project.Variables.env) ,'5432','correspondence',Project.Variables.keyspring_db_user_name,Project.Variables.keyspring_db_pwd,query, True)
    
    if len(data_record)!=0 and 'None' not in str(data_record):
      for dta in data_record:
        batch_run_id = dta[0]
        break
    else:
      aqUtils.Delay(30000)
  Project.Variables.batch_run_id = batch_run_id
  job_run_date = aqConvert.DateTimeToFormatStr(aqDateTime.Now(), "%m/%d/%Y")
  query = "UPDATE %s SET batch_run_id='%s',job_run_date='%s'" % (Project.Variables.test_data_table,batch_run_id,job_run_date)
  DataFunctions.executeQueryQADB(query, False)
  query = "select create_date from reports.bill_run_event br where br.bill_id='{}'".format(bill_id)
  data_record = DataFunctions.executeQueryPostgresql('{client_id}.db.{env}.corvesta.net'.format(client_id = Project.Variables.client_id.lower(),env=Project.Variables.env) ,'5432','correspondence',Project.Variables.keyspring_db_user_name,Project.Variables.keyspring_db_pwd,query, True)
  for dta in data_record:
    start_date = aqConvert.DateTimeToFormatStr(dta[0], "%m/%d/%Y")
  end_date = aqConvert.DateTimeToFormatStr(aqDateTime.Now(), "%m/%d/%Y")
  home_page = Home_Page()
  home_page.navigate_to_home()
  job_info = home_page.get_job_info(batch_run_id)
  assert 'COMPLETED' in job_info['Batch Status']
  
@then("I download the pdf document")
def step_impl():
  LoginPage.login()
  query = "SELECT * FROM %s where test_case_id='%s' and account_type='%s'" % (Project.Variables.test_data_table,Project.Variables.test_case_id,Project.Variables.account_type)
  test_data = DataFunctions.executeQueryQADB(query, True)  
  for test_dta in test_data:
    subscriber_id = test_dta.subscriber_id
    batch_run_id = test_dta.batch_run_id
    bill_id = test_dta.bill_id
  home_page = Home_Page()
  home_page.get_pdf(batch_run_id,bill_id)

@then("the document delivery type is {arg}")
def step_impl(param1):
   home_page = Home_Page()
   query = "SELECT * FROM %s where test_case_id='%s' and account_type='%s'" % (Project.Variables.test_data_table,Project.Variables.test_case_id,Project.Variables.account_type)
   test_data = DataFunctions.executeQueryQADB(query, True)  
   for test_dta in test_data:
      subscriber_id = test_dta.subscriber_id
      bill_number = test_dta.bill_id
   delivery_preference = home_page.get_delivery_preference(bill_number)
   assert param1 == delivery_preference

@then("the data in pdf and xlsx documents matches with data in HE")
def step_impl():
   query = "SELECT * FROM %s where test_case_id='%s' and account_type='%s'" % (Project.Variables.test_data_table,Project.Variables.test_case_id,Project.Variables.account_type)
   test_data = DataFunctions.executeQueryQADB(query, True)  
   for test_dta in test_data:
      subscriber_id = test_dta.subscriber_id
      bill_number = test_dta.bill_id
   SearchFunctions.searchTask('Manager',"Members","subscription", [{"name":"Member ID", "value":subscriber_id+'-01' }],True)
   account_number = HEMemberFunctions.get_account_number().split('-')[0]
   Project.Variables.account_number = account_number
   file_path = Project.Variables.file_path + 'individual_risk_bill_'+account_number+'_'+bill_number+'.pdf'
#   file_path = 'C:\\Automation\\Downloads\\individual_risk_bill_00000009996_312927'+'.pdf'
   pdf_content = CommonFunctions.read_PDF(file_path,0)
   top_right = HelperFunctions.get_data_from_pdf(pdf_content,'top_right')
   all_bill_details = HEAccountFunctions.get_bills()
   bill_detail = next(iter(item for item in all_bill_details if item['Bill Number'] == str(int(bill_number))), None)
   subscription = HEMemberFunctions.get_subscription()
   
   # PDF data validation
   assert bill_detail['Bill Number'] == top_right['Bill Number']
   assert aqConvert.DateTimeToFormatStr(bill_detail['Billing Date'], "%m/%d/%Y") == top_right['Eligibility as of']
   assert aqConvert.DateTimeToFormatStr(bill_detail['Due Date'], "%m/%d/%Y") == top_right['Due Date']
   assert subscription['subscription id'] == top_right['Subscription ID']
   assert top_right['Account Number'] == account_number
   
   billing_summary = HelperFunctions.get_data_from_pdf(pdf_content,'billing_summary')
   if ',' in billing_summary['Balance Forward']:
    balance_fwd = billing_summary['Balance Forward'].replace(',','')
   else:
    balance_fwd = billing_summary['Balance Forward']
   assert balance_fwd =='$'+str( '{0:.2f}'.format(float(bill_detail['Balance Forward'])))
   assert billing_summary['Current Charges'] == '$'+str( '{0:.2f}'.format(float(bill_detail['New Charges']))) 
   assert billing_summary['Manual Adjustments'] == '$'+str( '{0:.2f}'.format(float(bill_detail['Adjustments']))) 
   if ',' in billing_summary['Balance Forward']:
    tot_amt_due = billing_summary['Total Amount Due'] .replace(',','')
   else:
    tot_amt_due = billing_summary['Total Amount Due'] 
   assert tot_amt_due == '$'+str( '{0:.2f}'.format(float(bill_detail['Amount Due']))) 
   
   top_right_info_with_payment = HelperFunctions.get_data_from_pdf(pdf_content,'top_right_info_with_payment')
   assert bill_detail['Bill Number'] == top_right_info_with_payment['Bill Number']
   assert aqConvert.DateTimeToFormatStr(bill_detail['Billing Date'], "%m/%d/%Y") == top_right_info_with_payment['Eligibility as of']
   assert aqConvert.DateTimeToFormatStr(bill_detail['Due Date'], "%m/%d/%Y") == top_right_info_with_payment['Due Date']
   assert subscription['subscription id'] == top_right_info_with_payment['Subscription ID']
   assert top_right_info_with_payment['Account Number'] == account_number
   
   # Check number validation
   pattern =r'\b\d{31}\b'
   matches = re.findall(pattern, pdf_content)  
   if matches:
       check_no = matches[0]
   
   due_date = top_right_info_with_payment['Due Date'].split('/')
   chk_date = due_date[2]+due_date[0]+due_date[1]  
   chk_dig_calc = CheckDigitCalculation()
   chk_due_amt = str(round(float(tot_amt_due.replace('$',''))))
   if len(chk_due_amt)<4:
    chk_dgt_1 = str(chk_dig_calc.calculate_check_digit(subscriber_id))+'00'
   else:
     chk_dgt_1 = str(chk_dig_calc.calculate_check_digit(subscriber_id))+'0'
   chk_dgt_2 = '00'+str(chk_dig_calc.calculate_check_digit(chk_date+subscriber_id+chk_dgt_1+chk_due_amt))
   chk_digit = chk_date+subscriber_id+chk_dgt_1+chk_due_amt+chk_dgt_2
   assert check_no == chk_digit
   
   total_due_with_payment = HelperFunctions.get_data_from_pdf(pdf_content,'total_due_with_payment')
   if ',' in total_due_with_payment['Total Due']:
    total_due_with_payment = total_due_with_payment['Total Due'].replace(',','')
   else:
    total_due_with_payment = total_due_with_payment['Total Due']
   assert total_due_with_payment == '$'+str( '{0:.2f}'.format(float(bill_detail['Amount Due']))) 
   
   bill_info = HEAccountFunctions.get_bill_details(bill_detail['Bill Number'])
   prev_throug_dt = aqConvert.DateTimeToFormatStr(aqConvert.StrToDate( bill_info['Prev. Through Date']),"%m/%d/%Y")
   through_dt = aqConvert.DateTimeToFormatStr(aqConvert.StrToDate( bill_info['Through Date']),"%m/%d/%Y")
   coverage_period = prev_throug_dt+'-'+through_dt
   assert coverage_period == top_right['Coverage Period']
   
   #Excel data validation
   file_path = Project.Variables.file_path + 'individual_risk_bill_'+account_number+'_'+bill_number+'.xlsx'
#   file_path = Project.Variables.file_path + 'individual_risk_bill_'+'00000009997'+'_'+'302822'+'.xlsx'
   DDT.ExcelDriver(file_path,'Bill Summary')
   while not DDT.CurrentDriver.EOF():
      dict_data = {}
      dict_data['Account Number'] = DDT.CurrentDriver.Value['Account Number']
      dict_data['Subscription Id'] = DDT.CurrentDriver.Value['Subscription Id']
      dict_data['Bill Number'] = DDT.CurrentDriver.Value['Bill Number']
      dict_data['Eligibility As Of'] = DDT.CurrentDriver.Value['Eligibility As Of']
      dict_data['Coverage Period'] = DDT.CurrentDriver.Value['Coverage Period']
      dict_data['Due Date'] = DDT.CurrentDriver.Value['Due Date']
      dict_data['Balance Forward'] = DDT.CurrentDriver.Value['Balance Forward']
      dict_data['Current Charges'] = DDT.CurrentDriver.Value['Current Charges']
      dict_data['Manual Adjustments'] = DDT.CurrentDriver.Value['Manual Adjustments']
      dict_data['Total Amount Due'] = DDT.CurrentDriver.Value['Total Amount Due']
      break
   assert dict_data['Account Number'] == account_number and dict_data['Subscription Id']  == subscription['subscription id']
   assert dict_data['Bill Number'] == bill_detail['Bill Number'] and dict_data['Eligibility As Of']  == aqConvert.DateTimeToFormatStr(bill_detail['Billing Date'], "%m/%d/%Y")
   assert dict_data['Coverage Period'] == coverage_period and dict_data['Due Date']  == aqConvert.DateTimeToFormatStr(bill_detail['Due Date'], "%m/%d/%Y")
   assert dict_data['Balance Forward'] == bill_detail['Balance Forward'] and dict_data['Current Charges']  == bill_detail['New Charges']
   assert dict_data['Manual Adjustments'] == bill_detail['Adjustments']  and dict_data['Total Amount Due']  == bill_detail['Amount Due']
  
@then("the address in pdf matches with {arg} address")
def step_impl(param1):
  query = "SELECT * FROM %s where test_case_id='%s' and account_type='%s'" % (Project.Variables.test_data_table,Project.Variables.test_case_id,Project.Variables.account_type)
  test_data = DataFunctions.executeQueryQADB(query, True)  
  for test_dta in test_data:
    subscriber_id = test_dta.subscriber_id
    bill_number = test_dta.bill_id
  account_number = Project.Variables.account_number
  file_path = Project.Variables.file_path + 'individual_risk_bill_'+account_number+'_'+bill_number+'.pdf'
#  file_path = Project.Variables.file_path + 'individual_risk_bill_'+'00000009997'+'_'+'302924'+'.pdf'
  pdf_content = CommonFunctions.read_PDF(file_path,0)
  top_right = str(HelperFunctions.get_data_from_pdf(pdf_content,'payee_address'))
  
  if param1 == "responsible party":
    # Search same member since the control is not in member details page
    SearchFunctions.searchTask('Manager',"Members","subscription", [{"name":"Member ID", "value":subscriber_id+'-01' }],True)
    subscription = HEMemberFunctions.get_subscription()
    temp = subscription['subscriber name'].split(',')
    subscriber_name = temp[1].strip()+' '+temp[0]
    pers_rep_details = HEMemberFunctions.get_personal_representative_details()
    assert (subscriber_name in top_right or  pers_rep_details['Name'] in top_right) and pers_rep_details['Address'] in top_right and pers_rep_details['City'] in top_right and pers_rep_details['Zip/Postal Code'] in top_right
  
  elif param1 == 'correspondence':  
    data = HEMemberFunctions.get_subscriber_details(subscriber_id+'-01')
    assert data[0] in top_right and data[0][0] in top_right and data[0][1] in top_right and data[0][2] in top_right
    
@then("I download the xlsx document")
def step_impl():
  query = "SELECT * FROM %s where test_case_id='%s' and account_type='%s'" % (Project.Variables.test_data_table,Project.Variables.test_case_id,Project.Variables.account_type)
  test_data = DataFunctions.executeQueryQADB(query, True)  
  for test_dta in test_data:
    subscriber_id = test_dta.subscriber_id
    bill_number = test_dta.bill_id
  home_page = Home_Page()
  home_page.get_excel(bill_number)

@given("I run a bill for a subscription with {arg} who is {arg} and {arg},correspondence definition {arg},member  delivery preference {arg} and responsibile party {arg} {arg} email")
def step_impl(param1, param2, param3, param4, param5, param6, param7):
  Project.Variables.account_type = param1

@when("I apply Adjustments")
def step_impl():
  Log.Message("Adjustments applied!!!")


@when("I add payment")
def step_impl():
  Log.Message("Payment applied!!!")