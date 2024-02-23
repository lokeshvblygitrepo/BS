import SearchFunctions
import CommonFunctions
import re

  
def get_supplier_details(supplier_id,is_search=True):
  # To get  supplier name and address
  # supplier_npi : a valid supplier_npi from dw
  # is_search : True - search the supplier, False - Skip search, user when supplier details card is already open
  if is_search:
    SearchFunctions.searchTask( "Manager","Provider",'supplier', [{"name":"Supplier ID/NPI", "value":supplier_id}], True)
  home = Sys.Process("HealthEdge.Manager").WaitChild('''WinFormsObject("HomeForm")''')
  supplier_name = home.FindChild("labelText", '''Supplier Name:''',6).FindChild('Name','''WinFormsObject("TextEdit", "")''',3)
  sup_name_txt = supplier_name.wText
  tab_pnl = home.FindChild('Name','''WinFormsObject("panelControlDetail")''',3)
  tab = tab_pnl.FindChild('Name','''WinFormsObject("xtraTabControlSupplier")''',3) 
  tab.ClickTab('Contact')
  tab.WaitChild('''WinFormsObject("xtraTabPageContact")''',3000)
  other_address = tab.FindChild('Name','''WinFormsObject("repeaterPanelOtherAddress")''',5)
  corres_info = other_address.FindChild('Name','''WinFormsObject("RepeatableSupplierCorrespondenceInformation")''',3)
  
  panel_corres = corres_info.FindChild('Name','''WinFormsObject("headerGroupControlOtherCorrespondence")''',3)
  panel_corres.Click()
  panel_address = corres_info.WaitChild('''WinFormsObject("headerGroupControlCorrespondenceInformation")''',10000) 
  postal_address = panel_corres.FindChild("Name", '''WinFormsObject("subEntityPanelAddressInformation")''',5) 
  address = postal_address.FindChild("Name", '''WinFormsObject("autoEditAddress")''',2).FindChild("Name", '''WinFormsObject("TextEdit", "")''',5) 
  city = postal_address.FindChild("Name", '''WinFormsObject("autoEditCityName")''',2).FindChild("Name", '''WinFormsObject("TextEdit", "")''',5) 
  state = postal_address.FindChild("Name", '''WinFormsObject("autoEditState")''',2).FindChild("Name", '''WinFormsObject("LookUpEdit", "")''',5)
  zip = postal_address.FindChild("Name", '''WinFormsObject("autoEditZipCode")''',2).FindChild("Name", '''WinFormsObject("TextEdit", "")''',5) 
  country = postal_address.FindChild("Name", '''WinFormsObject("autoEditCountry")''',2).FindChild("Name", '''WinFormsObject("LookUpEdit", "")''',5)
  pay_to_address = []
  
  pay_to_address.append(address.Text.OleValue)  
  pay_to_address.append(city.Text.OleValue)
  pay_to_address.append(state.Text.OleValue)
  pay_to_address.append(zip.Text.OleValue)
  pay_to_address.append(country.Text.OleValue)
  Log.Message(sup_name_txt)
  Log.Message(str(pay_to_address))
  return sup_name_txt,pay_to_address

  
def get_provider():
   # To get  practitioner liscence
  home_form = Sys.Process("HealthEdge.Manager").WaitChild('''WinFormsObject("HomeForm")''',7000)
  panel_control_detail = home_form.waitWinFormsObject("panelControlDetail",3000)
  tab_control_claim = panel_control_detail.Findchild("WinFormsControlName","tabControlClaim",3)
  provider_ref = tab_control_claim.Findchild("WinFormsControlName","headerGroupProvider",6)  
  provider = provider_ref.Findchild("Name",'''WinFormsObject("textEditPractitionerID")''',8)
  pract_lisc_text = provider.Text.OleValue
  return pract_lisc_text
  
  
