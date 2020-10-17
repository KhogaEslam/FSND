#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import traceback
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_migrate import Migrate
from sqlalchemy.sql.elements import Null
from sqlalchemy import func
from datetime import datetime

from temp.data_genre import data as data_genre
from temp.data_artist import data as data_artist
from temp.data_venue import data as data_venue
from temp.data_album import data as data_album
from temp.data_song import data as data_song
from temp.data_show import data as data_show
from forms import *
from temp import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
all_orphan = "all, delete-orphan"

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

venue_genre = db.Table('venue_genre',
    db.Column('venue_id', db.Integer, db.ForeignKey('venues.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

#----------------------------------------------------------------------------#

artist_genre = db.Table('artist_genre',
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

#----------------------------------------------------------------------------#

class Genre(db.Model):
  __tablename__ = 'genres'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, unique=True)

#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'venues'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String)
  state = db.Column(db.String)
  address = db.Column(db.String)
  phone = db.Column(db.String)
  image_link = db.Column(db.String)
  facebook_link = db.Column(db.String)
  website = db.Column(db.String)
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String)

  # each venu has many shows
  shows = db.relationship('Show', lazy=True, cascade=all_orphan, backref='venue')
  # each venue has many genres
  genres = db.relationship('Genre', secondary=venue_genre, lazy=True, backref=db.backref('venue', lazy=True))

#----------------------------------------------------------------------------#

class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)

  # middle table as a many-to-many relation between venus and artists
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)

#----------------------------------------------------------------------------#

class Artist(db.Model):
  __tablename__ = 'artists'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String)
  state = db.Column(db.String)
  phone = db.Column(db.String)
  image_link = db.Column(db.String)
  facebook_link = db.Column(db.String)
  website = db.Column(db.String)
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String)
  available_from = db.Column(db.DateTime, nullable=False)
  available_to = db.Column(db.DateTime, nullable=False)

  # each artist has many shows
  shows = db.relationship('Show', lazy=True, cascade=all_orphan, backref='artist')
  # each artist has many albums
  albums = db.relationship('Album', lazy=True, cascade=all_orphan, backref='artist')
  # each artist has many genres
  genres = db.relationship('Genre', secondary=artist_genre, lazy='subquery', backref=db.backref('artist', lazy=True))

#----------------------------------------------------------------------------#

class Album(db.Model):
  __tablename__ = 'albums'

  id = db.Column(db.Integer,primary_key=True)
  title = db.Column(db.String,nullable=False)

  # each album has one artist/band
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  # each album has many songs
  songs = db.relationship('Song', lazy=True, cascade=all_orphan, backref='album')

#----------------------------------------------------------------------------#

