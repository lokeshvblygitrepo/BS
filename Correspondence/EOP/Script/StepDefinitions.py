import CommonFunctions
import CreateClaim
import DataFunctions
import DW_Helper_Functions
import HE_Helper_Functions
import Login_Page
import random
import SearchFunctions
from Home_Page import Home_Page
from Correspondence_Helper_Functions import Correspondence_Helper_Functions
from Basic_Actions import Basic_Actions
import us

TABLE = Project.Variables.test_data_table

@given("I have a {arg} claim with payment type {arg} {arg} email and {arg} payment")
def step_impl(param1, param2, param3,param4):
  pass
      
@when("I run {arg}")
def step_impl(param1):
  
  type = param1.split('-')[1].strip()
  
  #check if the job has been executed
  is_ran = eval('Project.Variables.%s_payment_run' % type.lower())
  
  if not is_ran:
  
    #get the latest eop_event_id
    record = get_eop_event_record(is_latest=True)
    latest_id = record.lastest_eop_event_id

    if type.lower() == 'subscriber':
      query = "SELECT member_id FROM %s WHERE claim_id is not null and batch_run_id is null and test_type='subscriber' ORDER BY id " % TABLE
      
    elif type.lower() == 'supplier':
      query = "SELECT supplier_hcc_id FROM %s WHERE claim_id is not null and batch_run_id is null and test_type='supplier' ORDER BY id " % TABLE

    data_record = DataFunctions.executeQueryQADB(query,True)
  
    list_data = []
    for i in data_record:
      if type.lower() == 'subscriber':
        list_data.append(i[0].split('-')[0]+'-01')
      else:
        list_data.append(i[0])
    
    CommonFunctions.triggerPaymentRunUpdated(param1,list_data)
    
    #update project variable
    if type.lower() == 'subscriber':
      Project.Variables.subscriber_payment_run = True
        
    elif type.lower() == 'supplier':
      Project.Variables.supplier_payment_run = True
    
    is_wait = True
    time_count = 0
  
    while is_wait and time_count < 20: #waiting for 20 mins
      #wait for batch_run_id is available
      for i in list_data:
        record = get_eop_event_record(recipient_hcc_id=i, latest_id=latest_id)
    
        if record is not None: #eop event record is generated
          #update to eop test data table
          if record.payment_fact_key is not None:
            if type.lower() == 'subscriber':
              query = "UPDATE %s SET transaction_number='%s' WHERE member_id like '%s%%' " % (TABLE,record.payment_fact_key,i.split('-')[0])
          
            elif type.lower() == 'supplier':
              query = "UPDATE %s SET transaction_number='%s' WHERE supplier_hcc_id = '%s' " % (TABLE,record.payment_fact_key,i)
          
            DataFunctions.executeQueryQADB(query,False)
        
          #update to eop test data table
          if record.batch_run_id is not None:
            today_date = aqConvert.DateTimeToFormatStr(aqDateTime.Today(), "%m/%d/%Y")
            if type.lower() == 'subscriber':
              query = "UPDATE %s SET batch_run_id='%s', job_run_date='%s' WHERE member_id like '%s%%' and test_type='subscriber' " % (TABLE,record.batch_run_id,today_date,i.split('-')[0])
          
            elif type.lower() == 'supplier':
              query = "UPDATE %s SET batch_run_id='%s', job_run_date='%s' WHERE supplier_hcc_id = '%s' and test_type='supplier'" % (TABLE,record.batch_run_id,today_date,i)
        
            DataFunctions.executeQueryQADB(query,False)

      #check if the job is completed      

      query = "SELECT * FROM %s WHERE claim_id is not null and batch_run_id is null and test_type='%s' ORDER BY id " % (TABLE,type.lower())
      data_record = DataFunctions.executeQueryQADB(query,True)    
    
      try:
        batch_run_id = data_record[0][0]        
      except:
        is_wait = False    
        break
      
      time_count+=1
      aqUtils.Delay(60000)

  Login_Page.login()


