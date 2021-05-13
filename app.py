from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from flask import Flask, request, jsonify, redirect, Response
import json
import uuid
import time

# Connect to our local MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Choose database
db = client['InfoSys']

# Choose collections
students = db['Students']
users = db['Users']

# Initiate Flask App
app = Flask(__name__)

users_sessions = {}

def create_session(username):
    user_uuid = str(uuid.uuid1())
    users_sessions[user_uuid] = (username, time.time())
    return user_uuid  

def is_session_valid(user_uuid):
    return user_uuid in users_sessions
 
# ΕΡΩΤΗΜΑ 1: Δημιουργία χρήστη
@app.route('/createUser', methods=['POST'])
def create_user():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "username" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    if users.find({"username":data["username"]}).count() == 0 :
        user = {"username": data['username'], "password": data['password']}
        users.insert_one(user)

        # Μήνυμα επιτυχίας
        return Response(data['username']+" was added to the MongoDB.\n",status = 200, mimetype='application/json') 
    
    # Διαφορετικά, αν υπάρχει ήδη κάποιος χρήστης με αυτό το username.
    else:
        return Response("A user with the given email already exists. \n",status = 400, mimetype='application/json') 
       
    

# ΕΡΩΤΗΜΑ 2: Login στο σύστημα
@app.route('/login', methods=['POST'])
def login():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "username" in data or not "password" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    user = users.find_one({"username":data['username']})
    if user == None : 
        return Response("no user with such name \n",status=500,mimetype='application/json')
    if user["password"] == data['password']:
        user_uuid = create_session(data['username'])
        res = {"uuid": user_uuid, "username": data['username']}
        return Response(json.dumps(res , indent=4) + "\n",status = 200, mimetype='application/json') 

    # Διαφορετικά, αν η αυθεντικοποίηση είναι ανεπιτυχής.
    else:
        # Μήνυμα λάθους (Λάθος username ή password)
        return Response("Wrong username or password.\n",status = 400 , mimetype='application/json') 

# ΕΡΩΤΗΜΑ 3: Επιστροφή φοιτητή βάσει email 
@app.route('/getStudent', methods=['GET'])
def get_student():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")
    
    uuid = request.headers.get('authorization')
    if is_session_valid(uuid) == False :
        return Response("the user is not authorized \n" , status=401 ,mimetype='application/json' )
    else : #αυθεντικοποιηση αληθης 
        student = students.find_one({"email":data['email']}) 
        if student == None :
            return Response ("no user with such name \n",status=500,mimetype='application/json')
        else :
            student['_id'] = None
            return Response(json.dumps(student , indent = 4), status=200, mimetype='application/json')
  
# ΕΡΩΤΗΜΑ 4: Επιστροφή όλων των φοιτητών που είναι 30 ετών
@app.route('/getStudents/thirties', methods=['GET'])
def get_students_thirty():
    
    
    uuid = request.headers.get('authorization')
    if is_session_valid(uuid) == False :
        return Response("the user is not authorized" , status=401 ,mimetype='application/json' )
    else : #αυθεντικοποιηση αληθης 
        studentsAge30 = students.find({"yearOfBirth":(1991)})
        out = []
        if studentsAge30 :
            for student in studentsAge30 :
                student['_id'] = None
                out.append(student)
            return Response(json.dumps(out , indent = 4) + "\n", status=200, mimetype='application/json')              
        else :
             return Response ("no student with age 30  \n",status=500,mimetype='application/json')


# ΕΡΩΤΗΜΑ 5: Επιστροφή όλων των φοιτητών που είναι τουλάχιστον 30 ετών
@app.route('/getStudents/oldies', methods=['GET'])
def get_students_above_thirty():
   
    uuid = request.headers.get('authorization')
    if is_session_valid(uuid) == False :
        return Response("the user is not authorized" , status=401 ,mimetype='application/json' )
    else : #αυθεντικοποιηση αληθης 
        studentsAgeAbove30 = students.find( {"yearOfBirth": { "$lt": 1991} })
        out = []
        for student in studentsAgeAbove30 :
                student['_id'] = None
                out.append(student)
        if out:
                return Response(json.dumps(out , indent = 4) + "\n", status=200, mimetype='application/json')
        else :
                return Response ("no student with age above 30  \n",status=500,mimetype='application/json')
   

