

# GraphRAG-Compatible Rulebook Format

## Paid → Paid Mismatch Validation

### Total Claim Cost Differences

#### Rule: Ingredient Cost Change

**Cause**: PRE_INGREDIENT_COST_CLIENT ≠ POST_INGREDIENT_COST_CLIENT
**Effect**: Total Claim Cost differs → Valid mismatch
**Node_Type**: Validation_Rule
**Parent_Node**: Total_Claim_Cost_Differences
**Edge_Type**: Causes
**Edge_Target**: Valid_Mismatch

#### Rule: Dispensing Fee Change

**Cause**: PRE_DISPENSING_FEE ≠ POST_DISPENSING_FEE
**Effect**: Total Claim Cost differs → Valid mismatch
**Node_Type**: Validation_Rule
**Parent_Node**: Total_Claim_Cost_Differences
**Edge_Type**: Causes
**Edge_Target**: Valid_Mismatch

#### Rule: Flat Sales Tax Change

**Cause**: PRE_AMOUNT_ATTR_TO_SALES_TAX ≠ POST_AMOUNT_ATTR_TO_SALES_TAX
**Effect**: Total Claim Cost differs → Valid mismatch
**Node_Type**: Validation_Rule
**Parent_Node**: Total_Claim_Cost_Differences
**Edge_Type**: Causes
**Edge_Target**: Valid_Mismatch

#### Rule: Percentage Sales Tax Change

**Cause**: PRE_SALEX_TAX_PERC_PAID ≠ POST_SALEX_TAX_PERC_PAID
**Effect**: Total Claim Cost differs → Valid mismatch
**Node_Type**: Validation_Rule
**Parent_Node**: Total_Claim_Cost_Differences
**Edge_Type**: Causes
**Edge_Target**: Valid_Mismatch

#### Rule: Incentive Fee Change

**Cause**: PRE_INCENTIVE_FEE ≠ POST_INCENTIVE_FEE
**Effect**: Total Claim Cost differs → Valid mismatch
**Node_Type**: Validation_Rule
**Parent_Node**: Total_Claim_Cost_Differences
**Edge_Type**: Causes
**Edge_Target**: Valid_Mismatch

### Patient Pay Differences

#### Rule: Copay Amount Change

**Cause**: PRE_COPAY_AMOUNT ≠ POST_COPAY_AMOUNT
**Effect**: Patient Pay differs → Valid mismatch
**Node_Type**: Validation_Rule
**Parent_Node**: Patient_Pay_Differences
**Precondition**: All_TCC_Rules_False
**Edge_Type**: Causes
**Edge_Target**: Valid_Mismatch

#### Rule: Deductible Applied Amount Change

**Cause**: PRE_APPR_AMT_APPL_PER_DED ≠ POST_APPR_AMT_APPL_PER_DED
**Effect**: Patient Pay differs → Valid mismatch
**Node_Type**: Validation_Rule
**Parent_Node**: Patient_Pay_Differences
**Precondition**: All_TCC_Rules_False
**Edge_Type**: Causes
**Edge_Target**: Valid_Mismatch

#### Rule: Brand DAW Penalty Change

**Cause**: PRE_PROD_SELECTION_PENALTY ≠ POST_PROD_SELECTION_PENALTY
**Effect**: Patient Pay differs → Valid mismatch
**Node_Type**: Validation_Rule
**Parent_Node**: Patient_Pay_Differences
**Precondition**: All_TCC_Rules_False
**Edge_Type**: Causes
**Edge_Target**: Valid_Mismatch

### Root Cause Differences

#### Rule: Drug Specific Copay Change

**Cause**: PRE_DRUG_SPECIFIC_COPAY ≠ POST_DRUG_SPECIFIC_COPAY
**Effect**: Potential Root Cause → Valid mismatch
**Node_Type**: Validation_Rule
**Parent_Node**: Root_Cause_Differences
**Precondition**: All_TCC_Rules_False AND All_Patient_Pay_Rules_False
**Edge_Type**: Causes
**Edge_Target**: Valid_Mismatch