def get_claim_lines(view):
  #Function to get claim line details
  #view : Helps to select claim line view(Classic/Dental-Pricing) and return the result
  home = Sys.Process("HealthEdge.Manager").WaitChild('''WinFormsObject("HomeForm")''',10000)
  tab = home.FindChild('ClrClassName','''XtraTabControl''',3)
  tab.ClickTab('Lines')
  tab.WaitChild('''WinFormsObject("tabPageLines")''',5000)
  view_drpdwn = home.FindChild('ClrClassName','ImageComboBoxEdit',8)  
  selected_view = view_drpdwn.wText
  if selected_view.lower() != view.lower() :
    view_drpdwn.ClickItem(view)
  if view.lower()=='classic':  
    claim_pnl = home.FindChild('WinFormsControlName','repeaterClaimLines',9)
    lst_records = []
    for itr in range(1,claim_pnl.ChildCount+1):
      per_row = claim_pnl.FindChild('Text_3','{}:*'.format(str(itr)),2)
      lst_records.append(per_row.Text_3.OleValue)
    lst_temp = []
    for data in lst_records:
      lst_temp.append(data.split(','))
    lst_claim_lines = []
    for lines in lst_temp:
      dict_claim_lines = {}
      dict_claim_lines['Line'] = lines[0].split(': ')[0].strip()
      dict_claim_lines['Date'] = lines[0].split(': ')[1]
      dict_claim_lines['Code'] =lines[1]
      dict_claim_lines['Billed'] = lines[2].split('=')[1].strip()
      dict_claim_lines['HCC Amount'] = lines[3].split('=')[1].strip()
      dict_claim_lines['Paid'] = lines[4].split('=')[1].strip()
      dict_claim_lines['Member Responsibility'] = lines[5].split('=')[1].strip()
      lst_claim_lines.append(dict_claim_lines)
  elif view.lower()=='dental-pricing':
    lines_radio_control = home.FindChild('Name','''WinFormsObject("radioGroupHideLines")''',11)
    if lines_radio_control.Visible:
      text = lines_radio_control.wItem[0]
      lines_radio_control.ClickItem(text)
    grid = home.FindChild('Name','''WinFormsObject("gridControlResults")''',9)
    grid.load
    lst_claim_lines=[]
    for rc in range(0,grid.wRowCount):
      dict_claim_lines = {}
      for col in range(0,grid.wColumnCount):
        try:        
          dict_claim_lines.update({grid.wColumn[col]:grid.wValue[rc,grid.wColumn[col]].oleValue})
        except: #When no values present in a cell
          dict_claim_lines.update({grid.wColumn[col]:''})
      lst_claim_lines.append(dict_claim_lines)
  else:
    Log.Error("no claim lines present for the selected view %{}".format(view))
  return lst_claim_lines
  
  
  
def get_message():
    home_form = Sys.Process("HealthEdge.Manager").WinFormsObject("HomeForm")
    panel_control_detail = home_form.waitWinFormsObject("panelControlDetail",3000)
    tab_control_claim = panel_control_detail.FindChild("WinFormsControlName","tabControlClaim",3)
    
    tab_control_claim.ClickTab("Summary")
    claim_summary = panel_control_detail.WaitChild('''WinFormsObject("Claim")''',3000)
    
    grid_denials = claim_summary.FindChild("WinFormsControlName","gridControlDenials",6)
    
    codes = []
    for each_row in range(grid_denials.wRowCount):
      codes_dict = {}
      code = grid_denials.wValue[each_row,1]
      description = grid_denials.wValue[each_row,2]
      codes_dict[code.OleValue] = description.OleValue
      codes.append(codes_dict)
    
    return codes
    
    
def get_interest():
    
  interest_dict = {}
  home_form = Sys.Process("HealthEdge.Manager").WinFormsObject("HomeForm")
  panel_control_detail = home_form.waitWinFormsObject("panelControlDetail",3000)
  tab_control_claim = panel_control_detail.FindChild("WinFormsControlName","tabControlClaim",3)
    
  tab_control_claim.ClickTab("Financial History")
  financial_history = tab_control_claim.WaitChild('''WinFormsObject("tabPageFinancialHistory")''',3000)
    
  panel_control_top = financial_history.FindChild("WinFormsControlName","panelControlTop",2)
  edit_amount_interest = panel_control_top.FindChild("WinFormsControlName","textEditAmountInterest",5)
  interest_dict['interest'] = edit_amount_interest.wText
      
  return interest_dict
      
def get_check():
  home_form = Sys.Process("HealthEdge.Manager").WinFormsObject("HomeForm")
  panel_control_detail = home_form.waitWinFormsObject("panelControlDetail",10000)
  tab_control_claim = panel_control_detail.FindChild("WinFormsControlName","tabControlClaim",3)
  home_form.WaitChild('''WinFormsObject("hyperLinkLabelNetAdjustmentView")''',3000)
  tab_control_claim.ClickTab("Financial History")
  tab_control_claim.WaitChild('''WinFormsObject("tabPageFinancialHistory")''',20000)
  financial_history = tab_control_claim.WaitChild('''WinFormsObject("tabPageFinancialHistory")''',10000)
    
  panel_control_top = financial_history.FindChild("WinFormsControlName","panelControlTop",2)
  financial_history_control = financial_history.FindChild("WinFormsControlName","panelControlDetailView",2)
  financial_summary_view = financial_history.FindChild("WinFormsControlName","gridControlFinancialSummary",2)
  detail_view = panel_control_top.FindChild("WndCaption","Detail View",2)
  
  if not detail_view.Exists:
    panel_control_top.WaitChild('''WinFormsObject("hyperLinkLabelNetAdjustmentView")''',9000).Click()
    financial_history_control.WaitChild('''WinFormsObject("gridControlFinancialHistory")''',9000)
    
  list_check_details = []
  for each_item in range(financial_summary_view.wRowCount):
    check_details = {}
    try:
      check_details["check number"] = financial_summary_view.wValue[each_item,2].OleValue
    except:
      check_details["check number"] ='0'
    check_details["date"] = financial_summary_view.wValue[each_item,'Payment Date'].OleValue
    check_details["amount"] = "$"+str(financial_summary_view.wValue[each_item,"Net Claim Paid"].OleValue)
    list_check_details.append(check_details)
  Log.Message( str(list_check_details))    
  return list_check_details
  
