from pydantic import BaseModel, Field
from typing import Literal
from datetime import date

from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, Field

class BasicInfo(BaseModel):
    firstName: str = Field(..., description="The candidate's legal given name or first name.")
    lastName: str = Field(..., description="The candidate's legal family name or last name.")
    dob: Optional[date] = Field(..., description="The candidate's Date of Birth. Must be strictly formatted as an ISO-8601 date string (YYYY-MM-DD). Return NA if you don't find")
    Mobile: int = Field(..., description="The candidate's primary mobile contact number including country code if available, extracted as continuous digits without spaces or dashes.")
    email: str = Field(..., description="The candidate's primary professional email address. Extract full email address.")
    aadhar: Optional[int] = Field(..., description="The unique 12-digit national identification number (Aadhaar number) of the candidate. Return NA if you don't find it")
    experienceType: Literal['Fresher', 'Experienced'] = Field(..., description="Categorization of the candidate. Use 'Fresher' if they have zero professional industry experience, or 'Experienced' if they have worked in corporate or contract positions.")
    expInYears: float = Field(..., description="The total cumulative professional experience of the candidate measured in years. Express partial years as decimals (e.g., 2.5 for two and a half years).")
    currentCompany: Optional[str] = Field(None, description="The name of the company where the candidate is currently employed. Return null or an empty string if they are currently unemployed or a fresher.")
    experienceSummary: str = Field(..., description="A high-level summary overview of the candidate's professional career path, core competencies, and domain expertise.")
    role: str = Field(..., description="The current professional designation, job title, or functional role of the candidate (e.g., 'Backend Engineer').")

class ProjectHistory(BaseModel):
    title: str = Field(..., description="The formal title or name of the project the candidate worked on.")
    description: str = Field(..., description="A detailed description outlining the project scope, technical stack used, and the overall goals of the project.")
    startDate: date = Field(..., description="The date when the candidate started working on this specific project.")
    endDate: Optional[date] = Field(None, description="The date when the candidate finished working on this project. Leave blank or null if the project is ongoing or current.")
    role: str = Field(..., description="The specific role, capacity, or job title held by the candidate while working on this particular project.")
    activities: str = Field(..., description="A detailed breakdown of the candidate's core responsibilities, key contributions, individual tasks, and accomplishments within the project.")

class SkillSet(BaseModel):
    skillName: str = Field(..., description="The explicit name of a technical tool, framework, programming language, or soft skill possessed by the candidate (e.g., 'FastAPI').")
    expLevel: Literal['Beginner', 'Professional', 'Expert'] = Field(..., description="The candidate's proficiency tier in this specific skill. Choose 'Beginner' for introductory knowledge, 'Professional' for regular production-use capability, or 'Expert' for deep mastery.")

class Certifications(BaseModel):
    certicateName: str = Field(..., description="The formal name of the professional certification, license, or credential achieved by the candidate.")
    YearOfCertification: int = Field(..., description="The calendar year (4-digit format, e.g., 2024) in which the certification was officially awarded.")

class Awards(BaseModel):
    awardName: str = Field(..., description="The name of the award, honor, token of recognition, or accolade received by the candidate.")
    YearOfAward: int = Field(..., description="The 4-digit calendar year when the candidate received the award.")
    companyName: str = Field(..., description="The name of the organization, institute, or employer that issued and conferred the award to the candidate.")

class ProfileInfo(BaseModel):
    candidateInfo: BasicInfo = Field(..., description="The foundational contact, identity, and high-level career summary details of the candidate.")
    candidateProjectHistory: list[ProjectHistory] = Field(default_factory=list, description="An itemized list containing the historical record of individual projects the candidate has executed throughout their career.")
    candidateSkillSet: list[SkillSet] = Field(default_factory=list, description="A comprehensive inventory list of the candidate's verified skills along with their corresponding proficiency levels.")
    candidateCertifications: list[Certifications] = Field(default_factory=list, description="A chronological list of all valid industrial credentials, certifications, or professional licenses held by the candidate.")
    candidateAwards: list[Awards] = Field(default_factory=list, description="A collection list of honors, competitive rewards, or company recognitions earned by the candidate.")