#### Rule: Client Patient Schedule Change

**Cause**: PRE_CLIENT_PATIENT_SCHEDULE ≠ POST_CLIENT_PATIENT_SCHEDULE
**Effect**: Potential Root Cause → Valid mismatch
**Node_Type**: Validation_Rule
**Parent_Node**: Root_Cause_Differences
**Precondition**: All_TCC_Rules_False AND All_Patient_Pay_Rules_False
**Edge_Type**: Causes
**Edge_Target**: Valid_Mismatch

#### Rule: Plan Code Change

**Cause**: PRE_XREF_PLAN_CODE ≠ POST_XREF_PLAN_CODE
**Effect**: Potential Root Cause → Valid mismatch
**Node_Type**: Validation_Rule
**Parent_Node**: Root_Cause_Differences
**Precondition**: All_TCC_Rules_False AND All_Patient_Pay_Rules_False
**Edge_Type**: Causes
**Edge_Target**: Valid_Mismatch

### Fallback Rule

#### Rule: No Identified Differences

**Cause**: No matching differences found in expected fields
**Effect**: SME Review Required → Invalid mismatch
**Node_Type**: Fallback_Rule
**Precondition**: All_TCC_Rules_False AND All_Patient_Pay_Rules_False AND All_Root_Cause_Rules_False
**Edge_Type**: Requires
**Edge_Target**: Invalid_Mismatch

## Reject → Reject Mismatch Validation

### Scope of Validation

#### Rule: In-Scope Reject Code Pairs

**Cause**: PRE_REJECT_CODE_1 and POST_REJECT_CODE_1 are one of the following pairs: (76, 76), (75, 76), (76, 75)
**Effect**: Proceed with validation
**Node_Type**: Scope_Rule
**Parent_Node**: Validation_Scope
**Edge_Type**: Proceeds_To
**Edge_Target**: Reject_Code_Comparison

#### Rule: Out-of-Scope Reject Code Pairs

**Cause**: PRE_REJECT_CODE_1 and POST_REJECT_CODE_1 are not among valid pairs
**Effect**: Reject validation skipped → Invalid mismatch
**Node_Type**: Scope_Rule
**Parent_Node**: Validation_Scope
**Edge_Type**: Results_In
**Edge_Target**: Invalid_Mismatch

### Same Reject Code Case

#### Rule: Matching Local Messages (Same Reject)

**Cause**: PRE_REJECT_CODE_1 = POST_REJECT_CODE_1 = 76 AND PRE_LOCAL_MESSAGE = POST_LOCAL_MESSAGE
**Effect**: Same reject and message → Invalid mismatch
**Node_Type**: Validation_Rule
**Parent_Node**: Same_Reject_Code_Case
**Precondition**: In_Scope_Rule_True
**Edge_Type**: Results_In
**Edge_Target**: Invalid_Mismatch

#### Rule: Different Local Messages (Same Reject)

**Cause**: PRE_REJECT_CODE_1 = POST_REJECT_CODE_1 = 76 AND PRE_LOCAL_MESSAGE ≠ POST_LOCAL_MESSAGE
**Effect**: Local Message change → Invalid mismatch
**Node_Type**: Validation_Rule
**Parent_Node**: Same_Reject_Code_Case
**Precondition**: In_Scope_Rule_True
**Edge_Type**: Results_In
**Edge_Target**: Invalid_Mismatch

### Cross Reject Code Cases

#### Rule: Matching Local Messages (Cross Reject)

**Cause**: PRE_REJECT_CODE_1 ≠ POST_REJECT_CODE_1 AND PRE_LOCAL_MESSAGE = POST_LOCAL_MESSAGE
**Effect**: Reject code changed, but message same → Invalid mismatch
**Node_Type**: Validation_Rule
**Parent_Node**: Cross_Reject_Code_Cases
**Precondition**: In_Scope_Rule_True
**Edge_Type**: Results_In
**Edge_Target**: Invalid_Mismatch

