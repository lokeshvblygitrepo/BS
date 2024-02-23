from Basic_Actions import Basic_Actions
import CommonFunctions
import re

class Home_Page(Basic_Actions):
  
  def __init__(self):
    super().__init__()
    page_url = '''Page("https://ddva.qa.keyspring.com/*")'''
    self.page = Sys.Browser("Chrome").WaitChild(page_url, 10000)
    self.job_type_drpdwn_xpath = "//span[contains(@class,'mat-select') and text()='Search by Batch Job Type']"
    self.search_job_txtbox = "//input[@aria-label='dropdown search']"
    self.select_option_xpath = "//mat-option//span[contains(text(),'{}')]"
    self.start_end_date_xpath = "//input[@formcontrolname ='{}']" #startDate/endDate
    self.search_btn_xpath = "//span[text()=' Search ']"
    self.table_cell_xpath = "//mat-card//mat-table//mat-cell"
    self.id_xpath = "//mat-card//mat-table//mat-cell//a[contains(text(),'{}')]"
    self.payment_fact_key = "//span[text()='{}']/ancestor::mat-row//mat-cell[4]"
    self.pdf_icn = "//span[text()='{}']/ancestor::mat-row//i[@class='pdf-icon']"
    self.download_btn = "//pdf-toolbar//button[@id='download']"
    self.pdf_pnl = "//pdf-toolbar"
    self.run_status = "//mat-cell//a[contains(text(),'{}')]/ancestor::mat-row"
    self.inc_online_bills_chkbx_xpath = "//input[@type='checkbox']"
    self.table_header = "(//mat-table//mat-header-row)"#//mat-header-cell)"
    self.home_btn_xpth = "//span[text()='Correspondence ']"
    self.event_hdr_xpath = "(//mat-header-row)"
    self.desired_row = "//span[contains(text(),'{}')]/ancestor::mat-row"
    self.clear_xpath = "//span[text()=' Clear ']"
    
  def navigate_to_home(self):
    home_btn = self.get_object(self.home_btn_xpth)
    home_btn.Click()
    
  def clear_search(self):
    self.get_object(self.clear_xpath).Click()
    
  def search_jobs(self,start_date,end_date,id,job_name,include_online_bills=False):
    # To search different types of jobs in home page
    # start_date : Start date
    # end_date : End date
    #job name : Job which is to be searched
    #include_online_bills: True/False, False by default
