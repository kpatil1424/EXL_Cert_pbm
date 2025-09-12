# Paid → Paid Mismatch Validation (GraphRAG-Compatible Rulebook)

## Total Claim Cost Differences

### Rule: Ingredient Cost Change
**Cause**: PRE_INGREDIENT_COST_CLIENT ≠ POST_INGREDIENT_COST_CLIENT  
**Effect**: Total Claim Cost differs → Valid mismatch  
**Node_Type**: Validation_Rule  
**Parent_Node**: Total_Claim_Cost_Differences  
**Edge_Type**: Causes  
**Edge_Target**: Valid_Mismatch  

### Rule: Dispensing Fee Change
**Cause**: PRE_DISPENSING_FEE ≠ POST_DISPENSING_FEE  
**Effect**: Total Claim Cost differs → Valid mismatch  
**Node_Type**: Validation_Rule  
**Parent_Node**: Total_Claim_Cost_Differences  
**Edge_Type**: Causes  
**Edge_Target**: Valid_Mismatch  

### Rule: Flat Sales Tax Change
**Cause**: PRE_AMOUNT_ATTR_TO_SALES_TAX ≠ POST_AMOUNT_ATTR_TO_SALES_TAX  
**Effect**: Total Claim Cost differs → Valid mismatch  
**Node_Type**: Validation_Rule  
**Parent_Node**: Total_Claim_Cost_Differences  
**Edge_Type**: Causes  
**Edge_Target**: Valid_Mismatch  

### Rule: Percentage Sales Tax Change
**Cause**: PRE_SALEX_TAX_PERC_PAID ≠ POST_SALEX_TAX_PERC_PAID  
**Effect**: Total Claim Cost differs → Valid mismatch  
**Node_Type**: Validation_Rule  
**Parent_Node**: Total_Claim_Cost_Differences  
**Edge_Type**: Causes  
**Edge_Target**: Valid_Mismatch  

### Rule: Incentive Fee Change
**Cause**: PRE_INCENTIVE_FEE ≠ POST_INCENTIVE_FEE  
**Effect**: Total Claim Cost differs → Valid mismatch  
**Node_Type**: Validation_Rule  
**Parent_Node**: Total_Claim_Cost_Differences  
**Edge_Type**: Causes  
**Edge_Target**: Valid_Mismatch  

---

## Patient Pay Differences

### Rule: Copay Amount Change
**Cause**: PRE_COPAY_AMOUNT ≠ POST_COPAY_AMOUNT  
**Effect**: Patient Pay differs → Valid mismatch  
**Node_Type**: Validation_Rule  
**Parent_Node**: Patient_Pay_Differences  
**Precondition**: All_TCC_Rules_False  
**Edge_Type**: Causes  
**Edge_Target**: Valid_Mismatch  
**Supporting Fields**: POST_XREF_PLAN_CODE, POST_TIER_NUM, POST_DELIVERY_SYSTEM, POST_DAYS_SUPPLY  

### Rule: Copay Amount Validation from BPS Plan
**Cause**: PRE_COPAY_AMOUNT ≠ POST_COPAY_AMOUNT  

**Effect**:  
Validate POST_COPAY_AMOUNT against the correct cost-share table in the BPS document, using:  
- POST_XREF_PLAN_CODE → Plan section (BASIC / ECONOMY / HDHP)  
- POST_DELIVERY_SYSTEM  
- POST_TIER_NUM  
- POST_DAYS_SUPPLY  
- POST_DRUG_SPECIFIC_COPAY  
- POST_NETWORK  

**Validation Logic**:
1. Map `POST_XREF_PLAN_CODE` to document plan:
   - PCCBPPO → BASIC PLAN  
   - PCEPPPO → ECONOMY PLAN  
   - PCHDHP → HDHP PLAN
2. Choose the appropriate *Member Cost Share* section:
   - If `POST_DELIVERY_SYSTEM` = Specialty → **Specialty Member Cost Share**.  
   - Else if `POST_NETWORK` in {GOV90P, GOVCLP} → **Stepped Member Cost Share for VA**.  
   - Else if `POST_DRUG_SPECIFIC_COPAY` = SX_MST-EES → **Specialty Member Cost Share** (even for Mail/Retail).  
   - Else → standard **Member Cost Share**.
3. Within the section, find the row where:
   - Tier = `POST_TIER_NUM`  
   - Delivery = `POST_DELIVERY_SYSTEM`  
     - *(Special Case)*: if Delivery = Retail and Days Supply = 90, use Mail copay value if defined.
   - Match Days Supply as applicable.
4. Compare the copay from the plan with `POST_COPAY_AMOUNT`.

