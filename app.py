from flask import Flask, render_template, request, g, redirect, url_for
import sqlite3 as sql
import flask_login
import collections
import logging
from logging.handlers import RotatingFileHandler
import time

app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
DATABASE = 'blog.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sql.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.before_request
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('db_schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.route('/')
def home():
   return "Hello world"

@app.route('/enternew')
def new_student():
   return render_template('student.html')

@app.route('/adduser',methods = ['POST', 'GET'])
@flask_login.login_required
def adduser():
   if request.method == 'POST':
      try:
         username = request.form['username']
         password = request.form['password']
         
         with sql.connect("blog.db") as con:
            cur = con.cursor()
            
            cur.execute("INSERT INTO login (username,password) VALUES (?,?)",(username, password) )
            
            con.commit()
            msg = "Record successfully added"
      except Exception, e:
         con.rollback()
         msg = str(e)
      
      finally:
         return render_template("result.html",msg = msg)
         con.close()


@app.route('/list')
@flask_login.login_required
def list():
   if flask_login.current_user.id == 'xxx':
      con = sql.connect("blog.db")
      con.row_factory = sql.Row
      
      cur = con.cursor()
      cur.execute("select * from login")
      
      rows = cur.fetchall();
      con.close()
      return render_template("list.html",rows = rows)
   else :
      return "Unauthorized"

class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    users=get_users()
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    users=get_users()
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['pw'] == users[email]['password']

    return user
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
      if flask_login.current_user.is_authenticated:
        return redirect(url_for('protected'))
    except Exception,e:
      app.logger.info(str(e))

    if request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'></input>
                <input type='password' name='pw' id='pw' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form>
               '''
    email = request.form['email']
    users = get_users()
    try:
      if request.form['pw'] == users[email]['password']:
          user = User()
          user.id = email
          flask_login.login_user(user)
          return redirect(url_for('protected'))
    except Exception,e:
      return "username not found"

    return 'Bad login'


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id
    
    
@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'
    
@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

def get_users():
   con = sql.connect("blog.db")
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * from login")
   
   rows = cur.fetchall();
   con.close()
   d=collections.defaultdict(dict)
   for row in rows:
      d[row[0]]['password']=row[1]

   return d

@app.route('/write_new')
@flask_login.login_required
def function():
   con = sql.connect("blog.db")
   con.row_factory = sql.Row
   cur = con.cursor()
   cur.execute("select * from category")
      
   categories = cur.fetchall();
   con.close()
   return render_template('write_new.html',categories=categories)

@app.route('/addarticle',methods = ['POST', 'GET'])
@flask_login.login_required
def addarticle():
   if request.method == 'POST':
      try:
         title = request.form['title']
         content = request.form['content']
         cat_id = request.form.get('select')
         
         with sql.connect("blog.db") as con:
            cur = con.cursor()
            
            cur.execute("INSERT INTO article (title,content,author,category_id,a_date) VALUES (?,?,?,?,?)",(title, content,flask_login.current_user.id,cat_id,time.strftime("%H:%M:%S")) )
            
            con.commit()
            msg = "Record successfully added"
      except Exception, e:
         con.rollback()
         msg = str(e)
      
      finally:
         return render_template("result.html",msg = msg)
         con.close()

@app.route('/new_category')
@flask_login.login_required
def new_category():
   return render_template('new_category.html')

@app.route('/addCategory',methods = ['POST', 'GET'])
@flask_login.login_required
def addCategory():
   if isAdmin():
      if request.method == 'POST':
         try:
            category = request.form['category']
            
            with sql.connect("blog.db") as con:
               cur = con.cursor()
               
               cur.execute("INSERT INTO category (category_name) VALUES (?)",(category,) )
               
               con.commit()
               msg = "Category successfully added"
         except Exception, e:
            con.rollback()
            msg = str(e)
         
         finally:
            return render_template("result.html",msg = msg)
            con.close()
   else:
      return "Golmal"




def isAdmin():
   return flask_login.current_user.id=='xxx'

if __name__ == '__main__':
   handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
   handler.setLevel(logging.INFO)
   app.logger.addHandler(handler)
   app.run(debug = True)
