from sqlalchemy import REAL, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Student(Base):
    __tablename__ = "student"
    id = Column(Integer, primary_key= True, autoincrement= True, index= True, nullable=False)
    name = Column(String(100), nullable=False)
    class_id = Column(Integer,ForeignKey("class.id"), nullable=False, index=True)

    grade = relationship("Grade", back_populates="student_grade")
    in_class = relationship("Class", back_populates="student_in")


class Class(Base):
    __tablename__ = "class"
    id = Column(Integer, primary_key= True, nullable= False, autoincrement= True)
    name = Column(String (50), nullable= False)
    #group = Column(String, index = True, nullable=False)

    student_in = relationship("Student", back_populates="in_class")

class Subject(Base):
    __tablename__ = 'subject'
    id  = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    name = Column(String(50), nullable=False)

    grade = relationship("Grade", back_populates="subject_grade")

#grades per subject
class Grade(Base):
    __tablename__ = 'grade'
    #row_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student.id"), primary_key=True,  index=True, nullable=False)
    subject_id = Column(Integer, ForeignKey("subject.id"), primary_key=True,  index=True, nullable=False)
    mid_term = Column(REAL, index=True, nullable=False)
    end_term = Column(REAL, index=True, nullable=False)
    final = Column(REAL, index=True, nullable=False)

    student_grade = relationship("Student", back_populates="grade")
    subject_grade = relationship("Subject", back_populates="grade")
    