class Song(db.Model):
  __tablename__ = 'songs'

  id = db.Column(db.Integer,primary_key=True)
  name = db.Column(db.String,nullable=False)

  # each song has one album
  album_id = db.Column(db.Integer, db.ForeignKey('albums.id'), nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  new_format = format

  if format == 'full':
      new_format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      new_format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, new_format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

# Home
@app.route('/')
def index():
  data = {}

  recent_10_venues = Venue.query.limit(10).all()
  recent_10_artists = Artist.query.limit(10).all()

  data['venues'] = recent_10_venues
  data['artists'] = recent_10_artists

  return render_template('pages/home.html', data=data)

#  Venues
#  ----------------------------------------------------------------
#  ----------------------------------------------------------------

# List all...
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():

    venues = Venue.query.order_by('city', 'state', 'name').all()

    data = []
    location = {}

    previous_location = ''
    for venue in venues:
        current_location = venue.city + venue.state

        if current_location != previous_location:
            previous_location = current_location
            location = {
                'city': venue.city,
                'state': venue.state,
                'venues': []
            }

            data.append(location)

        upcoming_shows_count = Show.query.with_parent(venue).filter(Show.start_time > datetime.today()).count()

        location['venues'].append({
            'id': venue.id,
            'name': venue.name,
            'num_shows': upcoming_shows_count
        })

    return render_template('pages/venues.html', areas=data)

# Search...
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')

    venues = Venue.query.filter(func.lower(Venue.name).contains(func.lower(search_term))).all()

    response = {
        'count': len(venues),
        'data': venues
    }

    return render_template('pages/search_venues.html', results=response, search_term=search_term)

# details...
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.get(venue_id)

  if venue:
    shows = Show.query.with_parent(venue).all()

    venue.past_shows = []
    venue.upcoming_shows = []
    venue.past_shows_count = 0
    venue.upcoming_shows_count = 0

    for show in shows:
      if show.start_time < datetime.today():
          show.artist_id = show.artist.id
          show.artist_name = show.artist.name
          show.artist_image_link = show.artist.image_link
          show.start_time = show.start_time.strftime('%Y-%m-%dT%I:%M:%S.%sZ')
          venue.past_shows.append(show)
      else:
          show.artist_id = show.artist.id
          show.artist_name = show.artist.name
          show.artist_image_link = show.artist.image_link
          show.start_time = show.start_time.strftime('%Y-%m-%dT%I:%M:%S.%sZ')
          venue.upcoming_shows.append(show)

    venue.past_shows_count  = len(venue.past_shows)
    venue.upcoming_shows_count = len(venue.upcoming_shows)

  return render_template('pages/show_venue.html', venue=venue)

#  Create...
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    form = VenueForm(request.form)

    if form.validate():
        try:
            venue = Venue(
                      name=form.name.data,
                      image_link=form.image_link.data,
                      city=form.city.data,
                      state=form.state.data,
                      address=form.address.data,
                      phone=form.phone.data,
                      genres=form.genres.data,
                      seeking_talent=form.seeking_talent.data,
                      seeking_description=form.seeking_description.data,
                      website=form.website.data,
                      facebook_link=form.facebook_link.data
            )
            db.session.add(venue)
            db.session.commit()
            flash('Venue ' + venue.name + ' was successfully listed!')
        except Exception:
            db.session.rollback()
            traceback.print_exc()
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        finally:
            db.session.close()

    return render_template('pages/home.html')

#  Update...
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={}
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Delete...
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
#  ----------------------------------------------------------------

# List all...
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  return render_template('pages/artists.html', artists=data)

# Search...
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={}
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# Details...
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data1={}
  data2={}
  data3={}
  data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Create...
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

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')

#  Update...
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={}
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

#  Delete...
#  ----------------------------------------------------------------
@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a artist_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Artist on a Artist Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Shows
#  ----------------------------------------------------------------
#  ----------------------------------------------------------------

#  List all...
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  return render_template('pages/shows.html', shows=data)

#  Create...
#  ----------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

#  Errors
#  ----------------------------------------------------------------
#  ----------------------------------------------------------------

#  404
#  ----------------------------------------------------------------
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

#  500
#  ----------------------------------------------------------------
@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

#  Launch config
#  ----------------------------------------------------------------
#  ----------------------------------------------------------------
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

#----------------------------------------------------------------------------#
# Feeders.
#----------------------------------------------------------------------------#

def feed_genres():
  try:
    data = data_genre.data

    for val in data:
      genre = Genre(
                name = val.get('name', '')
              )

      db.session.add(genre)

    db.session.commit()
  except Exception:
    db.session.rollback()
    traceback.print_exc()
  finally:
    db.session.close()

#----------------------------------------------------------------------------#

def feed_artists():
  try:
    data = data_artist.data

    for val in data:
      artist = Artist(
                name = val.get('name', ''),
                city = val.get('city', ''),
                state = val.get('state', ''),
                phone = val.get('phone', ''),
                image_link = val.get('image_link', ''),
                facebook_link = val.get('facebook_link', ''),
                website = val.get('website', ''),
                seeking_venue = val.get('seeking_venue', False),
                seeking_description = val.get('seeking_description', ''),
                available_from = val.get('available_from', ''),
                available_to = val.get('available_to', '')
              )

      genres = val.get('genres')
      for genre_name in genres:
        genre = Genre.query.filter(func.lower(Genre.name).contains(func.lower(genre_name))).one()
        artist.genres.append(genre)

      db.session.add(artist)

    db.session.commit()
  except Exception:
    db.session.rollback()
    traceback.print_exc()
  finally:
    db.session.close()

#----------------------------------------------------------------------------#

def feed_venus():
  try:
    data = data_venue.data

    for val in data:
      venue = Venue(
                name =  val.get('name', ''),
                city =  val.get('city', ''),
                state = val.get('state', ''),
                address = val.get('address', ''),
                phone = val.get('phone', ''),
                image_link = val.get('image_link', ''),
                facebook_link = val.get('facebook_link', ''),
                website = val.get('website', ''),
                seeking_talent = val.get('seeking_talent', False),
                seeking_description = val.get('seeking_description', '')
              )

      genres = val.get('genres')
      for genre_name in genres:
        genre = Genre.query.filter(func.lower(Genre.name).contains(func.lower(genre_name))).one()
        venue.genres.append(genre)

      db.session.add(venue)

    db.session.commit()
  except Exception:
    db.session.rollback()
    traceback.print_exc()
  finally:
    db.session.close()

#----------------------------------------------------------------------------#

def feed_albums():
  try:
    data = data_album.data

    for val in data:
      album = Album(
                title = val.get('title', Null),
                artist_id = val.get('artist_id', Null)
              )

      db.session.add(album)

    db.session.commit()
  except Exception:
    db.session.rollback()
    traceback.print_exc()
  finally:
    db.session.close()

#----------------------------------------------------------------------------#

def feed_songs():
  try:
    data = data_song.data

    for val in data:
      song = Song(
              name = val.get('name', Null),
              album_id = val.get('album_id', Null)
            )

      db.session.add(song)

    db.session.commit()
  except Exception:
    db.session.rollback()
    traceback.print_exc()
  finally:
    db.session.close()

#----------------------------------------------------------------------------#

def feed_shows():
  try:
    data = data_show.data

    for val in data:
      show = Show(
              start_time = val.get('start_time', Null),
              artist_id = val.get('artist_id', Null),
              venue_id = val.get('venue_id', Null)
            )

      db.session.add(show)

    db.session.commit()
  except Exception:
    db.session.rollback()
    traceback.print_exc()
  finally:
    db.session.close()


# Feed DB with test data
@app.route('/feed_db')
def insert_test_data():
  if Genre.query.count() <= 0:
    feed_genres()
  if Artist.query.count() <= 0:
    feed_artists()
  if Venue.query.count() <= 0:
    feed_venus()
  if Album.query.count() <= 0:
    feed_albums()
  if Song.query.count() <= 0:
    feed_songs()
  if Show.query.count() <= 0:
    feed_shows()

  return 'Done Inserting  Data!', 200

#  ----------------------------------------------------------------