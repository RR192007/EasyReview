import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class book(db.Model):
    __tablename__ = "books"
    isbn = db.Column(db.String, primary_key = True)
    title = db.Column(db.String, nullable = False)
    author = db.Column(db.String, nullable = False)
    year = db.Column(db.String, nullable = False)
    reviews = db.relationship("Review", backref="book", lazy=True)

    def __init__(self, isbn, title, author, year):
      isbn = self.isbn
      title = self.title
      author = self.author
      year = self.year

class member(db.Model):
    __tablename__ = "member"
    username = db.Column(db.String, primary_key = True)
    password = db.Column(db.String, nullable = False)
    name = db.Column(db.String, nullable = False)
    email = db.Column(db.String, nullable = False)
    review = db.relationship("Review", backref="member", lazy=True)


    def add_member(self, username, password, name, email):
      m = member(username = username, password = password, name = name, email = email)
      db.session.add(m)
      db.session.commit()

    def add_review(self, isbn, rating, review):
      r = member(isbn = isbn, member_username = self.username, rating = rating, review = review)
      db.session.add(r)
      db.session.commit()

class Review(db.Model):
    __tablename__ = "review"
    isbn = db.Column(db.String, db.ForeignKey("books.isbn"), primary_key=True)
    member_username = db.Column(db.String, db.ForeignKey("member.username"), nullable = False)
    rating = db.Column(db.Integer, nullable = False)
    review = db.Column(db.String, nullable = False)