#    self.navigate_to_home()
    self.get_object(self.job_type_drpdwn_xpath).Click()
    self.get_object(self.search_job_txtbox).Keys(job_name)
    self.get_object(self.select_option_xpath.format(job_name)).Click()
    self.get_object(self.start_end_date_xpath.format('startDate')).Keys(start_date)
    self.get_object(self.start_end_date_xpath.format('endDate')).Keys(end_date)
    if include_online_bills:
      self.get_object(self.inc_online_bills_chkbx_xpath).Click()
    self.get_object(self.search_btn_xpath).Click()
    
  def get_job_info(self,id):
    # For getting all the records in a row from home page, with the keyword Id
    #id : batch_run_id, from postgres correspondence DB  
    self.get_object(self.table_cell_xpath)
    self.page.Wait() 
    headers = self.get_object(self.table_header).contentText.split('\n')
    headers.insert(3,'Info')   
    for itr in range(0,30): # Waiting for a row in correspondence UI 
      self.get_object(self.table_cell_xpath)
      self.page.Wait()   
      status_row = self.get_object(self.run_status.format(id))
      if status_row == None:
       self.page.Keys("[F5]")
       aqUtils.Delay(30000)
       self.page.Wait()
      else:
        break
    if status_row!=None:
      for itr in range(0,30): # Waiting for the batch status and print vendor to be completed
        self.page.Wait()        
        status_rec = self.get_object(self.run_status.format(id)).contentText.split('\n')
        if "COMPLETED" in status_rec[2] or "FAILED" in status_rec[2]:
          break
        else:
          self.page.Keys("[F5]")
          aqUtils.Delay(30000)
          self.page.Wait()
      job_info = dict(zip(headers, status_rec))
      return job_info
    else:
      return {}
      
  def get_print_vendor_status(self,id):
    # To wait for print vendor status to be in Success
    # id : batch_run_id
    status = ''
    job_status = self.get_job_info(id)
    if job_status:
      if "COMPLETED" in job_status['Batch Status']:
        for itr in (0,10):
          status = self.get_object(self.run_status.format(id)).contentText.split('\n')[6]
          if status in["FAILED","SUCCESS","PAUSE","--"]:
            break
          else:
            self.page.Keys("[F5]")
            aqUtils.Delay(30000)
            self.page.Wait()
      return status
    else:
      return ''
    
  def get_pdf(self,start_date,end_date,id,job_name,member_id):
    # Function to download eop df files
    # PreCondition : User should be logged in to correspondance portal 
    #              : User should have access to view pdf
    self.search_jobs(start_date,end_date,id,job_name)
    self.page.Wait()
    self.get_object(self.table_cell_xpath.format(id))
    self.page.Wait()
    self.get_object(self.id_xpath.format(id)).Click()
    pay_fact_key = self.get_object(self.payment_fact_key.format(member_id)).contentText
    browser = Sys.Browser(Project.Variables.required_browser)
    self.page = browser.Page("*correspondence*")
    self.get_object(self.pdf_icn.format(member_id)).Click()  
    self.page = browser.Page("*document-reader*")
    aqUtils.Delay(2000)
    Project.Variables.eop_doc_url = self.page.URL
    self.get_object(self.pdf_pnl).Click()
    self.page.Wait()
    self.get_object(self.pdf_pnl)
    aqUtils.Delay(1000)
    self.page.Wait()
    element = self.get_object(self.download_btn)
    element.Click()
    browser.BrowserWindow(0).Keys("^[F4]")
    return pay_fact_key
   
  def get_event_status(self,pay_fact_key):
    # To get the event details
    headers = self.get_object(self.event_hdr_xpath).contentText.split('\n')
    headers.pop(headers.index('Select'))
    headers.pop(headers.index('Documents'))
    values = self.get_object(self.desired_row.format(pay_fact_key)).contentText.split('\n')
    return dict(zip(headers, values))

  
  def get_data_from_pdf(self,pdf_content,keyword):
          
          eachline = pdf_content.split("\r\n")[0].split('\n') 
          list_dict = []
          total_lines = len(eachline)
          for each_line in range(total_lines):
            inner_dict = {}
            if keyword == "claim_lines":
              temp = ['code','tooth_or_cavity','date_of_service','Submitted','Contract Allowance','Plan Allowance','Ded.'
              ,'Over Max','COB','Plan Coins%','Plan Plays','Patient Pays','Prov Adjust','Message code(s)']
              found_val = re.search("^D[0-9]{4}",eachline[each_line])
              if found_val != None :
                codes_list = eachline[each_line].split(' ')
                pos = 0
                for each_value in range(len(temp)):
                    if len(temp) == len(codes_list):
                      inner_dict[temp[each_value]] = codes_list[each_value]
                    elif len(codes_list) <= 13:
                      if temp[each_value] == 'code':
                        inner_dict[temp[each_value]] = codes_list[each_value]
                      elif temp[each_value] == 'tooth_or_cavity' :
                        if codes_list[each_value].find('/') == 2:
                          inner_dict[temp[each_value]] = ' '
                          pos = pos+1
                        else:
                          inner_dict[temp[each_value]] = codes_list[each_value] 
                          pos = pos+1
                        
                      elif temp[each_value] == 'date_of_service' :
                        if codes_list[each_value].find('/') == 2 :
                           inner_dict[temp[each_value]] = codes_list[each_value] 
                           pos = pos+1
                        elif codes_list[each_value-1].find('/') == 2:
                           inner_dict[temp[each_value]] = codes_list[each_value-1]
                           
                           
                      elif len(codes_list) == 13 :
                        if temp[each_value] != 'Message code(s)': 
                          if pos ==1 :
                            inner_dict[temp[each_value]] = codes_list[each_value-1] 
                          else:
                            inner_dict[temp[each_value]] = codes_list[each_value]   
                    
                        elif temp[each_value] == 'Message code(s)':     
                          if re.search('^\$',codes_list[each_value-1]) != None :
                            inner_dict[temp[each_value]] = ' '
                          else:
                            if codes_list[each_value-1].find('M') > -1 :
                              inner_dict[temp[each_value]] = codes_list[each_value-1] 
                              
                      elif len(codes_list) == 12 :
                        if temp[each_value] != 'Message code(s)':
                          if pos ==1 :
                            inner_dict[temp[each_value]] = codes_list[each_value-1] 
                          else:
                            inner_dict[temp[each_value]] = codes_list[each_value]
                            
                        elif temp[each_value] == 'Message code(s)':
                          if re.search('^\$',codes_list[each_value-2]) != None :
                            inner_dict[temp[each_value]] = ' '
                          else:
                            if codes_list[each_value-2].find('M') > -1 :
                              inner_dict[temp[each_value]] = codes_list[each_value-2]
                       
                
                
                list_dict.append(inner_dict)
                
            elif keyword == 'check_num' :   
              found_val = re.search("^[0-9]{8}$",eachline[each_line])
              if found_val != None :
                inner_dict[keyword] = eachline[each_line]
                list_dict.append(inner_dict)
                break
            elif keyword == 'amount' : 
              found_val = re.search("^\$",eachline[each_line])
              if found_val != None :
                inner_dict[keyword] = eachline[each_line]
                list_dict.append(inner_dict)
                break   
            elif keyword == 'claim_summary' : 
              temp = ['Subscriber Name', 'Subscriber ID', 'Provider ID/Loc',  'Patient Name', 'Birthdate',  'Interest', 'Claim NO']
              found_val = re.search("[0-9]{12}$",eachline[each_line])
              if found_val != None :
                inner_dict = {}
                codes_list = eachline[each_line].split(' ')
                for each_value in range(len(temp)):
                  if temp[each_value] == 'Subscriber Name' and len(codes_list)>7 :
                    if len(codes_list) >= 8: 
                        namein_codes_list = eachline[each_line].split(',')[0]
                        sub_id = re.search('^[0-9]{14}',codes_list[each_value+1])
                        if sub_id != None:
                          sub_name = codes_list[each_value] 
                        else:
                          sub_id = re.search('^[0-9]{14}',codes_list[each_value+2])
                          if sub_id != None: 
                            sub_name = codes_list[each_value] +codes_list[each_value+1]
                          else:
                            sub_name = codes_list[each_value]+ ' '+codes_list[each_value+1]+ ' '+codes_list[each_value+2]
                        inner_dict[temp[each_value]] = sub_name
                  elif len(codes_list) == 8 :
                    inner_dict[temp[each_value]] = codes_list[each_value+1]
                  elif len(codes_list) == 9 :
                    inner_dict[temp[each_value]] = codes_list[each_value+2]
                  else:
                    inner_dict[temp[each_value]] = codes_list[each_value]
                list_dict.append(inner_dict)
            
            elif keyword == 'total' : 
              found_val = re.search("^TOTAL",eachline[each_line])
              if found_val != None :
                inner_dict[keyword] = eachline[each_line].replace('TOTAL','').strip()
                list_dict.append(inner_dict)  
              
            elif keyword == 'date' : 
              temp = [keyword]
              found_val = re.search("^[0-9]{2}/[0-9]{2}/[0-9]{4}",eachline[each_line])
              
              if found_val != None :
                inner_dict[keyword] = eachline[each_line]
                list_dict.append(inner_dict)
                break
              
            elif keyword == 'message_codes' : 
              found_val = re.search("MESSAGE CODE EXPLANATION:",eachline[each_line])
              count_dos = 1
              if found_val != None :
                for service_date in  range(total_lines):
                  found_val_date = re.search("^[0-9]{2}/[0-9]{2}/[0-9]{4}",eachline[each_line+service_date+1])
                  if found_val_date == None:
                    count_dos = count_dos+1
                    continue
                  else:
                    break
                for each_mscode in range(count_dos):
                  inner_dict = {}
                  found_val_1digit = re.search("^[0-9] ",eachline[each_line+each_mscode+1])
                  found_val_2digits = re.search("^[0-9]{2} " ,eachline[each_line+each_mscode+1])
                  found_val_3digits = re.search("^[0-9]{3} ",eachline[each_line+each_mscode+1])
                  found_val_1char = re.search("^[A-Z]-",eachline[each_line+each_mscode+1])
                  found_val_2char_1digit = re.search("^[A-Z]{2}-[0-9]{1} " ,eachline[each_line+each_mscode+1])
                  found_val_char_2digit = re.search("^[A-Z]{2}-[0-9]{2} " ,eachline[each_line+each_mscode+1])
                  found_val_char_3digit = re.search("^[A-Z]{3}-[0-9]{3} " or "^[A-Z]{2}-[0-9]{3} ",eachline[each_line+each_mscode+1])
                  found_val_3char_3digit = re.search("^[A-Z]{3}[0-9]{3} ",eachline[each_line+each_mscode+1])
                  found_values_list = [found_val_1digit,found_val_2digits,found_val_3digits,found_val_1char,found_val_2char_1digit,found_val_char_2digit,found_val_char_3digit,found_val_3char_3digit]
                  if found_val != None and found_val_1digit != None or  found_val_2digits!=None or found_val_3digits != None or found_val_1char != None or found_val_2char_1digit != None or found_val_char_2digit != None or found_val_char_3digit!=None or found_val_3char_3digit != None:
                    messagecodes =  eachline[each_line+each_mscode+1]
                    if re.search('[0-9]',eachline[each_line+each_mscode+2])== None :
                      messagecodes = messagecodes + eachline[each_line+each_mscode+2]
                      if re.search('[0-9]',eachline[each_line+each_mscode+3])== None :
                        messagecodes = messagecodes + eachline[each_line+each_mscode+3]
                    inner_dict[keyword] = messagecodes
                    list_dict.append(inner_dict)
            elif keyword == 'total_submitted' or keyword == 'total_paid': 
              found_val = re.search("^Provider ID:",eachline[each_line])
              if found_val != None :
                if keyword == 'total_submitted':
                  if eachline[each_line].split('Total ')[1].split(': ')[0] == 'Submitted':
                    inner_dict[keyword] = eachline[each_line].split('Total ')[1].split(': ')[1]
                elif keyword == 'total_paid':
                  if eachline[each_line].split('Total ')[2].split(': ')[0] == 'Paid':
                    inner_dict[keyword] =  eachline[each_line].split('Total ')[2].split(': ')[1]
                list_dict.append(inner_dict)
              
            elif keyword == "payee" or keyword == "payee_address":
              address = ' '
              found_val_without_check = re.search("EOPADDRESS",eachline[each_line])
              found_val_with_check = re.search("^\$",eachline[each_line])
              if found_val_without_check != None or found_val_with_check != None:
                if keyword == "payee" :
                  inner_dict[keyword] = eachline[each_line+1]
                  list_dict.append(inner_dict)
                  break
                elif keyword == "payee_address" and found_val_with_check != None :
                  address_lines_withcheck = re.search("[0-9]{8}",eachline[each_line+len(eachline) - (each_line+1)-1])
                  for address_line in range (len(eachline) - (each_line+1)-2):
                    if address_lines_withcheck != None and re.search('[0-9]',eachline[each_line+address_line+1])!= None:
                      if re.search(eachline[each_line+address_line+1],address) == None:
                        address = address + eachline[each_line+address_line+1] +' '
                      inner_dict[keyword] = address
                  list_dict.append(inner_dict)
                  
                elif keyword == "payee_address" and found_val_without_check != None :
                  address_lines_withoutcheck = re.search("TEST",eachline[each_line+len(eachline) - (each_line+1)])
                  for address_line in range (len(eachline) - (each_line+1)-1):
                    if address_lines_withoutcheck != None :
                      if re.search(eachline[each_line+address_line+2],address) == None:
                        if re.search('TEST',eachline[each_line+address_line+2]) != None:
                          address = address + eachline[each_line+address_line+2].split('TEST')[0]
                        else:
                          address = address + eachline[each_line+address_line+2] +' '
                      inner_dict[keyword] = address
                  list_dict.append(inner_dict)
          Log.Message(str(list_dict))
          return list_dict
def example_get_data_from_pdf():
  home = Home_Page()
  import json
  file_path =  "C:\\Users\\lveerappa\\Downloads\\eop_189004_05192023.pdf"
  pdf_content = CommonFunctions.read_PDF(file_path,0)
#  keyword = "total"
  Log.Message(pdf_content)
  data = home.get_data_from_pdf(pdf_content,'message_codes')
  
def tt():
  home = Home_Page()
  home.get_pdf()
      
    
    
    
