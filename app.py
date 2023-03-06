######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
import numpy as np
import operator
import collections

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'NOcap122020!'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	supressText = request.args.get('supress') != 'False'
	return render_template('register.html', supress=supressText)

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		first_name=request.form.get('firstName')
		last_name=request.form.get('lastName')
		date_of_birth=request.form.get('DOB')
		gender=request.form.get('gender')
		hometown=request.form.get('hometown')
		
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Users (email, password, first_name, last_name, date_of_birth, gender, hometown) VALUES ('{0}', '{1}', '{2}', '{3}','{4}', '{5}', '{6}')".format(email, password, first_name, last_name, date_of_birth, gender, hometown)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("email not unique")
		return flask.redirect(flask.url_for('register', supress=False))

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		album = request.form.get('albums')
		photo_data =imgfile.read()
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Pictures (imgdata, user_id, caption, album_id) VALUES (%s, %s, %s, %s )''', (photo_data, uid, caption, album))
		update_contribution(uid)
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid), base64=base64)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		cursor = conn.cursor()
		cursor.execute('''SELECT album_id, album_name FROM Albums WHERE user_id=%s''', (uid))
		albums = cursor.fetchall()
		return render_template('upload.html', albums=albums)
#end photo uploading code

@app.route('/create_album', methods=['GET', 'POST'])
@flask_login.login_required
def create_album():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		album_name=request.form.get('album-name')
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Albums (album_name, user_id) VALUES (%s, %s)''', (album_name, uid))
		conn.commit()
		return  flask.redirect(flask.url_for("create_album"))
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		cursor = conn.cursor()
		cursor.execute('''SELECT album_name FROM Albums WHERE user_id=%s''', (uid))
		albums = cursor.fetchall()
		return render_template('createalbum.html', albums=albums)

@app.route("/friends", methods=['GET', 'POST'])
@flask_login.login_required
def friends():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		friend = getUserIdFromEmail(request.form.get('friend-email'))
		if notFriends(uid, friend):
			cursor = conn.cursor()
			cursor.execute('''INSERT INTO Friends (userID1, userID2) VALUES (%s, %s)''',(uid, friend))
			conn.commit()
			return flask.redirect(flask.url_for("friends"))
		else:
			return flask.redirect(flask.url_for("friends", error='True'))
	else:
		recommendations = getRecommendedFriends(uid)
		print(recommendations)
		error = request.args.get('error') == 'True'
		uid = getUserIdFromEmail(flask_login.current_user.id)
		cursor = conn.cursor()
		cursor.execute('''SELECT first_name, last_name, email FROM Friends INNER JOIN Users ON userID2=user_id WHERE userID1=%s
''', (uid))
		friends = cursor.fetchall()
		return render_template('friends.html', error=error, friends=friends, recommendations=recommendations)

def notFriends(userID1, userID2):
	cursor = conn.cursor()
	cursor.execute('''SELECT * FROM Friends WHERE userID1=%s AND userID2=%s''',(userID1, userID2))
	if len(cursor.fetchall()) == 0:
		return True
	return False

@app.route('/galary', methods=['GET'])
def galary():
	cursor = conn.cursor()
	cursor.execute('''SELECT album_id, album_name FROM Albums''')
	albums = cursor.fetchall()
	print(albums)
	return render_template('galary.html', albums=albums, base64=base64)

@app.route('/album/<album_id>', methods=['GET'])
def album(album_id):
	cursor = conn.cursor()
	cursor.execute('''SELECT imgdata,caption,picture_id FROM Pictures WHERE album_id=%s''', (album_id))
	photos = cursor.fetchall()
	return render_template('view_album.html', photos=photos, base64=base64)
	
@app.route('/user_albums', methods=['GET', 'POST'])
@flask_login.login_required
def user_albums():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		album_id = request.form.get("albums")
		print(album_id)
		cursor = conn.cursor()
		cursor.execute('''DELETE FROM Albums WHERE album_id=%s''', (album_id))
		conn.commit()
		return flask.redirect(flask.url_for('user_albums'))
	else:
		cursor = conn.cursor()
		cursor.execute('''SELECT album_id, album_name FROM Albums WHERE user_id=%s''', (uid))
		albums = cursor.fetchall()
		return render_template('user_albums.html', albums=albums)

@app.route('/user_albums/<album_id>', methods=['GET', 'DELETE'])
@flask_login.login_required
def manage_user_album(album_id): 
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		picture_id = request.form.get("picture_id")
		cursor = conn.cursor()
		cursor.execute('''DELETE FROM Pictures WHERE picture_id=%s''', (picture_id))
		conn.commit()
		return flask.redirect('/user_albums/{}'.format(album_id))
	else:
		cursor = conn.cursor()
		cursor.execute('''SELECT imgdata,caption FROM Pictures WHERE album_id=%s''', (album_id))
		photos = cursor.fetchall()
	return render_template('user_album.html', photos=photos,  base64=base64)

def isPhotoOfCurrentUser(uid, pid):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Pictures WHERE picture_id = '{0}'".format(pid))
	picture_uid = cursor.fetchone()[0]
	return picture_uid == uid

