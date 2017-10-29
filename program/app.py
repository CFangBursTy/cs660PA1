# Shanhai Path: C:/Users/廖山海/Desktop/CS/Database/Project1/program
# Chao path: D:/BUCS/PhotoShare/program
import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
from datetime import date,datetime

# for image uploading
# from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Hellcat'
app.config['MYSQL_DATABASE_DB'] = 'photoshare_pa'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email FROM Users")
users = cursor.fetchall()

#Global variable
Photo_Tags = {}
working_path = os.getcwd() + '/static'


def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM Users")
    return cursor.fetchall()


class User(flask_login.UserMixin):
    pass




'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''
def getUsersId(uid):
    cursor=conn.cursor()
    cursor.execute("select user_id from users where Email='{0}'".format(uid))
    return cursor.fetchone()[0]

def getUsersInfor(uid):
    cursor=conn.cursor()
    cursor.execute("Select * from users where Email='{0}' or user_id='{0}'".format(uid))
    return cursor.fetchall()

def getUserFriend(uid):
    cursor=conn.cursor()
    userid=getUsersId(flask_login.current_user.id)
    if cursor.execute("select * from friends where User_id_1='{0}'or FriendsUser_id_2='{0}'".format(userid)):
        return cursor.fetchall()

def getAllPhotoCaption():
    cursor=conn.cursor()
    query = "select Caption from photos"
    cursor.execute(query)
    allCap = cursor.fetchall()
    result =[]
    if len(allCap) != 0:
        for cap in allCap:
            result.append(cap[0])

    return result


def AddFriend(uid):
    cursor=conn.cursor()
    curid=getUsersId(flask_login.current_user.id)
    print(getUsersId(uid))
    print(cursor.execute("insert into friends(User_id_1,FriendsUser_id_2) values('{0}','{1}')".format(curid,getUsersId(uid))))
    conn.commit()

def DeleteFriend(uid):
    cursor=conn.cursor()
    curid=getUsersId(flask_login.current_user.id)
    print(cursor.execute("delete from friends where (User_id_1='{0}' and FriendsUser_id_2='{1}') or (User_id_1='{1}' and FriendsUser_id_2='{0}')".format(curid,getUsersId(uid))))
    conn.commit()
def getUsersPhotos(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]


def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

def addAlbum(aname, uid):
    cursor = conn.cursor()
    uid = getUserIdFromEmail(uid)
    Date= datetime.now().date()
    print(Date)
    query = "insert into albums(Album_name, User_id,Create_Date) values ('{0}', {1},'{2}')". format(aname, uid,Date)
    cursor.execute(query)
    conn.commit()

def deleteAlbum(aname, uid):
    cursor = conn.cursor()
    uid = getUserIdFromEmail(uid)
    query = "delete from albums where User_id = '{0}' and Album_name = '{1}'".format(uid, aname)
    cursor.execute(query)
    conn.commit()

def addTag(tname):
    cursor = conn.cursor()
    query = "insert into tags(Tag_name) values ('{0}')".format(tname)
    # pid = getPhotoIdFromCaption(caption)
    # query = query + "insert into tagged(Photo_id, Tag_id) values({0}, {1}) ".format(pid, )
    cursor.execute(query)
    conn.commit()

def getPhotoIdFromCaption(caption):
    cursor = conn.cursor()
    query = "select Photo_id from photos where Caption = '{0}'".format(caption)
    cursor.execute(query)
    return cursor.fetchone()[0]

def getTagsFromCaption(caption):
    cursor = conn.cursor()
    query = "select Photo_id from photos where Caption = '{0}'".format(caption)
    cursor.execute(query)
    pid = cursor.fetchone()[0]

    query = "select Tag_name from tags, tagged where tags.Tag_id = tagged.Tag_id and tagged.Photo_id = '{0}'".format(pid)
    cursor.execute(query)
    tags = cursor.fetchall()
    result = []
    for tag in tags:
        result.append(tag[0])

    return result
    

def addTagged(caption, uid, aid):

    # Get newest added tag id
    cursor = conn.cursor()
    alltags = "select Tag_id from tags"
    cursor.execute(alltags)
    latest_tag_id = cursor.fetchall()[-1][0]


    # Get photo id based on the given caption
    uid = getUserIdFromEmail(uid)
    query = "select Photo_id from photos where Caption = '{0}' and  User_id = '{1}' and Album_id = '{2}'".format(
        caption, uid, aid)
    cursor.execute(query)
    pid = cursor.fetchone()[0]


    query = "insert into tagged(Photo_id, Tag_id) values ('{0}', '{1}')".format(pid, latest_tag_id)
    cursor.execute(query)
    conn.commit()

# def addTagged(tid, pid):


def getUserAlbums(uid):
    cursor = conn.cursor()
    uid = getUserIdFromEmail(uid)
    query = "Select * from albums where User_id = '{0}'".format(uid)
    if cursor.execute(query):
        return cursor.fetchall()


