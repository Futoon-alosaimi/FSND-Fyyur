#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(255), nullable=True)
    shows = db.relationship('Show', backref='Venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(255), nullable=True)
    shows = db.relationship('Show', backref='Artist', lazy=True)

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    start_time = db.Column(db.DateTime(), nullable=False)    

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data=[]
  venues = Venue.query.all()
  for venue in venues:

    data.append({
      "city" : venue.city ,
      "state" : venue.state ,
      "venues" : [{
        "id" : venue.id,
        "name" : venue.name 
      }]
    })

  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  data = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  venue=[]
  for i in data:
    venue.append({
      "id":i.id,
      "name": i.name
    })
    
  response={
    "count": len(data),
    "data": venue
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue1=Venue.query.get(venue_id)
  past_shows =[]
  upcoming_shows = []
  shows=Show.query.filter_by(venue_id=venue_id).all()

  for show in shows:

    if start_time_obj(show.start_time) < datetime.now():


     past_shows.append({
     "venue_id": show.venue_id,
     "Venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
     "Venue_image_link":Venue.query.filter_by(id=show.venue_id).first().image_link ,
     "start_time": format_datetime(str(show.start_time)) })
    else:
      upcoming_shows.append({
       "venue_id": show.venue_id,
     "Venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
     "Venue_image_link":Venue.query.filter_by(id=show.venue_id).first().image_link ,
     "start_time": format_datetime(str(show.start_time)) })
  

  data = {
    "id": venue1.id,
    "name": venue1.name,
    "genres": venue1.genres ,
    "address": venue1.address,
    "city": venue1.city,
    "state": venue1.state,
    "phone": venue1.phone,
    "website": venue1.website,
    "facebook_link": venue1.facebook_link,
    "image_link":venue1.image_link ,
    "past_shows":past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }


 
  return render_template('pages/show_venue.html', venue=data)





#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
   form = VenueForm()
   
   try:
      data = Venue(
           name=request.form['name'],
           city=request.form['city'],
           state=request.form['state'],
           address=request.form['address'],
           phone=request.form['phone'],
          genres=request.form.getlist('genres'),
          facebook_link=request.form['facebook_link']
              
        )
      db.session.add(data)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
   except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
    
   finally:
    db.session.close()

 
  
 
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback() 
  finally:
    db.session.close()
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=[]
  artists = Artist.query.all()
  for ar in artists:

    data.append({
      "id" : ar.id ,
      "name" : ar.name ,
    })


  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  data = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  ar=[]
  for i in data:
    ar.append({
      "id":i.id,
      "name": i.name
    })
    
  response={
    "count": len(data),
    "data": ar
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist1 = Artist.query.get(artist_id)
  past_shows =[]
  upcoming_shows = []
  shows=Show.query.filter_by(artist_id=artist_id).all()

  for show in shows:

    if start_time_obj(show.start_time) < datetime.now():

     past_shows.append({
     "artist_id": show.artist_id,
     "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
     "artist_image_link":Artist.query.filter_by(id=show.artist_id).first().image_link ,
     "start_time": format_datetime(str(show.start_time)) })
    else:
      upcoming_shows.append({
      "artist_id": show.artist_id,
     "artist_id": Artist.query.filter_by(id=show.artist_id).first().name,
     "artist_id":Artist.query.filter_by(id=show.artist_id).first().image_link ,
     "start_time": format_datetime(str(show.start_time)) })

  data = {
    "id": artist1.id,
    "name": artist1.name,
    "genres": artist1.genres ,
    "city": artist1.city,
    "state": artist1.state,
    "phone": artist1.phone,
    "website": artist1.website,
    "facebook_link": artist1.facebook_link,
    "image_link":artist1.image_link ,
    "past_shows":past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
     }   
  
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
      data = Artist(
           name=request.form['name'],
           city=request.form['city'],
           state=request.form['state'],
           phone=request.form['phone'],
          genres=request.form.getlist('genres'),
          facebook_link=request.form['facebook_link']
              
        )
      db.session.add(data)
      db.session.commit()
      flash('Artist  ' + request.form['name'] + ' was successfully listed!')
    except:
      flash('An error occurred. Artist  ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
      print(sys.exc_info())
    
    finally:
     db.session.close()
     return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data=[]
  shows = Show.query.all()

  for show in shows:

    
    data.append({
    "venue_id": show.venue_id,
    "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
    "artist_id": show.artist_id,
    "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
    "artist_image_link":Artist.query.filter_by(id=show.artist_id).first().image_link ,
    "start_time": format_datetime(str(show.start_time)) })
 
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
 form = ShowForm()

 try:
   data = Show(
     artist_id = request.form['artist_id'],
     venue_id = request.form['venue_id'],
     start_time=request.form['start_time'],
      )
   
   db.session.add(data)
   db.session.commit()
   flash('Show was successfully listed!')
 except:
   flash('An error occurred Show could not be listed.')
   db.session.rollback()
   print(sys.exc_info())
    
 finally:
   db.session.close()
   return render_template('pages/home.html')

def start_time_obj(start_time):
    formatted_date = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    return formatted_date




@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
