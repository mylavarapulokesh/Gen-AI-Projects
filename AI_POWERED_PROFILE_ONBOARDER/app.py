import streamlit as st 
import os
from document_ingestion import pdf_to_docs, extractInfo_And_InsertIntoDB
from langchain_community.document_loaders import PyMuPDFLoader
from pathlib import Path

# 1. Page Configuration Setup
st.set_page_config(
    page_title="Nuvosol Document Analyzer",
    page_icon="☀️",
    layout="centered"
)

TARGET_DIR = "all_resumes"
os.makedirs(TARGET_DIR,exist_ok=True)

st.title(" AI Powered Profile Onboarder")
st.subheader("Extract and structure personal info")
st.markdown("---")

# 2. File Uploader Component Placement
# You can customize the accepted file extensions inside the 'type' list parameter
uploaded_file = st.file_uploader(
    label="Upload your resume",
    type=["pdf"],
    accept_multiple_files=False,
    help="Supported formats: PDF"
)
file_path=""

# 3. Handling the Uploaded File File-Stream Safely
if uploaded_file is not None:
    # Fetch file metadata attributes cleanly
    file_name = uploaded_file.name
    file_type = uploaded_file.type
    file_size_kb = uploaded_file.size / 1024

    file_path = os.path.join(TARGET_DIR,file_name)

    with open(file_path,'wb') as f:
        f.write(uploaded_file.getbuffer())


    # Visual container status card layout
    with st.expander("📊 Uploaded File Details", expanded=True):
        st.write(f"**Filename:** {file_name}")
        st.write(f"**MIME Type:** {file_type}")
        st.write(f"**File Size:** {file_size_kb:.2f} KB")

    st.success(f"🎉 '{file_name}' uploaded successfully!")

file_path = file_path.replace("\\","/")

print(f"file path is: {file_path}")

#loader = PyMuPDFLoader(file_path=file_path)
docs = pdf_to_docs(file_path=file_path)
extractInfo_And_InsertIntoDB(docs=docs) # takes documents and process them and isert into DB
