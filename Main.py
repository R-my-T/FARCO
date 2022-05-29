#----------------------------------------------------------------------------#
#                    FARCO - FACE RECOGNITION ATTENDANCE SYSTEM              #
#----------------------------------------------------------------------------#


#Importing all the necessary libraries
from asyncio.windows_events import NULL
from flask import Flask, render_template, request,redirect,session
from flask import redirect, url_for, session, Response
from flask import session, request
import pandas as pd
import sqlite3,os
from datetime import datetime
from flask_session import Session
from flask import *
from passlib.hash import sha256_crypt
import cv2
import numpy as np
import face_recognition as fr
import time
from datetime import date
from werkzeug.utils import secure_filename

app = Flask(__name__)
app = Flask(__name__, template_folder= "templates")

UPLOAD_FOLDER = 'CSV_Input_files'
UPLOAD_IMAGE_FOLDER = 'Face_Imgs'
ALLOWED_EXTENSIONS = set(['png','jpg','jpeg'])

app.secret_key= b'\xdaKmm\x02|_\x8f\xcb\xc4,j'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_IMAGE_FOLDER'] = UPLOAD_IMAGE_FOLDER
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#Function to check if the given file has a valid filetype:
def allowed_filetype(filename):
   return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

#Function to parse the content of the csv file:
def parseCSV(filePath):
   columns=['Register_No','Name','Contact']
   data = pd.read_csv(filePath,names=columns,header=None)
   return data

#Function to connect with the database and mark present:
def mark_attendance(Person_ID):

   print ("Making a connection : To mark present")
   connection = sqlite3.connect('attendance.db')
   cursor = connection.cursor()
   cursor.execute("select Present_Days from People where P_ID=(?)",(Person_ID,))
   PresentDays = cursor.fetchall()
   PresentDays = PresentDays[0][0]+1
   cursor.execute("update People set Present_Days=(?) where P_ID=(?)",(PresentDays,Person_ID,))
   print ("Database updated")
   connection.commit()
   print ("Closing the connection")
   connection.close()

#Function to connect with the database and mark absent:
def mark_absent(Person_ID):

   print ("Making a connection : To mark absent")
   connection = sqlite3.connect('attendance.db')
   cursor = connection.cursor()
   cursor.execute("select Absent_Dates from People where P_ID=(?)",(Person_ID,))
   AbsentDates = cursor.fetchall()

   Current_date = str(date.today())
   if(AbsentDates[0][0]== None):
      AbsentDates = str(Current_date)
   else:
      AbsentDates = str(AbsentDates[0][0]+ ',' + Current_date)

   cursor.execute("update People set Absent_Dates=(?) where P_ID=(?)",(AbsentDates,Person_ID,))
   print ("Closing the connection")
   connection.commit()
   connection.close()

#------- Home Page -----------
@app.route('/')
def Home_Page():
   return render_template("Home_Page.html")

#------- Register Organisation -----------
@app.route('/Register_Organisation',methods=['GET','POST'])
def Register_Org():
   if request.method == 'POST':
      name = request.form['name']
      type = request.form['type']
      password = request.form['password']

      if(len(password)<6):
         flash("Password length is less than 6 characters")
         return redirect(url_for('Reg_Org'))
      password = sha256_crypt.encrypt(password)

      try:

         print ("Making a connection with the database : Registering new organisation")
         connection = sqlite3.connect('attendance.db')
         cursor = connection.cursor()
         cursor.execute("INSERT into Organisations (Name,Password,Type) values (?,?,?)",(name,password,type))  
         print ("Commiting the changes")
         connection.commit()
         print ("Closing the datbase")
         connection.close()

         return redirect(url_for('Home_Page'))

      except Exception as error:
         return_message = str(error)
         if(return_message=='UNIQUE constraint failed: Organisations.Name'):
            flash('Organisation name already exists. Please try a different one')
            return redirect(url_for('Register_Org'))
         else:
            return(error)
   else:
      return render_template("Register_Org.html")

#------- Log In Page -----------
@app.route('/Log_In',methods=['GET','POST'])
def Log_In():
   if request.method == 'POST':
      name = request.form['name']
      password = request.form['password']
      session["user"] = name
      try:

         print("Making a connection : To retrieve user login credentials")
         connection = sqlite3.connect('Attendance.db')
         cursor = connection.cursor()
         cursor.execute("SELECT Password,Org_ID from Organisations where Name=?", (name,))
         all_information = cursor.fetchall()
         print("Closing the connection")
         connection.close()

         if(len(all_information)==0):
            flash("Incorrect Name! Please try again.")
            return redirect(url_for('Log_In'))

         elif (sha256_crypt.verify(password,all_information[0][0])):
            session['Org_ID']=all_information[0][1]
            return redirect(url_for('Check_Empty'))

         else:
            flash("Incorrect Password! Please try again.")
            return redirect(url_for('Log_In'))

      except Exception as error:
         return_message = str(error)
         return(return_message)
   else:
      return render_template("Login.html")

