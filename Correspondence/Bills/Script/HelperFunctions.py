import CommonFunctions
import re

def get_nth_buisiness_day(date,day):
  # date : mm/dd/yyyy format, type string
  # day : buisiness day to be returned
#  date = '05/01/2023'
#  day=7
  req_date = aqConvert.StrToDate(date)
  flag = True
  day_counter = 1
  while day_counter<day:
    if aqDateTime.GetDayOfWeek(req_date) == 1 or aqDateTime.GetDayOfWeek(req_date) == 7:
      req_date = aqDateTime.AddDays(req_date,1)
    else:
      req_date = aqDateTime.AddDays(req_date,1)
      day_counter = day_counter+1
  return  req_date
  
def get_data_from_pdf(pdf_data,keyword):
  # To capture data from individual bills pdf
  # keyword : part of the pdf from which values needs to be retrieved
  #eg: total_due_with_payment, payee_address, billing_summary, top_right_info_with_payment, total_due_with_payment
  
  req_data = pdf_data.split('Total Amount Due')[1].strip().split('\n')
  dict_data = {}  
  if keyword == 'top_right':
    keys = ['Eligibility as of','Subscription ID','Due Date','Bill Number','Coverage Period','Account Number']
    lst_dta = []
    for rec in req_data:
      if '$' not in rec and any(char.isalpha() for char in rec)==False and rec not in lst_dta and not re.match('^20.*', rec):
        lst_dta.append(rec)
      dict_data=dict(zip(keys, lst_dta))
    
  if keyword =='payee_address':
    lst_address = []
    for rec in req_data[::-1]:
      if 'TEST DOCUMENT' in rec:
        name = rec.replace('TEST DOCUMENT','')
        lst_address.append(name)       
      elif any(char.isalpha() for char in rec)==False:
        break
      else:
        lst_address.append(rec)
    return lst_address
    
  if keyword =='billing_summary':
    keys = ['Balance Forward','Current Charges','Manual Adjustments','Total Amount Due']
    for ky in keys:
      for rec in req_data:
        if '$' in rec:
          dict_data[ky] = rec
          req_data.remove(rec)
          break
  if keyword == 'top_right_info_with_payment':
     keys = ['Eligibility as of','Subscription ID','Due Date','Bill Number','Coverage Period','Account Number']
     lst_dta = []
     for rec in req_data:
      if '$' not in rec and any(char.isalpha() for char in rec)==False and re.match('^20.*', rec)==None:
        if rec in lst_dta:
          lst_dta[lst_dta.index(rec)] = rec
        else:
          lst_dta.append(rec)
     dict_data=dict(zip(keys, lst_dta))
  
  if keyword == 'total_due_with_payment':
    amounts = []
    for rec in req_data:
      if '$' in rec:
        amounts.append(rec)
    dict_data['Total Due']= amounts[-1]
    
  return dict_data
  