**Node_Type**: Validation_Rule  
**Parent_Node**: Patient_Pay_Differences  
**Precondition**: All_TCC_Rules_False  
**Edge_Type**: Causes  
**Edge_Target**: Valid_Mismatch  
**Supporting Fields**: POST_XREF_PLAN_CODE, POST_TIER_NUM, POST_DELIVERY_SYSTEM, POST_DAYS_SUPPLY, POST_DRUG_SPECIFIC_COPAY, POST_NETWORK, POST_COPAY_AMOUNT  

### Rule: Deductible Applied Amount Change
**Cause**: PRE_APPR_AMT_APPL_PER_DED ≠ POST_APPR_AMT_APPL_PER_DED  
**Effect**: Patient Pay differs → Valid mismatch  
**Node_Type**: Validation_Rule  
**Parent_Node**: Patient_Pay_Differences  
**Precondition**: All_TCC_Rules_False  
**Edge_Type**: Causes  
**Edge_Target**: Valid_Mismatch  
**Supporting Fields**: POST_XREF_PLAN_CODE, POST_TIER_NUM, POST_DELIVERY_SYSTEM, POST_DAYS_SUPPLY  

### Rule: Brand DAW Penalty Change
**Cause**: PRE_PROD_SELECTION_PENALTY ≠ POST_PROD_SELECTION_PENALTY  
**Effect**: Patient Pay differs → Valid mismatch  
**Node_Type**: Validation_Rule  
**Parent_Node**: Patient_Pay_Differences  
**Precondition**: All_TCC_Rules_False  
**Edge_Type**: Causes  
**Edge_Target**: Valid_Mismatch  
**Supporting Fields**: POST_XREF_PLAN_CODE, POST_TIER_NUM, POST_DELIVERY_SYSTEM, POST_DAYS_SUPPLY  

---

## Root Cause Differences

### Rule: Drug Specific Copay Change
**Cause**: PRE_DRUG_SPECIFIC_COPAY ≠ POST_DRUG_SPECIFIC_COPAY  
**Effect**: Potential Root Cause → Valid mismatch  
**Node_Type**: Validation_Rule  
**Parent_Node**: Root_Cause_Differences  
**Precondition**: All_TCC_Rules_False AND All_Patient_Pay_Rules_False  
**Edge_Type**: Causes  
**Edge_Target**: Valid_Mismatch  

### Rule: Client Patient Schedule Change
**Cause**: PRE_CLIENT_PATIENT_SCHEDULE ≠ POST_CLIENT_PATIENT_SCHEDULE  
**Effect**: Potential Root Cause → Valid mismatch  
**Node_Type**: Validation_Rule  
**Parent_Node**: Root_Cause_Differences  
**Precondition**: All_TCC_Rules_False AND All_Patient_Pay_Rules_False  
**Edge_Type**: Causes  
**Edge_Target**: Valid_Mismatch  

### Rule: Plan Code Change
**Cause**: PRE_XREF_PLAN_CODE ≠ POST_XREF_PLAN_CODE  
**Effect**: Potential Root Cause → Valid mismatch  
**Node_Type**: Validation_Rule  
**Parent_Node**: Root_Cause_Differences  
**Precondition**: All_TCC_Rules_False AND All_Patient_Pay_Rules_False  
**Edge_Type**: Causes  
**Edge_Target**: Valid_Mismatch  

### Rule: Member Accumulation Phase Difference
**Cause**: PRE_ACCUM_PHASE ≠ POST_ACCUM_PHASE  
**Effect**: Patient Pay differs due to accumulation → Valid mismatch  
**Node_Type**: Validation_Rule  
**Parent_Node**: Root_Cause_Differences  
**Precondition**: All_TCC_Rules_False AND All_Patient_Pay_Rules_False  
**Edge_Type**: Causes  
**Edge_Target**: Valid_Mismatch  

### Rule: Tier Change
**Cause**: PRE_TIER_NUM ≠ POST_TIER_NUM  
**Effect**: Tier difference → Valid mismatch  
**Node_Type**: Validation_Rule  
**Parent_Node**: Root_Cause_Differences  
**Precondition**: All_TCC_Rules_False AND All_Patient_Pay_Rules_False  
**Edge_Type**: Causes  
**Edge_Target**: Valid_Mismatch  

---

## Fallback Rule

### Rule: No Identified Differences
**Cause**: No matching differences found in expected fields  
**Effect**: SME Review Required → Invalid mismatch  
**Node_Type**: Fallback_Rule  
**Precondition**: All_TCC_Rules_False AND All_Patient_Pay_Rules_False AND All_Root_Cause_Rules_False  
**Edge_Type**: Requires  
**Edge_Target**: Invalid_Mismatch
