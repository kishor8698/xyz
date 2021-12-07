from enum import unique
from os import stat_result
from flask import Flask, render_template, redirect, request, session,make_response, flash,jsonify
from flask.helpers import safe_join
#from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, current
from sqlalchemy.orm import backref
from sqlalchemy.sql.schema import ForeignKey
from datetime import datetime
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_user, UserMixin, logout_user,current_user
# from flask_json import FlaskJSON, JsonError, json_response, as_json
# from flask_bcrypt import Bcrypt
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employee.sqlite3'
app.config["SESSION_PERMANENT"] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "thisisddsecret"
#Session(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
# json = FlaskJSON(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', lazy='dynamic',back_populates='author')
    #posts=db.relationship('Post',backref='owner')
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
class Post(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User')

    def __repr__(self):
        return '<Post {}>'.format(self.body)
    
class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    
admin=Admin(app)  
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Post, db.session))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

'''
db.drop_all()
db.create_all()

# Susan will be both created and added to the session
u1 = User(username='susan', email='susan@example.com')
db.session.add(u1)

# John will be created, but not added
u2 = User(username='john', email='john@example.com')

# Create a post by Susan
p1 = Post(body='this is my post!', author=u1)

# Add susan's post to the session
db.session.add(p1)

# Create a post by john, since john does not yet exist as a user, he is created automatically
p2 = Post(body='this is my post!', author=u2)

# Add john's post to the session
db.session.add(p2)

# After the session has everything defined, commit it to the database
db.session.commit()
'''
  
# result = emp.query.filter_by(name='kishor').first()
# db.session.delete(result)
# db.session.commit()
# result=emp(name='kishor',city='parola',address='maharashtra')
# db.session.add(result)
# db.session.commit()

@app.route('/jquery_demo',methods=['POST','GET'])
def show1():
    return render_template("jquery_validate.html")

@app.route("/")
def index():
    result=Post.query.all()
    return render_template('index.html',result=result)

@app.route("/user_reg", methods=["POST", "GET"])
def user_reg():
    if request.method=='POST':
        username=request.form['username']
        email=request.form['email']
        password=request.form['password']
        con_password=request.form['con_password']
        encrypt_password=sha256_crypt.encrypt(password)
        #content=request.form['content']
        resp={}
        if password == con_password:
            try:
                u_data=User(username=username,email=email,password_hash=encrypt_password)
                db.session.add(u_data)
                db.session.commit()
                flash("Registration Completed Successfully","info")
                resp['username'] = username
                resp['email'] = email
                resp['password'] = encrypt_password
                resp['status'] = 'True'
                resp['messages'] = 'Registerd successfully!'
                return jsonify(resp)  
            except:
                resp['status'] = 'False'
                resp['messages'] = 'Username or Mail Already Exist...'
                return jsonify(resp)  
        else:
            flash("Can't Match Your Password and Conform Password",'danger')
            return redirect("/user_reg")
    database_data=User.query.all()
    return render_template("user_register.html",database_data=database_data)

