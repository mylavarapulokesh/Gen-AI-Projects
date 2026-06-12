from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import date
from sqlalchemy import BigInteger

# =====================================================================
# 1. BANK STRUCTURAL INFORMATION
# =====================================================================
class BankDetails(BaseModel):
    bankName: str = Field(description="The full corporate name of the banking institution issuing the statement (e.g., 'HDFC Bank', 'Chase', 'ICICI'). Look at the main header or logo area.")
    bankBranch: str = Field(description="The localized branch name or location where the account is maintained. Often found near the bank's contact details or address header.")
    ifscNumber: str = Field( description="The 11-character alphanumeric Indian Financial System Code. Look for patterns matching 4 letters, followed by '0', followed by 6 digits/letters (e.g., 'HDFC0001234').")
    micrCode: Optional[str] = Field(default=None,description="The 9-digit Magnetic Ink Character Recognition code printed at the bottom of check leaves or listed in the header. If missing, return None.")


# =====================================================================
# 2. CUSTOMER / ACCOUNT RELATIONSHIP METADATA
# =====================================================================
class CustomerDetails(BaseModel):
    accNumber: str = Field(description="The complete primary bank account number belonging to the customer. Look for labels like 'Account No.', 'A/C Num', or 'Account Identifier'.")
    customerAddress: str = Field(description="The physical mailing or residential address of the account holder. Extract the entire multi-line block text exactly as printed.")
    accOpenDate: Optional[date] = Field(default=None,description="The date the account was originally opened. If not explicitly stated in the summary section, return None. Always return dates in ISO format (YYYY-MM-DD). Convert dd/mm/yyyy or mm/dd/yyyy into ISO before output.")
    accType: str = Field(description="The structural type classification of the banking account. Categorize or extract values like 'Savings', 'Current', 'Checking', or 'Salary Account'.")
    cifNumber: Optional[str] = Field(description="The Customer Information File number or unique Customer ID. Look for labels like 'CIF No.', 'Customer ID', or 'Cust ID'. If missing, return None.")
    nomineeExists: Literal['Yes', 'No'] = Field(description="Determine if a registration nominee is listed on the account. If a nominee name or 'Registered' is present, output 'Yes'. If explicitly 'Not Registered' or absent, output 'No'.")
    mobileNumber: Optional[int] = Field(default=None,description="The registered mobile contact number of the customer. Strip out symbols or spaces if present. Return None if not visible.")
    emailId: Optional[str] = Field(default=None,description="The email address of the account holder. Look for the standard user@domain pattern in the communication header block. Return None if missing.")


# =====================================================================
# 3. STATEMENT RANGE SPECIFICATIONS
# =====================================================================
class StatementDetails(BaseModel):
    statementDate: date = Field(description="The exact calendar date the statement document was generated or printed by the bank engine. Always return dates in ISO format (YYYY-MM-DD). Convert dd/mm/yyyy or mm/dd/yyyy into ISO before output.")
    fromDate: date = Field(description="The start boundary date of the transactional reporting period (e.g., the 'From' date in 'Statement period from 01-Jan-2026 to 31-Jan-2026'). Always return dates in ISO format (YYYY-MM-DD). Convert dd/mm/yyyy or mm/dd/yyyy into ISO before output.")
    toDate: date = Field(description="The end boundary date of the transactional reporting period (e.g., the 'To' date in 'Statement period from 01-Jan-2026 to 31-Jan-2026'). Always return dates in ISO format (YYYY-MM-DD). Convert dd/mm/yyyy or mm/dd/yyyy into ISO before output.")


# =====================================================================
# 4. CORE LEDGER TRANSACTION SCHEMAS
# =====================================================================
class TransactionDetails(BaseModel):
    transactionDate: date = Field(description="The calendar date the transaction was processed or posted. Look for headings like 'Txn Date', 'Value Date', or 'Post Date'.(e.g., the 'To' date in 'Statement period from 01-Jan-2026 to 31-Jan-2026'). Always return dates in ISO format (YYYY-MM-DD). Convert dd/mm/yyyy or mm/dd/yyyy into ISO before output.")
    description: str = Field(description="The text narrative context explaining the financial movement. Look for headings like 'Particulars', 'Narration', 'Remarks', or 'Description'.")
    transNumber: Optional[str] = Field(default=None,description="The internal system reference tracking string or UPI/IMPS reference identifier number. Look for labels like 'Ref No.', 'Transaction ID', or 'UPI Ref'.")
    chequeNumber: Optional[str] = Field(default=None,description="The specific leaf number if a check or instrument was used. Look under columns named 'Chq No.', 'Cheque No.', or 'Inst.No.'. Return None for online/digital transfers.")
    debitAmount: float = Field(default=0.0,description="The monetary value being taken out of the bank account. Look under columns named 'Debit', 'Withdrawal', or 'Paid Out'. Convert empty values or hyphens to 0.0.")
    creditAmount: float = Field(default=0.0,description="The monetary value being added to the bank account. Look under columns named 'Credit', 'Deposit', or 'Paid In'. Convert empty values or hyphens to 0.0.")
    balanceAmount: float = Field(description="The closing ledger asset balance remaining after the transaction row execution. Look under columns named 'Balance', 'Running Balance', or 'Net Balance'.")


# =====================================================================
# 5. HIGH LEVEL CONTAINER ROOT ENTRY OBJECTS
# =====================================================================
class GenericDetails(BaseModel):
    """Container schema holding top-level static text blocks."""
    bankdetails: BankDetails
    customerDetails: CustomerDetails
    statementDetails: StatementDetails

class BankStatementPayload(BaseModel):
    """Container schema holding the core chunk arrays from the main grid."""
    transactions: list[TransactionDetails]