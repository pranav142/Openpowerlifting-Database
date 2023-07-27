from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

app.config["MYSQL_USER"] = os.getenv("MY_SQL_USER")
app.config["MYSQL_PASSWORD"] = os.getenv("MY_SQL_PASSWORD")
app.config["MYSQL_DB"] = "openpowerlifting"
app.config["MYSQL_HOST"] = os.getenv("MY_SQL_HOST")

mysql = MySQL(app)


@app.route("/api/")
def get_all_record():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM competitors")
    data = cur.fetchall()
    cur.close()
    return jsonify(data)