def get_eop_event_record(is_latest=False, recipient_hcc_id='', latest_id=0):
  
  if is_latest:
    query = "SELECT max(eop_event_id) as lastest_eop_event_id FROM reports.eop_events "
    
  else:
    query = "SELECT * FROM reports.eop_events WHERE recipient_hcc_id='%s' and eop_event_id>%s " % (recipient_hcc_id,latest_id)
    
  data_record = DataFunctions.executeQueryPostgresql('ddva.db.qa.corvesta.net', 5432, 'correspondence','general_test_automation','MqZG$FgpjwMI', query, True)
  
  try:
    for i in data_record:
      return i
  except:
    return None
    
      
@then("EOP is generated {arg} check")
def step_impl(param1):
  home = Home_Page()
  if Project.Variables.job_in_correspondence:
    lst_test_result = []
    query = "SELECT * FROM correspondence.tbl_correspondence_eop_test_data where test_case_id='{t_id}'".format(t_id=Project.Variables.test_case_id)
    data_record = DataFunctions.executeQueryQADB(query,True)  
    for index in data_record:
      id = index.id
      member_id = index.member_id
      batch_run_id = index.batch_run_id
      supplier_id = index.supplier_hcc_id
      test_type = index.test_type
      supplier_npi = index.supplier_npi
      
    query = "select create_date from reports.eop_events where batch_run_id={}".format(batch_run_id)
    data_record = DataFunctions.executeQueryPostgresql('ddva.db.qa.corvesta.net', 5432, 'correspondence','general_test_automation','MqZG$FgpjwMI', query, True)
    for bid in data_record:
      pdf_date = aqConvert.DateTimeToFormatStr(bid.create_date,"%m%d%Y")
    temp = member_id.split('-')
    subscriber_id = temp[0]+'-01'
    pay_fact_keys = Project.Variables.eop_pay_fact_keys
#    required_date = aqConvert.DateTimeToFormatStr(aqDateTime.Today(), "%m%d%Y")
    file_name = Project.Variables.download_path+'eop_'+pay_fact_keys+'_'+pdf_date+'.pdf'
  #  file_name = Project.Variables.download_path+"eop_191135_05242023.pdf"#+file_name
    pdf_content = CommonFunctions.read_PDF(file_name,0)
  
    #Check Validation
    chf = Correspondence_Helper_Functions()
    chk_cntnt = chf.get_check(pdf_content)
    if test_type.lower()=='subscriber':
      he_info = HE_Helper_Functions.get_subscriber_details(subscriber_id) 
    elif test_type.lower()=='supplier':
      he_info = HE_Helper_Functions.get_supplier_details(supplier_id) 
    if param1 == 'with': #PDF with check 
      check_no_pdf = home.get_data_from_pdf(pdf_content,'check_num')[0]['check_num']
      check_amount = home.get_data_from_pdf(pdf_content,'amount')[0]['amount']
      if chk_cntnt['dollar_amount'] != check_amount:
        Log.Error("Failed to verify check number")
        lst_test_result.append('Failed')
      if chk_cntnt['check_id']!=check_no_pdf:
        Log.Error("Check number validation failed")
        lst_test_result.append('Failed')
      if chk_cntnt['bank_info'] =='':
        Log.Error("Bank info not present")
      if chk_cntnt['dollar_literal']=='':
        Log.Error("Dollar literal not present")
      if chk_cntnt['payee']==he_info[0].strip()!=chk_cntnt['payee']:
        Log.Error("Failed to verify subscriber name")
        lst_test_result.append('Failed')
    elif 'bank_info' in chk_cntnt==True:
      Log.Error("Check details present for a record without check")  
  
    assert 'Failed' not in lst_test_result
  else:
    Log.Error("Payment Job in correspondence is not in FINAL status, Check validation failed!!!")
  

