#!/usr/bin/env python

import sys
from correlation import pearson_similarity as pearson
import pymongo
from collections import defaultdict
import traceback
import model
from model import User

db = None

def movie_details(movie_id):
    movie = db.movies.find_one({"_id": movie_id})

    if not movie:
        print "No movie with id %d"%movie_id

    print """\
%d: %s
%s"""%(movie['_id'], movie['title'], ", ".join(movie['genres']))
    return """\
%d: %s
%s"""%(movie['_id'], movie['title'], ", ".join(movie['genres']))
    movie_d = []
    movie_d.append(movie['_id'])
    movie_d.append(movie['title'])    
    movie_d.append(movie['genres'])
    return movie_d
    # return """
    # %d: %s
    # %s"""%(movie['_id'], movie['title'], ", ".join(movie['genres']))
    pass


def movie_details_title(movie_title):
    movie = db.movies.find_one({"_title": title})

    if not movie:
        print "No movie with that title %s"%title

    print """\
%d: %s
%s"""%(movie['_id'], movie['title'], ", ".join(movie['genres']))
    return """\
%d: %s
%s"""%(movie['_id'], movie['title'], ", ".join(movie['genres']))
    movie_t = []
    movie_t.append(movie['title'])    
    movie_t.append(movie['genres'])
    return movie_t
    # return """
    # %d: %s
    # %s"""%(movie['_id'], movie['title'], ", ".join(movie['genres']))
    pass














def error(msg = "Unknown command"):
    print "Error:", msg

def quit():
    print "Goodbye!"
    sys.exit(0)

def average_rating(movie_id):
    rating_records = get_ratings(movie_id=movie_id)
    ratings = [ rec['rating'] for rec in rating_records ]
    avg = float(sum(ratings))/len(ratings)

    print "%.2f"%(avg)

def user_details(user_id):
    user = User.get(user_id)
    print user

def user_rating(movie_id, user_id):
    rating = get_rating(movie_id, user_id)
    if not rating:
        print "Sorry, user %d has not rated movie %d"%(user_id, movie_id)
        return
    movie = get_movie(movie_id)
    print "User %d rated movie %d (%s) at %d stars"%(\
            user_id, movie_id, movie['title'],
            rating)

def rate_movie(movie_id, rating):
    movie = get_movie(movie_id)
    db.ratings.update({"movie_id": movie_id, "user_id": 0},
            {"$set": {"rating": rating}}, upsert=True)
    print "You rated movie %d: %s at %d stars."%(\
            movie_id, movie['title'],
            rating)

def get_movie(movie_id):
    return db.movies.find_one(movie_id)

def get_ratings(movie_id=None, user_id=None):
    query = {}
    if movie_id is not None:
        query['movie_id'] = movie_id
    if user_id is not None:
        query['user_id'] = user_id

    records = db.ratings.find(query)
    return [ rec for rec in records ]
  
def get_rating(movie_id, user_id):
    record = db.ratings.find_one({"movie_id": movie_id, "user_id": user_id})
    if record:
        return record['rating']

def get_my_movies():
    ratings_user0 = get_ratings(user_id=0)
    rated_movies = []
    for record in ratings_user0:
        rated_movies.append(record['movie_id'])
    # print rated_movies
    return rated_movies

def convert_ratings_to_dict(list_of_ratings):
    # [ {uid: rating} ]
    movie_ratings = {}
    for rating in list_of_ratings:
        movie_ratings[rating['user_id']] = rating['rating']
    return movie_ratings

def get_all_rating_dicts(movie_ids):
    all_ratings = []
    for id in movie_ids:
        ratings = get_ratings(movie_id=id)
        rating_dict = convert_ratings_to_dict(ratings)
        all_ratings.append(rating_dict)
    return all_ratings

def predict(movie_id):
    ratings = get_ratings(movie_id=movie_id)
    target_movie = get_movie(movie_id)
   
    my_movie_ids = get_my_movies() #list of movies
    target_film_ratings = convert_ratings_to_dict(ratings)
    comparison_film_ratings = get_all_rating_dicts(my_movie_ids)
    similarities = []
    for base_movie in my_movie_ids:
        base_movie_ratings = convert_ratings_to_dict(get_ratings(movie_id=base_movie))
        # print "pearson score", pearson(target_film_ratings, base_movie_ratings)
        similarities.append((pearson(target_film_ratings, base_movie_ratings), get_rating(base_movie, 0)))
    similarities.sort()
    similarities.reverse()
    print "TYPE TWO", type(similarities)
    # top_five = similarities[-5:]
    num = 0.0
    den = 0.0
    # Use a weighted mean rather than a strict top similarity
    for sim, m in top_five:
        num += (float(sim) * m)
        den += sim
    rating = num/den
    print "Best guess for movie %d: %s is %.2f stars"%\
            (movie_id, target_movie['title'], rating)

def parse(line, dispatch):
    tokens = line.split()
    if not tokens:
        return error()

    cmd = tokens[0]
    command = dispatch.get(cmd)

    if not command:
        return error()
     
    if len(tokens) != len(command):
        return error("Invalid number of arguments")

    function = command[0]

    if len(command) == 1:
        return function()

    try:
        type_tuples = zip(command[1:], tokens[1:])
        typed_arguments = [ _type(arg) for _type, arg in type_tuples ]
        return function(*typed_arguments)

    except Exception, e:
        traceback.print_exc()
        return error("Invalid argument to %s"%(cmd))

def connect_db(host, port, user, password, db_name):
    connect_string = "mongodb://%s:%s@%s:%d/%s" % \
            (user, password, host, port, db_name)
    c = pymongo.connection.Connection(connect_string)
    print c[db_name]
    return c[db_name]
    
def main():
    global db
    # db = pymongo.connection.Connection("localhost")
    db = connect_db("dbh36.mongolab.com", 27367, "movie_user", "password", "movies")
    db = db['movies']
    model.db = db

    dispatch = {
            "movie": (movie_details, int),
            "q": (quit,),
            "avg": (average_rating, int),
            "user": (user_details, int),
            "rating": (user_rating, int, int),
            "rate": (rate_movie, int, int),
            "predict": (predict, int)
            }

    while True:
        line = raw_input("> ")
        parse(line, dispatch)
   
if __name__ == "__main__":
    main()
