import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv
from flask import request

engine = create_engine(os.getenv("DATABASE_URL")) # database engine object from SQLAlchemy that manages connections to the database
                                                # DATABASE_URL is an environment variable that indicates where the database lives
db = scoped_session(sessionmaker(bind=engine))    # create a 'scoped session' that ensures different users' interactions with the

def register():
    username = request.form.get("txtname")
    email = request.form.get("txtemail")
    username = request.form.get("txtusername")
    password = request.form.get("txtpassword")
    db.execute("INSERT INTO member_info (username, password, email, name) VALUES (:password, :username, :email, :name)",
                {"username": username, "password": password, "email": email, "name": name})                                                 # database are kept separate

db.commit() # transactions are assumed, so close the transaction finished