def get_patient():
    patient_details = {}
    home_form = Sys.Process("HealthEdge.Manager").WinFormsObject("HomeForm")
    panel_control_detail = home_form.waitWinFormsObject("panelControlDetail",3000)
    tab_control_claim = panel_control_detail.Findchild("WinFormsControlName","tabControlClaim",3)
    member_reference = tab_control_claim.Findchild("WinFormsControlName","headerGroupControlMemberReference",6)
    hyper_member_name = member_reference.Findchild("WinFormsControlName","hyperLinkEditMemberName",3)
    member_name = hyper_member_name.Findchild("WinFormsControlName","hyperLinkEditHyperLinkId",3)
    member_id = member_reference.Findchild("WinFormsControlName","textEditMemberID",3)
    member_dob = member_reference.Findchild("WinFormsControlName","textEditMemberBirthDate",3)
    patient_details["member full name"] = member_name.Text.OleValue
    patient_details["member id"] = member_id.wText
    patient_details["member dob"] = member_dob.wText
    
    return patient_details
    
    
def get_subscription():
  subscription_details = {}
  home_form = Sys.Process("HealthEdge.Manager").WinFormsObject("HomeForm")
  panel_control = home_form.WinFormsObject("panelControlDetail")
  subscription_treeview = panel_control.Findchild("WinFormsControlName","treeListSubscription",7)
#  tab = home_form.WinFormsObject("panelControlDetail").WinFormsObject("Claim").WinFormsObject("tabControlClaim")
#  tab.ClickTab('Header')
  panel_control.WaitChild('''WinFormsObject("xtraTabPageContact")''',3000)
  subscription_name = subscription_treeview.FocusedValue.OleValue
  subscriber_name = subscription_name.split('(')[0]
  
  panel_control_version = home_form.Findchild("WinFormsControlName","panelControlVersion",1)
  version_summary = panel_control_version.Findchild("WinFormsControlName","VersionSummary",3)
  version_navigator = version_summary.Findchild("WinFormsControlName","versionNavigator",2)
  label_id = version_navigator.Findchild("WinFormsControlName","labelControlId",8)
  subscription_details["subscriber name"] = subscriber_name
  subscription_details["subscription id"] = label_id.Text.OleValue
  return subscription_details
  
def get_claim_number():
  # Function to get claim number from HE claims page
  home = Sys.Process("HealthEdge.Manager").WaitChild('''WinFormsObject("HomeForm")''',10000)  
  claim_no = home.FindChild("Name", '''WinFormsObject("autoEditClaimId")''',4).FindChild('Name','''WinFormsObject("TextEdit", "")''',3)
  return claim_no.Text.OleValue
 
def get_subscriber_details(subscriber_id,is_search=True):
  if is_search:
    SearchFunctions.searchTask("Manager","Members", "subscription", [{"name":"Member ID", "value":subscriber_id}],True)
  home = Sys.Process("HealthEdge.Manager").WaitChild('''WinFormsObject("HomeForm")''',10000)
  subscriber_name = home.FindChild("labelText", '''Primary Name:''',16).FindChild('Name','''WinFormsObject("personNameView")''',3)
  sub_name_txt = subscriber_name.Text.OleValue
  tab_pnl = home.FindChild('Name','''WinFormsObject("MemberView")''',6)
  tab = home.FindChild('Name','''WinFormsObject("tabControlMember")''',6) 
  tab.WaitChild('''WinFormsObject("xtraTabPageContact")''',3000)
  tab.ClickTab('Contact')
  tab.WaitChild('''WinFormsObject("xtraTabPageContact")''',10000)
  corp_control = home.FindChild('Name','''WinFormsObject("memberCorrespondenceControl")''',10)
  
  address_field = corp_control.FindChild('Name','''WinFormsObject("address")''',5)
  edit_address = address_field.FindChild('WinFormsControlName','''autoEditAddress''',5)
  control_auto_edit =edit_address.FindChild('WinFormsControlName','''panelControlAutoEdit''',3)
  address = control_auto_edit.FindChild('Name','''WinFormsObject("TextEdit", "")''',2)
  postal_address = address_field.FindChild('WinFormsControlName','''subEntityPanelPostalAddress''',5)
  edit_city = postal_address.FindChild('WinFormsControlName','''autoEditCityName''',5)
  city = edit_city.FindChild('Name','''WinFormsObject("TextEdit", "")''',2) 
  edit_state = postal_address.FindChild("WinFormsControlName", '''autoEditState''',2)
  state = edit_state.FindChild("Name", '''WinFormsObject("LookUpEdit", "")''',2)
  edit_zip = postal_address.FindChild("WinFormsControlName", '''autoEditZipCode''',2)
  zip_auto_edit = edit_zip.FindChild('WinFormsControlName','''panelControlAutoEdit''',3)
  zip = zip_auto_edit.FindChild('Name','''WinFormsObject("TextEdit", "")''',2)
  sub_address = []
  sub_address.append(address.Text.OleValue)  
  sub_address.append(city.Text.OleValue)
  sub_address.append(state.Text.OleValue)
  sub_address.append(zip.Text.OleValue)
  Log.Message(str(sub_address))
  Log.Message(sub_name_txt)

  return sub_name_txt,sub_address

    