@app.route("/live_data",methods=["GET", "POST"])
def search_fun():
    dict_resp={}
    list_resp=[]
    if request.method == 'POST':
        search_username=request.form['term']
        if search_username !="":
            # result=User.query.filter(User.username == search_username ).first()
            result = User.query.filter(User.username.like('%'+search_username+'%')).all()
            for username in result:
                list_resp.append(username.username) 
            dict_resp["result"]=list_resp
            print(dict_resp,"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            return jsonify(dict_resp)
        else:
            dict_resp['error']="no data found"
            return jsonify(dict_resp)
            

@app.route("/login", methods=['POST', 'GET'])
def login_fun():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        database_password = user.password_hash
        database_username=user.username
        if username !="" and password !="":
            if database_username == username and sha256_crypt.verify(password, database_password):
                login_user(user)
                flash('Login Successfully','success')
                session['username']=username
                return redirect("/comment")
            else:
                flash('Invalid User', 'danger')
                return redirect("/login")
        else:
            flash("Please Enter Username or Password","danger")
            return redirect("/login")
    return render_template('login.html')

@app.route("/logout")
def logout_fun():
    logout_user()
    session["username"]=None
    flash("logout successfully",'info')
    return redirect("/") 

@app.route("/comment")
def comment_redire():
    result=Post.query.order_by(Post.id.desc()).first()
    return render_template("comment.html",result=result)

@app.route("/comment",methods=["POST","GET"])
def comment_add():
    if current_user.username:
        uid=current_user.id    
        if request.method=="POST":
            comment=request.form['post_data']
            post_id=request.form['post_id']
            print(comment)
            data=Post.query.filter_by(id=post_id).first()
            data.id=post_id
            data.body=comment
            db.session.commit()
            var_comment= {}
            var_comment['cmt']=comment
            
            return jsonify(var_comment)
    return render_template("comment.html")


@app.route("/comment_btn",methods=['POST','GET'])
def com():     
    if current_user.username:
        uid=current_user.id    
        if request.method=="POST":
            comment=request.form['comment']
            data=Post(body=comment,author_id=uid)
            db.session.add(data) 
            db.session.commit()
            return redirect("/comment")
    return render_template("comment.html")

# @app.route("/edit_post/<int:pid>",methods=['POST','GET'])
# def edit_post(pid):
#     data=Post.query.get(pid)
#     if request.method == "POST":
#         content=request.form['comment']
#         data.body=content
#         db.session.commit()
#         flash("Record Updated Successfully",'success')
#         return redirect("/")
#     return render_template("edit_post.html",data=data)

# @app.route("/delete_post/<int:pid>",methods=['POST','GET'])
# def delete_post(pid):
#     data=Post.query.get(pid)
#     db.session.delete(data)
#     db.session.commit()
#     flash("Record Deleted Successfully",'success')
#     return redirect("/")

@app.route("/edit_data",methods=['POST','GET'])
def edit_data():
    id = request.get_data()
    if request.method == 'POST':
        id=request.form['id']
        database_data=Post.query.get(id)
        body=database_data.body
        resp= {"id":id,"body":body}
        return jsonify(resp)

@app.route("/update_data",methods=['POST','GET'])
def update_data(): 
    if request.method == 'POST':     
        id=request.form['id']
        comment=request.form["comment"]
        data=Post.query.get(id)
        data.body=comment
        db.session.commit()
        resp = {}
        resp["comment"] = comment
        resp["id"] = id
        return jsonify(resp)
        
@app.route("/delete_post",methods=['POST','GET'])
def delete_post():
    if request.method == 'POST':
        pid=request.form.get('id')
        print(pid)
        data=Post.query.get(pid)
        db.session.delete(data)
        db.session.commit()
        re={"status":"done"}
        return jsonify(re)

@app.route("/pagination",methods=['POST','GET'])
def pagination():
    if request.method == 'POST':
        draw=request.form['draw'];
        row_data=int(request.form['start'])
        rowperpage=int(request.form['length'])
        total_record_list=User.query.all();
        total_records=len(total_record_list)
        
        filtered_data=User.query.order_by(User.username.asc())[row_data:rowperpage]
        #filtered_data=query.User.order_by(User.username.asc())[:5].all()
        #print(filtered_data,">>>>>>>>>>>>>>>>>>>>>>>>>>>>>fitlered data")
        
        data=[]
        for row in filtered_data:
            data.append({
                         "username":row.username,
                        "email":row.email,
                        "password":row.password_hash,
                        })
        response={
                    'draw':draw,
                    'iTotalRecords':total_records,
                    'iTotalDisplayRecords':17,
                    'aaData':data,
                }
        return jsonify(response)
            
@app.route('/delete_user_record',methods=['POST','GET'])
def del_users():
    print(request.form,"<<<<<<<>>>>>>>>>>")
    resp={}
    list_del=[]
    if request.method == 'POST':
        check_list=request.form.getlist('data[]')
        for data in check_list:
            list_del.append(data)
            print(list_del)
    
            result=User.query.get(data)
            db.session.delete(result)
            db.session.commit()
            print(check_list,"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<checkbox just check demo") 
        resp={'success':"done",'del_id':list_del}
        return jsonify(resp)                  

if __name__=="__main__":
    app.run(debug=True)
    

