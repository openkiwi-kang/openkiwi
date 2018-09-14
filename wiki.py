# -*- coding: utf-8 -*-
#!/usr/bin/env python3
from flask import Flask,render_template,request,redirect,url_for,session,send_from_directory,flash,make_response
import sqlite3
import hashlib
import os
import codecs
import json
import urllib
import pickle
from parsing_kiwi import parser_kiwi
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, AnyOf
from flask_wtf.csrf import CSRFProtect
from tool import check_ip

#loopstart
class LoginForm(FlaskForm):
    username = StringField('username',validators=[InputRequired('A username is required!')])
    password = PasswordField('password',validators=[InputRequired('A password is required!')])
class SearchForm(FlaskForm):
    keyword = StringField('Search',validators=[InputRequired()])
#setup
print(" * load wiki")
settingjson = open("setting.json")
settingdic = json.load(settingjson)
if settingdic["db"] == "mariadb" or settingdic["db"] == "mysql":
    import pymysql
    conn = pymysql.connect(host=settingdic["hostname"], port=int(settingdic["port"]), user=settingdic["id"], passwd=settingdic["passwd"], db=settingdic["dbname"],charset='utf8',autocommit=True)
else:
    if settingdic["db"] == 'sqlite3' or settingdic["db"] == 'sqlite':
        conn = sqlite3.connect(settingdic["dbname"]+".db",check_same_thread=False,isolation_level = None)
    else:
        print(">>>wrong setting error!")

skin = "kiyee"
curs = conn.cursor()
app = Flask(__name__)
secretkey = "testsecretkey"
app.secret_key = secretkey
app.config["APPLICATION_ROOT"] = '/'
wiki = "openkiwi"
csrf = CSRFProtect(app)
csrf.init_app(app)

curs.execute('create table if not exists user(userid text, pw text, acl text, date text, email text, login text, salt text)')
curs.execute('create table if not exists backlink(title text,back text)')
curs.execute('create table if not exists pages(title text,data text)')
curs.execute('create table if not exists acls(title text,acl text)')
curs.execute('create table if not exists namespaceacl(namespace text,acl text)')

conn.commit()
def hashpass(password,salt):
    data = password + salt
    hash = hashlib.sha512(bytes(data, 'utf-8')).hexdigest()
    return hash
def md5(email):
    return hashlib.md5(bytes(email, 'utf-8')).hexdigest()
@app.route('/')
def index():
    form = SearchForm()
    if "login" in session:
        if "email" in session:
            if tokencheck(session['login']):
                hashed_email = md5(str(session['email']))
                imageurl = "https://www.gravatar.com/avatar/"+hashed_email+"?s=40&d=retro"
                #print("user:"+str(tokencheck(session['login']))+":"+imageurl)
                return render_template(skin+'/index.html',wikiname = wiki,imageurl = imageurl,form = form)
            else:
                return render_template(skin+'/index.html',wikiname = wiki,form = form)
        else:
            return render_template(skin+'/index.html',wikiname = wiki,form = form)
    else:
        return render_template(skin+'/index.html',wikiname = wiki,form = form)

@app.route('/',methods=['POST'])
def gotosearch():
    form = SearchForm()
    keyword = form.keyword.data
    #print(keyword)
    return redirect('/search/'+keyword)

@app.route('/login')
def login_form():
    form = LoginForm()
    return render_template(skin+'/login.html',form=form)

@app.route('/logout')
def logout():
    if "login" in session:
        if tokencheck(session['login']):
            curs.execute("update user set login = ? where userid = ?",(codecs.encode(os.urandom(64), 'hex').decode(),tokencheck(session['login'])))
            session['email'] = None
            session['login'] = None
            flash('You were successfully logged out')
            return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    text = form.username.data
    id = text
    #print(id)
    text = form.password.data
    password = text
    #print(password)
    curs.execute("select salt from user where userid = (?)",[id])
    temp =curs.fetchall()
    if temp:
        salt = str(temp[0][0])
    else:
        salt = None
    #print(salt)
    curs.execute("select pw from user where userid = (?)",[id])
    temp =curs.fetchall()
    if temp:
        dbhash = str(temp[0][0])
    else:
        dbhash = None
    #print(dbhash)
    if dbhash and salt:
        hash = hashpass(password,salt)
    else:
        hash = "dsaghjkfhhajhfkhdsakjhjdfhjkhdsajkfhjfhkja"

    if hash == dbhash:
        rand = codecs.encode(os.urandom(32), 'hex').decode()
        curs.execute("update user set login = ? where userid = ?",(rand,id))
        curs.execute("select email from user where userid = (?)",[id])
        usr_email = curs.fetchall()[0][0]
        session['email'] = usr_email
        session['login'] = rand
        flash('You were successfully logged in')
        flash('hello  '+id+'!!')
        return redirect(url_for('index'))
    else:
        return render_template(skin+'/error_passmatch-e.html')


@app.route('/signup')
def signup_form():

    form = LoginForm()

    return render_template(skin+'/signup.html',form=form)

@app.route('/signup', methods=['POST'])
def signup():
    id = request.form['uname']
    email = request.form['email']
    psw = request.form['psw']
    pswck = request.form['pswck']
    if psw == pswck:
        logintoken = codecs.encode(os.urandom(32), 'hex').decode()
        salt = codecs.encode(os.urandom(32), 'hex').decode()
        hash = hashpass(psw,salt)
        #userid text, pw text, acl text, date text, email text, login text salt text
        curs.execute('insert into user(userid,pw,acl,date,email,login,salt) values (?,?,?,?,?,?,?)',(id,hash,"user",gettime(),email,logintoken,salt))
        session['login'] = logintoken
        return redirect(url_for('login'))
    else:
        return render_template(skin+'/error_passmatch-e.html')
    conn.commit()

