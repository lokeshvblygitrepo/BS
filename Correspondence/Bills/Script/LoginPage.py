home_btn_xpath = "//span[text()='CORRESPONDENCE360']"
adfs_btn_xpath = "(//input[@value='ddva-adfs-provider'])[2]" 
first_row = "(//mat-row//mat-cell)[1]"

browser=Project.Variables.required_browser
      
def enter_credentials():
  TestedApps.chrome.Run()
  Sys.Browser(browser).BrowserWindow(0).Maximize()
  page = Sys.Browser(browser).Page("*")
  page.WaitChild(adfs_btn_xpath,'6000')
  adfs = page.WaitElement(adfs_btn_xpath,5000)
  adfs.Click()
  login_window = page.WaitChild('Login',50000)
  if login_window.Exists :
    page.Login().UserName = "QAAutomationPortal"
    page.Login().Password = "U2#h8?Pw"
    page.Login().Button("OK").Click()
    page.wait()
    page.WaitElement(first_row,'30000')

def login():
  if Sys.WaitProcess(browser,500).Exists:
    page = Sys.Browser(browser).Page("*")
    home_btn =  page.WaitElement(home_btn_xpath,'10000')
    if home_btn.Exists:
      home_btn.Click()
      page.Keys("[F5]")
      page.Wait()
      home = page.WaitElement(home_btn_xpath,'10000')
      if home.Exists:
        Log.Message("User is Logged In!!!")
      else:
          Sys.Process(browser).Close()
          enter_credentials()
    else:     
      Sys.Process(browser).Close()
      enter_credentials()
  else:
    enter_credentials()