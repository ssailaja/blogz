from flask import Flask, request, redirect, session, render_template, flash
import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'y337kGcys&zP3B'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blog123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/')
def index():        
    users = User.query.all()
    return render_template("index.html", users=users)

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog')
def allposts():
    if request.args.get('id'):
        owner_id = request.args.get('id')
        person = User.query.filter_by(id=owner_id).first()
        blogs = Blog.query.filter_by(owner=person).all()
    else:
        blogs=Blog.query.all()

    return render_template('list_form.html', blogs = blogs)


@app.route('/singleUser')
def blog():
    if request.args.get('blog_id'):
        blog_id = request.args.get('blog_id')
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template("singleUser.html", blog = blog)
    
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if('username' not in session):
        return redirect("/login")

    title = ""
    body = ""

    if request.method=='POST':
        title = request.form['title']
        body = request.form['body']
        errorExists = False

        if title == "":
            flash("Title should not be an empty", "error")
            errorExists = True
        
        if body == "":
            flash("Body should not be an empty", "error")
            errorExists = True
        
        if not errorExists:
            owner = User.query.filter_by(username=session['username']).first()
            blog = Blog(title, body, owner)
            db.session.add(blog)
            db.session.commit()
            return render_template("singleUser.html", blog = blog)
        
    return render_template('new_post.html', title=title, body=body)

@app.route('/login',methods=['POST', 'GET'])
def login():
    if(request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('Username or password is incorrect, or user does not exist', 'error')

    return render_template('login.html')
    
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify_password']
        errorExists = False

        if(username == ""):
            flash("Username should not be an empty!", "error")
            errorExists = True
        
        if(password == ""):
            flash("Password should not be an empty!", "error")
            errorExists = True

        if(verify_password == ""):
            flash("Verify Password should not be an empty!", "error")
            errorExists = True
        
        if(password and password != verify_password):
            flash("Passwords do not match", "error")
            errorExists = True
        
        if(len(username) < 3 or len(password) < 3):
            flash("Either username or password is invalid", "error")
            errorExists = True
        
        if not errorExists:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                flash("signup")
                return redirect('/newpost')
            else:
                flash("Username already exists", "error")
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


if __name__ == '__main__':
    app.run()