# This is the entry point 
# Note: CustomerDetails,BankDetails,StatementDetails are treated as Generic Details extracted in one step and TransactionDetails are extracted in another step
import streamlit as st
import os
import json
from dotenv import load_dotenv
from pydantic import ValidationError
from sqlmodel import Session,SQLModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pdf_ingestion import pdf_to_docs, extract_and_process_tables
from db_schema import BankDetails,CustomerDetails,StatementDetails,TransactionDetails
from response_schema import GenericDetails
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

st.set_page_config(page_title='Chatbot: Chat with Documents', page_icon='👇')
st.title('AI BANKSTATEMENT ANALYZER')
uploaded_cv = st.sidebar.file_uploader(label='Upload CV', type=['PDF'])

BANKSTATEMENTS_DIR = r"all_bankstatements" # whenever a user uploads a pdf it is stored in this directory and it serves as cloud

file_path = "" # it is directory path where pdf is stored eg: all_bankstatement/statement.pdf

if uploaded_cv:
    content = uploaded_cv.read()
    file_name = uploaded_cv.name
    
    with open(os.path.join(BANKSTATEMENTS_DIR,file_name), 'wb') as new_file:
        new_file.write(content)
        file_path = os.path.join(BANKSTATEMENTS_DIR,file_name)

file_path = file_path.replace("\\","/")

print(f"file path is: {file_path}")

docs = pdf_to_docs(file_path=file_path) # it takes file path of pdf uploaded and convert it into langchain Documents

doc1_page_content = docs[0].page_content # to extract BankDetails,CustomerDetails,AccountDetails we are reading 1st page as 1st page contains all the basic details

llm_4o = ChatOpenAI(model="gpt-4o",temperature=0.0)

llm_4o_structured = llm_4o.with_structured_output(GenericDetails) # GenericDetails is pydantic object

basic_details_prompt = """ 
You are a professional pdf analyser,extract bankdetails, customer details,statementdetails
based on below page content \n {page_content}
"""

basic_details_prompt_template = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an expert financial document analyzer. "
        "Extract the exact bank details, customer details, and statement summary metadata "
        "requested by the output schema."
    )),
    ("user", "Here is the raw text from the first page of the bank statement:\n\n{page_content}")
])

final_generic_response_json = None # O/p in json format will be assigned to this variable to push data into DB

extraction_chain = basic_details_prompt_template | llm_4o_structured
try:
    final_generic_response = extraction_chain.invoke({"page_content": doc1_page_content})
    #print(f"Extracted Core Metadata: {final_generic_response}")
    with open('generic_response.json','w',encoding='utf-8') as f: # just to view O/p in json format for debugging
        final_generic_response_json = final_generic_response.model_dump_json(indent=4)
        f.write(final_generic_response_json)
        print("successfully dumped pydantic object into generic_response.json")

except ValidationError as pydantic_err:
    print(f"Pydantic Type Validation Error: Your target schema fields did not match the extracted strings. Detail: {pydantic_err}")

except Exception as e:
    print(f"API or General Pipeline Error: {e}")

transaction_payload_json = None # it holds all the transactions in a statement in json format
transaction_payload = extract_and_process_tables(file_path=file_path) # transaction_payload is pydantic object that contains all the trasaction records in list

with open('transaction_response.json','w',encoding='utf-8') as f:
    transaction_payload_json = transaction_payload.model_dump_json(indent=4)
    f.write(transaction_payload_json)
    print("successfully dumped pydantic object into transaction_response.json")

# Pushing data into Postgresql
DATABASE_URL = "postgresql+psycopg2://postgres:Lokesh123$@localhost:5432/bankstatement"

def create_tables(DATABASE_URL:str): # this will create tables based on pydantic schemas mentioned in db_schema.py and its schemas are imported here
    engine = create_engine(DATABASE_URL,echo=True)
    SQLModel.metadata.create_all(engine)
    return engine

engine = create_tables(DATABASE_URL=DATABASE_URL)

with Session(engine) as session: # final step to push our data into DB
    try:
        final_generic_response_dict = json.loads(final_generic_response_json)
        bankdetails = BankDetails(**final_generic_response_dict.get('bankdetails'))
        session.add(bankdetails)
        session.flush()

        customerdetails = CustomerDetails(bank_id = bankdetails.id, **final_generic_response_dict.get('customerDetails'))
        session.add(customerdetails)
        session.flush()

        statementdetails = StatementDetails(customerId = customerdetails.id,**final_generic_response_dict.get('statementDetails'))
        session.add(statementdetails)
        session.flush()
    
        transaction_payload_dict = json.loads(transaction_payload_json)
        transaction_payload_todb = [TransactionDetails(statement_id = statementdetails.id,**transaction) for transaction in transaction_payload_dict.get('transactions')]
        session.add_all(transaction_payload_todb)
    
        session.commit()
    except SQLAlchemyError as db_error:
            # If anything fails anywhere inside this block, rollback completely
            session.rollback()
            print(f"Database Transaction Failed! Rolling back changes. Error: {db_error}")
            raise db_error
            
    except Exception as general_error:
            session.rollback()
            print(f"Unexpected application mapping failure: {general_error}")
            raise general_error

print("successfully inserted values in the DB")    