@then("Sent to print vendor for {arg}")
def step_impl(param1):
  home = Home_Page()
  query = "SELECT * FROM correspondence.tbl_correspondence_eop_test_data where test_case_id='{t_id}'".format(t_id=Project.Variables.test_case_id)
  data_record = DataFunctions.executeQueryQADB(query,True)  
  for i in data_record:
    id = i.id
    member_id = i.member_id
    batch_run_id = i.batch_run_id
    payment = i.payment
    payment_type = i.payment_type
    email = i.email
  job_info = home.get_job_info(batch_run_id)
  if 'COMPLETED' not in job_info['Batch Status']:
    Log.Error('Failed to complete the job!!!')
  if payment.lower()=='some' and payment_type.lower()=='check':    
    print_vndr_status = home.get_print_vendor_status(batch_run_id)
  assert print_vndr_status == 'SUCCESS'
  
@then("I download {arg} PDF document")
def step_impl(param1):
  Project.Variables.job_in_correspondence == True
  home = Home_Page()
  query = "SELECT * FROM correspondence.tbl_correspondence_eop_test_data where test_case_id='{t_id}'".format(t_id=Project.Variables.test_case_id)
  data_record = DataFunctions.executeQueryQADB(query,True)  
  for index in data_record:
    member_id = index.member_id
    batch_run_id = index.batch_run_id
    supplier_id = index.supplier_hcc_id
    test_type = index.test_type
    required_date = index.job_run_date
  temp = member_id.split('-')[0]
  subscriber_id = temp+'-01'
  job_info = home.get_job_info(batch_run_id)
  if 'COMPLETED' not in job_info['Batch Status']:
    Log.Error('Failed to complete the job!!!')
    Project.Variables.job_in_correspondence = False
  todays_date = aqConvert.DateTimeToFormatStr(aqDateTime.Today(), "%m/%d/%Y")
  
  if test_type.lower()=='subscriber':
    pay_fact_keys = home.get_pdf(required_date,todays_date,batch_run_id,param1,subscriber_id)
  elif test_type.lower()=='supplier':
    pay_fact_keys = home.get_pdf(required_date,todays_date,batch_run_id,param1,supplier_id)
  Project.Variables.eop_pay_fact_keys = pay_fact_keys
  assert Project.Variables.job_in_correspondence == True
  
  
