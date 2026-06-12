from langchain_community.document_loaders import PyMuPDFLoader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import pdfplumber
from pydantic import ValidationError
from typing import List
from db_schema import BankDetails,CustomerDetails,StatementDetails,TransactionDetails
from response_schema import BankStatementPayload
import os



def pdf_to_docs(file_path:str):
    loader = PyMuPDFLoader(file_path=file_path)
    docs = loader.load()
    return docs

def rawtable_to_structured_pydantic(headers: List[str], page_rows: List[List[str]]) -> BankStatementPayload:
    """
    Takes a structural list of columns and raw table rows, passes them to gpt-4o,
    and returns a cleanly structured and validated BankStatementPayload object.
    """
    # 1. Initialize the model with absolute zero temperature for deterministic accuracy
    llm_4o = ChatOpenAI(model="gpt-4o", temperature=0.0)
    
    # 2. Instruct the LLM to strictly output data matching your master schema container
    structured_llm = llm_4o.with_structured_output(BankStatementPayload)

    # 3. Clean up your prompt template using professional System and User separation roles
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a professional financial data extraction clerk. Your task is to align "
            "the provided list of raw spreadsheet/table rows with the actual schema target layout. "
            "Use the provided column names context to identify dates, descriptions, reference IDs, "
            "and debit/credit money amounts precisely."
        )),
        ("user", (
            "Columns Configuration:\n{column_names}\n\n"
            "Raw Row Matrix Text:\n{row_data}"
        ))
    ])

    # 4. Formulate the execution pipeline chain
    transformation_chain = prompt_template | structured_llm

    # 5. Transform raw list items into clean, readable tabular text lines for the prompt
    column_names_str = " | ".join(headers)
    row_data_str = "\n".join([" | ".join(row) for row in page_rows])

    print(f"Sending batch window ({len(page_rows)} rows) to gpt-4o for structural extraction...")

    # 6. Execute the chain with safe exception handling wrappers
    try:
        structured_output: BankStatementPayload = transformation_chain.invoke({
            "column_names": column_names_str,
            "row_data": row_data_str
        })
        return structured_output
        
    except ValidationError as pydantic_err:
        print(f"Structural Validation Error: The LLM output failed your Pydantic schema constraints. Detail: {pydantic_err}")
        return BankStatementPayload(transactions=[])
        
    except Exception as general_err:
        print(f"Ingestion Pipeline Failure: Failed to communicate or process via API. Detail: {general_err}")
        return BankStatementPayload(transactions=[])

        
def extract_and_process_tables(file_path:str): # Takes a filepath of pdf uploaded
    """ 
    Extracts tables pagewise and 
    sends rows along with headers to LLM i.e. rawtable_to_structured_pydantic(headers,page_rows)
    """
    master_headers = None # holds the column names of table
    individual_statements_pydanticObj = []

    with pdfplumber.open(file_path) as pdf:
        print(f"pdf.pages gives:\n {pdf.pages}") # O/p: [<Page:1>, <Page:2>, <Page:3>]

        for i,page in enumerate(pdf.pages):
            all_transactions = []
            tables = page.extract_tables() # here we get list[lists] i.e we get list[tables] and table has list of rows
            if not tables: # sometimes page maynot have tables so we skip this iteration i.e a page in pdf
                continue
            statement_table = tables[-1] # extracting only last table in a current page because in 1st page we may have 2 tables, 1st table has basic info and from 2nd table onwards we have transaction details that span upto end of the pdf statement
            #print(f"tables extracted from statement table is: \n{statement_table}")

            cleaned_statement_table = [[str(cell).strip() if cell is not None else "" for cell in row] for row in statement_table]
            #print(f"cleaned_statement is: \n{cleaned_statement_table}")
            if master_headers is None: 
                # 1. Lock the master headers as a clean list on Page 1
                master_headers = cleaned_statement_table[0]
        
                # 2. Add page 1 data rows, safely skipping the header row
                all_transactions.extend(cleaned_statement_table[1:]) # index 0 has list of column names
                print(f"Master Headers locked on Page {i+1}: {master_headers}")

            else:
            # 3. Compare the list structures directly (No clumsy string joining needed)
                if cleaned_statement_table[0] == master_headers: # if table spans into next page and sometimes column names repeat there, here we are cross checking and skip the column headers
                    # The bank repeated headers on this page break; skip row 0 safely
                    all_transactions.extend(cleaned_statement_table[1:])
                    print(f"Page {i+1}: Repeated headers detected and skipped.")
                else:
                    # No headers present; the whole table chunk is raw transaction data
                    all_transactions.extend(cleaned_statement_table)
                    print(f"Page {i+1}: Raw data cut detected. Stitched seamlessly.")

            # 4. To print it cleanly, convert the rows matrix into string lines dynamically
            printable_matrix = "\n".join([" | ".join(row) for row in all_transactions])
            print(f"\n Accumulated statement table data rows so far:\n{printable_matrix}\n")
            structured_statement_pydanticObj = rawtable_to_structured_pydantic(headers=master_headers,page_rows=all_transactions) # For each page table we get O/p of transactions individually here
            individual_statements_pydanticObj.append(structured_statement_pydanticObj) # now all the individual pydantic objects that contains respective pdf page tables 

    
    # Append all pydantic obj into consolidated obj by combining all list values in each individual list values in each pydantic obj
    final_structured_transactions = [
        transaction 
        for individual_list_of_trans in individual_statements_pydanticObj 
        for transaction in individual_list_of_trans.transactions
    ]
    print(f"final_structured_transaction_list is:\n{final_structured_transactions}")
    final_master_payload = BankStatementPayload(transactions=final_structured_transactions)
    return final_master_payload



#flattended_pydantic = [ele for pyd in lists for ele in pyd.transactions]
            # 1. Outer Loop First
# for individual_list_of_trans in individual_statements_pydanticObj:
#     # 2. Inner Loop Second
#     for transaction in individual_list_of_trans.transactions:
#         # 3. The Target Item
#         append(transaction)
            