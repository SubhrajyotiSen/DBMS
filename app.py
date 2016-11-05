from flask import Flask, render_template, request, g
import sqlite3 as sql

app = Flask(__name__)

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

if __name__ == '__main__':
   app.run(debug = True)
