# -*- coding: utf-8 -*-
#!/usr/bin/env python3
from flask import Flask,render_template,request,redirect,url_for,session,send_from_directory,flash,make_response,jsonify
import sqlite3
import hashlib
import os
import codecs
import json
import urllib
import urllib.request
import pickle
import sys
import time
import logging
from parsing_kiwi import parser_kiwi
from datetime import datetime, timedelta, timezone
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
curs.execute('create table if not exists apikey(key text,user text,acl text)')
curs.execute('create table if not exists cache(title text,html text)')

conn.commit()
def gettime():
    return str(datetime.now())

def hashpass(password,salt):
    data = password + salt
    hash = hashlib.sha384(bytes(hashlib.sha512(bytes(data, 'utf-8')).hexdigest(), 'utf-8')).hexdigest()
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
    curs.execute('select userid from user where userid = (?)',[id])
    if psw == pswck and not curs.fetchall():
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
        curs.execute('select html from cache where title = ?',[pagename])
        if curs.fetchall():
            curs.execute('select html from cache where title = ?',[pagename])
            output = curs.fetchall()[0][0]
        else:
            output = parser_kiwi(pagename,data)
            #print(output)
            curs.execute('insert into cache values (?,?)',[pagename,output])
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
            flash ('Access Denied','error')
            return redirect(url_for('index'))
    else:
        if "login" in session and "email" in session and tokencheck(session['login']):
            hashed_email = md5(str(session['email']))
            imageurl = "https://www.gravatar.com/avatar/"+hashed_email+"?s=40&d=retro"
            return render_template(skin+'/index.html',wikiname = wiki,imageurl = imageurl,form = form)
        else:
            return render_template(skin+'/index.html',wikiname = wiki,form = form)

@app.route('/edit/<pagename>',methods=['GET'])
def editpage(pagename):
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
    if not acltest(pagename,"edit",useracl):
        return "<h2>Access Denied</h2>"
    form_ = SearchForm()
    curs.execute("select data from pages where title = ?",[pagename])
    if curs.fetchall():
        curs.execute("select data from pages where title = ?",[pagename])
        data = curs.fetchall()[0][0]
    else:
        data = "#None"
    form = """<form method="POST" class="form-control" id="editform">
    <textarea name="edit" wrap="soft" rows="20" cols="40" style="width:90%;">"""+data+"""</textarea>
    <br>"""+str(form_.csrf_token)+"""</form><button type="submit" class="btn btn-primary" form="editform">Submit</button>"""
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
    #print(keyword)
    return redirect('/search/'+keyword)

@app.route('/edit/<pagename>',methods=['POST'])
def edit(pagename):
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
    if not acltest(pagename,"edit",useracl):
        return "<h2>Access Denied</h2>"
    form = SearchForm()
    if not form.keyword.data:
        data = request.form['edit']
        curs.execute("delete from cache where title = (?)",[pagename])
        curs.execute("delete from pages where title = (?)",[pagename])
        curs.execute("insert into pages values (?,?)",(pagename,data))
        output = parser_kiwi(pagename,data)
        curs.execute('insert into cache values (?,?)',[pagename,output])
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

@app.route("/apiv1/<apitype>/<apikey>")
def apiget(apitype,apikey):
    curs.execute("select acl from apikey where key = (?)",[apikey])
    apiacl = curs.fetchall()

    if apiacl:
        apiacl = apiacl[0][0]
        apiacl = json.loads(apiacl)
    else:
        apiacl = {"GETRAW":False,"EDITRAW":False,"GETHTML":False,"GETUSER":False,"GETACL":False}
    
    if apitype == "GETRAW":
        if apiacl["GETRAW"]:
            try:
                pagename = request.args['page']
                curs.execute("select data from pages where title = ?",[pagename])
                pagedata = curs.fetchall()
                curs.execute("select user from apikey where key = (?)",[apikey])
                temp = curs.fetchall()
                curs.execute("select acl from user where userid = (?)",[temp[0][0]])
                if pagedata and acltest(pagename,"read",curs.fetchall()[0][0]):
                    data = json.dumps({"success":True,"request":pagename,"data":pagedata[0][0]},indent=2)
                else:
                    data = json.dumps({"success":False},indent=2)
            except:
                data = json.dumps({"success":False},indent=2)
        else:
            data = json.dumps({"success":False},indent=2)
        resp = app.response_class(response=data,status=200,mimetype='application/json')
        return resp
    elif apitype == "GETHTML":
        if apiacl["GETHTML"]:
            try:
                pagename = request.args['page']
                curs.execute("select data from pages where title = ?",[pagename])
                pagedata = curs.fetchall()
                curs.execute("select user from apikey where key = (?)",[apikey])
                temp = curs.fetchall()
                curs.execute("select acl from user where userid = (?)",[temp[0][0]])
                if pagedata and acltest(pagename,"read",curs.fetchall()[0][0]):
                    data = json.dumps({"success":True,"request":pagename,"data":parser_kiwi(pagename,pagedata[0][0])},indent=2)
                else:
                    data = json.dumps({"success":False},indent=2)
            except:
                data = json.dumps({"success":False},indent=2)
        else:
            data = json.dumps({"success":False},indent=2)
        resp = app.response_class(response=data,status=200,mimetype='application/json')
        return resp
    
