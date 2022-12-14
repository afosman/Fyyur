#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import os
import json
from datetime import datetime
import logging
from logging import Formatter, FileHandler
import dateutil.parser
import babel

from flask import Flask,render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, Length, URL, Optional, ValidationError, Regexp
import phonenumbers

from forms import *
# from models import Artist, Venue, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
  

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(500), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False, nullable=True)
    seeking_description = db.Column(db.String(500), nullable=True)
    
    shows = db.relationship('Show', backref='venue', lazy=True)
    genres = db.Column(db.String(120))
    
    
    def __repr__(self):
      return f'<Venue id={self.id}, name={self.name}, state={self.state}, city={self.city}>'

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# Per my experience when the model was moved to a the models.py, it failed to
# to create the database tables in the db when `flask db migrate` and `flask db upgrade` are run

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False, nullable=True)
    seeking_description = db.Column(db.String(500),nullable=True)
    
    shows = db.relationship('Show', backref='artist', lazy=True)
    # venues = db.relationship('Venue', secondary=artists_venues, backref=db.backref('artists', lazy=True))
    genres = db.Column(db.String(120))
    
    def __repr__(self):
      return f'<Artist id={self.id}, name={self.name}, state={self.state}, city={self.city}>'


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime(timezone=True), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id  = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False) 
    
    def __repr__(self):
      return f'<Show id={self.id}, start_time={self.start_time}, venue_id={self.venue_id}, artist_id={self.artist_id}>'


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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = db.session.query(Venue).all()
  data = []
  
  if venues:
    states_cities = list(set((venue.state,venue.city) for venue in venues))
  
    time_now = datetime.now()
    
    # Populating the data by state and city
    for state_city in states_cities:
      state, city = state_city
      state_city_venues = db.session.query(Venue).filter_by(state=state,city=city).all()
      data.append({
        "city": city,
        "state": state,
        "venues": [{
          "id": scv.id,
          "name": scv.name,
          "num_upcoming_shows": db.session.query(Show).filter(Show.venue_id==scv.id).filter(Show.start_time > time_now).count()              
        } for scv in state_city_venues]
      })
    
    return render_template('pages/venues.html', areas=data)

    
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  time_now = datetime.now()
  response = {}
  if not search_term.strip():
    return redirect(url_for('venues'))  
    
  venues = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
    
  response = {
    "count": len(venues),
    "data": [
      {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time > time_now).count()
      } for venue in venues
    ]
  }
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  time_now = datetime.now()
  
  venue = db.session.query(Venue).get(venue_id)
  
  if not venue:
    flash(f'The venue does not exist')  
    return redirect(url_for('venues'))
  
  past_shows = db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time < time_now)
  upcoming_shows = db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time > time_now)
  
  data = {}
  data['id'] = venue.id
  data['name'] = venue.name
  data['genres'] = venue.genres.removeprefix('{').removesuffix('}').split(',')
  data['address'] = venue.address
  data['city'] = venue.city
  data['state'] = venue.state
  data['phone'] = venue.phone
  data['website'] = venue.website_link
  data['facebook_link'] = venue.facebook_link
  data['seeking_talent'] = venue.seeking_talent
  data['seeking_description'] = venue.seeking_description
  data['image_link'] = venue.image_link
  data['past_shows'] = [{
      "artist_id": ps.artist.id,
      "artist_name": ps.artist.name,
      "artist_image_link": ps.artist.image_link,
      "start_time": str(ps.start_time)
    } for ps in past_shows
  ]
  
  data['upcoming_shows'] = [{
      "artist_id": ps.artist.id,
      "artist_name": ps.artist.name,
      "artist_image_link": ps.artist.image_link,
      "start_time": str(ps.start_time)
    } for ps in upcoming_shows
  ]
  
  data['past_shows_count'] = past_shows.count()
  data['upcoming_shows_count'] = upcoming_shows.count()
  
  return render_template('pages/show_venue.html', venue=data)


  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  # print(f'{data=}')

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  form = VenueForm(request.form)

  if form.validate():
    # print("Form is valid")
    # To prevent duplicate venues
    venue = db.session.query(Venue).filter_by(name=form.name.data,address=form.address.data).all()
    
    if venue:
      flash(f'Venue with name {form.name.data} and {form.address.data} already exist.')
      return render_template('forms/new_venue.html',form = form)  
    
    else:      
      try:    
        data = form.data
        print(f'{data=}')
        new_venue = Venue(**data)

        # new_venue = Venue(
        #   name = request.form['name'],
        #   genres = request.form.getlist('genres'),
        #   address = request.form['address'],
        #   city = request.form['city'],
        #   state = request.form['state'],
        #   phone = request.form['phone'],
        #   website = request.form['website'],
        #   facebook_link = request.form['facebook_link'],
        #   seeking_talent = bool(request.form['seeking_talent']),
        #   seeking_description = request.form['seeking_description'],
        #   image_link = request.form['image_link']
        # )
        
        db.session.add(new_venue)  
        print("Added to session")
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('venues'))
      except Exception as exc:
        db.session.rollback()
        print(f"{exc=}")
        flash(f'An error occurred while creating venue {request.form["name"]}')
        return render_template('forms/new_venue.html', form=form)
      finally:
        db.session.close() 
      
  else:
    flash('Form not validated')
    flash(form.errors)
    return render_template('forms/new_venue.html',form=form)
            

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # return render_template('pages/home.html')
  return redirect(url_for('index'))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  
  try:
      venue = db.session.query(Venue).get(venue_id)
      # print(f"{venue!r}")
      db.session.delete(venue)
      db.session.commit()
      # flash("successfully deleted venue")
      response = jsonify({
        'status': 'success',
        'statusMessage': 'Successfully deleted Venue'
      })
              
  except:
      db.session.rollback()
      response = jsonify({
        'status': 'Error',
        'statusMessage': 'Could not delete Venue. An error occured!'
      })
      
  finally:
      db.session.close()   
           
  return response
  
  
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  venue = db.session.query(Venue).get(venue_id)
  if not venue:
    flash('The venue does not exist')  
    return redirect(url_for('venues'))
  
  form = VenueForm(formdata=request.form, obj=venue)
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

  # form = VenueForm()
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  venue = db.session.query(Venue).get(venue_id)
  if not venue:
    flash('The artist does not exist')  
    return redirect(url_for('venues'))
  
  form = VenueForm(formdata = request.form)

  if form.validate():
    try:
      print('form validated')
      # form.populate_obj(venue)
      genres = form.genres.data
      venue.genres = genres
      venue.facebook_link = form.facebook_link.data
      venue.website_link = form.website_link.data
      venue.name = form.name.data
      venue.address = form.address.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.phone = form.phone.data
      venue.image_link = form.image_link.data
      venue.seeking_description = form.seeking_description.data
      venue.seeking_talent = form.seeking_talent.data
      db.session.add(venue)
      db.session.commit()

      flash('Venue updated')
    except:
      flash(f'An exception occured. Venue could not be updated')
      db.session.rollback
      
    finally:
      db.session.close()
  else:
    print('form not validated')
    flash(form.errors)

  return redirect(url_for('show_venue', venue_id=venue_id))



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = db.session.query(Artist).all()
  data = [
    {
      "id": artist.id,
      "name": artist.name
    } for artist in artists
  ]
  
  return render_template('pages/artists.html', artists=data)

  
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term = request.form.get('search_term', '')
  time_now = datetime.now()
  response = {}
  if not search_term.strip():
    return redirect(url_for('artists'))  
    
  artists = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  
  response = {
    "count": len(artists),
    "data": [
      {
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": db.Session.query(Show).filter(Show.artist_id==artist.id).filter(Show.start_time > time_now).count()
      } for artist in artists
    ]
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

  
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  
  
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  time_now = datetime.now()
  
  artist = db.session.query(Artist).get(artist_id)
  
  if not artist:
    flash(f'The artist does not exist')  
    return redirect(url_for('artists'))
  
  data = {}
  
  data['id'] = artist.id
  data['name'] = artist.name
  data['genres'] = artist.genres.removeprefix('{').removesuffix('}').split(',')
  data['city'] = artist.city
  data['state'] = artist.state
  data['phone'] = artist.phone
  data['website'] = artist.website_link
  data['facebook_link'] = artist.facebook_link
  data['seeking_description'] = artist.seeking_description
  data['image_link'] = artist.image_link
  
  past_shows = db.session.query(Show).filter(Show.artist_id==artist.id).filter(Show.start_time < time_now)
  upcoming_shows = db.session.query(Show).filter(Show.artist_id==artist.id).filter(Show.start_time > time_now)
  
  
  data['past_shows'] = [{
      "venue_id": ps.venue.id,
      "venue_name": ps.venue.name,
      "venue_image_link": ps.venue.image_link,
      "start_time": str(ps.start_time)
    } for ps in past_shows
  ]
  
  data['upcoming_shows'] = [{
      "venue_id": ps.venue.id,
      "venue_name": ps.venue.name,
      "venue_image_link": ps.venue.image_link,
      "start_time": str(ps.start_time)
    } for ps in upcoming_shows
  ]
  
  data['past_shows_count'] = past_shows.count()
  data['upcoming_shows_count'] = upcoming_shows.count()

  return render_template('pages/show_artist.html', artist=data)

  
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]