def query_builder(account_type,age_group,handicapped,member_delivery_pref,resp_party,resp_party_email,selected_subr):
  # To develop query based on member requirements for generating Indiv Risk Bill
  if account_type == 'ACA Exchange Individual':
    account_name = Project.Variables.account_aca_exchange_indiv
  elif account_type == "Non-Exchange Individual":
    account_name = Project.Variables.account_non_exchange_indiv
  query = "select mem.SUBSCRIPTION_HCC_ID, ac.ACCOUNT_HCC_ID,bp.benefit_plan_name,ac.account_name "
  query += "from payor_dw.account ac "
  query += "join PAYOR_DW.ACCOUNT_PLAN_SELECT_FACT ap "
  query += "on ap.account_key=ac.account_key "
  query += "join PAYOR_DW.BENEFIT_PLAN bp "
  query += "on bp.benefit_plan_key=ap.benefit_plan_key "
  query += "join payor_dw.member mem "
  query += "on mem.account_key=ac.account_key  "
  query += "join payor_dw.date_dimension dt "
  query += "on dt.date_key=mem.member_birth_date_key "
  query += "left join payor_dw.billing billing "
  query += "on billing.subscription_hcc_id = mem.subscription_hcc_id "
  query += "left join payor_dw.DOCUMENT_DELIVERY_METHOD_CODE doc "
  query += "on doc.DOCUMENT_DELIVERY_METHOD_KEY = mem.DOCUMENT_DELIVERY_METHOD_KEY "
  query += "left join payor_dw.MEMBER_HIST_FACT_TO_RESP_PRSN hfrp "
  query += "on mem.MEMBER_HISTORY_FACT_KEY = hfrp.MEMBER_HISTORY_FACT_KEY  "    
  query += "left join PAYOR_DW.RESPONSIBLE_PERSON rp "
  query += "on rp.RESPONSIBLE_PERSON_KEY = hfrp.RESPONSIBLE_PERSON_KEY   "
  query += "left join PAYOR_DW.resp_person_type_code rptc "
  query += "on rptc.resp_person_type_key=rp.RESP_PERSON_TYPE_KEY "
  query += "where ac.ACCOUNT_LEVEL='2' "
  for i in selected_subr:
    query += "and mem.member_hcc_id not like '%s%%' " % i
  query += "and (billing.bill_period_to = (SELECT MAX(b.BILL_PERIOD_TO) "
  query += "FROM PAYOR_DW.BILLING b "
  query += "where b.subscription_hcc_id = billing.subscription_hcc_id "
  query += "group by b.subscription_hcc_id) "
  query += "or billing.bill_period_to is null) "
  query += "and nvl(billing.bill_period_to,sysdate) <= ADD_MONTHS(SYSDATE, 12 * 2) "
  query += "and ac.account_name = '{}' ".format(account_name)
  if age_group == 'child':
    query += "and (SELECT TRUNC(MONTHS_BETWEEN(SYSDATE, TO_DATE(dt.DATE_NAME_2 , 'MM/DD/YYYY')) / 12) AS years FROM dual)<18 "
  else:
    query += "and (SELECT TRUNC(MONTHS_BETWEEN(SYSDATE, TO_DATE(dt.DATE_NAME_2 , 'MM/DD/YYYY')) / 12) AS years FROM dual)>18 "
  if handicapped != 'handicapped':
    query += "and mem.IS_HANDICAPPED='U' "
  else:
    query += "and mem.IS_HANDICAPPED='Y' "
  query += "and nvl(doc.DOCUMENT_DELIVERY_METHOD_NAME, 'Nothing') = '{}' ".format(member_delivery_pref.capitalize())#-- 'Nothing', if no document delivery method for the test
  if resp_party == '':
    query += "and nvl(resp_person_type_name, 'None') = 'None' "#--'Legal Guardian' --'None', if None for responsible party
  else:
    query += "and nvl(resp_person_type_name, 'None') = '{}' ".format(resp_party)
  if resp_party_email !='with':
    query += "and rp.RESP_PERSON_EMAIL_ADDRESS is null "
  else:
    query += "and rp.RESP_PERSON_EMAIL_ADDRESS is not null "
  query += "ORDER BY DBMS_RANDOM.RANDOM fetch next 1 row only"
  return query
  
def get_he_version():
  Project.Variables.he_version = CommonFunctions.get_he_latest_version()
  
  
class CheckDigitCalculation:
    weight_array = [7, 5, 3, 2]
    char_array = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    num_array = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "1", "2", "3", "4", "5", "6", "7", "8", "9", "1", "2", "3", "4", "5", "6", "7", "8"]

    @staticmethod
    def calculate_check_digit(account_number):
#        account_number= "51000000011210"
        try:
            if account_number is None:
                raise ValueError("AccountNumber is None")
            
            sum_ = 0
            addition = 0
            multiplication = 0
            account_number_alpha_array = []
            trimed_account_number = account_number.replace("-", "")
            account_number_array = list(trimed_account_number)

            # Checking if Alphabet is there in Account Number
            check_is_alphabet = CheckDigitCalculation.is_alpha(trimed_account_number)
            
            if check_is_alphabet:
                for char in account_number_array:
                    # Checking if the character is an alphabet
                    if char.isalpha():
                        # Getting the index of the character in char_array
                        index_value = CheckDigitCalculation.char_array.index(char)
                        # Getting the element value from num_array based on the index above
                        ascii_value = CheckDigitCalculation.num_array[index_value]
                        # Assigned the value to the current character
                        account_number_array[account_number_array.index(char)] = ascii_value
                account_number_alpha_array = account_number_array
            else:
                account_number_alpha_array = account_number_array

            # Iterate over the accountNumber array
            for position, digit in enumerate(account_number_alpha_array):
                multiplication = int(digit) * CheckDigitCalculation.weight_array[position % 4]
                # Sum the digits of the results
                addition = CheckDigitCalculation.get_sum(multiplication)
                sum_ += addition

            # Divide the sum by the modulus 10 to determine the remainder
            remainder = sum_ % 10

            # Subtract the remainder from 10 to determine the check digit
            final_check_digit = 10 - remainder

            final_check_digit_remainder = final_check_digit % 10

            return final_check_digit_remainder
        except Exception as ex:
            # Temporary fix
            print("Error occurred during check digit calculation, return default value - 0")
            return 0

    @staticmethod
    def get_sum(digit_sum):
        sum_ = 0
        while digit_sum != 0:
            sum_ += digit_sum % 10
            digit_sum = digit_sum // 10

        return sum_

    @staticmethod
    def is_alpha(s):
        return any(c.isalpha() for c in s)
        
def test():
  a = CheckDigitCalculation()
  t = a.calculate_check_digit('2024090151000000010785900378')