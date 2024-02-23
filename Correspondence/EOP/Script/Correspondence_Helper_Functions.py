import PyPDF2
import re
from Basic_Actions import Basic_Actions
import CommonFunctions

class Correspondence_Helper_Functions:

  def get_check(self,pdf_content):
      eachline = pdf_content.split("\r\n")[0].split('\n') 
      inner_dict = {}
      total_lines = len(eachline)
      temp = ["bank_info","check_id","dollar_literal","dollar_amount","payee","payee_address","routing_number","account_number","check_number"]
      for each_temp in range(len(temp)):
        for each_line in range(total_lines):
          if temp[each_temp] == "bank_info":
            found_val = re.search("^Refer",eachline[each_line])
            if found_val != None:
              inner_dict[temp[each_temp]] = eachline[each_line+1]+ eachline[each_line+2]+str(eachline[each_line+3])[:-5]

          elif temp[each_temp] == "check_id":
            found_val = re.search("^[0-9]{8}$",eachline[each_line])
            if found_val != None:
              codes_list = eachline[each_line].split(' ')
              for each_value in range(len(codes_list)):
                inner_dict[temp[each_temp]] = codes_list[each_value]

          elif temp[each_temp] == "dollar_literal": 
            found_val = eachline[each_line].find('**')
            if found_val != -1:
              codes_list = eachline[each_line].replace('**','')
              inner_dict[temp[each_temp]] = codes_list.strip()

          elif temp[each_temp] == "dollar_amount":
            found_val = re.search("^\$",eachline[each_line])
            if found_val != None:
              inner_dict[temp[each_temp]] = eachline[each_line]
              
          elif temp[each_temp] == "payee":
            found_val = re.search("^\$",eachline[each_line])
            if found_val != None:
              inner_dict[temp[each_temp]] = eachline[each_line+1]

          elif temp[each_temp] == "payee_address":
            found_val = re.search("^\$",eachline[each_line])
            if found_val != None:
              is_check_num = re.search("^[0-9]{8}",eachline[each_line+7])
              if is_check_num != None:
                inner_dict[temp[each_temp]] = eachline[each_line+3]+" "+eachline[each_line+5]
              else:
                inner_dict[temp[each_temp]] = eachline[each_line+3]+" "+eachline[each_line+5]+" "+eachline[each_line+7]
              
          elif temp[each_temp] == "routing_number":
            found_val = re.search("^[A-Z][0-9]{8}",eachline[each_line])
            if found_val != None:
              inner_dict[temp[each_temp]] = eachline[each_line].split()[0][1:9]
              
          elif temp[each_temp] == "account_number":
            found_val = re.search("^ [A-Z][0-9]{9}[A-Z] ",eachline[each_line])
            if found_val != None:
              inner_dict[temp[each_temp]] = eachline[each_line].split()[0][1:-1]
              
          elif temp[each_temp] == "check_number":
            found_val = re.search("^ [A-Z][0-9]{9}[A-Z] ",eachline[each_line])
            if found_val != None:
              inner_dict[temp[each_temp]] = eachline[each_line].split()[1][:-1]
              
      return inner_dict

def example_get_data_from_pdf():
  import json
  file_path =  "C:\\Users\\lveerappa\\Downloads\\eop_187056_05112023.pdf"
  pdf_content = CommonFunctions.read_PDF(file_path,0)
  chf = Correspondence_Helper_Functions()
  inner_dict = chf.get_check(pdf_content)
  Log.Message(str(inner_dict))
  