#### Rule: Different Local Messages (Cross Reject)

**Cause**: PRE_REJECT_CODE_1 ≠ POST_REJECT_CODE_1 AND PRE_LOCAL_MESSAGE ≠ POST_LOCAL_MESSAGE
**Effect**: Message changed → Proceed to deeper field check
**Node_Type**: Validation_Rule
**Parent_Node**: Cross_Reject_Code_Cases
**Precondition**: In_Scope_Rule_True
**Edge_Type**: Proceeds_To
**Edge_Target**: Deeper_Field_Differences

### Deeper Field Differences

#### Rule: PA Layer Changed

**Cause**: PRE_PA_LAYER_DETAILS ≠ POST_PA_LAYER_DETAILS
**Effect**: Valid mismatch due to PA Layer change
**Node_Type**: Validation_Rule
**Parent_Node**: Deeper_Field_Differences
**Precondition**: Cross_Reject_Different_Messages_True
**Edge_Type**: Results_In
**Edge_Target**: Valid_Mismatch

#### Rule: Drug List Changed

**Cause**: PRE_DRUGLIST_DETAIL ≠ POST_DRUGLIST_DETAIL
**Effect**: Valid mismatch due to Drug List change
**Node_Type**: Validation_Rule
**Parent_Node**: Deeper_Field_Differences
**Precondition**: Cross_Reject_Different_Messages_True
**Edge_Type**: Results_In
**Edge_Target**: Valid_Mismatch

#### Rule: Smart PA Overall Changed

**Cause**: PRE_SMART_PA_OVERALL ≠ POST_SMART_PA_OVERALL
**Effect**: Valid mismatch due to Smart PA change
**Node_Type**: Validation_Rule
**Parent_Node**: Deeper_Field_Differences
**Precondition**: Cross_Reject_Different_Messages_True
**Edge_Type**: Results_In
**Edge_Target**: Valid_Mismatch

#### Rule: Days Supply Changed

**Cause**: PRE_DAYS_SUPPLY ≠ POST_DAYS_SUPPLY
**Effect**: Valid mismatch due to Days Supply difference
**Node_Type**: Validation_Rule
**Parent_Node**: Deeper_Field_Differences
**Precondition**: Cross_Reject_Different_Messages_True
**Edge_Type**: Results_In
**Edge_Target**: Valid_Mismatch

#### Rule: Final Plan Code Changed

**Cause**: PRE_FINAL_PLAN_CODE ≠ POST_FINAL_PLAN_CODE
**Effect**: Valid mismatch due to Final Plan Code change
**Node_Type**: Validation_Rule
**Parent_Node**: Deeper_Field_Differences
**Precondition**: Cross_Reject_Different_Messages_True
**Edge_Type**: Results_In
**Edge_Target**: Valid_Mismatch

#### Rule: Network Changed

**Cause**: PRE_NETWORK ≠ POST_NETWORK
**Effect**: Valid mismatch due to Network change
**Node_Type**: Validation_Rule
**Parent_Node**: Deeper_Field_Differences
**Precondition**: Cross_Reject_Different_Messages_True
**Edge_Type**: Results_In
**Edge_Target**: Valid_Mismatch

### Fallback Rule

#### Rule: No Deeper Differences

**Cause**: All deeper fields match
**Effect**: No valid root cause identified → Invalid mismatch, SME review suggested
**Node_Type**: Fallback_Rule
**Precondition**: Cross_Reject_Different_Messages_True AND All_Deeper_Field_Rules_False
**Edge_Type**: Results_In
**Edge_Target**: Invalid_Mismatch


## Paid → Reject Mismatch Validation


### Scope of Validation

