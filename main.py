from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Welcome@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))
    

    def __init__(self, title, body):
        self.title = title
        self.body = body




@app.route('/blog')
def blog():
    
    id=request.args.get('id')
    blog = Blog.query.filter_by(id=id).all()
    return render_template('message_form.html', blog=blog)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    title_error=""
    body_error=""
    title=""
    body=""
    blogs_list=[]
    title_validation=""
    
    if request.method=='POST':
        title = request.form['title']
        body = request.form['body']
        
        if title=="":
            title_error= "title should not be an empty"
        
        if body=="":
            body_error="body should not be an empty"

        blogs_list=Blog.query.all()

        for blog in blogs_list:
            if title==blog.title:
                title_validation="title already existed" 
            if (not title_error and not body_error and not title_validation):
                newpost=Blog(title,body)
                db.session.add(newpost)
                db.session.commit()

                post_id = newpost.id
                post_id = str(post_id)

                return redirect('/blog?id='+post_id)
                   
    return render_template('submission_form.html', title=title, body=body, 
    title_error=title_error, body_error=body_error,title_validation=title_validation)


@app.route('/message', methods=['POST','GET'])
def message():
    if request.method== 'POST':
        title=request.form['title']
        body=request.form['body']


    return render_template('list_form.html')

@app.route('/', methods=['POST', 'GET'])
def index():
    blogs = Blog.query.all()
    
    return render_template('list_form.html', blogs=blogs)


if __name__ == '__main__':
    app.run()




