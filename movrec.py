import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import movies
import pymongo
import model
#global db

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

@app.before_request
def before_request():
	global db
	db = movies.connect_db("dbh36.mongolab.com", 27367, "movie_user", "password", "movies")
	db = db['movies']
	model.db = db
	movies.db = db #assign variable in the other py file

@app.route('/')
def show_movies():
	movie = movies.get_my_movies() #return a list 
	my_details = [] 
	for movie_id in movie:
		movie_d = movies.get_movie(movie_id) #return dictionary 
		my_details.append(movie_d) #append to a list called my_details
	return render_template('show_movies.html', details=my_details)
	#my_details matches with app.route, "details" matches with show_movies.html's jinja names

#works for searching the db by movie id number
# @app.route('/search',methods=['POST'])
# def search_movie():
# 	search = request.form['search']
# 	return movies.movie_details(int(search))

#trying to make it searchable by movie title word
@app.route('/search',methods=['POST'])
def search_movie():
	search = request.form['search']
	return movies.movie_details(int(search))

# @app.route('/top_movies', methods=['GET'])
# def top_movies():
	# show movies that was rated before 
	# get all movie ids in db
	# calculate in database and then just call that calculation.  too much processing
	#to do on command
	# for movie in movie_list:
	# 	average_rating = movies.average_rating(456)
	# rating_list = []
	# # get all their average rating
	# for movie_id in average_rating:
	# 	movie_r = movies.average_rating(movie_id)
	# 	rating_list.append(movie_r)
	# top_movies = rating_list[:10]
	# return render_template('top_movies.html', rating=top_movies)
	# return render_template('home.html')
	# pass

# @app.route('/recommend', methods=['GET'])
# def recommended_movies():
# 	# return top X movies for the user based on what she rated before
# 	pass
# 	# return render_template('')

if __name__ == "__main__":
	app.run(debug=True)