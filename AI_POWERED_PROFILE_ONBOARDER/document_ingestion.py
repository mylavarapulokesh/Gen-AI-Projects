from langchain_community.document_loaders import PyMuPDFLoader
from langchain_openai import ChatOpenAI
from schemas import ProfileInfo
from db_schema import UserAccount,create_tables,Db_BasicInfo,Db_ProjectHistory,Db_Skillset,Db_Certifications,Db_Awards
from sqlmodel import Session
import json
import uuid
import smtplib

import os
from dotenv import load_dotenv
load_dotenv()

os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

json_data = None # holds result in json_data in later steps

def pdf_to_docs(file_path:str):
    loader = PyMuPDFLoader(file_path=file_path)
    docs = loader.load()
    print(f"Number of documents in the pdf is: {len(docs)}")
    return docs

def concat_docs(docs):
    print(f"received documents in concat_docs function\n {docs}")
    doc_content = ""
    for doc in docs:
        print(doc)
        doc_content = doc_content + doc.page_content
    return doc_content

def extractInfo_And_InsertIntoDB(docs):
    doc_content = concat_docs(docs=docs)

    print(f"doc_content is: {doc_content}")
    llm = ChatOpenAI(model="gpt-4o")
    llm_structured = llm.with_structured_output(ProfileInfo)


    prompt = f""" 
    Assume you are a HR in an organisation and given below resume content, 
    your job is to understand the below content and extract the structured output
    {doc_content}
    """

    result = llm_structured.invoke(prompt)

    # 1. Convert the Pydantic object to a clean JSON string
    # 'indent=2' makes the output file human-readable and pretty-printed
    json_data = result.model_dump_json(indent=2)

    # 2. Write the string directly to a file
    with open("candidate_profile.json", "w", encoding="utf-8") as json_file:
        json_file.write(json_data)

    print("Successfully saved profile to candidate_profile.json!")

    DATABASE_URL = "postgresql+psycopg2://postgres:Lokesh123$@localhost:5432/flmdb"

    engine = create_tables(DATABASE_URL=DATABASE_URL)

    parsed_json = json.loads(json_data)

    user_id = None
    basic_info_id = None
    username = parsed_json['candidateInfo']['email']
    password = None

    with Session(engine) as session:
        userinfo = UserAccount(username=parsed_json['candidateInfo']['email'],password=str(uuid.uuid4()).replace("-", "")[:12])
        session.add(userinfo)
        session.commit()
        session.refresh(userinfo)
        user_id = userinfo.id
        password = userinfo.password

    with Session(engine) as session:
        basic_info = Db_BasicInfo(userId=user_id,**parsed_json['candidateInfo'])
        session.add(basic_info)
        session.commit()
        session.refresh(basic_info)
        basic_info_id = basic_info.id

    with Session(engine) as session:
        prj_his = [Db_ProjectHistory(profileId=basic_info_id,**his) for his in parsed_json['candidateProjectHistory']]
        session.add_all(prj_his)
        session.commit()

    with Session(engine) as session:
        can_skillset = [Db_Skillset(userId=basic_info_id,**skill) for skill in parsed_json['candidateSkillSet']]
        session.add_all(can_skillset)
        session.commit()

    with Session(engine) as session:
        cert = [Db_Certifications(userid=basic_info_id,**certification) for certification in parsed_json['candidateCertifications']]
        session.add_all(cert)
        session.commit()

    with Session(engine) as session:
        awards = [Db_Awards(userid=basic_info_id,**award) for award in parsed_json['candidateAwards']]
        session.add_all(awards)
        session.commit()

    server = smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    sender_email = os.getenv("SENDER_EMAIL")
    receiver_mail = os.getenv("RECEIVER_MAIL")
    password = os.getenv("PASSWORD")
    server.login(sender_email,password)
    text = f"""Your account is created and find your credentials here 
    user id: {username}, password: {password}
    """
    server.sendmail(sender_email,receiver_mail,text)
    print("Mail is sent")
