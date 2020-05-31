import os

from flask import Flask, session, render_template,  request, jsonify, send_from_directory
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from Convert import convertTuple
from models import *
import requests
from sqlalchemy import exc



app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Show the welcome page
@app.route("/")
def welcome():
    return render_template("Welcome.html")

# Show the login page
@app.route("/login")
def loginpage():
    return render_template("login.html")

# Process Login
@app.route("/processinglogin", methods=["POST"])
def login():

    username = request.form.get("txtusername")
    retrievedpasswordfromsqltuple = db.execute(f"SELECT password FROM member WHERE username = '{username}'").fetchone()
    enteredpassword = request.form.get("txtpassword")
    retrievedpasswordfromsql = convertTuple(retrievedpasswordfromsqltuple)
    retrievednamefromsqltuple = db.execute(f"SELECT name FROM member WHERE username = '{username}'").fetchone()
    retrievednamefromsql = convertTuple(retrievednamefromsqltuple)
    reviews = db.execute(f"SELECT * FROM review WHERE member_username ='{username}'")

    if retrievedpasswordfromsql == enteredpassword:
        db.commit()
        return render_template("account.html", retrievednamefromsql = retrievednamefromsql, reviews=reviews)
    else:
        db.commit()
        return render_template("error.html")

# Show the register page
@app.route("/register")
def registerpage():
    return render_template("register.html")

# Process registration
@app.route("/processingregistration", methods=["POST"])
def register():
    try:
        name = request.form.get("txtname")
        email = request.form.get("txtemail")
        username = request.form.get("txtusername")
        password = request.form.get("txtpassword")
        db.execute("INSERT INTO member(username, password, name, email) VALUES(:username, :password, :name, :email)",{"username": username, "password":password, "name":name, "email": email})
        db.commit()
        return render_template("successfile.html", name=name)
    except exc.IntegrityError:
        return render_template("registererror.html")
#Process search and show all books
@app.route("/search", methods=["POST"])
def search():
  keyword = request.form.get("txtsearch")
  books = db.execute(f"SELECT * FROM books WHERE isbn LIKE '%{keyword}%' OR title LIKE '%{keyword}%' OR author LIKE '%{keyword}%'")
  return render_template("searchresults.html", books = books)
@app.route("/search/<book_isbn>")
#Show book information
def singlebookinfo(book_isbn):
  isbn = book_isbn
  authortuple = db.execute(f"SELECT author FROM books WHERE isbn ='{book_isbn}'").fetchone()
  titletuple = db.execute(f"SELECT title FROM books WHERE isbn ='{book_isbn}'").fetchone()
  yeartuple = db.execute(f"SELECT year FROM books WHERE isbn ='{book_isbn}'").fetchone()
  author = convertTuple(authortuple)
  title = convertTuple(titletuple)
  year = convertTuple(yeartuple)

    # Getting all reviews.
  reviews = db.execute(f"SELECT * FROM review WHERE isbn ='{book_isbn}'")
  response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "3jxGpzGVi1ue84j2f7x5g", "isbns": f"{isbn}"})
  data = response.json()
  workratingscount = data["books"][0]['work_ratings_count']
  averagescore = data["books"][0]['average_rating']
  return render_template("book.html", isbn = isbn, author=author, title=title, year=year, workratingscount = workratingscount, averagescore = averagescore, reviews=reviews)

@app.route("/search/book/review", methods=["POST"])
#Allow users to review book
def insertreview():
  try:
      member_username = request.form.get("txtusername")
      corpasstuple = db.execute(f"SELECT password FROM member WHERE username = '{member_username}'").fetchone()
      corpass = convertTuple(corpasstuple)
      password = request.form.get("txtpassword")
      isbn = request.form.get("txtisbn")
      rating = int(request.form.get("txtrating"))
      review = request.form.get("txtreview")
      if corpass == password and rating < 6:
          db.execute("INSERT INTO review(isbn, member_username, rating, review) VALUES(:isbn, :member_username, :rating, :review)",{"isbn": isbn, "member_username":member_username, "rating":rating, "review":review})
          db.commit()
          return render_template("reviewsuccess.html")
      else:
          return render_template("processingerror.html", message="Review cannot be inserted! Please recheck password or recheck if rating is 5 or below.")
  except exc.IntegrityError:
      return render_template("processingerror.html", message="You cannot review a book twice.")

@app.route("/signingout")
#logout
def logout():
  return render_template("welcome.html")

@app.route("/api/<isbn>")
def book_api(isbn):
    try:
        """Return details about a single book."""
        books = db.execute(f"SELECT * FROM books WHERE isbn = '{isbn}'")
        for book in books:
          title = book.title
          author=book.author
          year = book.year
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "3jxGpzGVi1ue84j2f7x5g", "isbns": f"{isbn}"})
        data = res.json()
        averagescore = data["books"][0]['average_rating']
        reviewcount = data["books"][0]['reviews_count']
        return jsonify({
                "title": title,
                "author": author,
                "year": year,
                "isbn": isbn,
                "review_count": reviewcount,
                "average_score": averagescore
            })
    except UnboundLocalError:
        return jsonify({"error": "Book not found"}), 404
    except ValueError:
        return jsonify({"error": "Book not found"}), 404
