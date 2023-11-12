from pydantic import BaseModel 

class StudentBase(BaseModel):
    name: str
    class_name: str

class StudentCreate(StudentBase):
    pass

class ScoreBase(BaseModel):
    midScore: float
    endScore: float
class UpdateScore(BaseModel):
    studentID : int
    subjectID : int
    midScore: float
    endScore: float

class ClassBase(BaseModel):
    classID : int
class Classroom(BaseModel):
    className: str
    classid: int

class SubjectUpdate(BaseModel):
    subject_id: int
    subject_name: str