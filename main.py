from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:catsarethebest@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref="owner")
    
    def __init__(self, user, password):
        self.username = user
        self.pw_hash = make_pw_hash(password)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.Text(120))
    body = db.Column(db.Text(300))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/signup', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        user = request.form['user-name']
        password = request.form['user-password1']
        verify = request.form['user-password2']

        username_error = ''
        if user == "" or len(user) < 3 or len(user) > 20 or (' ' in user): 
            username_error = "Please enter a valid username."

        password_error1 = ''
        if password != verify:
            password_error1 = "Please enter matching passwords."

        password_error2 = ''
        if password == "" or len(password) < 3 or len(password) >20 or (' ' in password):
            password_error2 = "Please enter valid password."

        if username_error != '' or password_error1 != '' or password_error2 != '':
            return render_template('signup.html', username_error=username_error, password_error1=password_error1, password_error2=password_error2)

        if username_error == '' and password_error1 == '' and password_error2 == '':
            existing_user = User.query.filter_by(username=user).first()
            if not existing_user:
                new_user = User(user, password)
                db.session.add(new_user)
                db.session.commit()
                # TODO - "remember" the user
                return render_template('newpost.html')

    return render_template('signup.html')

@app.route('/login', methods='GET')
def login():
    return render_template('login.html')

@app.route('/login', methods='POST')
def post_login():
    user = request.form['user-name']
    password = request.form['user-password1']
    verify_user = User.query.filter_by(username=user).first()
    if check_pw_hash(password, verify_user.pw_hash) == True:
        return render_template('newpost.html')

    else:
        return render_template('login.html')
    

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