def example_Get_Data_From_HE():
  home = Sys.Process("HealthEdge.Manager").WaitChild('''WinFormsObject("HomeForm")''',10000)
  control = home.FindChild('Name','''WinFormsObject("radioGroupHideLines")''',11)
  text = control.wItem[0]
  control.ClickItem(text)
  pass


def get_available_service(member_id,lstServices):
  CommonFunctions.actionTopBarHomePage('Manager','Home')
  SearchFunctions.searchTask( "Manager","Members","subscription", [{"name":"Member ID", "value":member_id}], True)  
  
  objHome = Sys.Process("HealthEdge.Manager").WinFormsObject("HomeForm")
  objSubrView = objHome.WaitChild('''WinFormsObject("panelControlDetail")''',30000).WaitChild('''WinFormsObject("SubscriptionView")''',30000)
  objTab = objSubrView.FindChild("WinFormsControlName","tabControlMember",4)
  objTab.ClickTab('Accumulators')
  
  objAccumTab = objTab.WaitChild('''WinFormsObject("xtraTabPageAccumulators")''',60000)
  objProvision = objAccumTab.FindChild('WinFormsControlName','textEditProvisionLabel',3)
  objProvision.WinFormsObject("TextBoxMaskBox", "").Keys('BLS')
  
  #click on Apply
  objAccumTab.FindChild("WinFormsControlName","simpleButtonApply",3).Click()
  
  is_loading = True
  while is_loading:
    objGrid = objAccumTab.FindChild("WinFormsControlName","gridControlAccumulators",3)
    if objGrid.Exists:
      objGridData = objGrid.wChildView[0,0]
      if objGridData.wRowCount > 0:
        is_loading = False
  
  for i in range(objGridData.wRowCount):

    strService = objGridData.wValue[i, "Provision Label"].OleValue
    intRemainingCnt = int(objGridData.wValue[i,"Remaining"].OleValue)
    
    today_date = aqConvert.DateTimeToFormatStr(aqDateTime.Today(), "%m/%d/%Y")
    
    if strService in lstServices and intRemainingCnt > 0:
      strEffectiveDate = objGridData.wValue[i, "Effective Date"].OleValue
      if strEffectiveDate == 'Lifetime':
        return strService
      else:
        listDates = strEffectiveDate.split('through')
        strStartDate = listDates[0].strip()
        strEndDate = listDates[1].strip()
        if aqConvert.StrToDate(today_date) >= aqConvert.StrToDate(strStartDate) and  aqConvert.StrToDate(today_date) <= aqConvert.StrToDate(strEndDate):
          return strService
      
  return None
  
def get_he_version():
  Project.Variables.he_version = CommonFunctions.get_he_latest_version()
  
def get_attachments(payment_number):
  #To get Links from payments attachment tab
  SearchFunctions.searchTask("Manager","Financials", "payment", [{"name":"Payment Number", "value":payment_number}],True)
  home = Sys.Process("HealthEdge.Manager").WaitChild('''WinFormsObject("HomeForm")''',10000)
  parent_panel = home.WinFormsObject("panelControlDetail").WinFormsObject("PaymentView").WinFormsObject("xtraTabControl")
  parent_panel.ClickTab("Attachments")
  parent_panel.WaitChild('''WinFormsObject("xtraTabPageAttachments")''',10000)
  attachment_tab_parent = parent_panel.FindChild('Name','WinFormsObject("panelControl3")',8)
  attachment_tab = attachment_tab_parent.WaitChild('''WinFormsObject("gridControl1")''',10000)
  row_count = attachment_tab.wRowCount
  lst_link = []
  for itr in range(0,row_count):
    lst_link.append(attachment_tab.wValue[itr,1].OleValue)
  return lst_link
      