@app.route("/apiv1/<apitype>",methods=['POST'])
def postapi(apitype):
    if not request.json or not 'apikey' in request.json or not 'pagename' in request.json or not 'data' in request.json:
        data = json.dumps({"success":False},indent=2)
        resp = app.response_class(response=data,status=200,mimetype='application/json')
        return resp
    apikey = request.json["apikey"]
    pagename = request.json["pagename"]
    curs.execute("select acl from apikey where key = (?)",[apikey])
    apiacl = curs.fetchall()
    if apiacl:
        apiacl = apiacl[0][0]
        apiacl = json.loads(apiacl)
    else:
        apiacl = {"EDITRAW":False}
    if apitype == "EDITRAW":
        if not apiacl["EDITRAW"]:
            data = json.dumps({"success":False},indent=2)
            resp = app.response_class(response=data,status=200,mimetype='application/json')
            return resp
        else:
            curs.execute('SELECT user FROM apikey WHERE key = (?)',[apikey])
            temp = curs.fetchall()
            if temp:
                temp = temp[0][0]
                curs.execute('select acl from user where userid = (?)',[temp])
                useracl = curs.fatchall()[0][0]
                if acltest(pagename,"edit",useracl) and acltest(pagename,"read",useracl):
                    data = request.json[data]
                    curs.execute("delete from cache where title = (?)",[pagename])
                    curs.execute("delete from pages where title = (?)",[pagename])
                    curs.execute("insert into pages values (?,?)",(pagename,data))
                    output = parser_kiwi(pagename,data)
                    curs.execute('insert into cache values (?,?)',[pagename,output])
                    data = json.dumps({"success":True},indent=2)
                else:
                    data = json.dumps({"success":False},indent=2)
                    resp = app.response_class(response=data,status=200,mimetype='application/json')
                    return resp
            else:
                data = json.dumps({"success":False},indent=2)
                resp = app.response_class(response=data,status=200,mimetype='application/json')
                return resp
    
    resp = app.response_class(response=data,status=200,mimetype='application/json')
    return resp

def searchengine(keyword):
    curs.execute("select * from pages where title = (?)",[keyword])
    fullmatch = curs.fetchall()
    print(fullmatch)
    return True

@app.route("/random")
def title_random():
    curs.execute("select title from pages order by random() limit 1")
    data = curs.fetchall()
    if data:
        return redirect('/w/' + data[0][0])
    else:
        return redirect('/')

@app.route('/acl/<pagename>')
def aclview(pagename):
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
    if not acltest(pagename,"viewacl",useracl):
        flash ('Access Denied','error')
        return redirect('/')
    curs.execute("select acl from acls where title = (?)",[pagename])
    acl = curs.fetchall()
    if not acl:
        flash ('Access Denied','error')
        return redirect('/')
    acl=acl[0][0]
    acldic = json.loads(acl)
    aclrank = [] 
    for temp in acldic: 
        aclrank.append(temp)
    return str(aclrank)

def acltest(page,job,useracl):
    curs.execute("select acl from acls where title = (?)",[page])
    acl = curs.fetchall()
    if useracl == "admin":
        return True
    if not acl:
        #print("acl")
        temp = page.count(":")
        if temp == 0:
            namespace = "default"
        elif temp > 0:
            namespace = page.split(":")[0]
            if namespace == '':
                namespace = "default"
        curs.execute("select acl from namespaceacl where namespace = ?",[namespace])
        temp = curs.fetchall()
        if temp:
            temp = temp[0][0]
            curs.execute("insert into acls values(?,?)",[page,temp])
            return acltest(page,job,useracl)
        else:
            return False
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

def loadplugins():
    plugin_list = os.listdir("./plugins")
    temp = []
    for filename in plugin_list:
        if filename.endswith(".py"):
            temp.append(filename)
    
    plugin_list = temp
    for temp in plugin_list:
        time.sleep(0.4)
        sys.stdout.write(''' * "'''+str(temp)+'''" plugin detected!\n''')

#loadplugins()
#searchengine("hi")
#apprun
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5555,debug=True)