def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True

def dir_create(dirname):  #创建新目录
    if(os.path.exists(dirname)):  #检查目录是否已经存在
        print("目录已存在！\n")
        return True
    else:
        os.mkdir(dirname)         #不存在则按照要求新建该目录
        print("目录创建成功！\n")
        return False

def showPhotos(albumid):
     photopath = "/static/{0}/{1}".format(getUsersId(flask_login.current_user.id),albumid)
     print(photopath)
     filename=os.listdir(photopath)
     print(filename)
     return render_template('upload.html', photopath=photopath,uid=str(getUsersId(flask_login.current_user.id)),aid=str(albumid),photos=filename)

def AddPhoto(albumid,filename):
    userid=getUsersId(flask_login.current_user.id)
    cursor=conn.cursor()
    print(filename)
    cursor.execute("insert into photos(Caption,Album_id,User_id) values('{0}',{1},{2})".format(filename,albumid,userid))
    conn.commit()

def DeletePhoto(albumid,photoname):
    global working_path
    userid = getUsersId(flask_login.current_user.id)
    cursor = conn.cursor()
    print("albumid="+albumid)
    cursor.execute("delete from photos where Caption='{0}' and Album_id={1} and user_id={2}".format(photoname,albumid,userid))
    conn.commit()
    path = working_path + "/{0}/{1}/{2}".format(userid,albumid,photoname)
    os.remove(path)

@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0])
    user.is_authenticated = request.form['password'] == pwd
    return user

@app.route('/Friends',methods=["POST","GET"])
@flask_login.login_required
def protected():
    if request.method=='POST':
        if request.form.get('addfriend'):
           AddFriend(request.form.get('addfriend'))
        if request.form.get('deletefriend'):
            DeleteFriend(request.form.get('deletefriend'))


    friendsid=getUserFriend(flask_login.current_user.id)
    if friendsid==None:
        return render_template('Friends.html')
    friends=[]
    loginin_user=getUsersId(flask_login.current_user.id)
    for item in friendsid:
        if item[0]==loginin_user:
            friends.append(getUsersInfor(item[1]))
        else:
            friends.append(getUsersInfor(item[0]))
    return render_template('Friends.html',friends=friends)

@app.route('/login', methods=['GET'])
def login():
    if flask_login.current_user == None or not flask_login.current_user.is_authenticated:
        return render_template('login.html')
    elif flask_login.current_user.is_authenticated:
        return redirect(url_for('homepage', name=flask_login.current_user.id))
        # '''
			#    <form action='login' method='POST'>
			# 	<input type='text' name='email' id='email' placeholder='email'></input>
			# 	<input type='password' name='password' id='password' placeholder='passworddddddd'></input>
			# 	<input type='submit' name='submit'></input>
			#    </form></br>
		 #   <a href='/'>Home</a>
			#    '''
    # The request method is POST (page is recieving data)
@app.route('/login', methods=['POST'])
def login_post():
    email = flask.request.form['email']
    cursor = conn.cursor()
    # check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user)  # okay login in user

            #current_visiting_UserId = getUsersId(flask_login.current_user.id)
            data=getUsersInfor(flask_login.current_user.id)
            #return redirect(url_for('homepage', name=flask_login.current_user.id))

            return render_template('hello.html', name=flask_login.current_user.id, message="1Here's your profile",data=data)
            #return flask.redirect(flask.url_for('protect3d'))  # protected is a function defined in this file

    # information did not match
    return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/homepage')
@flask_login.login_required
def homepage():
    #print(request.args.get('data').split())
    data = getUsersInfor(request.args.get('name'))
    return render_template('hello.html', name=request.args.get('name'), message='Awesome Photoshare System', data=data)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('login.html', message='Logged out')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html', supress='True')


