# -*- coding: utf-8 -*-
#!/usr/bin/env python3
from flask import Flask,render_template,request,redirect,url_for,session,send_from_directory,flash,make_response,jsonify,abort,current_app
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
from functools import wraps
#import logging
import difflib
#from parsing_kiwi import parser_kiwi
from datetime import datetime, timedelta, timezone , date
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, AnyOf
#from flask_wtf.csrf import CSRFProtect


from tool import check_ip

if "TESTMODE" in os.environ and os.environ['TESTMODE'] == "TRUE":
    testmode = True
else:
    testmode = False


#loopstart
class LoginForm(FlaskForm):
    username = StringField('username',validators=[InputRequired('A username is required!')])
    password = PasswordField('password',validators=[InputRequired('A password is required!')])
class SearchForm(FlaskForm):
    keyword = StringField('Search',validators=[InputRequired()])
#setup
settingjson = open("./setting.json","r")
settingdic = json.load(settingjson)
settingjson.close()
try:
    exec("from "+settingdic["parser"]+" import parser_kiwi")
except:
    print("ImportError")

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
secretkey = settingdic["secretkey"]
app.secret_key = secretkey
app.config["APPLICATION_ROOT"] = '/'
wiki = "openkiwi"
#csrf = CSRFProtect(app)
#csrf.init_app(app)
#logging.basicConfig(filename='./logs/debug.log',level=logging.DEBUG)
curs.execute('create table if not exists user(userid text, pw text, acl text, date text, email text, login text, salt text)')
curs.execute('create table if not exists backlink(title text,back text)')
curs.execute('create table if not exists pages(title text,data text)')
curs.execute('create table if not exists acls(title text,acl text)')
curs.execute('create table if not exists namespaceacl(namespace text,acl text)')
curs.execute('create table if not exists apikey(key text,user text,acl text)')
curs.execute('create table if not exists cache(title text,html text)')

conn.commit()
print(" * load pagename list")
curs.execute('select title from pages')
pagelist = curs.fetchall()
pagelisttemp = []
if pagelist:
    for temp in pagelist:
        pagelisttemp.append(temp[0])
else:
    pagelist = []
pagelist = pagelisttemp
print(" * load finish")
def gettime():
    return str(datetime.now())
def getatime():
    return int(time.time())
def gethtime():
    today = date.today()
    return str(time.strftime('%A', time.localtime(time.time()))+today.isoformat())
def genlog(msg):
    time = gethtime()
    logfile = open(logfilename,"a")
    logfile.write("["+time+"] - "+msg+"\n")
    logfile.close()
def loginit():
    global logtime
    global logfilename
    logtime = gethtime()
    logfilename = "./logs/"+logtime+".txt"
    if not os.path.exists(os.path.join('logs',logtime+".txt")):
        newfile = open(logfilename,'w')
        newfile.write("\n")
        newfile.close()

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
    #logging.debug(request.headers["User-Agent"]+"  in  "+getip(request))
    genlog("user-get-page"+request.headers["User-Agent"]+"  in  "+getip(request)+"  page:"+pagename)
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
    form = """<form method="POST" class="form-control" id="editer">
    <textarea name="editform" wrap="soft" rows="20" cols="40" style="width:90%; id="editform">"""+data+"""</textarea>
    <br>"""+"""<input class="btn btn-primary" type="submit" value="전송"></form><script>CKEDITOR.replace('editform',{customConfig: '/statics/config/ckeditor_config.js'});</script>"""
    if "login" in session:
        if "email" in session:
            if tokencheck(session['login']):
                hashed_email = md5(str(session['email']))
                imageurl = "https://www.gravatar.com/avatar/"+hashed_email+"?s=40&d=retro"
                #print("user:"+str(tokencheck(session['login']))+":"+imageurl)
                return render_template(skin+'/index.html',wikiname = wiki,imageurl = imageurl,data = form,form = form_,editer=True)
            else:
                return render_template(skin+'/index.html',wikiname = wiki,data = form,form = form_,editer=True)
        else:
            return render_template(skin+'/index.html',wikiname = wiki,data = form,form = form_,editer=True)
    else:
        return render_template(skin+'/index.html',wikiname = wiki,data = form,form = form_,editer=True)

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
        #print(request.form)
        data = request.form['editform']
        curs.execute("delete from cache where title = (?)",[pagename])
        curs.execute("delete from pages where title = (?)",[pagename])
        curs.execute("insert into pages values (?,?)",(pagename,data))
        output = parser_kiwi(pagename,data)
        #output = data
        curs.execute('insert into cache values (?,?)',[pagename,output])
        if not pagename in pagelist:
            pagelist.append(pagename)
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
        if not "EDITRAW" in apiacl:
            data = json.dumps({"success":False},indent=2)
            resp = app.response_class(response=data,status=200,mimetype='application/json')
            return resp
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
                useracl = curs.fetchall()[0][0]
                if acltest(pagename,"edit",useracl) and acltest(pagename,"read",useracl):
                    data = request.json["data"]
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

