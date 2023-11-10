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
    midScore: int
    endScore: int