#------- Checking if there are no departments registered -----------
@app.route('/Empty',methods=['GET','POST'])
def Check_Empty():
   if not session.get("user"):
      return redirect(url_for('Log_In'))
   Org_ID = session.get('Org_ID', None)

   try:

      print("Making a connection: To check if there are depts registered")
      connection = sqlite3.connect('Attendance.db')
      cursor = connection.cursor()
      cursor.execute("SELECT Dept_Name from Departments where Org_ID=?", (Org_ID,))
      all_information = cursor.fetchall()
      print("Closing the connection")
      connection.close()

      if(len(all_information)==0):
         return render_template('Empty.html')

      else:
         return redirect(url_for('List_Depts'))

   except Exception as error:
      return_message = str(error)
      return(return_message)

#------- Viewing the list of Departments -----------
@app.route('/List_Depts',methods=['GET','POST'])
def List_Depts():
   if not session.get("user"):
      return redirect(url_for('Log_In'))

   try:

      Org_ID = session.get('Org_ID', None)
      print("Making a connection: Retrieving department information")
      connection = sqlite3.connect('Attendance.db')
      cursor = connection.cursor()
      cursor.execute("SELECT Dept_Name,Description,No_of_People from Departments where Org_ID=?", (Org_ID,))
      all_information = cursor.fetchall()
      cursor = connection.cursor()
      cursor.execute("SELECT Type from Organisations where Org_ID=?", (Org_ID,))
      type = cursor.fetchall()
      print("Closing the connection")
      connection.close()

      if(type[0][0] =='School'):
         type='classroom'
      elif(type[0][0] == 'Office'):
         type='department'
      else:
         type='subdivision'
      
      if request.method == 'POST':
         dept = request.form['dept']
         session['Dept'] = dept
         return redirect(url_for('Set_Timer'))

      else:
         return render_template('List_Depts.html',Depts=all_information,type=type)

   except Exception as error:
      return_message = str(error)
      return(return_message)

#------- Setting Timer -----------
@app.route('/Set_Timer',methods=['GET','POST'])
def Set_Timer():
   if not session.get("user"):
      return redirect(url_for('Log_In'))
   if request.method == 'POST':
      timer = request.form['timer']
      session['timer'] = timer

      return redirect(url_for('Take_Attendance'))
   else:
      return render_template("Set_Timer.html")

#------- Recognizing Faces -----------
@app.route('/Take_Attendance',methods=['GET','POST'])
def Take_Attendance():
   timer = int(session['timer'])
   return render_template('Take_Attendance.html',timer = timer)

@app.route('/Attendance',methods=['GET','POST'])
def Attendance():
   Dept = session['Dept']
   timer = int(session['timer'])

   print ("Making a connection : To retrieve people's information to recognise their faces")
   connection = sqlite3.connect('attendance.db')
   cursor = connection.cursor()
   cursor.execute("select Dept_ID from Departments where Dept_Name=?",(Dept,))
   Dept_ID = cursor.fetchall()
   cursor.execute("select * from people where Dept_Id=?",(Dept_ID[0][0],))
   all_profiles = cursor.fetchall() 
   print ("Closing the datbase")
   connection.close()
 
   encoded_list = []
   known_names=[]
   present_names=[]
   AllPerson_ID=[]

   for profile in all_profiles:
      imgPerson = cv2.imread(profile[6])
      imgPerson = cv2.cvtColor(imgPerson,cv2.COLOR_BGR2RGB)
      encode = fr.face_encodings(imgPerson)[0]
      encoded_list.append(encode)
      known_names.append(profile[4])
      AllPerson_ID.append(profile[0])

   print("Encoding complete")
   capture = cv2.VideoCapture(0,cv2.CAP_DSHOW)
   present_names=[]
   present_PID=[]

   def generate_frames():  
      print("Recognising faces has started..") 
      #Website recognises faces for given number of seconds
      timeout = timer*60 
      timeout_start = time.time()
      while time.time() < timeout_start + timeout:
         success,frame = capture.read()
         #Reduce size of our image to make processing faster and easier
         img_small = cv2.resize(frame,(0,0),None,0.25,0.25)
         img_small = cv2.cvtColor(img_small,cv2.COLOR_BGR2RGB)
         
         #Getting the face measures from the webcam and encoding it
         current_face = fr.face_locations(img_small)
         encoded_current_face = fr.face_encodings(img_small,current_face)

         for encoded_face,face_location in zip(encoded_current_face,current_face):
            matches = fr.compare_faces(encoded_list,encoded_face)
            face_dist = fr.face_distance(encoded_list,encoded_face)
            #Face distances with least value will be chosen as the best match
            matchIndex = np.argmin(face_dist)

            if matches[matchIndex]:
               name = known_names[matchIndex]
               if(name not in present_names):
                  present_names.append(name)
                  present_PID.append(AllPerson_ID[matchIndex])
                  mark_attendance(AllPerson_ID[matchIndex])

               y1,x2,y2,x1 = face_location 
               #Scaling the image back up to display in the website
               y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4 
               cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
               cv2.rectangle(frame,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
               cv2.putText(frame,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),2)

         ret, buffer = cv2.imencode('.jpg', frame)
         frame = buffer.tobytes()
         yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

      print("Recognising faces has stopped")
      capture.release()
      for ID in AllPerson_ID:
         if ID not in present_PID:
            mark_absent(ID)
      return(0)

   if(generate_frames()!=0):
      return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
   else:
      capture.release()
      cv2.destroyAllWindows()
      return redirect(url_for('Home_Page'))

