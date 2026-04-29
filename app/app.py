from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'petvida-secret')

def get_db():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'mysql-service'),
        user=os.environ.get('DB_USER', 'petvida'),
        password=os.environ.get('DB_PASSWORD', 'petvida123'),
        database=os.environ.get('DB_NAME', 'petvida_db')
    )

