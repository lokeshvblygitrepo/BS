Feature: EOP for subscribers (Test Plan: KSQA-367)

  Scenario: EOP for subscirber with check, email and some payment (KSQA-348)
    Given I have a "subscriber" claim with payment type "Check" "with" email and "some" payment
    When I run "DDVA Weekly Claims Payment Run - Subscriber" 
    Then Sent to print vendor for "subscriber" 
    And I download "EOP - Subscriber With Check" PDF document
    And EOP is generated "with" check 
    And the data for "subscriber" in pdf matches with HE data
    And the link is created in HE attachments
    
  Scenario: EOP for subscirber with check, email and zero payment (KSQA-351)
    Given I have a "subscriber" claim with payment type "Check" "with" email and "zero" payment
    When I run "DDVA Weekly Claims Payment Run - Subscriber"
    Then I download "EOP - Subscriber Without Check" PDF document    
    And EOP is generated "without" check
    And the data for "subscriber" in pdf matches with HE data
    
  Scenario: EOP for subscirber with check, without email and some payment (KSQA-352)
    Given I have a "subscriber" claim with payment type "Check" "with" email and "some" payment
    When I run "DDVA Weekly Claims Payment Run - Subscriber"  
    Then Sent to print vendor for "subscriber" 
    And I download "EOP - Subscriber With Check" PDF document
    And EOP is generated "with" check
    And the data for "subscriber" in pdf matches with HE data
    And the link is created in HE attachments
    
  Scenario: EOP for subscirber with check, without email and zero payment (KSQA-353)
    Given I have a "subscriber" claim with payment type "Check" "without" email and "zero" payment
    When I run "DDVA Weekly Claims Payment Run - Subscriber" 
    Then I download "EOP - Subscriber Without Check" PDF document
    And EOP is generated "without" check
    And the data for "subscriber" in pdf matches with HE data
    
  Scenario: EOP - Subscriber payment type ACH, with some payment and email (KSQA-354)
    Given I have a "subscriber" claim with payment type "ACH" "with" email and "some" payment
    When I run "DDVA Weekly Claims Payment Run - Subscriber"
    Then I download "EOP - Subscriber Without Check" PDF document
    And EOP is generated "without" check
    And the data for "subscriber" in pdf matches with HE data
    And the link is created in HE attachments
    
  Scenario: EOP - Subscriber payment type ACH, with some payment and no email (KSQA-355)
    Given I have a "subscriber" claim with payment type "ACH" "without" email and "some" payment
    When I run "DDVA Weekly Claims Payment Run - Subscriber"
    Then I download "EOP - Subscriber Without Check" PDF document
    And email address is not available
    And EOP is generated "without" check
    And the data for "subscriber" in pdf matches with HE data
    And the link is created in HE attachments
    
  Scenario: EOP - Subscriber payment type ACH, with zero payment and email (KSQA-356)
    Given I have a "subscriber" claim with payment type "ACH" "with" email and "zero" payment
    When I run "DDVA Weekly Claims Payment Run - Subscriber"
    Then I download "EOP - Subscriber Without Check" PDF document
    And EOP is generated "without" check
    And the data for "subscriber" in pdf matches with HE data
    
  Scenario: EOP - Subscriber payment type ACH, with zero payment and no email (KSQA-357)
    Given I have a "subscriber" claim with payment type "ACH" "without" email and "zero" payment
    When I run "DDVA Weekly Claims Payment Run - Subscriber"
    Then I download "EOP - Subscriber Without Check" PDF document
    And email address is not available
    And EOP is generated "without" check
    And the data for "subscriber" in pdf matches with HE data