#------- Adding departments -----------
@app.route('/Add_Dept',methods=['GET','POST'])
def Add_Dept():
   if not session.get("user"):
      return redirect(url_for('Log_In'))
   if request.method == 'POST':
      Org_ID = session['Org_ID']
      Dept_Name = request.form['Dept_Name']
      Dept_Desc = request.form['Description']
      No_of_People = request.form['No_of_People']

      try:

         print("Making a connection : To add new department")
         connection = sqlite3.connect('Attendance.db')
         cursor = connection.cursor()
         cursor.execute("Insert into Departments (Org_ID,Dept_Name,Description,No_of_People) values (?,?,?,?)",(Org_ID,Dept_Name,Dept_Desc,No_of_People,))
         connection.commit()
         connection.close()
         connection = sqlite3.connect('Attendance.db')
         cursor = connection.cursor()
         cursor.execute("select Dept_ID from Departments where Org_ID=(?) and Dept_Name=(?)",(Org_ID,Dept_Name,))
         Dept_ID = cursor.fetchall()
         session['Add_Dept']=Dept_ID[0][0]
         print("Closing the connection")
         connection.close()

         return redirect(url_for('Add_People'))

      except Exception as error:
         return_message = str(error)
         return(return_message)
   
   else:
      return render_template('Add_Dept.html')

#------- Adding people to their departments -----------
@app.route('/Add_People',methods=['GET','POST'])
def Add_People():
   if not session.get("user"):
      return redirect(url_for('Log_In'))
   if request.method == 'POST':
      uploaded_file = request.files['CSVfile']
      image_files = request.files.getlist('files[]')
      images=[]
      if uploaded_file.filename!='':
         file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
         uploaded_file.save(file_path)
         #Read the values from the uploaded csv file and store it in data
         data = parseCSV(file_path)
         Org_ID = session['Org_ID']
         Dept_ID = session['Add_Dept']
         
         for image in image_files:
            if image and allowed_filetype(image.filename):
               filename = secure_filename(image.filename)
               image.save(os.path.join(app.config['UPLOAD_IMAGE_FOLDER'],filename))
               #Append all the uploaded images' address to the images list
               images.append(UPLOAD_IMAGE_FOLDER+'/'+filename)

         for row,values in data.iterrows():
            try:

               print("Making a connection : To save new people's information")
               connection = sqlite3.connect('Attendance.db')
               cursor = connection.cursor()
               cursor.execute("Insert into People (Org_ID,Dept_ID,Register_No,Name,Contact,Face_Img) values (?,?,?,?,?,?)",(Org_ID,Dept_ID,values['Register_No'],values['Name'],values['Contact'],images[row]))
               connection.commit()
               connection.close()

            except Exception as error:
               return_message = str(error)
               return(return_message)

         #To remove the csv file after reading to save memory
         os.remove(file_path) 
         return redirect(url_for('List_Depts'))

   else:
      return render_template("Add_People.html")

