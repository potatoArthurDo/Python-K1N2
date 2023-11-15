
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
              description= des.description, openapi_tags= des.tags,
               contact={
                   "name" : "Source code",
                   "url" : "https://github.com/potatoArthurDo/Python-K1N2/tree/main"
               } )

@app.get('/', response_class=HTMLResponse, tags=['Trang chủ'])
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
    <div style="text-align: center; color: maroon; font-size: 24px; font-weight: 500;">Nhóm 5</div>
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
@app.get("/NonZeroNP", tags=['Anh Thư Numpy'],
         description=des.des_api['AnhThuNP']['ThongKeDiem0'])
def non_zero(db: Session = Depends(get_db)):
    query_rs = db.query(models.Grade.final.label("Grade")).all()
    array = np.array(query_rs)
    np.reshape(array, -1)
    non = np.count_nonzero(array)/100
    return {
         "msg" : f'The percentage of score that is not zero is {non}%',
         #"comment" : f'Quite realistic if you compare it to this class s mid-score report, lol',
         "data" : non
    }



#Change student's one subject score 
@app.post("/ChangeScoreNP", tags=['Anh Thư Numpy'],
          description=des.des_api['AnhThuNP']['CapNhatDiemSo'])
def get_change(student : schema.UpdateScore, db : Session = Depends(get_db)):
     if student.studentID > 0:
        if student.subjectID > 0 and student.subjectID < 6:
            if student.midScore < 4:
                student.endScore = 0
                db.query(models.Grade).filter(
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

                db.query(models.Grade).filter(
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
            df = pd.DataFrame.from_dict(query_rs)
            return df.T
        else:
             raise HTTPException(status_code=404, detail= {
             "field" : "subjectID",
             "msg" : "Subject ID is a number from 1 to 5"
         })

     else:
         raise HTTPException(status_code=404, detail= {
             "field" : "studentID",
             "msg" : "Student ID must be larger than 0"
         })
               



################## AnhThu pandas
#Students that achived score "10" for final, return a html table
@app.get("/getTopPD", tags=['Anh Thư Pandas'],
         description= des.des_api['AnhThuPD']['DanhSachDiem10'])
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
@app.post("/getSimilarPD", tags=['Anh Thư Pandas'],
          description=des.des_api['AnhThuPD']['DanhSachGiongNhau'])
def get_similar(score : schema.ScoreBase, db : Session = Depends(get_db)):
    if score.midScore < 0 or score.endScore < 0:
         raise HTTPException(status_code=404, detail= {
             "field" : "midScore,endScore",
             "msg" : "Score must be postitive"
         })
    else:
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
        if (data == []) :
            return {"result" : "No data"}
        table = df.to_html()
        text_file = open("similar_list.html", "w")
        text_file.write(table)
        text_file.close()
        webbrowser.open(os.getcwd() + '/similar_list.html')
        return HTMLResponse(content = table, status_code = 200)

############################## VuDuong Region
## np
## Lấy sĩ số lớp dựa theo mã lớp
@app.post('/subject/GetClassSize', tags=["Thế Dương Numpy"],
          description= des.des_api['TheDuongNP']['SiSoLop'])

def Send_Id_GetClassSz(classID : schema.ClassBase , db: Session = Depends(get_db)):
    if classID.classID != None and classID.classID > 0:
        classSz = db.query(models.Student).join(models.Class).filter(models.Class.id == classID.classID).all()
        fullClass = db.query(models.Class).all()
        #Tổng số sinh viên  trong lớp
        num_Student_inClass = len(np.array(classSz))
        #Tổng số lớp
        allClass = len(np.array(fullClass))

        if (classID.classID > allClass):
            return f"Mã lớp {classID.classID} không tồn tại !"
        else:
            return f"Sĩ số lớp có mã lớp {classID.classID} là {num_Student_inClass} sinh viên "
    else:
        raise HTTPException(status_code=404, detail=
            f"Mã lớp {classID.classID} không hợp lệ !"
        )
#np
#Hiển thị điểm trung bình môn theo mã lớp, mã môn
@app.get('/subject/ClassSubjectAvgPoint/{classid}/{subjectid}',
         tags = ['Thế Dương Numpy'],
         description= des.des_api['TheDuongNP']['TrungBinhMon'])

def get_avg_point_subject(  classid: Union[int, None] = None, subjectid: Union[int, None] = None , db: Session = Depends(get_db)):
        if classid > 0:
            if subjectid > 0:
                classPoint = db.query(  models.Subject.name.label('Môn học'),
                                        models.Class.name.label('Lớp'),
                                        models.Grade.final.label('Điểm tổng kết')
                                    ).select_from(models.Student).join(models.Class).join(models.Grade).join(models.Subject).filter(
                                    and_(
                                        models.Student.class_id == classid,
                                        models.Grade.subject_id == subjectid
                                        )
                                        ).all()
                df = pd.DataFrame.from_dict(classPoint)
                Lop = df['Lớp'][0]
                subject = df['Môn học'][0]
                diemTK= np.array([df['Điểm tổng kết']])
                diem = np.round(np.mean(diemTK), 1)
                return f'Điểm trung bình môn {subject} của lớp {Lop} là {diem}'
            else:
                raise HTTPException(status_code=404, detail={
                    "field": "subjectid",
                    "errMsg": "Thông tin không hợp lệ"
                })
        else:
            raise HTTPException(status_code=404, detail={
                "field": "classid",
                "errMsg": "Thông tin không hợp lệ"
            })
        
#pd
#Thống kê điểm của môn học theo lớp
@app.get('/statistic/Subject/{subjectid}',
         tags = ['Thế Dương Pandas'],
         description= des.des_api['TheDuongPD']['ThongKeDiemTheoMonHoc'])
def get_point_subject_class(subjectid: int, db: Session = Depends(get_db)):
    if(subjectid > 0):
        getSubject = db.query(models.Subject).all()
        if(subjectid > len(getSubject)):
            return {
                "msg": "Không tồn tại môn học"
            }
        else:
            listStudent = db.query(models.Student.name.label('Họ và tên'),
                    models.Class.name.label('Lớp'),
                    models.Subject.name.label('Môn học'),
                    models.Grade.mid_term.label('Điểm giữa kỳ'),
                    models.Grade.end_term.label('Điểm cuối kỳ'),
                    models.Grade.final.label('Điểm tổng kết')).select_from(models.Student).join(models.Class).join(models.Grade).join(models.Subject).filter(
                     and_(
                            models.Grade.subject_id == subjectid
                        )
                    ).all()
            if( len(listStudent) != 0):
                df = pd.DataFrame.from_dict(listStudent)
                classList = df.groupby(df['Lớp']).mean(numeric_only = True).applymap(lambda x: np.round(x, 2))
                subjectName = df['Môn học'][0]
                return {
                    "msg": f"Thống kê điểm tổng kết theo lớp môn {subjectName}",
                    "data" : classList.T
                }
            else:
                return {
                    "msg": "Không tồn tại bản ghi nào"
                }
    else:
        raise HTTPException(status_code=404, detail={
                "field" : "subjectid",
                "errMsg" : "Giá trị subjectid không thể nhỏ hơn hoặc bằng 0"
            })
#pd
#Cập nhật tên lớp theo mã lớp
@app.post('/class/UpdateNameClass', tags=['Thế Dương Pandas'],
          description= des.des_api['TheDuongPD']['CapNhatTenLop'])
def post_classroom(classroom: schema.Classroom, db : Session = Depends(get_db)):
    result = " "
    if classroom.classid >0 :
        db.query(models.Class).filter(models.Class.id == classroom.classid).update(
            {
                'name': classroom.className
            })
        db.commit()
        result = db.query(models.Class).filter(models.Class.id == classroom.classid).first()
    
    else:
        result = {
            "field": "classid",
            "errMsg": "Thông tin không hợp lệ"
        }

    return result

############################## TranTu Region
#Numpy

#Tính điểm trung bình cuối kì tất cả các môn của một sinh viên  theo mã sinh viên 
@app.get('/average_grade/{student_id}', tags=['Trần Văn Tú Numpy'],
         description= des.des_api['TranTuNP']['TrungBinhCuoiKi'])
def get_average_grade(student_id: int, db: Session = Depends(get_db)):

    student = db.query(models.Student).filter(models.Student.id == student_id).first()

    if student:
        grades = db.query(models.Grade).filter(models.Grade.student_id == student_id).all()

        if grades:
            grade_values = np.array([grade.final for grade in grades])
            average_grade = np.mean(grade_values)
            return student.name + ' mã sinh viên  ' + str(student_id) + ' có điểm cuối kì trung bình là  ' + str(average_grade)
        
        else:
            return {
                "Không tồn tại bản ghi nào"
            }
        
    else:
        raise HTTPException(status_code=404, detail=f"sinh viên  với ID {student_id} không tồn tại.")
    
################################
#Điểm trung bình cuối kì tất cả các môn của một lớp theo mã lớp
@app.post('/class/CalculateClassAvg', tags=['Trần Văn Tú Numpy'],
          description= des.des_api['TranTuNP']['TrungBinhCuoiKiLop'])
def Calculate_Class_Avg(classID: schema.ClassBase, db: Session = Depends(get_db)):
    if classID.classID != None and classID.classID > 0:
        
        grades = db.query(models.Grade).join(models.Student).join(models.Class).filter(models.Class.id == classID.classID).all()

        finals = np.array([grade.final for grade in grades])

        avg_final = np.mean(finals)
        
        # Lấy danh sách tất cả lớp
        fullClass = db.query(models.Class).all()
        
        # Tính tổng số lớp
        allClass = len(np.array(fullClass))
        
        if classID.classID > allClass:
            return f"Mã lớp {classID.classID} không tồn tại!"
        else:
            return f"Điểm trung bình cuối tất cả các môn của lớp có mã lớp {classID.classID} là {avg_final:.2f}"
    else:
        raise HTTPException(status_code=404, detail=f"Mã lớp {classID.classID} không hợp lệ!")
    

#Pandas

#Đếm số sinh viên qua môn
@app.get('/passing_students/{subject_id}', tags=['Trần Văn Tú Pandas'],
         description=des.des_api['TranTuPD']['QuaMon'])
def count_passing_students_by_subject(subject_id: int, db: Session = Depends(get_db)):
    if subject_id > 0:
        get_subject = db.query(models.Subject).all()
        if subject_id > len(get_subject):
            return {"msg": "Không tồn tại môn học"}
        else:
            subject = get_subject[subject_id - 1]

            df_students = pd.read_sql_query(
                f"SELECT final AS 'Điểm tổng kết' FROM Student "
                f"JOIN Class ON Student.class_id = Class.id "
                f"JOIN Grade ON Student.id = Grade.student_id "
                f"JOIN Subject ON Grade.subject_id = Subject.id "
                f"WHERE Subject.id = {subject_id} AND Grade.final >= 4",
                db.bind
            )

            num_passing_students = len(df_students)

            return {
                "msg": f"Số sinh viên  qua môn {subject.name} là: {num_passing_students}"
            }
    else:
        raise HTTPException(status_code=404, detail={
            "field": "subject_id",
            "errMsg": "Giá trị subject_id không thể nhỏ hơn hoặc bằng 0"
        })

#Cập nhật tên môn học
@app.post('/subject/UpdateSubjectName', tags=['Trần Văn Tú Pandas'],
          description=des.des_api['TranTuPD']['CapNhatTenMon'])
def update_subject_name(subject_update: schema.SubjectUpdate, db: Session = Depends(get_db)):
    result = {}
    subject = db.query(models.Subject).filter(models.Subject.id == subject_update.subject_id).first()
    
    if subject:
        db.query(models.Subject).filter(models.Subject.id == subject_update.subject_id).update(
            {
                'name': subject_update.subject_name
            }
        )
        db.commit()
        
        updated_subject = db.query(models.Subject).filter(models.Subject.id == subject_update.subject_id).first()
        
        result = {
            'message': 'Tên môn đã được cập nhật',
            'updated_subject': updated_subject
        }
    else:
        result = {
            'message': 'Mã môn không tồn tại'
        }

    return result

