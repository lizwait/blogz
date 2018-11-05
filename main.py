from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:catsarecool@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.Text(120))
    body = db.Column(db.Text(300))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['GET'])
def blog_entries():
    blogs = Blog.query.all()
    id = request.args.get('id', '')
    if id == '':
        return render_template('blog.html', blogs=blogs)

    blog = Blog.query.get(id)
    return render_template('blog-page.html', blog=blog)

@app.route("/newpost")
def new_blog_entry1():    
    return render_template('newpost.html')

@app.route("/newpost", methods = ['POST'])
def new_blog_entry2():

    titleError = ''
    title = request.form['title']
    if title == "": 
        titleError = "Please enter a blog title."
    
    bodyError = ''
    body = request.form['body']
    if body == "":
        bodyError = "Please enter a blog body."

    if titleError == '' and bodyError == '':
        new_blog = Blog(title, body)
        db.session.add(new_blog)
        db.session.commit()
        return redirect('/blog?id=' + str(new_blog.id))

    return render_template('newpost.html', titleError=titleError, bodyError=bodyError)


app.run()