# ΕΡΩΤΗΜΑ 6: Επιστροφή φοιτητή που έχει δηλώσει κατοικία βάσει email 
@app.route('/getStudentAddress', methods=['GET'])
def get_studentAddr():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")


    uuid = request.headers.get('authorization')
    if is_session_valid(uuid) == False :
        return Response("the user is not authorized" , status=401 ,mimetype='application/json' )
    else : #αυθεντικοποιηση αληθης 
        student = students.find_one({"email":data['email']})
        student['_id'] = None
        exist = 0
        for item in student :
            if item == "address" :
                exist = 1
                array  = student.get(item)
                for dicta in array :
                    for i in dicta :
                        if i == "street" :
                            street = dicta.get(i)
                    
                        if i == "postcode" :
                            postcode = dicta.get(i)

        if exist == 1 :        
            student = {'name': student["name"], 'street': street, 'postcode': postcode}
            return Response(json.dumps(student , indent=4), status=200, mimetype='application/json')         
        else :
            return Response("address or student not found.\n" , status=400 ,mimetype='application/json' )
       
    

# ΕΡΩΤΗΜΑ 7: Διαγραφή φοιτητή βάσει email 
@app.route('/deleteStudent', methods=['DELETE'])
def delete_student():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    uuid = request.headers.get('authorization')
    if is_session_valid(uuid) == False :
        return Response("the user is not authorized" , status=401 ,mimetype='application/json' )
    else : #αυθεντικοποιηση αληθης 
        
        student = students.find_one({'email':data["email"]})
        if student == None :
            msg = "no user with such email. \n"
            return Response(msg,status=500,mimetype='application/json')
        elif student != None :
            students.delete_one(student)
            msg = student["name"] + "was deleted.\n"
            return Response(msg, status=200, mimetype='application/json')
            
       
# ΕΡΩΤΗΜΑ 8: Εισαγωγή μαθημάτων σε φοιτητή βάσει email 
@app.route('/addCourses', methods=['PATCH'])
def add_courses():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data or not "courses" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

   

    uuid = request.headers.get('authorization')
    if is_session_valid(uuid) == False :
        return Response("the user is not authorized" , status=401 ,mimetype='application/json' )
    else : #αυθεντικοποιηση αληθης 
        student = students.find_one({'email':data["email"]})
        if student == None :
            msg = "no student with such email. \n"
            return Response(msg,status=500,mimetype='application/json')
        else :
            students.update_one({'email':data["email"]},{"$set": {'courses':data["courses"]}}) 
            msg = "courses added to " + student["name"] +".\n"
            return Response(msg, status=200, mimetype='application/json')

# ΕΡΩΤΗΜΑ 9: Επιστροφή περασμένων μαθημάτων φοιτητή βάσει email
@app.route('/getPassedCourses', methods=['GET'])
def get_courses():
    # Request JSON data
    data = None 
    try:
        data = json.loads(request.data)
    except Exception as e:
        return Response("bad json content",status=500,mimetype='application/json')
    if data == None:
        return Response("bad request",status=500,mimetype='application/json')
    if not "email" in data:
        return Response("Information incomplete",status=500,mimetype="application/json")

    
    uuid = request.headers.get('authorization')
    if is_session_valid(uuid) == False :
        return Response("the student is not authorized" , status=401 ,mimetype='application/json' )
    
    else : #αυθεντικοποιηση αληθης 
        
        student = students.find_one({'email':data["email"]})
        if student == None :
            msg = "no user with such email. \n"
            return Response(msg,status=500,mimetype='application/json')
        else :
            student['_id'] = None
            if not "courses" in student:
                return Response ("no courses")
            else :
                passedCourse = {}
                courseList = {"courses":student['courses']}
                for i in courseList.values():
                    for j in i:
                        for grade in j:
                            if j.get(grade) >= 5:
                                passedCourse[grade] = j.get(grade)    
                if len(passedCourse) != 0:
                    return Response(json.dumps(passedCourse , indent=4), status=200, mimetype='application/json')
                else :
                    return Response("Student"+student['name']+"has not passed any course." , status=200 , mimetype='application/json')
                   
                                        
                

# Εκτέλεση flask service σε debug mode, στην port 5000. 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)