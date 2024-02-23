import DataFunctions

def get_member(is_test_member , account_name, payment_type='', is_email='',selected_subr=[]):
  # Function to get a member based on payment type and email(with or w/o email)
  # is_test_member : True/False to select conditions in query
  # payment_type : ACH/Check
  # is_email : null/not null
  query  = "select distinct member_hcc_id "
  query += "from payor_dw.all_subscription_history_fact subr_fact "
  query += "join payor_dw.member  "
  query += "on subr_fact.subscription_hcc_id = member.subscription_hcc_id "
  query += "join payor_dw.payment_type_code payment "
  query += "on payment.payment_type_key = subr_fact.payment_type_key "
  query += "join payor_dw.account "
  query += "on member.account_key = account.account_key "
  
  if payment_type.lower() == 'ach':
    query += "join payor_dw.payee_bank_accounts_fact ba " #make sure a bank account record when ach
    query += "on member.subscription_key = ba.subscription_key " 
    
  query += "where subr_fact.subscription_status='a' "
  query += "and member.member_status='a' "
  query += "and account_name = '%s' " % account_name  
 
  for i in selected_subr:
    query += "and member_hcc_id not like '%s%%' " % i
    
  if is_test_member:
    query+= "and payment.payment_type_name = '{payment_type}' ".format(payment_type =payment_type)
    query+= "and member.email_address is {email} ".format(email = is_email)
    
  query += "ORDER BY DBMS_RANDOM.RANDOM()"

  records = DataFunctions.getDataDW(Project.Variables.env,query)
  list_member = []
  for itr in records:
    if itr[0] not in list_member:
      list_member.append(itr[0])
    
  return list_member
  
def test():
  x=get_supplier(True, 'ACH','NULL')
  
def get_supplier(is_test_supplier, payment_type='', is_email='',selected_supplier=[]):

# here is the query for paying to supplier location
#  query = "select distinct sup.supplier_npi,sup.supplier_hcc_id,sup.supplier_name, ci.email_addr_txt as supplier_location_email, "
#  query += "sup_loc.supplier_location_name,sup_loc.supplier_location_hcc_id,prac.practitioner_npi, "
#  query += "prac.practitioner_full_name,prac.practitioner_hcc_id " 
#  query += "from payor_dw.practitioner_role_history_fact prac_role "
#  query += "join payor_dw.practitioner prac "
#  query += "on prac_role.practitioner_key = prac.practitioner_key "
#  query += "join payor_dw.supplier sup "
#  query += "on prac_role.supplier_key = sup.supplier_key "
#  query += "join payor_dw.supplier_location sup_loc "
#  query += "on prac_role.supplier_location_key = sup_loc.supplier_location_key "
#  query += "join payor_dw.payment_type_code  p "
#  query += "on sup_loc.payment_type_key = p.payment_type_key "
#  query += "join payor_dw.supp_loc_hist_to_contact_info slhtci "
#  query += "on sup_loc.supplier_loc_hist_fact_key = slhtci.supplier_loc_hist_fact_key "
#  query += "join payor_dw.contact_information ci "
#  query += "on slhtci.contact_info_key = ci.contact_info_key "
#  query += "join payor_dw.contact_information_type cit "
#  query += "on ci.contact_information_type_key = cit.contact_information_type_key "
#  query += "where prac_role.practitioner_role_status = 'a' "
#  query += "and prac.practitioner_status='a' " 
#  query += "and sup.supplier_status = 'a' "
#  query += "and sup_loc.supplier_location_status = 'a' "
#  query += "and prac.practitioner_npi is not null "
#  query += "and sup.supplier_npi is not null "
#  query += "and prac.practitioner_hcc_id like '{}%' ".format(Project.Variables.state_code.upper())
#  query += "and prac_role.practitioner_role_hist_fct_key in  (select max(practitioner_role_hist_fct_key) from payor_dw.practitioner_role_history_fact where practitioner_key = prac.practitioner_key) "
#  
#  if selected_supplier != []:
#    query += "and sup.supplier_npi not in (%s) " % ', '.join(f"'{i}'" for i in selected_supplier)
#  
#  if is_test_supplier:
#    query += "and cit.contact_info_type_name='Pay To' "
#    query += "and p.payment_type_name = '{payment_type}' ".format(payment_type = payment_type)
#    query += "and ci.email_addr_txt is {email} ".format(email = is_email)


# here is the query for paying to supplier
  query  = "select distinct sup.supplier_npi,sup.supplier_hcc_id, sup.supplier_name, ci.email_addr_txt as supplier_email, sup_loc.supplier_location_name,sup_loc.supplier_location_hcc_id,prac.practitioner_npi, prac.practitioner_full_name,prac.practitioner_hcc_id "
  query += "from payor_dw.practitioner_role_history_fact prac_role join payor_dw.practitioner prac on prac_role.practitioner_key = prac.practitioner_key join payor_dw.supplier sup on prac_role.supplier_key = sup.supplier_key join payor_dw.supplier_location sup_loc "
  query += "on prac_role.supplier_location_key = sup_loc.supplier_location_key join payor_dw.payment_type_code p on sup_loc.payment_type_key = p.payment_type_key join payor_dw.supp_hist_to_contact_info shtci on shtci.supplier_history_fact_key = sup.supplier_history_fact_key " 
  query += "join payor_dw.contact_information ci on shtci.contact_info_key = ci.contact_info_key " 
  
  if payment_type.lower() == 'ach':
    query += "join payor_dw.payee_bank_accounts_fact ba " #make sure a bank account record when ach
    query += "on sup.supplier_key = ba.supplier_key " 
    
  query += "where prac_role.practitioner_role_status = 'a' "
  query += "and prac.practitioner_status='a' "
  query += "and sup.supplier_status = 'a' "
  query += "and sup_loc.supplier_location_status = 'a' "
  query += "and prac.practitioner_hcc_id like 'VA%' "
  query += "and sup_loc.claim_payment_payee_sel_code='s' "
  query += "and prac_role.practitioner_role_hist_fct_key in  (select max(practitioner_role_hist_fct_key) from payor_dw.practitioner_role_history_fact where practitioner_key = prac.practitioner_key) "
  query += "and sup.supplier_name like 'KS QA AUTOMATION ONLY SUPPLIER%' "
  
  if selected_supplier != []:
   query += "and sup.supplier_hcc_id not in (%s) " % ', '.join(f"'{i}'" for i in selected_supplier)
   
  if is_test_supplier:
   query += "and p.payment_type_name = '{payment_type}' ".format(payment_type = payment_type)
   query += "and ci.email_addr_txt is {email} ".format(email = is_email) 
  
  query += "ORDER BY DBMS_RANDOM.RANDOM() fetch next 20 row only"
  records = DataFunctions.getDataDW(Project.Variables.env,query)
  
  list_supplier_details = []
  for itr in records:
    supplier_details = {}
    supplier_details['supplier_npi'] = itr[0]
    supplier_details['supplier_hcc_id'] = itr[1]
    supplier_details['supplier_name'] = itr[2]
    supplier_details['practitioner_hcc_id'] = itr[8]
    
    list_supplier_details.append(supplier_details)
    Log.Message(str(supplier_details))
  return list_supplier_details