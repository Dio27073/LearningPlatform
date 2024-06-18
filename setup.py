import pymysql

conn = pymysql.connect(host="localhost",user="Derek",password="incorrect")

cur = conn.cursor()

cur.execute("CREATE DATABASE IF NOT EXISTS testlet;")
cur.execute("USE testlet")
print('Opened database successfully')

cur.execute("CREATE TABLE courses(courseID INTEGER PRIMARY KEY, courseTitle VARCHAR(20), instructorID INTEGER, FOREIGN KEY (instructorID) REFERENCES users(id));")
cur.execute("CREATE TABLE users(userID INTEGER PRIMARY KEY, email VARCHAR(20), firstName VARCHAR(10), lastName VARCHAR(10), role VARCHAR(10));")
cur.execute("CREATE TABLE flashcardSet(setID INTEGER PRIMARY KEY, title VARCHAR(20), description VARCHAR(50), creatorID INTEGER, FOREIGN KEY (creatorID) REFERENCES users(userID));")
cur.execute("CREATE TABLE flashcard(cardID INTEGER PRIMARY KEY, setID INTEGER, question VARCHAR(30), answer VARCHAR(30), FOREIGN KEY setID REFERENCES flashcardSet(setID));")
cur.execute("CREATE TABLE quizzes(quizID INTEGER PRIMARY KEY, title VARCHAR(10), questionFormat VARCHAR (10), creatorID INTEGER, length INTEGER, setID INTEGER, FOREIGN KEY (creatorID) REFERENCES users(userID), FOREIGN KEY (setID) REFERENCES flashcardSet(setID));")
print('Table created')

cur.execute("CREATE ROLE instructor;")
cur.execute("CREATE ROLE student;")

cur.execute("GRANT INSERT ON * TO instructor;")
cur.execute("GRANT SELECT ON * TO instructor;")
cur.execute("GRANT SELECT ON flashcardSet TO student;")

conn.close()
