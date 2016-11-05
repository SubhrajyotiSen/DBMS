from flask import Flask, render_template, request, g, redirect, url_for
import sqlite3 as sql
import flask_login
import collections

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
   con = sql.connect("blog.db")
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * from login")
   
   rows = cur.fetchall();
   con.close()
   return render_template("list.html",rows = rows)

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
    if request.form['pw'] == users[email]['password']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return redirect(url_for('protected'))

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


if __name__ == '__main__':
   app.run(debug = True)
