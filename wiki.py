# -*- coding: utf-8 -*-
#!/usr/bin/env python3
from flask import Flask,render_template,request,redirect,url_for,session,send_from_directory,flash
import sqlite3
import hashlib
import os
import codecs
import json
import urllib
from parsing_kiwi import parser_kiwi
from datetime import datetime

#loopstart
#setup
skin = "kiyee"
conn = sqlite3.connect('test.db',check_same_thread=False,isolation_level = None)
curs = conn.cursor()
app = Flask(__name__)
secretkey = "testsecretkey"
app.secret_key = secretkey
app.config["APPLICATION_ROOT"] = '/'
wiki = "openkiwi"

curs.execute('create table if not exists user(userid text, pw text, acl text, date text, email text, login text, salt text)')
curs.execute('create table if not exists backlink(title text,back text)')
curs.execute('create table if not exists pages(title text,data text)')

conn.commit()
def hashpass(password,salt):
    data = password + salt
    hash = hashlib.sha512(bytes(data, 'utf-8')).hexdigest()
    return hash
def md5(email):
    return hashlib.md5(bytes(email, 'utf-8')).hexdigest()
@app.route('/')
def index():
    if "login" in session:
        if "email" in session:
            if tokencheck(session['login']):
                hashed_email = md5(str(session['email']))
                imageurl = "https://www.gravatar.com/avatar/"+hashed_email+"?s=40&d=retro"
                #print("user:"+str(tokencheck(session['login']))+":"+imageurl)
                return render_template(skin+'/index.html',wikiname = wiki,imageurl = imageurl)
            else:
                return render_template(skin+'/index.html',wikiname = wiki)
        else:
            return render_template(skin+'/index.html',wikiname = wiki)
    else:
        return render_template(skin+'/index.html',wikiname = wiki)

@app.route('/',methods=['POST'])
def gotosearch():
    keyword = request.form['Search']
    print(keyword)
    return redirect('/search/'+keyword)

@app.route('/login')
def login_form():
    return render_template(skin+'/login.html')

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
    text = request.form['uname']
    id = text
    text = request.form['psw']
    password = text
    curs.execute("select salt from user where userid = (?)",[id])
    salt = curs.fetchall()[0][0]
    curs.execute("select pw from user where userid = (?)",[id])
    dbhash = curs.fetchall()[0][0]
    hash = hashpass(password,salt)

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
    return render_template(skin+'/signup.html')

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
        conn.close()
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
    if pagename == "":
        return redirect(url_for('index'))
    curs.execute("select data from pages where title = ?",[pagename])
    if curs.fetchall():
        curs.execute("select data from pages where title = ?",[pagename])
        data = curs.fetchall()[0][0]
        output = parser_kiwi(pagename,data)
        if "login" in session and "email" in session:
            if tokencheck(session['login']):
                hashed_email = md5(str(session['email']))
                imageurl = "https://www.gravatar.com/avatar/"+hashed_email+"?s=40&d=retro"
                return render_template(skin+'/index.html',wikiname = wiki,imageurl = imageurl,data = output)
            else:
                return render_template(skin+'/index.html',wikiname = wiki,data = output)
        else:
            return render_template(skin+'/index.html',wikiname = wiki,data = output)
    else:
        if "login" in session and "email" in session and tokencheck(session['login']):
            hashed_email = md5(str(session['email']))
            imageurl = "https://www.gravatar.com/avatar/"+hashed_email+"?s=40&d=retro"
            return render_template(skin+'/index.html',wikiname = wiki,imageurl = imageurl)
        else:
            return render_template(skin+'/index.html',wikiname = wiki)
@app.route('/edit/<pagename>',methods=['GET'])
def editpage(pagename):
    curs.execute("select data from pages where title = ?",[pagename])
    if curs.fetchall():
        curs.execute("select data from pages where title = ?",[pagename])
        data = curs.fetchall()[0][0]
    else:
        data = "#None"
    form = """<form method="POST" id="editform">
    <textarea name="edit" rows="25" cols="160">"""+data+"""</textarea>
    <br>
    </form>
    <button type="submit" form="editform">Submit</button>"""
    if "login" in session:
        if "email" in session:
            if tokencheck(session['login']):
                hashed_email = md5(str(session['email']))
                imageurl = "https://www.gravatar.com/avatar/"+hashed_email+"?s=40&d=retro"
                #print("user:"+str(tokencheck(session['login']))+":"+imageurl)
                return render_template(skin+'/index.html',wikiname = wiki,imageurl = imageurl,data = form)
            else:
                return render_template(skin+'/index.html',wikiname = wiki,data = form)
        else:
            return render_template(skin+'/index.html',wikiname = wiki,data = form)
    else:
        return render_template(skin+'/index.html',wikiname = wiki,data = form)

@app.route('/edit/<pagename>',methods=['POST'])
def edit(pagename):
    data = request.form['edit']
    curs.execute("update pages set data = ? where title = ?",(data,pagename))
    return redirect('/w/'+pagename)

#apprun
app.run(host='0.0.0.0',port=80,debug=True)
