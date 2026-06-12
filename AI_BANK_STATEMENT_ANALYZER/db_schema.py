from pydantic import BaseModel
from datetime import date
from typing import Literal,Optional
from sqlmodel import Field,create_engine,SQLModel
from sqlalchemy import BigInteger

class BankDetails(SQLModel,table=True):
    __tablename__: str = "bank_details"
    id: int | None = Field(default=None, primary_key=True)
    bankName: str 
    bankBranch: str 
    ifscNumber: str 
    micrCode: Optional[str] = Field(default=None,nullable=True)
class CustomerDetails(SQLModel,table=True):
    __tablename__: str = "customer_details"
    id: int | None = Field(default=None, primary_key=True)
    bank_id: int = Field(foreign_key="bank_details.id")# from BankDetails
    accNumber: str
    customerAddress: str 
    accOpenDate: Optional[date] = None
    accType: str 
    cifNumber: Optional[str] = Field(default=None,nullable=True)
    nomineeExists: str 
    mobileNumber: Optional[int] = Field(sa_type=BigInteger,default=None, nullable=True)
    emailId: Optional[str] = None
    
class StatementDetails(SQLModel,table=True):
    __tablename__: str = "statement_details"
    id: int | None = Field(default=None, primary_key=True)
    customerId: int = Field(foreign_key="customer_details.id")# from customerDetails 
    statementDate: date 
    fromDate: date 
    toDate: date

class TransactionDetails(SQLModel,table=True):
    __tablename__: str = "transaction_details"
    id: int | None = Field(default=None, primary_key=True)
    statement_id: int = Field(foreign_key="statement_details.id")# from StatementDetails
    transactionDate: date
    description: str
    transNumber: Optional[str] = Field(default=None)
    chequeNumber: Optional[str] = Field(default=None,description="The specific leaf number if a check or instrument was used. Look under columns named 'Chq No.', 'Cheque No.', or 'Inst.No.'. Return None for online/digital transfers.")
    debitAmount: float = Field(default = 0.0)
    creditAmount: float = Field(default = 0.0)
    balanceAmount: float = Field(default = 0.0)