def getPicture(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, caption, picture_id FROM Pictures WHERE picture_id = '{0}'".format(pid))
	return cursor.fetchone()

@app.route("/photo/<pid>", methods=['GET'])
def get_single_photo(pid=-1):
	assert pid != -1
	if request.method == 'GET':
		photo = getPicture(pid)
		if flask_login.current_user.id == -1 or not isPhotoOfCurrentUser(getUserIdFromEmail(flask_login.current_user.id), pid):
			return render_template('singlePhotoView.html', photo=photo,base64=base64)
		else:
			return render_template('singlePhotoView.html', photo=photo,base64=base64)

#begin code for tags management
@app.route("/photos", methods=['GET','POST'])
@flask_login.login_required
def get_all_user_photos():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'GET':
		return render_template('photosView.html', photos=getUsersPhotos(uid),tags=getTop10Tags(),base64=base64)
	else:
		tags = request.form.get('tags')
		return render_template('photosView.html', photos=getUsersPhotosByTags(uid,tags),tags=getTop10Tags(),base64=base64)


@app.route("/all_photos/<tags>", methods=['GET'])
def get_all_photos_by_tags(tags=""):
	assert tags != None or tags != ""
	return render_template('allPhotosView.html', photos=getAllPhotosByTags(tags),tags=getTop10Tags(),base64=base64)

@app.route("/all_photos", methods=['GET','POST'])
def get_all_photos():
	if request.method == 'GET':
		return render_template('allPhotosView.html', photos=getAllPhotos(),tags=getTop10Tags(),base64=base64)
	else:
		tags = request.form.get('tags')
		return render_template('allPhotosView.html', photos=getAllPhotosByTags(tags),tags=getTop10Tags(),base64=base64)

@app.route("/photos/<tags>", methods=['GET'])
def get_all_user_photos_by_tags(tags=""):
	assert tags != None or tags != ""
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('photosView.html', photos=getUsersPhotosByTags(uid,tags),tags=getTop10Tags(),base64=base64)
	
#end code for tags management

#functions for tags management
def getTop10Tags():
	cursor = conn.cursor()
	cursor.execute("SELECT tag_word FROM Tags ORDER BY num_used DESC LIMIT 10")    #Tags table must have a num_used column for this to work
	return cursor.fetchall()

def getUsersPhotosByTags(uid, tags):
	t=tags.split(',')
	cursor = conn.cursor()
	photos = []
	for tag in t:
		cursor.execute("""
						SELECT imgdata, picture_id FROM Pictures pics 
						WHERE EXISTS (SELECT * FROM Tagged tg INNER JOIN
               							Tags t ON t.tag_id = tg.tag_id
              						    WHERE pics.picture_id = tg.picture_id
                                        AND t.tag_word = '{0}' AND pics.user_id = '{1}')
					   """.format(tag,uid))
		photos+=cursor.fetchall()
	final = [photo for photo, count in collections.Counter(photos).items() if count == len(t)] 
	return final

def getAllPhotosByTags(tags):
	t=tags.split(',')
	cursor = conn.cursor()
	photos = []
	for tag in t:
		cursor.execute("""
						SELECT imgdata, picture_id FROM Pictures pics 
						WHERE EXISTS (SELECT * FROM Tagged tg INNER JOIN
               							Tags t ON t.tag_id = tg.tag_id
              						  WHERE pics.picture_id = tg.picture_id
                                       AND t.tag_word = '{0}')
					   """.format(tag))
		photos+=cursor.fetchall()
	final = [photo for photo, count in collections.Counter(photos).items() if count == len(t)] 
	return final

def getAllPhotos():
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id FROM Pictures")
	return cursor.fetchall() 

# start of comment code

@app.route("/comment/<picture_id>", methods=['GET', 'POST'])
def leave_comment(picture_id):
	if request.method == 'GET':
		error = request.args.get('error') == 'True'
		cursor = conn.cursor()
		cursor.execute('''SELECT comment_text FROM Comments WHERE picture_id=%s''', (picture_id))
		comments = cursor.fetchall()
		return render_template("comments.html", picture_id=picture_id, comments=comments, error=error, likes=current_likes(picture_id))
	else:
		cursor = conn.cursor()
		comment = request.form.get('comment')
		if flask_login.current_user.is_authenticated:
			uid = getUserIdFromEmail(flask_login.current_user.id)
			if checkPictureIsNotUsers(uid, picture_id):
				update_contribution(uid)
				cursor.execute('''INSERT INTO Comments (comment_text, user_id, picture_id) VALUES (%s, %s, %s)''', (comment, uid, picture_id))
			else:
				return flask.redirect("/comment/{0}?error={1}".format(picture_id,'True'))
		else:	
			cursor.execute('''INSERT INTO Comments (comment_text, picture_id) VALUES (%s, %s)''', (comment, picture_id))	
		conn.commit()
		return flask.redirect("/comment/{}".format(picture_id))

def checkPictureIsNotUsers(uid, picture_id):
	cursor = conn.cursor()
	cursor.execute('''SELECT caption FROM Pictures WHERE user_id=%s AND picture_id=%s''', (uid, picture_id))
	picture = cursor.fetchall()
	return len(picture) != 1

#end of comment code

#start of like code

@app.route("/like/<picture_id>", methods=['POST'])
@flask_login.login_required
def like(picture_id):
	cursor = conn.cursor()
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor.execute('''INSERT INTO Likes (picture_id, user_id) VALUES (%s, %s)''', (picture_id, uid))
	conn.commit()
	return flask.redirect(url_for('galary'))

def current_likes(picture_id):
	cursor = conn.cursor()
	cursor.execute('''SELECT first_name, last_name FROM Users INNER JOIN Likes ON Likes.user_id=Users.user_id WHERE picture_id=%s''', (picture_id))
	return cursor.fetchall()
# end of like code

# start of contribution score code
@app.route("/leaderboard", methods=['GET'])
def leaderboard():
	cursor = conn.cursor()
	cursor.execute('''SELECT first_name, last_name, contributionScore FROM Users ORDER BY contributionScore DESC LIMIT 10''')
	leaderboard=cursor.fetchall()
	return render_template('leaderboard.html', leaderboard=leaderboard)

def update_contribution(user_id):
	cursor = conn.cursor()
	cursor.execute('''UPDATE Users SET contributionScore = contributionScore + 1 WHERE user_id=%s''', (user_id))
	conn.commit()
# end of contribution score code



#start of you may like recommendation code
@app.route("/recommendations", methods=['GET'])
@flask_login.login_required
def get_top_recommended_photos():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('recommendation.html', recommendations=getTopYouMayLike(uid), base64 =base64)

#The function returns a list of dictionaries, where each dictionary represents a recommended picture with its ID, 
# the number of matched tags, and the total number of tags. The pictures are ranked by the number of matched tags in 
# descending order and the total number of tags in ascending order.
def getTopYouMayLike(uid):
    cursor = conn.cursor()
    # Create a temporary table containing the picture IDs for the user's photos
    cursor.execute("""SELECT p.picture_id, p.imgdata, COUNT(*) AS matched_tags, COUNT(pt.tag_id) AS total_tags
FROM Pictures p
INNER JOIN Tagged pt ON pt.picture_id = p.picture_id
INNER JOIN Tags t ON t.tag_id = pt.tag_id
INNER JOIN (
    SELECT pt2.tag_id, COUNT(*) AS num_tags
    FROM Tagged pt2
    INNER JOIN Pictures p2 ON pt2.picture_id = p2.picture_id
    WHERE p2.user_id = '{0}'
    GROUP BY pt2.tag_id
    ORDER BY num_tags DESC
    LIMIT 3
) top_tags ON t.tag_id = top_tags.tag_id
GROUP BY p.picture_id, p.imgdata
HAVING matched_tags > 0
ORDER BY matched_tags DESC, total_tags ASC
LIMIT 10;
    """.format(uid))
    output = cursor.fetchall()

    # Convert the query results to a list of dictionaries
    recommendations = []
    for row in output:
        recommendations.append(    #picture_id, img_data, matched_tags, total_tags
            [row[0], row[1], row[2], row[3]]
        )

    print(len(recommendations))
    return recommendations



#end of you may like recommendation code



# start of friend recommendations
def getRecommendedFriends(user_id):
	cursor = conn.cursor()
	cursor.execute('''SELECT userID2 FROM Friends WHERE userID1=%s''', (user_id))
	friends = cursor.fetchall()
	friendsDict = {}
	for friend in friends:
		cursor.execute('''SELECT userID2 FROM Friends WHERE userID1=%s''', (friend[0]))
		keyFriends = cursor.fetchall()
		friendsDict[friend[0]] = keyFriends
	finalIntersect = ()
	for tup in friendsDict:
		if finalIntersect == ():
			finalIntersect = friendsDict[tup]
		else:
			finalIntersect = tuple(set(finalIntersect).intersection(set(friendsDict[tup])))
	recommendedIDs = []
	for value in finalIntersect:
		if value[0] != user_id:
			recommendedIDs.append(value[0])
	friendsList = []
	for id in recommendedIDs:
		cursor.execute('''SELECT first_name, last_name, email FROM Users WHERE user_id=%s''', (id))
		friendInfo = cursor.fetchall()
		friendsList.append(friendInfo[0])
	return friendsList
# end of friend recommendations

# start of comment search
@app.route("/comment_search", methods=['GET', 'POST'])
def comment_search():
	if request.method == "GET":
		return render_template('searchComments.html')
	else:
		comment = request.form.get("comment-input")
		cursor = conn.cursor()
		cursor.execute('''SELECT first_name, last_name FROM Users INNER JOIN Comments ON Users.user_id=Comments.user_id WHERE Comments.comment_text=%s''', (comment))
		users = cursor.fetchall()
		commentDict = {}
		for user in users:
			name = user[0]+" "+user[1]
			if name in commentDict:
				commentDict[name] += 1
			else:
				commentDict[name] = 1
		sortedUsers = sorted(commentDict.items(), key=operator.itemgetter(1),reverse=True)
		return render_template('searchComments.html', comments=sortedUsers)
# end of comment search

#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
