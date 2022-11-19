from cProfile import run
from turtle import st
from flask import Flask, render_template, request, redirect, url_for, session,jsonify
from markupsafe import escape
from flask_mail import Mail,Message

import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


import ibm_db
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=19af6446-6171-4641-8aba-9dcff8e1b6ff.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30699;SECURITY=SSL;SSLServerCertificate=C:/Users/SONA COLLEGE/Desktop/IBM-PROJECT-DEMO/Containment Zone alerting app/templates/DigiCertGlobalRootCA.crt;UID=qxc23007;PWD=4rIT5VpkoO6D0FQM",'','')

app = Flask(__name__)
app.secret_key = "unique secret key"

app.config['MAIL_SERVER'] ='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'x@gmail.com'
app.config['MAIL_PASSWORD'] = '123456'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail= Mail(app)

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/login1')
def login1():
  return render_template('login.html')

@app.route('/adduser')
def new_student():
  return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
  return render_template('dashboard.html')

@app.route('/logout')
def logout():
  return render_template('home.html')


def send_mail(email):
    print(email)
    message = Mail(from_email='risingragul@gmail.com',
                   to_emails=email,
                   subject='caution',
                   plain_text_content='Please Stay Safe',
                   html_content='<h2>You are entering into a containment Zone</h2>')

    try:
        sg = SendGridAPIClient(apikey='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')
        response = sg.send(message)
        print(response.status.code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)


@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
  if request.method == 'POST':

    name = request.form['name']
    email = request.form['email']
    password = request.form['pwd']

    sql = "SELECT * FROM user WHERE name =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,name)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)

    if account:
      return render_template('list.html', msg="You are already a member, please login using your details")
    else:
      insert_sql = "INSERT INTO user VALUES (?,?,?)"
      prep_stmt = ibm_db.prepare(conn, insert_sql)
      ibm_db.bind_param(prep_stmt, 1, name)
      ibm_db.bind_param(prep_stmt, 2, email)
      ibm_db.bind_param(prep_stmt, 3, password)

      ibm_db.execute(prep_stmt)
    
    return render_template('home.html', msg="Student Data saved successfuly..")

@app.route('/list')
def list():
  students = []
  sql = "SELECT * FROM user"
  stmt = ibm_db.exec_immediate(conn, sql)
  dictionary = ibm_db.fetch_both(stmt)
  while dictionary != False:
    # print ("The Name is : ",  dictionary)
    students.append(dictionary)
    dictionary = ibm_db.fetch_both(stmt)

  if students:
    return render_template("list.html", students = students)

# @app.route('/delete/<name>')
# def delete(name):
#   sql = f"SELECT * FROM user WHERE name='{escape(name)}'"
#   print(sql)
#   stmt = ibm_db.exec_immediate(conn, sql)
#   student = ibm_db.fetch_row(stmt)
#   print ("The Name is : ",  student)
#   if student:
#     sql = f"DELETE FROM Students WHERE name='{escape(name)}'"
#     print(sql)
#     stmt = ibm_db.exec_immediate(conn, sql)

#     students = []
#     sql = "SELECT * FROM Students"
#     stmt = ibm_db.exec_immediate(conn, sql)
#     dictionary = ibm_db.fetch_both(stmt)
#     while dictionary != False:
#       students.append(dictionary)
#       dictionary = ibm_db.fetch_both(stmt)
#     if students:
#       return render_template("list.html", students = students, msg="Delete successfully")


  
  # # while student != False:
  # #   print ("The Name is : ",  student)







@app.route('/login',methods = ['POST', 'GET'])
def login():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['pwd']


    sql = "SELECT * FROM user WHERE email =? AND pwd=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,email)
    ibm_db.bind_param(stmt,2,password)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)


    if account:
      session['email']=email
      return render_template('dashboard.html',mail=session['email'])
    else:
      return render_template('login.html',msg="please try again, password email or password!!")




@app.route('/home',methods = ['POST', 'GET'])
def submit():
  if(request.method == "POST"):
        # get data
        lat = request.form["lat"]
        lon = request.form["lon"]
        vis = 0
        
        sql = "SELECT * FROM location WHERE lat =? AND lon=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,lat)
        ibm_db.bind_param(stmt,2,lon)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
          return render_template('dashboard.html', msg="Already Zone is marked as Containment zone")
        else:
          insert_sql = "INSERT INTO location(lat,lon,vis) VALUES (?,?,?)"
          prep_stmt = ibm_db.prepare(conn, insert_sql)
          ibm_db.bind_param(prep_stmt, 1, lat)
          ibm_db.bind_param(prep_stmt, 2, lon)
          ibm_db.bind_param(prep_stmt, 3, vis)

          ibm_db.execute(prep_stmt)
        
        return render_template('dashboard.html', msg=" Data saved successfuly..",mail=session['email'])