def tokencheck(token):
    curs.execute("select userid from user where login = ?",[token])
    if curs.fetchall():
        curs.execute("select userid from user where login = ?",[token])
        return curs.fetchall()[0][0]
    else:
        return False

def gettime():
    return str(datetime.now())

@app.route('/w/<pagename>')
def pagerender(pagename):
    print(request.headers["User-Agent"]+"  in  "+getip(request))
    form = SearchForm()
    useracl = "ipuser"
    if "login" in session:
        if tokencheck(session['login']):
            curs.execute("select acl from user where userid = (?)",[tokencheck(session['login'])])
            if curs.fetchall():
                curs.execute("select acl from user where userid = (?)",[tokencheck(session['login'])])
                useracl = curs.fetchall()[0][0]
            else:
                useracl = "ipuser"
    else:
        useracl = "ipuser"
    if pagename == "":
        return redirect(url_for('index'))
    curs.execute("select data from pages where title = ?",[pagename])
    if curs.fetchall():
        curs.execute("select data from pages where title = ?",[pagename])
        data = curs.fetchall()[0][0]
        output = parser_kiwi(pagename,data)
        if acltest(pagename,"read",useracl):
            if "login" in session and "email" in session:
                if tokencheck(session['login']):
                    hashed_email = md5(str(session['email']))
                    imageurl = "https://www.gravatar.com/avatar/"+hashed_email+"?s=40&d=retro"
                    return render_template(skin+'/index.html',wikiname = wiki,imageurl = imageurl,data = output,form = form)
                else:
                    return render_template(skin+'/index.html',wikiname = wiki,data = output,form = form)
            else:
                return render_template(skin+'/index.html',wikiname = wiki,data = output,form = form)
        else:
            return "<h2>Access Denied</h2>"
    else:
        if "login" in session and "email" in session and tokencheck(session['login']):
            hashed_email = md5(str(session['email']))
            imageurl = "https://www.gravatar.com/avatar/"+hashed_email+"?s=40&d=retro"
            return render_template(skin+'/index.html',wikiname = wiki,imageurl = imageurl,form = form)
        else:
            return render_template(skin+'/index.html',wikiname = wiki,form = form)

@app.route('/edit/<pagename>',methods=['GET'])
def editpage(pagename):
    form_ = SearchForm()
    curs.execute("select data from pages where title = ?",[pagename])
    if curs.fetchall():
        curs.execute("select data from pages where title = ?",[pagename])
        data = curs.fetchall()[0][0]
    else:
        data = "#None"
    form = """<form method="POST" id="editform">
    <textarea name="edit" wrap="soft" rows="20" cols="40" style="width:90%;">"""+data+"""</textarea>
    <br>"""+str(form_.csrf_token)+"""</form><button type="submit" form="editform">Submit</button>"""
    if "login" in session:
        if "email" in session:
            if tokencheck(session['login']):
                hashed_email = md5(str(session['email']))
                imageurl = "https://www.gravatar.com/avatar/"+hashed_email+"?s=40&d=retro"
                #print("user:"+str(tokencheck(session['login']))+":"+imageurl)
                return render_template(skin+'/index.html',wikiname = wiki,imageurl = imageurl,data = form,form = form_)
            else:
                return render_template(skin+'/index.html',wikiname = wiki,data = form,form = form_)
        else:
            return render_template(skin+'/index.html',wikiname = wiki,data = form,form = form_)
    else:
        return render_template(skin+'/index.html',wikiname = wiki,data = form,form = form_)

@app.route('/w/<pagename>',methods=['POST'])
def gotosearch_1(pagename):
    form = SearchForm()
    keyword = form.keyword.data
    print(keyword)
    return redirect('/search/'+keyword)

@app.route('/edit/<pagename>',methods=['POST'])
def edit(pagename):
    form = SearchForm()
    if not form.keyword.data:
        data = request.form['edit']
        curs.execute("delete from pages where title = (?)",[pagename])
        curs.execute("insert into pages values (?,?)",(pagename,data))
        return redirect('/w/'+pagename)
    if form.keyword.data:
        return redirect('/search/'+form.keyword.data)

def getip(requests):
    ip = None
    try:
        ip = str(requests.headers["True-Client-IP"])
    except:
        try:
            ip = str(requests.headers["CF-Connecting-IP"])
        except:
            try:
                ip = str(requests.headers["X-Real-IP"])
            except:
                try:
                    ip = str(requests.headers["X-Forwarded-For"])
                except:
                    ip = str(requests.remote_addr)
    return ip

def acltest(page,job,useracl):
    curs.execute("select acl from acls where title = (?)",[page])
    acl = curs.fetchall()
    if not acl:
        return False
        #print("acl")
        temp = page.count(":")
        if temp == 0:
            namespace = "default"
        elif temp > 0:
            namespace = page.split(":")[0]
            if namespace == '':
                namespace = "default"
        curs.execute("select acl from namespaceacl where namespace = ?",[namespace])
        temp = curs.patchall()
        if temp:
            temp = temp[0][0]
            curs.execute("insert into acls(?,?)",[page,temp])
        else:
            False
    else:
        try:
            acldic = json.loads(acl[0][0])
            #print(acldic[useracl][job])
            if useracl in acldic:
                if job in acldic[useracl]:
                    return acldic[useracl][job]
                else:
                    return False
            else:
                return False
        except:
            print("Acl Error in %d"%page)
            return False
        
        
    

#apprun
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5555,debug=True)

