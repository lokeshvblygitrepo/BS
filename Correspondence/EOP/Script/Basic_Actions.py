class Basic_Actions:
  def __init__(self):
    
    self.page = Sys.Browser("Chrome").Page("*")
    self.wait_time = 15000
    
    
    
  def get_object(self,locator):
     #Function to get an object
     #locator : xpath/css of the element
     #wait_time in msecs
     #Returns the object if found, else None
     
     element = self.page.WaitElement(locator,self.wait_time)
     if element.Exists:
       return element
     else: 
       return None    
      
  def get_objects(self,locator):
      #Function to get a list of objects
      #locator : xpath/css of the element
      #wait_time in msecs
      #Returns the object if found, else None
        
     element = self.page.WaitElement(locator,self.wait_time)
     if element is not None:
       return self.page.FindElements(locator)
     else: 
       return None
     
          
  def click(self,object):
#     object : The object to be clicked
#     Function to click an object
    object.Click()
    
  def dbl_click(self,object):
#     object : The object to be clicked
#     Function to click an object
    object.DblClick()
          
  def clear_data(self,obj):
    obj.click()
    obj.Keys("^a")
    obj.Keys("[BS]")