@then("the data for {arg} in pdf matches with HE data")
def step_impl(param1):
  if Project.Variables.job_in_correspondence:
    home = Home_Page()
    lst_results = []
    query = "SELECT * FROM correspondence.tbl_correspondence_eop_test_data where test_case_id='{t_id}'".format(t_id=Project.Variables.test_case_id)
    data_record = DataFunctions.executeQueryQADB(query,True)
  
    for i in data_record:
      id = i.id
      member_id = i.member_id
      supplier_npi = i.supplier_npi
      claim_number = i.claim_id
      supplier_id = i.supplier_hcc_id
      batch_run_id = i.batch_run_id
    temp_id = member_id.split('-')
    subscriber_id = temp_id[0]+'-01'
    query = "select create_date from reports.eop_events where batch_run_id={}".format(batch_run_id)
    data_record = DataFunctions.executeQueryPostgresql('ddva.db.qa.corvesta.net', 5432, 'correspondence','general_test_automation','MqZG$FgpjwMI', query, True)
    for bid in data_record:
      pdf_date = aqConvert.DateTimeToFormatStr(bid.create_date,"%m%d%Y")
    file_path = Project.Variables.download_path+'eop_'+Project.Variables.eop_pay_fact_keys+'_'+pdf_date+'.pdf'

    pdf_content = CommonFunctions.read_PDF(file_path,0)
    pdf_content_chk_pge = CommonFunctions.read_PDF(file_path,1)
    claim_summary_pdf = home.get_data_from_pdf(pdf_content,'claim_summary')
    claim_line_pdf = home.get_data_from_pdf(pdf_content,'claim_lines')
    claim_lines_he_classic_dp = []  
    
    # Validation of supplier/member details from pdf page1
    if param1.lower()=='subscriber':
      he_info = HE_Helper_Functions.get_subscriber_details(subscriber_id,is_search=False) 
    elif param1.lower()=='supplier':
      he_info = HE_Helper_Functions.get_supplier_details(supplier_id,is_search=False)  
    supp_name = home.get_data_from_pdf(pdf_content_chk_pge,'payee')
    supp_address = home.get_data_from_pdf(pdf_content_chk_pge,'payee_address')
    state_code = supp_address[0]['payee_address'].split(',')[1].split(' ')[1]
    state = eval('us.states.%s.name' % state_code)
    if state.lower()!=he_info[1][2].lower():
      Log.Error("Failed to verify supplier name. Actual : {act}, Expected: {exp}".format(exp =he_info[1][2].lower(),act = state.lower()))
      lst_results.append('Failed')
    if param1.lower()=='subscriber':
      temp = he_info[0].split(' ')
      if supp_name[0]['payee'] != temp[1]+', '+temp[0]:
        Log.Error("Failed to verify supplier name. Actual : {act}, Expected: {exp}".format(exp =temp[1]+', '+temp[0],act = supp_name[0]['payee']   )) 
        lst_results.append('Failed')
    elif supp_name[0]['payee'] not in he_info[0]:
      Log.Error("Failed to verify supplier name. Actual : {act}, Expected: {exp}".format(exp =he_info[0],act = supp_name[0]['payee']   )) 
      lst_results.append('Failed')
    if he_info[1][0] not in supp_address[0]['payee_address']:
      Log.Error("Failed to verify Address Line1. Actual : {act}, Expected: {exp}".format(exp =he_info[0],act = supp_address[0]['payee_address'])) 
      lst_results.append('Failed')
    if he_info[1][0] not in supp_address[0]['payee_address']:
      Log.Error("Failed to verify Address Line1. Actual : {act}, Expected: {exp}".format(exp =he_info[1],act = supp_address[0]['payee_address'])) 
      lst_results.append('Failed')
    if he_info[1][3] not in supp_address[0]['payee_address']:
       Log.Error("Failed to verify Address Line1. Actual : {act}, Expected: {exp}".format(exp =he_info[1],act = supp_address[0]['payee_address'])) 
       lst_results.append('Failed')
  
    # Validation of claim lines
    for cl in claim_summary_pdf: #Getting claim summary based on number of claims
      SearchFunctions.searchTask('Manager',"claims", "all claims", [{"name":"Claim ID", "value":cl['Claim NO']}],True)  
      claim_lines_he_classic_dp.append(HE_Helper_Functions.get_claim_lines('Dental-Pricing'))
      lst_clm_line_he = []
      for dp in claim_lines_he_classic_dp: #converting claim lines to list of dict
        for data in dp:
          lst_clm_line_he.append(data)
    
    for itr in  range(0,len(claim_line_pdf)):
      if not claim_line_pdf[itr]['code'] == lst_clm_line_he[itr]['Service Code']:
        Log.Error("Service code verification failed, Actual: {act}, Expected: {exp}".format(act=claim_line_pdf[itr]['code'] ,exp=lst_clm_line_he[itr]['Service Code']))
        lst_results.append('Failed')
        
      temp = str(lst_clm_line_he[itr]['DOS From'])[:10].split('-')
      if not claim_line_pdf[itr]['date_of_service'] == temp[1]+'/'+temp[2]+'/'+temp[0]:
        Log.Error("Service date verification failed, Actual: {act}, Expected: {exp}".format(act=claim_line_pdf[itr]['date_of_service']  ,exp=temp[1]+'/'+temp[2]+'/'+temp[0]))
        lst_results.append('Failed')
      try:
         submitted = claim_line_pdf[itr]['Submitted'].replace(',','')
      except:
        submitted = claim_line_pdf[itr]['Submitted']
      if not submitted == "$"+str("{:.2f}".format(lst_clm_line_he[itr]['Billed'])):
        Log.Error("Billed info verification failed, Actual: {act}, Expected: {exp}".format(act=submitted ,exp="$"+str("{:.2f}".format(lst_clm_line_he[itr]['Billed']))))
        lst_results.append('Failed')
      if lst_clm_line_he[itr]['Paid'] == '':
      	paid_amt = '$0.00'
      else:
      	paid_amt = "$"+str("{:.2f}".format(lst_clm_line_he[itr]['Paid'])) 
      if not claim_line_pdf[itr]['Plan Plays'] == paid_amt:
        Log.Error("Paid Amount verification failed, Actual: {act}, Expected: {exp}".format(act=claim_line_pdf[itr]['Plan Plays'] ,exp=paid_amt))
        lst_results.append('Failed')
    
      if lst_clm_line_he[itr]['Member Responsibility'] == '': 
        mem_res = '$0.00' 
      else:
        mem_res = "$"+str("{:.2f}".format(lst_clm_line_he[itr]['Member Responsibility']))    
      if not claim_line_pdf[itr]['Patient Pays'] == mem_res:
        Log.Error("Patient Pays Amount verification failed, Actual: {act}, Expected: {exp}".format(act=claim_line_pdf[itr]['Patient Pays'] ,exp=mem_res))
        lst_results.append('Failed')
     
      if lst_clm_line_he[itr]['Allowed']=='': 
        ca = '$0.00' 
      else:
        ca = "$"+str("{:.2f}".format(lst_clm_line_he[itr]['Allowed']))       
      if not claim_line_pdf[itr]['Contract Allowance'] == ca:
        Log.Error("Patient Pays Amount verification failed, Actual: {act}, Expected: {exp}".format(act=claim_line_pdf[itr]['Contract Allowance'] ,exp=ca))
        lst_results.append('Failed')
    
      if lst_clm_line_he[itr]['Deductible'] =='': 
        ded = '$0.00' 
      else:
        ded = "$"+str("{:.2f}".format(lst_clm_line_he[itr]['Deductible']))     
      if not claim_line_pdf[itr]['Ded.'] == ded:
        Log.Error("Plan Allowance Amount verification failed, Actual: {act}, Expected: {exp}".format(act=claim_line_pdf[itr]['Ded.'] ,exp=ded))
        lst_results.append('Failed')
        
    # Validating claim line totals
    total = home.get_data_from_pdf(pdf_content,'total') 
    for cl in claim_summary_pdf:
      claim_no = HE_Helper_Functions.get_claim_number()
      if cl['Claim NO'] != claim_no:
        SearchFunctions.searchTask('Manager',"claims", "all claims", [{"name":"Claim ID", "value":cl['Claim NO']}],True)
      claim_rates = HE_Helper_Functions.get_claim_lines('Dental-Pricing')
      lst_rates = []
      for he_amt in claim_rates:
        lst_temp = []
        lst_temp.append(float("{:.2f}".format(he_amt['Billed'])))
        if he_amt['Paid'] =='':
          lst_temp.append(float('0.0'))
        else:
          lst_temp.append(float("{:.2f}".format(he_amt['Paid'])))
        if he_amt['Member Responsibility'] =='':
          lst_temp.append(float('0.0'))
        else:
          lst_temp.append(float("{:.2f}".format(he_amt['Member Responsibility'])))
        if he_amt['Allowed'] =='':
          lst_temp.append(float('0.0'))
        else:
          lst_temp.append(float("{:.2f}".format(he_amt['Allowed'])))
        if he_amt['Deductible'] =='':
          lst_temp.append(float('0.0'))
        else:
          lst_temp.append(float("{:.2f}".format(he_amt['Deductible'])))
        lst_rates.append(lst_temp)      
      temp = [sum(x) for x in zip(*lst_rates)]
      lst_total_rates = []
      for tot_rt in temp:
        lst_total_rates.append("$"+str("{:.2f}".format(tot_rt)))
      try:
        billed = total[0]['total'].split(' ')[0].replace(',','')
      except: 
        billed = total[0]['total'].split(' ')[0]
      if lst_total_rates[0] != billed:
        Log.Error("Failed to verify Billed/Submitted Amt, Actual: {act}, Expected: {exp}".format(act=lst_total_rates[0] ,exp= total[0]['total'].split(' ')[0]))
        lst_results.append('Failed')
      try:
        plan_pays = total[0]['total'].split(' ')[6].replace(',','')
      except: 
        plan_pays = total[0]['total'].split(' ')[6]  
      if plan_pays != lst_total_rates[1]:
        Log.Error("Failed to verify Plan Pays, Actual: {act}, Expected: {exp}".format(act=total[0]['total'].split(' ')[6],exp= lst_total_rates[1]))
        lst_results.append('Failed')
        
      if total[0]['total'].split(' ')[7] != lst_total_rates[2]:
        Log.Error("Failed to verify Member Paid Amt,  Actual: {act}, Expected: {exp}".format(act=total[0]['total'].split(' ')[7],exp= lst_total_rates[2]))
        lst_results.append('Failed')
        
      if total[0]['total'].split(' ')[2] != lst_total_rates[3]:
        Log.Error("Failed to verify Allowed, Actual: {act}, Expected: {exp}".format(act=total[0]['total'].split(' ')[1] ,exp=  lst_total_rates[3]))
        lst_results.append('Failed')
        
      if total[0]['total'].split(' ')[3] != lst_total_rates[4]:
        Log.Error("Failed to verify Deductible, Actual: {act}, Expected: {exp}".format(act=total[0]['total'].split(' ')[3] ,exp=  lst_total_rates[4]))
        lst_results.append('Failed')
      try:
        total.pop(0)
      except:
        pass
        
    #Validating total submitted for supplier only
    if param1.lower() == "supplier": 
      total = home.get_data_from_pdf(pdf_content,'total')
      claim_summary_pdf = home.get_data_from_pdf(pdf_content,'claim_summary')
      lst_prov = []
      for csp in claim_summary_pdf:
        lst_prov.append(csp['Provider ID/Loc'].split('/')[0])
      if len(list(set(lst_prov)))>0:
        tot_sub = home.get_data_from_pdf(pdf_content,'total_submitted')
        tot_paid = home.get_data_from_pdf(pdf_content,'total_paid')
        providers = []
        same_prov = []
        submitted = []
        paid = []
        for cs in range(0,len(claim_summary_pdf)):
          if claim_summary_pdf[cs]['Provider ID/Loc'].split('/')[0]not  in providers or len(same_prov)==0:  
            same_prov.append(total[cs])
        for sp in same_prov:
          submitted.append(sp['total'].split(' ')[0])
          paid.append(sp['total'].split(' ')[6])
        lst_tot_submitted = []
        for tsub in tot_sub:
          lst_tot_submitted.append(tsub['total_submitted'])
        total_paid = []
        for tpaid in tot_paid:
          total_paid.append(tpaid['total_paid'])
        if lst_tot_submitted.sort()!= submitted.sort():
          Log.Error("Failed to verify submitted. Expected {exp}, Actual : {act}".format(exp =str(lst_tot_submitted.sort()),act = str(submitted.sort()) ) )
        if total_paid.sort()!= paid.sort():
          Log.Error("Failed to verify Paid. Expected {exp}, Actual : {act}".format(exp =str(lst_tot_paid.sort()),act = str(paid.sort()) ) )  
      else:
        tot_sub = home.get_data_from_pdf(pdf_content,'total_submitted')[0]['total_submitted']
        tot_paid = home.get_data_from_pdf(pdf_content,'total_paid')[0]['total_paid']
        submitted = 0
        paid = 0
        for tot in total:
          submitted = submitted+float(tot['total'].split(' ')[0].replace('$',''))
          paid = paid+float(tot['total'].split(' ')[6].replace('$',''))
        submitted = '$'+"{:.2f}".format(submitted)
        paid = '$'+"{:.2f}".format(paid)    
        if tot_sub.strip().replace(',','') != submitted:
          Log.Error("Failed to verify Total submitted amount, Actual: {act}, Expected: {exp}".format(exp = tot_sub,act=total[0]['total'].split(' ')[0]))
          lst_results.append('Failed')
        if tot_paid.strip().replace(',','') != paid:
          Log.Error("Failed to verify Total paid amount, Actual: {act}, Expected: {exp}".format(exp = tot_paid,act=total[0]['total'].split(' ')[6]))
          lst_results.append('Failed')
        
    #Validation of message codes
    msg_codes = []
    msg_code_pdf = home.get_data_from_pdf(pdf_content,'message_codes')
    for cln in claim_summary_pdf:
      claim_no = HE_Helper_Functions.get_claim_number()
      if cln['Claim NO'] != claim_no:
        SearchFunctions.searchTask('Manager',"claims", "all claims", [{"name":"Claim ID", "value":cln['Claim NO']}],True)      
      if msg_code_pdf:
        msg_code = HE_Helper_Functions.get_message()
        msg_codes.append(msg_code)
    for cln in range(0,len(msg_code_pdf)):
      if msg_code_pdf: 
        if not msg_code_pdf[cln]['message_codes'][10:-1]in str(msg_codes):
           Log.Error("Failed to verify Message code, Actual: {act}, Expected: {exp}".format(exp = msg_code_pdf[0]['message_codes'][8:],act=str(msg_code)))
           lst_results.append('Failed')
           
    # Validation of check number,total and date
    check_no_he = HE_Helper_Functions.get_check()
    check_no_pdf = home.get_data_from_pdf(pdf_content,'check_num')
    check_amount = home.get_data_from_pdf(pdf_content,'amount')
    chk_date = home.get_data_from_pdf(pdf_content,'date')
    if str(check_no_he[0]['check number']) != '0':   # Validation only for payment with check 
      if not str(check_no_he[0]['check number'])==check_no_pdf[0]['check_num']:
        Log.Error("Check number verification failed, Actual: {act}, Expected: {exp}".format(act=str(check_no_he[0]['check number']) ,exp=check_no_pdf[0]['check_num']))
        lst_results.append('Failed')
      temp = str(check_no_he[0]['date'])[:10].split('-')
      if chk_date[0]['date'] != temp[1]+'/'+temp[2]+'/'+temp[0]:
        Log.Error("Failed to verify check date, Actual: {act}, Expected: {exp}".format(act=chk_date[0]['date'] ,exp=temp[1]+'/'+temp[2]+'/'+temp[0]))
        lst_results.append('Failed')
       
    totals = home.get_data_from_pdf(pdf_content,'total')
    total = 0
    for itr in totals:
      total=total+ float(itr['total'].split(' ')[6].replace('$',''))
  #  total = '$'+str("{:.2f}".format(total))
    total = '$'+str(total)
  #  res = [element for element in check_no_he  if element['amount'] == total]
    if str(float(total.replace('$','')))!=str(float(check_amount[0]['amount'].replace('$',''))):#res[0]['amount']:
      Log.Error("Failed to verify check amount, Actual: {act}, Expected: {exp}".format(act=total ,exp=check_amount[0]['amount']))
      lst_results.append('Failed')   
         
     # Validation of patient and claim summary details
    claim_summ_he = []
    if len(claim_summary_pdf)<2:
      claim_no = HE_Helper_Functions.get_claim_number()
    for cs in range(0,len(claim_summary_pdf)):
      temp_dict = {}
      if len(claim_summary_pdf)<2:
        if claim_summary_pdf[cs]['Claim NO'] !=  HE_Helper_Functions.get_claim_number():
          SearchFunctions.searchTask('Manager',"claims", "all claims", [{"name":"Claim ID", "value":claim_summary_pdf[cs]['Claim NO']}],True)
      else:
        SearchFunctions.searchTask('Manager',"claims", "all claims", [{"name":"Claim ID", "value":claim_summary_pdf[cs]['Claim NO']}],True)
      claim_no = HE_Helper_Functions.get_claim_number()
      temp_dict['provider']= HE_Helper_Functions.get_provider()
      temp_dict['member_name']= HE_Helper_Functions.get_patient()['member full name']
      temp_dict['member_dob']= HE_Helper_Functions.get_patient()['member dob']
      temp_dict['interest']= HE_Helper_Functions.get_interest()['interest']
      temp_dict['claim'] = HE_Helper_Functions.get_claim_number()      
      SearchFunctions.searchTask("Manager","Members", "subscription", [{"name":"Member ID", "value":claim_summary_pdf[cs]['Subscriber ID']+'-01'}],True)
      sub_details = HE_Helper_Functions.get_subscription()
      temp_dict['subscriber_name'] = sub_details["subscriber name"]
      temp_dict['subscription_id'] = sub_details["subscription id"]
      claim_summ_he.append(temp_dict)
      
      
    he_sorted = sorted(claim_summ_he, key=lambda i: i['claim'])
    pdf_sorted = sorted(claim_summary_pdf, key=lambda i: i['Claim NO'])
  
    for hs in he_sorted:
      for ps in pdf_sorted:
        if hs['provider'] not in ps['Provider ID/Loc']:
          Log.Error("Provider Location verification failed, Actual: {act}, Expected: {exp}".format(act=hs['provider'] ,exp=ps['Provider ID/Loc']))
          lst_results.append('Failed')    
          
        if not ps['Claim NO'] ==hs['claim']:
          Log.Error("Claim No verification failed, Actual: {act}, Expected: {exp}".format(act=ps['Claim NO'] ,exp=hs['claim']))
          lst_results.append('Failed')    
          
        temp = hs['member_dob'].split('/')
        if not ps['Birthdate'] =="{0:0=2d}".format(int(temp[0]))+'/'+"{0:0=2d}".format(int(temp[1]))+'/'+temp[2]:
          Log.Error("Birth Date verification failed, Actual: {act}, Expected: {exp}".format(act=ps['Birthdate'] ,exp="{0:0=2d}".format(int(temp[0]))+'/'+"{0:0=2d}".format(int(temp[1]))+'/'+temp[2]))
          lst_results.append('Failed')    
          
        if not ps['Interest'] ==hs['interest']:
          Log.Error("Interest verification failed, Actual: {act}, Expected: {exp}".format(act=ps['Interest'] ,exp=hs['interest']))
          lst_results.append('Failed')    
          
        if ps['Patient Name'] not in hs['member_name']:
          Log.Error("Patient name verification failed, Actual: {act}, Expected: {exp}".format(act=ps['Patient Name'] ,exp=hs['member_name']))
          lst_results.append('Failed')    
          
        if ps['Subscriber Name'].split(',')[0] not in hs['subscriber_name'] and ps['Subscriber Name'].split(',')[1] not in hs['subscriber_name']:
           Log.Error("Subscriber name verification failed, Actual: {act}, Expected: {exp}".format(act=ps['Subscriber Name'].split(',')[0] ,exp=hs['subscriber_name']))
           lst_results.append('Failed')
           
        if ps['Subscriber ID'] != hs['subscription_id']:
           Log.Error("Subscriber Id verification failed, Actual: {act}, Expected: {exp}".format(act=ps['Subscriber ID'].split(',')[0] ,exp=hs['subscription_id']))
           lst_results.append('Failed')
        pdf_sorted.pop(pdf_sorted.index(ps))
        break
      
    

   
    assert 'Failed' not in lst_results
  else:
    Log.Error("Payment Job in correspondence is not in FINAL status, PDF validation failed!!!")

@then("email address is not available")
def step_impl():
  home = Home_Page()
  pay_fact_key = Project.Variables.eop_pay_fact_keys
  event_details = home.get_event_status(pay_fact_key)
  assert event_details['Remarks']=="Email address not found" or event_details['Remarks']=="--"
  
@then("the link is created in HE attachments")
def step_impl():
    
  query = "SELECT payment_number FROM reports.eop_events where payment_fact_key='%s'" % (Project.Variables.eop_pay_fact_keys)    
  data_record = DataFunctions.executeQueryPostgresql('ddva.db.qa.corvesta.net', 5432, 'correspondence','general_test_automation','MqZG$FgpjwMI', query, True)
  for rec in data_record:
    payment_number = rec.payment_number
  lst_links_he = HE_Helper_Functions.get_attachments(payment_number)
  url_frm_ui = Project.Variables.eop_doc_url
  Project.Variables.eop_doc_url = ''
  assert url_frm_ui in lst_links_he
  
def test():
  home = Home_Page()
  file_path = "C:\\Users\\vsiby\\Downloads\\eop_191052_05252023.pdf"#+file_name
  pdf_content = CommonFunctions.read_PDF(file_path,0)
  total = home.get_data_from_pdf(pdf_content,'total')  
  

  