@app.route("/register", methods=['POST'])
def register_user():
    try:
        fn = request.form.get('first name')
        ln = request.form.get('last name')
        gender = request.form.get('gender')
        hometown = request.form.get('hometown')
        email = request.form.get('email')
        password = request.form.get('password')
        dob = request.form.get('dob')
    except:
        print("couldn't find all tokens")  # this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test = isEmailUnique(email)
    if test:
        if dob == '':
            dob = '0001-01-01'
        print(cursor.execute("INSERT INTO users (Lastname, Password, Firstname, Gender, Hometown, Birthdate, Email) "
                             "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(ln, password, fn, gender, hometown, dob, email)))
        conn.commit()
        # log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        data=getUsersInfor(flask_login.current_user.id)
        return render_template('hello.html', name=email, message='Account Created!',data=data)
    else:
        print("couldn't find all tokens")
        return flask.redirect(flask.url_for('register'))



# end login code
# Show how to upload files and Request Methods and directing pages
@app.route("/albums", methods=['GET'])
def album_get():
    albums = getUserAlbums(flask_login.current_user.id)
    albumsInfo = []
    albumIDs = []
    if albums != None:
        for a in albums:
            albumsInfo.append(a[1])
            albumIDs.append(a[0])

    return render_template('albums.html', albums=albumsInfo, IDs=albumIDs)

@app.route("/albums", methods=['POST'])
def album_post():
    print(str(request))
    global working_path
    if request.form.get('add album'):
        albums = getUserAlbums(flask_login.current_user.id)
        if albums == None:
            dir_create(working_path + "/{0}".format(getUsersId(flask_login.current_user.id)))
        addAlbum(request.form.get('add album'), flask_login.current_user.id)
        albumsInfo = []
        albumIDs = []
        albums = getUserAlbums(flask_login.current_user.id)
        for a in albums:
            albumsInfo.append(a[1])
            albumIDs.append(a[0])
        dir_create(working_path + "/{0}/{1}".format(
            getUsersId(flask_login.current_user.id),albumIDs[-1]))
        print(albumsInfo)
        print(albumIDs)
        return render_template('albums.html', albums=albumsInfo, IDs=albumIDs)

    if request.form:

        deleteAlbum(request.form['delete album'], flask_login.current_user.id)
        albums = getUserAlbums(flask_login.current_user.id)
        albumsInfo = []
        albumIDs = []
        if albums != None:
            for a in albums:
                albumsInfo.append(a[1])
                albumIDs.append(a[0])

        return render_template('albums.html', albums=albumsInfo, IDs=albumIDs)



@app.route('/upload', methods=['POST'])
@flask_login.login_required
def upload_file():
    global Photo_Tags
    global working_path
    albumid = request.args.get('album_id')
    UPLOAD_FOLDER = working_path + "/{0}/{1}".format(getUsersId(flask_login.current_user.id),
                                                                       albumid)
    photopath = "/static/{0}/{1}".format(getUsersId(flask_login.current_user.id), albumid)

    print(request.form)
    if request.form.get('add tag'):
        addTag(request.form.get('add tag'))
        addTagged(request.form.get('imgname'), flask_login.current_user.id, albumid)
        fname = os.listdir(UPLOAD_FOLDER)
        tags = getTagsFromCaption(request.form.get('imgname'))
        Photo_Tags[request.form.get('imgname')] = tags
        print(Photo_Tags)
        return render_template('upload.html', photopath=photopath, uid=str(getUsersId(flask_login.current_user.id)),
                                aid=albumid, fname=fname, tags=Photo_Tags)
    elif request.form.get('delete_photo', None) == "delete":
        print("helloworld")
        photoid = request.form.get('photoid')
        DeletePhoto(albumid, photoid)
        del Photo_Tags[photoid]
        print(Photo_Tags)
        print('55555555555555')
        fname = os.listdir(UPLOAD_FOLDER)

        return render_template('upload.html', photopath=photopath, uid=str(getUsersId(flask_login.current_user.id)),
                               aid=albumid, fname=fname, tags=Photo_Tags)
    else:
        dir_create(UPLOAD_FOLDER)
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        uploadfile = request.files['uploadFile']
        filename = uploadfile.filename
        fname = os.listdir(UPLOAD_FOLDER)
        if filename in getAllPhotoCaption():
            print('duplicate file name')
            return render_template('upload.html', photopath=photopath, uid=str(getUsersId(flask_login.current_user.id)),
                                   aid=albumid, fname=fname)
        else:
            uploadfile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            AddPhoto(albumid,filename)
            fname = os.listdir(UPLOAD_FOLDER)
            for f in fname:
                Photo_Tags[f] = getTagsFromCaption(f)
            print(Photo_Tags)
            return render_template('upload.html', photopath=photopath, uid=str(getUsersId(flask_login.current_user.id)),
                               aid=albumid, fname=fname, tags=Photo_Tags)

# E
@app.route('/upload', methods=['GET'])
@flask_login.login_required
def show_photo():
    global Photo_Tags, working_path
    print('66666666666666666666')
    albumid = request.args.get('album_id')
    photopath = "/static/{0}/{1}".format(getUsersId(flask_login.current_user.id), albumid)
    UPLOAD_FOLDER = working_path + "/{0}/{1}".format(
        getUsersId(flask_login.current_user.id), albumid)  ### CHANGE THIS
    print(UPLOAD_FOLDER)
    if not dir_create(UPLOAD_FOLDER):
        return render_template('upload.html')
    else:
       fname = os.listdir(UPLOAD_FOLDER)
       for f in fname:
           Photo_Tags[f] = getTagsFromCaption(f)
       print(Photo_Tags)
       print(os.getcwd())
       return render_template('upload.html', photopath=photopath, uid=getUsersId(flask_login.current_user.id),
                            aid=albumid, fname=fname, tags=Photo_Tags)


@app.route('/profile')
@flask_login.login_required
def protect3d():
    return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")

# default page
@app.route("/", methods=['GET'])
def hello():
    return render_template('login.html')


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