#------- Deleting departments -----------
@app.route('/Delete_Dept',methods=['GET','POST'])
def Delete_Dept():
   if not session.get("user"):
      return redirect(url_for('Log_In'))
   Org_ID = session['Org_ID']
   if request.method == 'POST':
      Dept_Name = request.form['Dept_Name']

      try:

         print("Making a connection : To delete an existing department")
         connection = sqlite3.connect('Attendance.db')
         cursor = connection.cursor()
         cursor.execute("select Dept_ID from Departments where Dept_Name = (?) and Org_ID=(?)",(Dept_Name,Org_ID))
         Dept_ID = cursor.fetchall()
         cursor.execute("Delete from Departments where Dept_ID = (?) and Org_ID=(?)",(Dept_ID[0][0],Org_ID))
         cursor.execute("Delete from People where Dept_ID = (?) and Org_ID=(?)",(Dept_ID[0][0],Org_ID))
         connection.commit()
         print("Closing the connection")
         connection.close()

         return redirect(url_for('List_Depts'))

      except Exception as error:
         return_message = str(error)
         return(return_message)
   
   else:
      try:

         print("Making a connection : To display the list of departments that can be deleted")
         connection = sqlite3.connect('Attendance.db')
         cursor = connection.cursor()
         cursor.execute("select Dept_Name from Departments where Org_ID=(?)",(Org_ID,))
         Dept_Names = cursor.fetchall()
         print("Closing the connection")
         connection.close()
      
      except Exception as error:
         return_message = str(error)
         return(return_message)

      return render_template('Delete_Dept.html',Dept_Names=Dept_Names)

#------- View department info -----------
@app.route('/View_Dept',methods=['GET','POST'])
def View_Dept():
   if not session.get("user"):
      return redirect(url_for('Log_In'))
   Org_ID = session['Org_ID']
   if request.method == 'POST':
      Dept_Name = request.form['Dept_Name']

      try:

         print("Making a connection : To view the people's information from chosen department")
         connection = sqlite3.connect('Attendance.db')
         cursor = connection.cursor()
         cursor.execute("select Dept_ID from Departments where Dept_Name = (?) and Org_ID=(?)",(Dept_Name,Org_ID))
         Dept_ID = cursor.fetchall()
         cursor.execute("Select Name,Contact,Face_Img,Present_Days,Absent_Dates,Register_No from People where Dept_ID = (?) and Org_ID=(?)",(Dept_ID[0][0],Org_ID))
         All_information = cursor.fetchall()
         print("Closing the connection")
         connection.close()

         return render_template('View_Information.html',All_information = All_information)

      except Exception as error:
         return_message = str(error)
         return(return_message)
   
   else:
      try:

         print("Making a connection: To display list of depts whose information can be viewed")
         connection = sqlite3.connect('Attendance.db')
         cursor = connection.cursor()
         cursor.execute("select Dept_Name from Departments where Org_ID=(?)",(Org_ID,))
         Dept_Names = cursor.fetchall()
         print("Closing the connection")
         connection.close()
      
      except Exception as error:
         return_message = str(error)
         return(return_message)

      return render_template('View_Select_Dept.html',Dept_Names=Dept_Names)

#------- Log Out -----------
@app.route("/logout")
def Log_Out():
    session["user"] = None
    return redirect(url_for('Home_Page'))

#------- View Attendance -----------
@app.route('/View_Attendance',methods=['GET','POST'])
def View_Attendance():
   if request.method == 'POST':
      Org_Name = request.form['Org_Name']
      Dept_Name = request.form['Dept_Name']
      Register_No = request.form['Register_No']
      
      try:

         print("Making a connection : To get people's attendance record")
         connection = sqlite3.connect('Attendance.db')
         cursor = connection.cursor()
         cursor.execute("SELECT Org_ID from Organisations where Name=?",(Org_Name,))
         Org_ID = cursor.fetchall()
         Org_ID = Org_ID[0][0]
         cursor.execute("SELECT Dept_ID from Departments where Dept_Name=?",(Dept_Name,))
         Dept_ID = cursor.fetchall()
         Dept_ID = Dept_ID[0][0]
         cursor.execute("SELECT Name,Present_Days,Absent_Dates from People where Org_ID=? and Dept_ID=? and Register_No=?",(Org_ID,Dept_ID,Register_No,))
         All_information = cursor.fetchall()
         print("Closing the connection")
         connection.close()

         return render_template("View_Attendance.html", All_information = All_information[0])

      except Exception as error:
         return_message = str(error)
         return(return_message)
   else:
      return render_template("View_Attendance_Login.html")

#------- About Me -----------
@app.route('/About_Me')
def About_Me():
   return render_template('About_Me.html')

if __name__ == '__main__':
   app.run()
   app.debug = True 
