import sqlite3
import numpy as np
import random

def Connect():
    conn = sqlite3.connect('StudentGrade.db')
    cursor = conn.cursor()

    subject_list = [
        ["Python"],
        ["Java"],
        ["Data Structure"],
        ["Calculus"],
        ['Linear Algebra']
    ]
    cursor.executemany('''INSERT INTO "subject"("name") VALUES (?)''', subject_list)

    #start_group = 31
    #end_group = 36
    group = [31,32,33,34,35,36]
    class_list = ["TT", "TI", "TE"]
    class_ini = ["A", "B", "C", "D", "E", "F", "G", "H"]
    for i in class_list:
        for j in group:
            for k in class_ini:
                cursor.execute(''' INSERT INTO "class"("name") VALUES (?)''', [f'{i}{j}{k}'])

    title_list = ["Mr. ", "Mrs. "]
    name_list = ["River", "Quinn", "Jordan", "Ryan", "Noah", "Kai", "Ash", "Drew", "Oakley",
                 "Robin", "Cleo", "Ariel", "Ocean", "Taylor", "True", "Lou", "Cheesey", "Pepe",
                 "Charlie", "Pope", "Storm", "Sea", "Buddy", "Sunday", "Seven", "Moon", "Bear"]
    lastname_list = ["Madworthy", "Pottywhistle", "SnotShine",
                     "Spotteye","Noodleworthy", "Rottenborn",
                     "Mudbean", "HippyBottom", "Bobabean", "WiggleBottom",
                     "Doodookins", "Bacon", "Salmon", "Focker"
                     "Dikshit", "Peabisbreath", "Longbottom", "Pusey",
                     "Onions", "Rollo-Koster", "Weed", "Panini",
                     "Wanket", "Cox", "Titball", "Poots", "Wacko"]
    



    student_each_class = 5
    all_class = len(class_list) * len(class_ini) * len(group)
    def setClass(class_id, student_each_class):
       in_class = cursor.execute('''SELECT * FROM "student" WHERE class_id = ?''', [class_id])

       if(len(in_class.fetchall()) < student_each_class):
          return class_id
       else:
           new_id = random.randint(0, all_class)
           new_student = student_each_class
           return setClass(new_id,new_student)
       
    def setStudent(class_id):
        title = title_list[random.randint(0,1)]
        first_name = name_list[int(np.floor(len(name_list) * np.random.random()))]
        last_name = lastname_list[int(np.floor(len(lastname_list) * np.random.random()))]
        cursor.execute(''' INSERT INTO "student"("name","class_id") VALUES(?,?)''', [f'{title}{first_name} {last_name}', class_id])

    all_student = (student_each_class * len(class_list) * len(class_ini) * len(group))

    for i in range(0, all_student + 1):
        class_id = int((len(class_list) * len(class_ini) * len(group)) * np.random.random())
        setStudent(setClass(class_id,student_each_class))

    for student in range(0, all_student):
       # subject_count = cursor.execute('''SELECT * FROM "subject"''')
        for subject in range(0, len(subject_list)):
            mid = random.randint(0,10)
            if(mid > 4):
                end = random.randint(0,10)
                final = (mid*0.3) + (end * 0.7)
            else:
                end = 0
                final = 0
            cursor.execute('''INSERT INTO "grade"("student_id","subject_id","mid_term","end_term","final")
                           VALUES (?,?,?,?,?)''',
                           [student+1, subject + 1, mid,end,final])
    conn.commit()
    conn.close()
               