def searchengine(keyword,depth=5):
    result = []
    #print(difflib.get_close_matches(keyword,pagelist,depth,0.1))
    result = result + difflib.get_close_matches(keyword,pagelist,depth,0.1)
    return result

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
    try:
        acldic = json.loads(acl)
    except:
        print(''' * Acl error in "'''+pagename+'"')
        flash ('Access Denied','error')
        return redirect('/')
    aclrank = []
    for temp in acldic:
        aclrank.append(temp)
    jobs = []
    acljob = []
    for temp in aclrank:
        for job in acldic[temp]:
            if not job in jobs:
                jobs.append(job)
                acljob.append([job,[temp,acldic[temp][job]]])
            else:
                idx = 0
                for temp2 in acljob:
                    if temp2[0] == job:
                        acljob[idx].append([temp,acldic[temp][job]])
                    idx = idx + 1
    form = SearchForm()
    if "email" in session and "login" in session:
        hashed_email = md5(str(session['email']))
        imageurl = "https://www.gravatar.com/avatar/"+hashed_email+"?s=40&d=retro"
        return render_template(skin+"/acl.html",acldata = acljob,imageurl = imageurl,form = form,skin=skin)
    return render_template(skin+"/acl.html",acldata = acljob,form = form,skin=skin)

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
        if filename.endswith(".init"):
            temp.append(filename)
    plugin_list = temp
    for temp in plugin_list:
        time.sleep(0.4)
        sys.stdout.write(''' * "'''+str(temp)[:-5]+'''" plugin detected!\n''')
        try:
            exec("import plugins."+str(temp)[:-5]+"."+str(temp)[:-5])
            exec("app.register_blueprint(plugins."+str(temp)[:-5]+"."+str(temp)[:-5]+".plugin"+")")
            sys.stdout.write(''' * "'''+str(temp)[:-5]+'''" plugin loaded!\n''')
        except:
            print(" * plugin "+str(temp)[:-5]+" load fail")
        time.sleep(0.4)
        

@app.route('/statics/<path:file>')
def static_host(file):
    if os.path.exists(os.path.join('statics', file)):
        #response.headers['Cache-Control'] = 'max-age = 43200'
        #response.headers['Server'] = 'nginx'
        return send_from_directory('./statics', file)
    else:
        return abort(404)

@app.route('/img/<path:file>')
def image_host(file):
    if os.path.exists(os.path.join('img', file)):
        #response.headers['Cache-Control'] = 'max-age = 43200'
        #response.headers['Server'] = 'nginx'
        data = send_from_directory('./img', file)
        return data
    else:
        return abort(404)
@app.after_request
def headercontrol(response):
    response.headers['Cache-Control'] = 'max-age = '+str(60*60*24)
    response.headers['Server'] = 'nginx'
    return response

@app.errorhandler(404)
def page_not_found(error):
    flash("""This page does not exist""")
    return redirect("/")
loadplugins()
#print(searchengine("ki",10))
#apprun


if testmode:
    exit(0)
if __name__ == "__main__":
    loginit()
    genlog("SERVERSTARTED")
    app.run(host='0.0.0.0',port=5555,debug=True)

