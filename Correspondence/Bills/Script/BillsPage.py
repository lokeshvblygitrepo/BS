from BasicActions import Basic_Actions
import CommonFunctions
import re

class Bills_Page(Basic_Actions):
  
  def __init__(self):
    super().__init__()
    page_url = '''Page("https://%s.%s.keyspring.com/*")'''%(Project.Variables.client_id,Project.Variables.env)
    self.page = Sys.Browser("Chrome").WaitChild(page_url, 10000)
    self.bills_icn_xpath = "//span[text()='Bills']/parent::a"
    self.indiv_risk_bill_icn_xpath = "//a[contains(text(),'{}')]"
    self.indiv_rskbill_chkbox = "//input[@id='mat-mdc-checkbox-9-input']" #"//a[contains(text(),'{}')]/ancestor::mat-row//mat-checkbox"
    self.bill_cycle_chkbx_cmn = "//span[normalize-space(text())='{}']/ancestor::mat-row//mat-checkbox"
    self.generate_bill_btn = "//span[normalize-space(text())='Generate {} Bills']"
    self.events_count = "//a[text()=' {} Individual Group Risk ']//ancestor::mat-row//mat-cell[4]"
    
  def generate_bills(self,bill_type,list_bill_cycles):
    # Function to generate bills 
    # bill_type : Type of bill to be generated: eg -  'Asc Admin Fee' , 'Individual Group Risk'...
    # list_bill_cycle : ['DDVA Individual Group Risk'] or ['DDVA ASC Admin Fee','DDVA ASC Admin Fee Self-Billedl']...
    self.get_object(self.bills_icn_xpath).Click()
    for bill_cyc in list_bill_cycles:
      if 'Individual Group Risk' in bill_cyc:
        bill_cycle_element = self.get_object(self.indiv_rskbill_chkbox)
        if not bill_cycle_element.checked:
          bill_cycle_element.Click()
        for itr in range(0,25) :
          event_count = self.get_object(self.events_count.format( Project.Variables.client_id)).ContentText
          if int(event_count)>0:
            self.get_object(self.generate_bill_btn.format(bill_type.lower())).Click()
            break
          else:
            self.page.Keys("[F5]")
            aqUtils.Delay(5000)
          
  
def tt():
  home = Bills_Page()
  home.generate_bills('Individual Group Risk',['{} Individual Group Risk'.format(Project.Variables.client_id.upper())])