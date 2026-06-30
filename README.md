# AI-Powered Financial Statement Analyzer

An enterprise-grade retrieval-augmented generation (RAG) application that ingests complex PDF financial statements, extracts highly accurate raw text, executes intelligent semantic semantic search, and saves parsed entities across a relational PostgreSQL schema.

## 🚀 Overview

Financial statements (Balance sheets, Income statements, and Audit logs) contain mixed structural grids and variable unstructured footnotes. The **AI-Powered Statement Analyzer** replaces manual document parsing by combining a **Streamlit** interactive analytics dashboard with a **LangChain RAG pipeline**. It extracts exact tables using `pdfplumber`, performs context-rich vector searches, and structures transactional facts into a normalized multi-table **PostgreSQL** database.

[PDF Statement] ──> [pdfplumber Extraction] ──> [LangChain RAG Processing] ──> [PostgreSQL]

---

## 🏗️ Core Architecture & Pipeline

### 1. Extraction Layer (`pdfplumber`)
Unlike standard pixel-by-pixel bounding boxes, the app uses `pdfplumber` to map structural vector boundaries. This preserves column layouts and text alignments from financial balance tables, ensuring numerical values match their exact structural field keys without alignment shifts.

### 2. Retrieval-Augmented Generation (RAG) Workflow
* **Chunking Strategy:** Text splits use overlapping semantic breaks to preserve tables alongside adjacent contextual footnotes.
* **Vector Store Integration:** Paragraph blocks are indexed inside a vector embedding database to enable users to ask open-ended questions (e.g., *"What are the primary depreciation liabilities noted in Q3?"*).

### 3. Database Layer (PostgreSQL)
Extracted facts are parsed into explicit Python typed objects (`Pydantic`) and structurally committed across unique, relational PostgreSQL database tables to prevent single-table data clutter:
* **`statements`:** Core metadata metadata mapping tracking the entity name, processing timestamp, and fiscal period.
* **`financial_metrics`:** Normalized rows holding metrics keys, values, currencies, and categories (Assets, Liabilities, Revenues).
* **`audit_notes`:** Relational text blocks capturing isolated disclosures, risks, and background qualitative statements.

---

## 🛠️ Tech Stack

* **Frontend UI:** Streamlit
* **Orchestration Framework:** LangChain (LCEL)
* **Document Parser:** pdfplumber
* **LLM Engine:** OpenAI GPT-4o / Anthropic Claude-3.5-Sonnet (configured with `.with_structured_output()`)
* **Database Layer:** PostgreSQL (managed via SQLAlchemy ORM / psycopg2)
* **Vector Vector Analytics:** FAISS / pgvector

Environment Variables (.env)
Create a .env configuration file in the project root folder:

Code snippet
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://db_user:db_password@localhost:5432/statement_analyzer_db
