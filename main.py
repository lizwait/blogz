from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:catsarethebest@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "8675309"

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
    title = db.Column(db.String(120))
    body = db.Column(db.Text(300))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner_id):
        self.title = title
        self.body = body
        self.owner_id= owner_id

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
            return render_template('signup.html', username_error=username_error, password_error1=password_error1, password_error2=password_error2, userName=user)

        if username_error == '' and password_error1 == '' and password_error2 == '':
            existing_user = User.query.filter_by(username=user).first()
            if not existing_user:
                new_user = User(user, password)
                db.session.add(new_user)
                db.session.commit()
                session['user_id'] = new_user.id
                session['User']= user
                return redirect('/newpost')
            else:
                user_exists_error="Whoops! This username already exits. Please try again."
                return render_template('signup.html', user_exists_error=user_exists_error, userName=user)
    return render_template('signup.html')

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'post_login', 'index', 'blog_entries']
    if request.endpoint not in allowed_routes and 'User' not in session:
        return redirect('/login')

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def post_login():
    user = request.form['user-name']
    password = request.form['user-password1']
    verify_user = User.query.filter_by(username=user).first()

    if verify_user == None:
        verification_error= "Please enter a valid username and password combination."
        return render_template('login.html', verification_error=verification_error)
        

    username_error = ''
    if user == "": 
        username_error = "Please enter a valid username."

    password_error1 = ''
    if password == "":
        password_error1 = "Please enter valid password."

    if username_error != '' or password_error1 != '':
        return render_template('login.html', username_error=username_error, password_error1=password_error1)

    if check_pw_hash(password, verify_user.pw_hash) == True:
        session['User'] = user
        existing_user = User.query.filter_by(username=user).first()
        session['user_id'] = existing_user.id
        return redirect('/newpost')

    else:
        verification_error= "Please enter a valid username and password combination."
        return render_template('login.html', verification_error=verification_error, userName=user)
    
@app.route('/blog', methods=['GET'])
def blog_entries():
    blogs = Blog.query.all()
    id = request.args.get('id', '')
    user_id = request.args.get('user', '')

    if id == '' and user_id == '':
        return render_template('blog.html', blogs=blogs)

    if id != '':
        blog = Blog.query.get(id)
        return render_template('blog-page.html', blog=blog)

    if user_id != '':
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('blog.html', blogs=blogs)

@app.route("/", methods=["GET"])
def index():
    user_list = User.query.all()
    return render_template('index.html', user_list=user_list)

@app.route("/newpost", methods=["GET"])
def new_blog_entry1():    
    return render_template('newpost.html')

@app.route("/newpost", methods=['POST'])
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
        user_id = session['user_id']
        new_blog = Blog(title, body, user_id)
        db.session.add(new_blog)
        db.session.commit()
        return redirect('/blog?id=' + str(new_blog.id))

    return render_template('newpost.html', titleError=titleError, bodyError=bodyError, blogBody=body, title=title)

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect('/login')

if __name__=='__main__':
    app.run()