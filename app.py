import mariadb
from flask import Flask, request, Response
import json
import dbcreds
from flask_cors import CORS
from uuid import uuid4

app = Flask(__name__)
CORS(app)

@app.route('/api/users', methods = ["POST", "PATCH", "DELETE"])
def userActions():
    if request.method == "POST":
        conn = None
        cursor = None
        email = request.json.get("email")
        username = request.json.get("username")
        password = request.json.get("password")
        birthdate = request.json.get("birthdate")
        rows = None
        session_rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users(email, username, password, birthdate) VALUES(?, ?, ?, ?)", [email, username, password, birthdate])
            conn.commit()
            rows = cursor.rowcount
            cursor.execute("SELECT id FROM users WHERE username=? AND password=?", [username, password])
            userId = cursor.fetchall()[0][0]
            loginToken = uuid4().hex
            cursor.execute("INSERT INTO user_session(userId, loginToken) VALUES(?, ?)", [userId, loginToken])
            conn.commit()
            session_rows = cursor.rowcount
        except Exception as error:
            print("SOMETHING WENT WRONG (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if rows == 1 and session_rows == 1:
                userData = {
                    "userId": userId,
                    "email": email,
                    "username": username,
                    "birthdate": birthdate,
                    "loginToken": loginToken
                }
                return Response(json.dumps(userData, default=str), mimetype="application/json", status=200)
            else:
                return Response("There was an error signing up.", mimetype="text/html", status=500)
    elif request.method == "PATCH":
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        email = request.json.get("email")
        username = request.json.get("username")
        password = request.json.get("password")
        birthdate = request.json.get("birthdate")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken=?", [loginToken])
            userId = cursor.fetchall()[0][0]
            print(userId)
            if email != "" and email != None:
                cursor.execute("UPDATE users SET email=? WHERE id=?", [email, userId])
            if username != "" and username != None:
                cursor.execute("UPDATE users SET username=? WHERE id=?", [username, userId])
            if password != "" and password != None:
                cursor.execute("UPDATE users SET password=? WHERE id=?", [password, userId])
            if birthdate != "" and birthdate != None:
                cursor.execute("UPDATE users SET birthdate=? WHERE id=?", [birthdate, userId])
            conn.commit()
            rows = cursor.rowcount
            cursor.execute("SELECT * FROM users WHERE id=?", [userId])
            user = cursor.fetchone()
        except Exception as error:
            print("Something went wrong (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if rows == 1:
                userData = {
                    "userId": userId,
                    "email": user[0],
                    "username": user[1],
                    "birthdate": user[3]
                }
                return Response(json.dumps(userData, default=str), mimetype="application/json", status=200)
            else:
                return Response("An error occurred updating.", mimetype="text/html", status=500)
    elif request.method == "DELETE":
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        password = request.json.get("password")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken=?", [loginToken])
            userId = cursor.fetchall()[0][0]
            cursor.execute("DELETE FROM users WHERE password=? AND id=?", [password, userId])
            conn.commit()
            rows = cursor.rowcount
        except Exception as error:
            print("Something went wrong (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if rows == 1:
                return Response("Profile deleted.", mimetype="text/html", status=204)
            else:
                return Response("An error occurred while deleting.", mimetype="text/html", status=500)

@app.route('/api/login', methods = ["POST", "DELETE"])
def login():
    if request.method == "POST":
        conn = None
        cursor = None
        email = request.json.get("email")
        password = request.json.get("password")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email=? AND password=?", [email, password])
            userId = cursor.fetchall()[0][0]
            loginToken = uuid4().hex
            if userId != None:
                cursor.execute("INSERT INTO user_session(userId, loginToken) VALUES (?, ?)", [userId, loginToken])
                conn.commit()
                rows = cursor.rowcount
                cursor.execute("SELECT email, username, birthdate FROM users WHERE email=? AND password=?", [email, password])
                user = cursor.fetchone()
            else:
                print("User does not exist. Incorrect login info.")
        except Exception as error:
            print("Something went wrong (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if rows == 1:
                userData = {
                    "userId": userId,
                    "email": user[0],
                    "username": user[1],
                    "birthdate": user[2],
                    "loginToken": loginToken
                }
                return Response(json.dumps(userData, default=str), mimetype="text/html", status=200)
            else:
                return Response("Login failed.", mimetype="text/html", status=500)
    elif request.method == "DELETE":
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_session WHERE loginToken=?", [loginToken])
            conn.commit()
            rows = cursor.rowcount
        except Exception as error:
            print("Something went wrong (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if rows == 1:
                return Response("Logged out successfully.", mimetype="text/html", status=204)
            else:
                return Response("Logout failed.", mimetype="text/html", status=500)

@app.route('/api/questions', methods = ["GET", "POST", "PATCH", "DELETE"])
def questions():
    if request.method == "GET":
        conn = None
        cursor = None
        questionId = request.args.get("questionId")
        questions = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            if questionId == None:
                cursor.execute("SELECT questions.*, users.username FROM questions INNER JOIN users ON users.id = questions.userId")
                questions = cursor.fetchall()
            else:
                cursor.execute("SELECT questions.*, users.username FROM questions INNER JOIN users ON users.id = questions.userId WHERE questions.id=?", [questionId])
                questions = cursor.fetchall()
        except Exception as error:
            print("SOMETHING WENT WRONG (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if questions != None:
                userData = []
                for question in questions:
                    userData.append({
                        "questionId": question[4],
                        "userId": question[0],
                        "username": question[5],
                        "title": question[1],
                        "content": question[2],
                        "createdAt": question[3]
                    })
                return Response(json.dumps(userData, default=str), mimetype="application/json", status=200)
            else:
                return Response("An error occurred.", mimetype="text/html", status=500)
    elif request.method == "POST":
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        title = request.json.get("title")
        content = request.json.get("content")
        rows = None
        question = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken=?", [loginToken])
            userId = cursor.fetchall()[0][0]
            cursor.execute("INSERT INTO questions(userId, title, content) VALUES(?, ?, ?)", [userId, title, content])
            conn.commit()
            questionId = cursor.lastrowid
            rows = cursor.rowcount
            cursor.execute("SELECT questions.*, users.username FROM questions INNER JOIN users ON users.id = questions.userId WHERE questions.id=?", [questionId])
            question = cursor.fetchall()
        except Exception as error:
            print("SOMETHING WENT WRONG (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if rows == 1:
                userData = {
                    "questionId": questionId,
                    "userId": userId,
                    "username": question[0][5],
                    "title": question[0][1],
                    "content": question[0][2],
                    "createdAt": question[0][3]
                }
                return Response(json.dumps(userData, default=str), mimetype="application/json", status=201)
            else:
                return Response("An error occurred.", mimetype="text/html", status=500)
    elif request.method == "PATCH":
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        questionId = request.json.get("questionId")
        title = request.json.get("title")
        content = request.json.get("content")
        rows = None
        edit = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken=?", [loginToken])
            userId = cursor.fetchall()[0][0]
            cursor.execute("SELECT userId FROM questions WHERE id=?", [questionId])
            qOwner = cursor.fetchall()[0][0]
            if userId == qOwner:
                if title != "" and title != None:
                    cursor.execute("UPDATE questions SET title=? WHERE id=?", [title, questionId])
                if content != "" and content != None:
                    cursor.execute("UPDATE questions SET content=? WHERE id=?", [content, questionId])
                conn.commit()
                rows = cursor.rowcount
                cursor.execute("SELECT * FROM questions WHERE id=?", [questionId])
                edit = cursor.fetchone()
            else:
                print("You didn't ask this question.")
        except Exception as error:
            print("SOMETHING WENT WRONG (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if rows == 1:
                userData = {
                    "questionId": questionId,
                    "title": edit[1],
                    "content": edit[2]
                }
                return Response(json.dumps(userData, default=str), mimetype="application/json", status=201)
            else:
                return Response("An error occurred.", mimetype="text/html", status=500)
    elif request.method == "DELETE":
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        questionId = request.json.get("questionId")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken=?", [loginToken])
            userId = cursor.fetchall()[0][0]
            cursor.execute("SELECT userId FROM questions WHERE id=?", [questionId])
            qOwner = cursor.fetchall()[0][0]
            if userId == qOwner:
                cursor.execute("DELETE FROM questions WHERE id=?", [questionId])
                conn.commit()
                rows = cursor.rowcount
            else:
                print("You didn't ask this question.")
        except Exception as error:
            print("SOMETHING WENT WRONG (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if rows == 1:
                return Response("Question deleted.", mimetype="text/html", status=204)
            else:
                return Response("An error occured.", mimetype="text/html", status=500)

@app.route('/api/answers', methods = ["GET", "POST", "PATCH", "DELETE"])
def answers():
    if request.method == "GET":
        conn = None
        cursor = None
        questionId = request.args.get("questionId")
        answers = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT answers.*, users.username, COUNT(likes.answerId) AS likeCount FROM answers INNER JOIN users ON users.id = answers.userId INNER JOIN likes ON likes.answerId = answers.id WHERE answers.questionId = ? GROUP BY users.username", [questionId])
            answers = cursor.fetchall()
        except Exception as error:
            print("SOMETHING WENT WRONG (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if answers != None:
                userData = []
                for answer in answers:
                    userData.append({
                        "questionId": answer[1],
                        "answerId": answer[3],
                        "userId": answer[0],
                        "username": answer[5],
                        "content": answer[2],
                        "createdAt": answer[4],
                        "amount": answer[6]
                    })
                return Response(json.dumps(userData, default=str), mimetype="application/json", status=200)
            else:
                return Response("An error occurred.", mimetype="text/html", status=500)
    elif request.method == "POST":
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        questionId = request.json.get("questionId")
        content = request.json.get("content")
        rows = None
        answerId = None
        answer = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken=?", [loginToken])
            userId = cursor.fetchall()[0][0]
            cursor.execute("INSERT INTO answers(userId, questionId, content) VALUES(?, ?, ?)", [userId, questionId, content])
            conn.commit()
            rows = cursor.rowcount
            answerId = cursor.lastrowid
            cursor.execute("SELECT answers.*, users.username FROM answers INNER JOIN users ON users.id = answers.userId WHERE answers.id=?", [answerId])
            answer = cursor.fetchall()
        except Exception as error:
            print("SOMETHING WENT WRONG (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if rows == 1:
                userData = {
                    "questionId": answer[0][1],
                    "answerId": answer[0][3],
                    "userId": answer[0][0],
                    "username": answer[0][5],
                    "content": answer[0][2],
                    "createdAt": answer[0][4]
                }
                return Response(json.dumps(userData, default=str), mimetype="application/json", status=201)
            else:
                return Response("An error occurred.", mimetype="text/html", status=500)
    elif request.method == "PATCH":
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        answerId = request.json.get("answerId")
        content = request.json.get("content")
        answer = None
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken=?", [loginToken])
            userId = cursor.fetchall()[0][0]
            cursor.execute("SELECT userId FROM answers WHERE id=?", [answerId])
            aOwner = cursor.fetchall()[0][0]
            if userId == aOwner:
                cursor.execute("UPDATE answers SET content=? WHERE id=?", [content, answerId])
                conn.commit()
                rows = cursor.rowcount
            else:
                print("You do not own this answer.")
            if rows == 1:
                cursor.execute("SELECT answers.*, users.username FROM answers INNER JOIN users ON users.id = answers.userId WHERE answers.id=?", [answerId])
                answer = cursor.fetchall()
        except Exception as error:
            print("SOMETHING WENT WRONG (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if rows == 1:
                userData = {
                    "questionId": answer[0][1],
                    "answerId": answer[0][4],
                    "userId": answer[0][0],
                    "username": answer[0][5],
                    "content": answer[0][2],
                    "createdAt": answer[0][3]
                }
                return Response(json.dumps(userData, default=str), mimetype="application/json", status=201)
            else:
                return Response("An error occurred.", mimetype="text/html", status=500)
    elif request.method == "DELETE":
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        answerId = request.json.get("answerId")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken=?", [loginToken])
            userId = cursor.fetchall()[0][0]
            cursor.execute("SELECT userId FROM answers WHERE id=?", [answerId])
            aOwner = cursor.fetchall()[0][0]
            if aOwner == userId:
                cursor.execute("DELETE FROM answers WHERE id=?", [answerId])
                conn.commit()
                rows = cursor.rowcount
            else:
                print("You can't delete that answer.")
        except Exception as error:
            print("SOMETHING WENT WRONG (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if rows == 1:
                return Response("Answer deleted.", mimetype="text/html", status=204)
            else:
                return Response("An error occurred.", mimetype="text/html", status=500)

@app.route('/api/likes', methods = ["GET", "POST", "DELETE"])
def likes():
    if request.method == "GET":
        conn = None
        cursor = None
        answerId = request.args.get("answerId")
        likes = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT likes.*, users.username FROM likes INNER JOIN users ON users.id = likes.userId WHERE likes.answerId=?", [answerId])
            likes = cursor.fetchall()
        except Exception as error:
            print("SOMETHING WENT WRONG (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if likes != None:
                userData = []
                for like in likes:
                    userData.append({
                        "answerId": like[0],
                        "userId": like[1],
                        "username": like[3]
                    })
                return Response(json.dumps(userData, default=str), mimetype="application/json", status=201)
            else:
                return Response("An error occurred.", mimetype="text/html", status=500)
    elif request.method == "POST":
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        answerId = request.json.get("answerId")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken=?", [loginToken])
            userId = cursor.fetchall()[0][0]
            cursor.execute("INSERT INTO likes(answerId, userId) VALUES(?, ?)", [answerId, userId])
            conn.commit()
            rows = cursor.rowcount
        except Exception as error:
            print("SOMETHING WENT WRONG (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if rows == 1:
                return Response("Answer liked.", mimetype="text/html", status=201)
            else:
                return Response("An error occurred.", mimetype="text/html", status=500)
    elif request.method == "DELETE":
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        answerId = request.json.get("answerId")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken=?", [loginToken])
            userId = cursor.fetchall()[0][0]
            cursor.execute("DELETE FROM likes WHERE userId=? AND answerId=?", [userId, answerId])
            conn.commit()
            rows = cursor.rowcount
        except Exception as error:
            print("SOMETHING WENT WRONG (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if rows == 1:
                return Response("Like removed.", mimetype="text/html", status=204)
            else:
                return Response("An error occured.", mimetype="text/html", status=500)

@app.route('/api/bookmarks', methods = ["GET", "POST", "DELETE"])
def bookmarks():
    if request.method == "GET":
        conn = None
        cursor = None
        loginToken = request.args.get("loginToken")
        bookmarks = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken=?", [loginToken])
            userId = cursor.fetchall()[0][0]
            cursor.execute("SELECT questions.* FROM questions INNER JOIN bookmarks ON questions.id = bookmarks.questionId WHERE bookmarks.userId=?", [userId])
            bookmarks = cursor.fetchall()
        except Exception as error:
            print("SOMETHING WENT WRONG (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if bookmarks != None:
                userData = []
                for bookmark in bookmarks:
                    userData.append({
                        "title": bookmark[1],
                        "content": bookmark[2],
                        "createdAt": bookmark[3],
                        "questionId": bookmark[4]
                    })
                return Response(json.dumps(userData, default=str), mimetype="application/json", status=200)
            else:
                return Response("An error occurred.", mimetype="text/html", status=500)
    elif request.method == "POST":
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        questionId = request.json.get("questionId")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken=?", [loginToken])
            userId = cursor.fetchall()[0][0]
            cursor.execute("INSERT INTO bookmarks(userId, questionId) VALUES(?, ?)", [userId, questionId])
            conn.commit()
            rows = cursor.rowcount
            bookmarkId = cursor.lastrowid
        except Exception as error:
            print("SOMETHING WENT WRONG (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if rows == 1:
                userData = {
                    "questionId": questionId,
                    "userId": userId,
                    "bookmarkId": bookmarkId
                }
                return Response(json.dumps(userData, default=str), mimetype="application/json", status=201)
            else: 
                return Response("An error occured.", mimetype="text/html", status=500)
    elif request.method == "DELETE":
        conn = None
        cursor = None
        loginToken = request.json.get("loginToken")
        questionId = request.json.get("questionId")
        rows = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken=?", [loginToken])
            userId = cursor.fetchall()[0][0]
            cursor.execute("DELETE FROM bookmarks WHERE questionId=? AND userId=?", [questionId, userId])
            conn.commit()
            rows = cursor.rowcount
        except Exception as error:
            print("SOMETHING WENT WRONG (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if rows == 1:
                return Response("Bookmark removed.", mimetype="text/html", status=204)
            else:
                return Response("An error occurred.", mimetype="text/html", status=500)