from Basic_Actions import Basic_Actions
import CommonFunctions
import re

class Batch_Distribution_Pref_Page(Basic_Actions):
  
  def __init__(self):
    super().__init__()
    page_url = '''Page("https://%s.%s.keyspring.com/*")'''%(Project.Variables.client_id,Project.Variables.env)
    self.page = Sys.Browser("Chrome").WaitChild(page_url, 10000)
    self.home = "//span[@class='logo']"
    self.dashboard_icn_xpath = "//mat-icon[text()='dashboard']/parent::a"
    self.batch_dist_pref_link_xpath = "//*[text()='Batch Distribution Preference']"
    self.row_to_select_xpath = "//*[text()='{}']/ancestor::mat-row"
    
    
  def get_batch_dist_pref(self, batch_job_type):
    # To click on batch distribution prefrence link
    # and return current selected preference for
    # payor_attachment, paper, email
    # batch_job_type :  a valid batch job type, eg: Individual Risk Bill
     self.get_object(self.home).Click()
     self.get_object(self.dashboard_icn_xpath).Click()
     self.get_object(self.batch_dist_pref_link_xpath).Click()
     preferences = self.get_object(self.row_to_select_xpath.format(batch_job_type)).contentText.split('\n')
     return {'Payor Attachment':preferences[1],'Paper':preferences[2],'Email':preferences[3]}
     

def tt():
  home = Batch_Distribution_Pref_Page()
  home.get_batch_dist_pref("Individual Risk Bill")
     