@app.route('/data')
def data():
  zones = []
  sql = "SELECT * FROM location"
  stmt = ibm_db.exec_immediate(conn, sql)
  dictionary = ibm_db.fetch_both(stmt)
  while dictionary != False:
    # print ("The Name is : ",  dictionary)
    zones.append(dictionary)
    dictionary = ibm_db.fetch_both(stmt)

  if zones:
    return render_template("data.html", zones = zones)

@app.route("/android_sign_up", methods=["POST"])
def upload():
    if(request.method == "POST"):

        # get the data from the form
        name = request.json['name']
        email = request.json['email']
        password = request.json['password']

        sql = "SELECT * FROM user WHERE email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
          return {'status': 'failure'}
        else:
          insert_sql = "INSERT INTO user VALUES (?,?,?)"
          prep_stmt = ibm_db.prepare(conn, insert_sql)
          ibm_db.bind_param(prep_stmt, 1, name)
          ibm_db.bind_param(prep_stmt, 2, email)
          ibm_db.bind_param(prep_stmt, 3, password)

          ibm_db.execute(prep_stmt)
          return {"id": "1"}
          # data = []
          # sql = "SELECT * FROM user WHERE email = ?' "
          # stmt = ibm_db.exec_immediate(conn, sql)
          # ibm_db.bind_param(stmt, 1, email)
          # ibm_db.execute(stmt)
          
          # dictionary = ibm_db.fetch_both(stmt)
          # while dictionary != False:
          #   # print ("The Name is : ",  dictionary)
          #   data.append(dictionary)
          #   dictionary = ibm_db.fetch_both(stmt)

          
                  
        # return {'status': 'failure'}

@app.route("/location_data")
def location_data():
  locationdata = []
  sql = "select * from location"
  stmt = ibm_db.exec_immediate(conn, sql)
  dictionary = ibm_db.fetch_both(stmt)
  while dictionary != False:
    #  print ("The Name is : ",  dictionary)
     locationdata.append(dictionary)
     dictionary = ibm_db.fetch_both(stmt)
  # # row_headers = [x[0] for x in conn.cursor().description]
  # json_data = []
  # for result in locationdata:
  #   json_data.append(dict(zip(result)))
  return json.dumps(locationdata)
  

@app.route("/post_user_location_data", methods=["POST"])
def post_user_location():
    if(request.method == "POST"):
      lat = request.json['lat']
      lon = request.json['long']
      id = request.json['id']
      ts = request.json['timestamp']

      insert_sql = "INSERT INTO USER_LOCATION VALUES (?,?,?,?)"
      prep_stmt = ibm_db.prepare(conn, insert_sql)
      ibm_db.bind_param(prep_stmt, 1, lat)
      ibm_db.bind_param(prep_stmt, 2, lon)
      ibm_db.bind_param(prep_stmt, 3, id)
      ibm_db.bind_param(prep_stmt, 4, ts)

      ibm_db.execute(prep_stmt)
      return {"response": "success"}

@app.route("/send_trigger",methods=["POST"])
def send_trigger():
    if(request.method == "POST"):
        # get the data from the form
        email = request.json['email']
        location_id = request.json['id']

        sql = "SELECT vis FROM Location WHERE SNO =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,location_id)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        
        if account:
          visited=account[0]
          visited=visited+1
          sql = "UPDATE LOCATION SET vis = ? WHERE SNO=?"
          stmt = ibm_db.prepare(conn, sql)
          ibm_db.bind_param(stmt,1,visited)
          ibm_db.bind_param(stmt,1,location_id)
          ibm_db.execute(stmt)

          send_mail(email)
          return {"response": "success"}
        else:
          return {"response": "failure"}

# @app.route("/send_trigger")
# def send_trigger():
#   msg=Message("Warning",sender="noreply@demo.com",recipients=['lakshmanakashnp@gmail.com'])
#   msg.body="YOu are in containment zone"
#   mail.send(msg)
#   return "sent email"

# @app.route("/send_trigger")
# def send_trigger():
#   # send_mail('lakshmanakashnp@gmail.com')
#   email="lakshmanakashnp@gmail.com"
#   print(email)
#   message = Mail(from_email='risingragul@gmail.com',
#                    to_emails=email,
#                    subject='caution',
#                    plain_text_content='Please Stay Safe',
#                    html_content='<h2>You are entering into a containment Zone</h2>')

#   try:
#     sg = SendGridAPIClient('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')
#     response = sg.send(message)
#     print(response.status.code)
#     print(response.body)
#     print(response.headers)
#   except Exception as e:
#         print(e)
#   return "success" 


if __name__ == '__main__':
    
    app.run(debug=True,host='0.0.0.0', port=5000)