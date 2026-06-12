from schemas import BasicInfo, ProjectHistory, SkillSet, Certifications, Awards, ProfileInfo
from sqlmodel import SQLModel, Field, create_engine
import uuid
from typing import Optional
from datetime import date
from sqlalchemy import BigInteger
# Each class is pydantic object i.e. a schema of DB tables to store Resume data
class UserAccount(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str # = Field(default=BasicInfo.email)
    password: str # = Field(default=str(uuid.uuid4()).replace("-", "")[:12])

class Db_BasicInfo(SQLModel,table=True):
    id: int | None = Field(default=None, primary_key=True)
    userId: int = Field(foreign_key="useraccount.id")  # id from useraccount
    firstName: str = Field(..., description="The candidate's legal given name or first name.")
    lastName: str = Field(..., description="The candidate's legal family name or last name.")
    dob: Optional[date] = Field(..., description="The candidate's Date of Birth. Must be strictly formatted as an ISO-8601 date string (YYYY-MM-DD). Return NA if you don't find")
    Mobile: int = Field(..., sa_type=BigInteger, description="The candidate's primary mobile contact number including country code if available, extracted as continuous digits without spaces or dashes.")
    email: str = Field(..., description="The candidate's primary professional email address. Extract full email address.")
    aadhar: Optional[int] = Field(..., description="The unique 12-digit national identification number (Aadhaar number) of the candidate. Return NA if you don't find it")
    experienceType: str = Field(..., description="Categorization of the candidate. Use 'Fresher' if they have zero professional industry experience, or 'Experienced' if they have worked in corporate or contract positions.")
    expInYears: float = Field(..., description="The total cumulative professional experience of the candidate measured in years. Express partial years as decimals (e.g., 2.5 for two and a half years).")
    currentCompany: Optional[str] = Field(None, description="The name of the company where the candidate is currently employed. Return null or an empty string if they are currently unemployed or a fresher.")
    experienceSummary: str = Field(..., description="A high-level summary overview of the candidate's professional career path, core competencies, and domain expertise.")
    role: str = Field(..., description="The current professional designation, job title, or functional role of the candidate (e.g., 'Backend Engineer').")

class Db_ProjectHistory(SQLModel,table=True):
    id: int | None = Field(default=None, primary_key=True)
    profileId: int = Field(foreign_key="db_basicinfo.id") # id from basicinfo
    title: str = Field(..., description="The formal title or name of the project the candidate worked on.")
    description: str = Field(..., description="A detailed description outlining the project scope, technical stack used, and the overall goals of the project.")
    startDate: date = Field(..., description="The date when the candidate started working on this specific project.")
    endDate: Optional[date] = Field(None, description="The date when the candidate finished working on this project. Leave blank or null if the project is ongoing or current.")
    role: str = Field(..., description="The specific role, capacity, or job title held by the candidate while working on this particular project.")
    activities: str = Field(..., description="A detailed breakdown of the candidate's core responsibilities, key contributions, individual tasks, and accomplishments within the project.")

class Db_Skillset(SQLModel,table=True):
    id: int | None = Field(default=None,primary_key=True)
    userId: int = Field(foreign_key="db_basicinfo.id") # id from basicinfo
    skillName: str = Field(..., description="The explicit name of a technical tool, framework, programming language, or soft skill possessed by the candidate (e.g., 'FastAPI').")
    expLevel: str = Field(..., description="The candidate's proficiency tier in this specific skill. Choose 'Beginner' for introductory knowledge, 'Professional' for regular production-use capability, or 'Expert' for deep mastery.")

class Db_Certifications(SQLModel,table=True):
    id: int | None = Field(default=None,primary_key=True)
    userid: int = Field(foreign_key="db_basicinfo.id") # id from basicinfo
    certicateName: str = Field(..., description="The formal name of the professional certification, license, or credential achieved by the candidate.")
    YearOfCertification: int = Field(..., description="The calendar year (4-digit format, e.g., 2024) in which the certification was officially awarded.")

class Db_Awards(SQLModel,table=True):
    id: int | None = Field(default=None,primary_key=True)
    userid: int = Field(foreign_key="db_basicinfo.id") # id from basicinfo
    awardName: str = Field(..., description="The name of the award, honor, token of recognition, or accolade received by the candidate.")
    YearOfAward: int = Field(..., description="The 4-digit calendar year when the candidate received the award.")
    companyName: str = Field(..., description="The name of the organization, institute, or employer that issued and conferred the award to the candidate.")

print(f"SQLModel.metadata is: {SQLModel.metadata}")

def create_tables(DATABASE_URL:str):
    engine = create_engine(DATABASE_URL,echo=True)
    SQLModel.metadata.create_all(engine)
    return engine

