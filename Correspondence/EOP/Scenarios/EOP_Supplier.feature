Feature: EOP for suppliers (Test Plan: KSQA-368)

  Scenario: EOP - Supplier payment type Check, with some payment and email (KSQA-358)
    Given I have a "supplier" claim with payment type "Check" "with" email and "some" payment
    When I run "DDVA Weekly Claims Payment Run - Supplier" 
    Then Sent to print vendor for "supplier" 
    And I download "EOP - Supplier With Check" PDF document
    And EOP is generated "with" check
    And the data for "supplier" in pdf matches with HE data
    And the link is created in HE attachments
    
  Scenario: EOP - Supplier payment type Check, with zero payment and email (KSQA-359)
    Given I have a "supplier" claim with payment type "Check" "with" email and "zero" payment
    When I run "DDVA Weekly Claims Payment Run - Supplier"
    Then I download "EOP - Supplier Without Check" PDF document 
    And EOP is generated "without" check
    And the data for "supplier" in pdf matches with HE data
    
  Scenario: EOP - Supplier payment type Check, with some payment and no email (KSQA-360)
    Given I have a "supplier" claim with payment type "Check" "without" email and "some" payment
    When I run "DDVA Weekly Claims Payment Run - Supplier" 
    Then Sent to print vendor for "supplier" 
    And I download "EOP - Supplier With Check" PDF document
    And EOP is generated "with" check
    And the data for "supplier" in pdf matches with HE data
    And the link is created in HE attachments
    
  Scenario: EOP - Supplier payment type Check, with zero payment and no email (KSQA-361)
    Given I have a "supplier" claim with payment type "Check" "without" email and "zero" payment
    When I run "DDVA Weekly Claims Payment Run - Supplier"
    Then I download "EOP - Supplier Without Check" PDF document 
    And EOP is generated "without" check
    And the data for "supplier" in pdf matches with HE data
    And the link is created in HE attachments
    
  Scenario: EOP - Supplier payment type ACH, with some payment and email (KSQA-362)
      Given I have a "supplier" claim with payment type "ACH" "with" email and "some" payment
      When I run "DDVA Weekly Claims Payment Run - Supplier"
      Then I download "EOP - Supplier Without Check" PDF document
      And EOP is generated "without" check
      And the data for "supplier" in pdf matches with HE data
      And the link is created in HE attachments
    
   Scenario: EOP - Supplier payment type ACH, with some payment and no email (KSQA-363)
      Given I have a "supplier" claim with payment type "ACH" "without" email and "some" payment
      When I run "DDVA Weekly Claims Payment Run - Supplier"
      Then I download "EOP - Supplier Without Check" PDF document
      And email address is not available
      And EOP is generated "without" check
      And the data for "supplier" in pdf matches with HE data
      And the link is created in HE attachments
      
   Scenario: EOP - Supplier payment type ACH, with zero payment and email (KSQA-364)
      Given I have a "supplier" claim with payment type "ACH" "with" email and "zero" payment
      When I run "DDVA Weekly Claims Payment Run - Supplier" 
      Then I download "EOP - Supplier Without Check" PDF document
      And EOP is generated "without" check
      And the data for "supplier" in pdf matches with HE data
    
    Scenario: EOP - Supplier payment type ACH, with zero payment and no email (KSQA-365)
      Given I have a "supplier" claim with payment type "ACH" "without" email and "zero" payment
      When I run "DDVA Weekly Claims Payment Run - Supplier"
      Then I download "EOP - Supplier Without Check" PDF document 
      And EOP is generated "without" check    
      And the data for "supplier" in pdf matches with HE data