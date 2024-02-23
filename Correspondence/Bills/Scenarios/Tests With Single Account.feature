Feature: Tests with Single Account (Test Plan: KSQA-465)
      
  Scenario Outline: Verify the bill for an account type who is child, not handicapped,correspondence definition mail and delivery preference paper (KSQA-406)
    Given I run a bill for a subscription with "<account_type>" who is "child" and "not handicapped",correspondence definition "E-Mail",member  delivery preference "Paper" and responsibile party "Legal Guardian" "with" email
    When I Generate "Individual Risk Bills" 
    Then batch status should be "Completed"
    And I download the pdf document
    And the document delivery type is "PAPER"
    And I download the xlsx document
    And the data in pdf and xlsx documents matches with data in HE
    And the address in pdf matches with "responsible party" address
    
    Examples: 
      |account_type|
      |Non-Exchange Individual|
      
  Scenario Outline: Verify the bill for an account type who is child, not handicapped,correspondence definition mail and delivery preference email (KSQA-407)
    Given I run a bill for a subscription with "<account_type>" who is "child" and "not handicapped",correspondence definition "E-Mail",member  delivery preference "Nothing" and responsibile party "Legal Guardian" "with" email
    When I Generate "Individual Risk Bills" 
    Then batch status should be "Completed"
    And I download the pdf document
    And the document delivery type is "PAPER"
    And I download the xlsx document
    And the data in pdf and xlsx documents matches with data in HE
    And the address in pdf matches with "responsible party" address
    Examples: 
      |account_type|
      |Non-Exchange Individual|
      
  Scenario Outline: Verify the bill for an account type who is child, not handicapped,member delivery preference nothing,legal guardian without email  (KSQA-409)
    Given I run a bill for a subscription with "<account_type>" who is "child" and "not handicapped",correspondence definition "E-Mail",member  delivery preference "Nothing" and responsibile party "Legal Guardian" "with out" email
    When I Generate "Individual Risk Bills" 
    Then batch status should be "Completed"
    And I download the pdf document
    And the document delivery type is "PAPER"
    And I download the xlsx document
    And the data in pdf and xlsx documents matches with data in HE
    And the address in pdf matches with "responsible party" address
    Examples: 
      |account_type|
      |Non-Exchange Individual|
      
  Scenario Outline: Verify the bill for an account type who is child, not handicapped,member delivery preference online,legal guardian with email (KSQA-410)
    Given I run a bill for a subscription with "<account_type>" who is "child" and "not handicapped",correspondence definition "E-Mail",member  delivery preference "Online" and responsibile party "Legal Guardian" "with" email
    When I Generate "Individual Risk Bills" 
    Then batch status should be "Completed"
    And I download the pdf document
    And the document delivery type is "EMAIL_WITH_ATTACHMENT"
    And I download the xlsx document
    And the data in pdf and xlsx documents matches with data in HE
    And the address in pdf matches with "responsible party" address
    Examples: 
      |account_type|
      |Non-Exchange Individual| 
      
  Scenario Outline: Verify the bill for an account type who is adult, handicapped,member delivery preference nothing  legal guardian with email(KSQA-411)
    Given I run a bill for a subscription with "<account_type>" who is "adult" and "handicapped",correspondence definition "E-Mail",member  delivery preference "Nothing" and responsibile party "Legal Guardian" "with" email
    When I Generate "Individual Risk Bills" 
    Then batch status should be "Completed"
    And I download the pdf document
    And the document delivery type is "PAPER"
    And I download the xlsx document
    And the data in pdf and xlsx documents matches with data in HE
    And the address in pdf matches with "responsible party" address
    Examples: 
      |account_type|
      |Non-Exchange Individual|
      
  Scenario Outline: Verify the bill for an account type who is adult, handicapped,member delivery preference paper,legal guardian with email (KSQA-412)
    Given I run a bill for a subscription with "<account_type>" who is "adult" and "handicapped",correspondence definition "E-Mail",member  delivery preference "Paper" and responsibile party "Legal Guardian" "with" email
    When I Generate "Individual Risk Bills" 
    Then batch status should be "Completed"
    And I download the pdf document
    And the document delivery type is "PAPER"
    And I download the xlsx document
    And the data in pdf and xlsx documents matches with data in HE
    And the address in pdf matches with "responsible party" address
    Examples: 
      |account_type|
      |Non-Exchange Individual|  
      
  Scenario Outline: Verify the bill for an account type who is adult, handicapped,member delivery preference Nothing,legal guardian without email (KSQA-414)
    Given I run a bill for a subscription with "<account_type>" who is "adult" and "handicapped",correspondence definition "E-Mail",member  delivery preference "Nothing" and responsibile party "Legal Guardian" "with out" email
    When I Generate "Individual Risk Bills" 
    Then batch status should be "Completed"
    And I download the pdf document
    And the document delivery type is "PAPER"
    And I download the xlsx document
    And the data in pdf and xlsx documents matches with data in HE
    And the address in pdf matches with "responsible party" address
    Examples: 
      |account_type|
      |Non-Exchange Individual|   
      
  Scenario Outline: Verify the bill for an account type who is adult, handicapped,member delivery preference online,legal guardian with email (KSQA-415)
    Given I run a bill for a subscription with "<account_type>" who is "adult" and "handicapped",correspondence definition "E-Mail",member  delivery preference "Online" and responsibile party "Legal Guardian" "with" email
    When I Generate "Individual Risk Bills" 
    Then batch status should be "Completed"
    And I download the pdf document
    And the document delivery type is "EMAIL_WITH_ATTACHMENT"
    And I download the xlsx document
    And the data in pdf and xlsx documents matches with data in HE
    And the address in pdf matches with "responsible party" address
    Examples: 
      |account_type|
      |Non-Exchange Individual|   
   
  Scenario Outline: Verify the bill for an account type who is adult, not handicapped,member delivery preference online,legal guardian with email (KSQA-416)
    Given I run a bill for a subscription with "<account_type>" who is "adult" and "not handicapped",correspondence definition "E-Mail",member  delivery preference "Nothing" and responsibile party "Legal Guardian" "with" email
    When I Generate "Individual Risk Bills" 
    Then batch status should be "Completed"
    And I download the pdf document
    And the document delivery type is "PAPER"
    And I download the xlsx document
    And the data in pdf and xlsx documents matches with data in HE
    And the address in pdf matches with "responsible party" address
    Examples: 
      |account_type|
      |ACA Exchange Individual|   
      
  Scenario Outline: Verify the bill for an account type who is adult, not handicapped,member delivery preference paper,legal guardian with email (KSQA-417)
    Given I run a bill for a subscription with "<account_type>" who is "adult" and "not handicapped",correspondence definition "E-Mail",member  delivery preference "Paper" and responsibile party "Legal Guardian" "with" email
    When I Generate "Individual Risk Bills" 
    Then batch status should be "Completed"
    And I download the pdf document
    And the document delivery type is "PAPER"
    And I download the xlsx document
    And the data in pdf and xlsx documents matches with data in HE
    And the address in pdf matches with "responsible party" address
    Examples: 
      |account_type|
      |ACA Exchange Individual|
   
  Scenario Outline: Verify the bill for an account type who is adult, handicapped,member delivery preference Nothing,legal guardian without email (KSQA-419)
    Given I run a bill for a subscription with "<account_type>" who is "adult" and "not handicapped",correspondence definition "E-Mail",member  delivery preference "Nothig" and responsibile party "Legal Guardian" "with out" email
    When I Generate "Individual Risk Bills" 
    Then batch status should be "Completed"
    And I download the pdf document
    And the document delivery type is "PAPER"
    And I download the xlsx document
    And the data in pdf and xlsx documents matches with data in HE
    And the address in pdf matches with "responsible party" address
    Examples: 
      |account_type|
      |ACA Exchange Individual|  
         
  Scenario Outline: Verify the bill for an account type who is adult, handicapped,member delivery preference online,legal guardian with email (KSQA-420)
    Given I run a bill for a subscription with "<account_type>" who is "adult" and "not handicapped",correspondence definition "E-Mail",member  delivery preference "Online" and responsibile party "Legal Guardian" "with" email
    When I Generate "Individual Risk Bills" 
    Then batch status should be "Completed"
    And I download the pdf document
    And the document delivery type is "EMAIL_WITH_ATTACHMENT"
    And I download the xlsx document
    And the data in pdf and xlsx documents matches with data in HE
    And the address in pdf matches with "responsible party" address
    Examples: 
      |account_type|
      |ACA Exchange Individual|     

  Scenario Outline: Verify the bill for an account type who is adult, not handicapped,member delivery preference paper (KSQA-421)
    Given I run a bill for a subscription with "<account_type>" who is "adult" and "not handicapped",correspondence definition "E-Mail",member  delivery preference "Paper" and responsibile party "None" "with out" email
    When I Generate "Individual Risk Bills" 
    Then batch status should be "Completed"
    And I download the pdf document
    And the document delivery type is "PAPER"
    And I download the xlsx document
    And the data in pdf and xlsx documents matches with data in HE
    And the address in pdf matches with "correspondence" address
    Examples: 
      |account_type|
      |ACA Exchange Individual|
      
   Scenario Outline: Verify the bill for an account type who is adult, not handicapped,member delivery preference Nothing (KSQA-422)
    Given I run a bill for a subscription with "<account_type>" who is "adult" and "not handicapped",correspondence definition "E-Mail",member  delivery preference "Nothing" and responsibile party "None" "with out" email
    When I Generate "Individual Risk Bills" 
    Then batch status should be "Completed"
    And I download the pdf document
    And the document delivery type is "PAPER"
    And I download the xlsx document
    And the data in pdf and xlsx documents matches with data in HE
    And the address in pdf matches with "correspondence" address
    Examples: 
      |account_type|
      |ACA Exchange Individual|
      
  Scenario Outline: Verify the bill for an account type who is adult, not handicapped,member delivery preference email (KSQA-423)
    Given I run a bill for a subscription with "<account_type>" who is "adult" and "not handicapped",correspondence definition "E-Mail",member  delivery preference "Online" and responsibile party "None" "with out" email
    When I Generate "Individual Risk Bills" 
    Then batch status should be "Completed"
    And I download the pdf document
    And the document delivery type is "EMAIL_WITH_ATTACHMENT"
    And I download the xlsx document
    And the data in pdf and xlsx documents matches with data in HE
    And the address in pdf matches with "correspondence" address
    Examples: 
      |account_type|
      |ACA Exchange Individual|
    
  Scenario Outline: Verify the bill for an account type who is adult after adding adjustments (KSQA-396)
    Given I run a bill for a subscription with "<account_type>" who is "adult" and "not handicapped",correspondence definition "E-Mail",member  delivery preference "Nothing" and responsibile party "None" "with out" email
    When I apply Adjustments
    And I Generate "Individual Risk Bills" 
    Then batch status should be "Completed"
    And I download the pdf document
    And the document delivery type is "PAPER"
    And I download the xlsx document
    And the data in pdf and xlsx documents matches with data in HE
    Examples: 
      |account_type|
      |ACA Exchange Individual|
      
  Scenario Outline: Verify the bill for an account type who is adult after adding payment (KSQA-397)
    Given I run a bill for a subscription with "<account_type>" who is "adult" and "not handicapped",correspondence definition "E-Mail",member  delivery preference "Nothing" and responsibile party "None" "with out" email
    When I add payment
    And I Generate "Individual Risk Bills" 
    Then batch status should be "Completed"
    And I download the pdf document
    And the document delivery type is "PAPER"
    And I download the xlsx document
    And the data in pdf and xlsx documents matches with data in HE
    Examples: 
      |account_type|
      |ACA Exchange Individual|
      
  Scenario Outline: Verify the bill for an account type who is adult after adding payment (KSQA-398)
    Given I run a bill for a subscription with "<account_type>" who is "adult" and "not handicapped",correspondence definition "E-Mail",member  delivery preference "Nothing" and responsibile party "None" "with out" email
    When I add payment
    And I apply Adjustments
    And I Generate "Individual Risk Bills" 
    Then batch status should be "Completed"
    And I download the pdf document
    And the document delivery type is "PAPER"
    And I download the xlsx document
    And the data in pdf and xlsx documents matches with data in HE
    Examples: 
      |account_type|
      |ACA Exchange Individual|