#### Rule: Valid Transition Status  
**Cause**: PRE_CLAIM_STATUS = "P" AND POST_CLAIM_STATUS = "R"  
**Effect**: Proceed with validation for Paid → Reject mismatch  
**Node_Type**: Scope_Rule  
**Parent_Node**: Validation_Scope  
**Edge_Type**: Proceeds_To  
**Edge_Target**: Reject_Code_Check


### Reject Code Check

#### Rule: Reject Code Is 75  
**Cause**: POST_REJECT_CODE_1 = 75  
**Effect**: Proceed with PA Local Message Check  
**Node_Type**: Validation_Rule  
**Parent_Node**: Reject_Code_Check  
**Precondition**: Valid_Scope_True  
**Edge_Type**: Proceeds_To  
**Edge_Target**: PA_Local_Message_Check

#### Rule: Reject Code Is Not 75  
**Cause**: POST_REJECT_CODE_1 ≠ 75  
**Effect**: Reject code not in scope → Invalid mismatch  
**Node_Type**: Validation_Rule  
**Parent_Node**: Reject_Code_Check  
**Precondition**: Valid_Scope_True  
**Edge_Type**: Results_In  
**Edge_Target**: Invalid_Mismatch


### PA Local Message Check

#### Rule: Local Message Indicates PA  
**Cause**: POST_LOCAL_MESSAGE contains any of the following phrases (case-insensitive):  
- "prior authorization"  
- "prior auth"  
- "prior auth req"  
- "requires prior authorization"  
- "prior auth required"  
- "pa required"  
**Effect**: Message suggests PA → Proceed with PA Reason/Layer comparison  
**Node_Type**: Validation_Rule  
**Parent_Node**: PA_Local_Message_Check  
**Precondition**: Reject_Code_75_True  
**Edge_Type**: Proceeds_To  
**Edge_Target**: PA_Reason_Layer_Comparison

#### Rule: Local Message Lacks PA Trigger  
**Cause**: POST_LOCAL_MESSAGE does NOT contain any PA-related phrases  
**Effect**: Not a PA rejection → Invalid mismatch  
**Node_Type**: Validation_Rule  
**Parent_Node**: PA_Local_Message_Check  
**Precondition**: Reject_Code_75_True  
**Edge_Type**: Results_In  
**Edge_Target**: Invalid_Mismatch


### PA Reason / Layer Comparison

#### Rule: PA Reason or Layer Changed  
**Cause**: PRE_PA_REASON_CODE ≠ POST_PA_REASON_CODE  
**OR** PRE_PA_LAYER_DETAILS ≠ POST_PA_LAYER_DETAILS  
**Effect**: Valid mismatch due to PA detail change  
**Node_Type**: Validation_Rule  
**Parent_Node**: PA_Reason_Layer_Comparison  
**Precondition**: Message_Has_PA_Trigger  
**Edge_Type**: Results_In  
**Edge_Target**: Valid_Mismatch

#### Rule: PA Reason and Layer Same  
**Cause**: PRE_PA_REASON_CODE = POST_PA_REASON_CODE  
**AND** PRE_PA_LAYER_DETAILS = POST_PA_LAYER_DETAILS  
**Effect**: No PA detail change → Invalid mismatch  
**Node_Type**: Validation_Rule  
**Parent_Node**: PA_Reason_Layer_Comparison  
**Precondition**: Message_Has_PA_Trigger  
**Edge_Type**: Results_In  
**Edge_Target**: Invalid_Mismatch


### Fallback Rule

#### Rule: Missing or Unexpected Data  
**Cause**: Reject code is not 75 OR required fields are missing  
**Effect**: Insufficient info → Invalid mismatch, SME review suggested  
**Node_Type**: Fallback_Rule  
**Parent_Node**: Validation_Scope  
**Precondition**: All_Rules_False  
**Edge_Type**: Results_In  
**Edge_Target**: Invalid_Mismatch

