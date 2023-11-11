from pydantic import BaseModel 

class StudentBase(BaseModel):
    name: str
    class_name: str

class StudentCreate(StudentBase):
    pass

class ScoreBase(BaseModel):
    midScore:int
    endScore:int
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