#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = db.session.query(Artist).get(artist_id)
  if not artist:
    flash('The artist does not exist')  
    return redirect(url_for('artists'))
  
  form = ArtistForm(formdata=request.form, obj=artist)
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

  # form = ArtistForm()
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = db.session.query(Artist).get(artist_id)
  if not artist:
    flash('The artist does not exist')  
    return redirect(url_for('artists'))
  form = ArtistForm(formdata = request.form)

  if form.validate():
    try:
      print('form validated')
      # form.populate_obj(artist)
      genres = form.genres.data
      artist.genres = genres
      artist.facebook_link = form.facebook_link.data
      artist.website_link = form.website_link.data
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.image_link = form.image_link.data
      artist.seeking_description = form.seeking_description.data
      artist.seeking_venue = form.seeking_venue.data
      db.session.add(artist)
      db.session.commit()
      flash('artist updated')
    except Exception as exc:
      db.session.rollback
      print(f"{exc=}")
      
    finally:
      db.session.close()
  else:
    print('form not validated')
    flash(form.errors)

  return redirect(url_for('show_artist', artist_id=artist_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = ArtistForm(request.form)

  if form.validate():
    # print("Form is valid")
    # To prevent duplicate venues
    artist = db.session.query(Artist).filter_by(name=form.name.data).all()
    
    if artist:
      flash(f'artist with name {form.name.data} already exist.')
      return render_template('forms/new_artist.html',form = form)  
    
    else:      
      try:    
        data = form.data
        print(f'{data=}')
        new_artist = Artist(**data)
        
        db.session.add(new_artist)  
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
      except Exception as exc:
        db.session.rollback()
        # print(f"{exc=}")
        flash(f'An error occurred while creating artist {request.form["name"]}')
        return render_template('forms/new_artist.html', form=form)
      finally:
        db.session.close() 
      
  else:
    flash('Form not validated')
    flash(form.errors)
    return render_template('forms/new_artist.html',form=form)
          
  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = db.session.query(Show).all() # rewrite to order by date desc
  
  data = [
    {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    } for show in shows
  ]
  
  return render_template('pages/shows.html', shows=data)

  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  
  
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

   # DONE: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)

  if form.validate():
    try:
      # new_show = Show(venue_id = form.venue_id.data, artist_id = form.artist_id.data,
      #         start_time = form.start_time.data
      # )
      
      new_show = Show(**form.data)
      
      db.session.add(new_show)
      db.session.commit()
      
      # on successful db insert, flash success
      flash('Show was successfully listed!')
      
    except:
      db.session.rollback()
      flash('Error occurred. Show could not be listed!.')
      
    finally:
      db.session.close()

  else:
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Show could not be listed!')
    flash(form.errors)
    
  return render_template('pages/home.html')


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



# Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', debug=True,port=port)
