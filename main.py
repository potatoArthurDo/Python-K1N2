
import os
import webbrowser
from fastapi import  FastAPI, Depends, HTTPException, Response
from typing import Union
from fastapi.responses import HTMLResponse

from sqlalchemy import and_
import sql.models as models
from database import engine, get_db
import sqlite3
import time
from sql.default_data import Connect
from sqlalchemy.orm import Session
import sql.schemas as schema
import numpy as np
import pandas as pd
import description as des


models.Base.metadata.create_all(bind = engine)
#Connect()
while True:
    try:
        conn = sqlite3.connect('StudentGrade.db')
        cursor = conn.cursor()
        print("Database connected")
        break
    except Exception as error:
        print ("Database Connection Failed")
        print("Error", error)
        time.sleep(2)


app = FastAPI( title= "Quản lý điểm sinh viên",
              description= des.description)

@app.get('/')
def home():
    html_content = '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <div style="text-align: center;"><h1>BÀI TẬP LỚN MÔN PYTHON</h1></div>
    <div style="text-align: center; color: maroon; font-size: 24px; font-weight: 500;">Nhóm 3</div>
    <div style="text-align: center; color: maroon; font-size: 25px; font-weight: 600;">Quản lý điểm sinh viên</div>
    <div style="text-align: left; font-size:  20px; font-weight: 700;">Thành viên: </div>
    <div s><ul style="list-style-type: none; display: block; text-align: left; font-size: 18px;; font-weight: 500;color: navy;">
        <li>A37527 - Đỗ Anh Thư</li>
        <li>A38322 - Trần Văn Tú</li>
        <li>A38221 - Vũ Thế Dương</li>
    </ul></div>
</body>
</html>'''
    return HTMLResponse(content=html_content, status_code=200)
        


################## AnhThu numpy     
# Calculate the percentage of non zero final scores
@app.get("/NonZeroNP")
def non_zero(db: Session = Depends(get_db)):
    query_rs = db.query(models.Grade.final.label("Grade")).all()
    array = np.array(query_rs)
    np.reshape(array, -1)
    non = np.count_nonzero(array)/100
    return {
         "msg" : f'The percentage of score zero is {non}%',
         #"comment" : f'Quite realistic if you compare it to this class s mid-score report, lol',
         "data" : non
    }



#Change student's one subject score 
@app.post("/ChangeScoreNP")
def get_change(student : schema.UpdateScore, db : Session = Depends(get_db)):
     if student.studentID > 0 and student.subjectID > 0:
        if student.midScore < 4:
            student.endScore = 0
            data = db.query(models.Grade).filter(
            and_(
                 models.Grade.student_id == student.studentID,
                 models.Grade.subject_id == student.subjectID
            )
             ).update({
            'mid_term' : student.midScore,
            'end_term' : 0,
            'final' : 0
            
             })
        else:

            data = db.query(models.Grade).filter(
                 and_(
                      models.Grade.student_id == student.studentID,
                      models.Grade.subject_id == student.subjectID
                 )
            ).update({
                 'mid_term' : student.midScore,
                 'end_term' : student.endScore,
                 'final' :np.round( student.midScore * 0.3 + student.endScore * 0.7)

            })
        db.commit()
        query_rs = db.query(models.Student.name.label("Name"),
                            models.Subject.name.label("Subject"),
                            models.Grade.mid_term.label("Mid Term"),
                            models.Grade.end_term.label("End Term"),
                            models.Grade.final.label("Final")).select_from(models.Student).join(models.Grade).join(models.Subject).filter(
             and_(
                  models.Grade.student_id== student.studentID,
                  models.Grade.subject_id == student.subjectID

             )
        ).all()
        return query_rs
     else:
         raise HTTPException(status_code=404, detail= {
             "field" : "studentID, subjectID",
             "msg" : "Invalid input"
         })
               



################## AnhThu pandas
#Students that achived score "10" for final, return a html table
@app.get("/getTopPD")
def get_top(db : Session = Depends(get_db)):
    query_rs = db.query(models.Student.name.label("Name"), models.Subject.name.label("Subject"),
                         models.Grade.final.label("Score")).filter(
                        models.Grade.final == 10 ).join(models.Student).join(models.Subject).all()
    df = pd.DataFrame.from_dict(query_rs)
    table = df.to_html()
    text_file = open("list.html", "w")
    text_file.write(table)
    text_file.close()
    webbrowser.open(os.getcwd() + '/list.html')
    return HTMLResponse(content = table, status_code = 200)

#Students that achived the same score as the input
@app.post("/getSimilarPD")
def get_similar(score : schema.ScoreBase, db : Session = Depends(get_db)):
    if score.midScore < 4:
        score.endScore = 0
    data = db.query(
                    models.Student.id.label("Student ID"),
                     models.Student.name.label("Student Name"),
                     models.Class.name.label("Class"),
                    models.Subject.name.label("Subject"),
                    models.Grade.mid_term.label("Mid term"),
                    models.Grade.end_term.label("End term")
                    ).select_from(models.Student).join(models.Class).join(models.Grade).join(models.Subject).filter(
                        and_(
                            models.Grade.mid_term == score.midScore,
                            models.Grade.end_term == score.endScore
                        )
                    ).all()
    df = pd.DataFrame.from_dict(data)
    table = df.to_html()
    text_file = open("similar_list.html", "w")
    text_file.write(table)
    text_file.close()
    webbrowser.open(os.getcwd() + '/similar_list.html')
    return HTMLResponse(content = table, status_code = 200)

##############################