#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import traceback
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
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

def log_form_errors(errors):
  for fieldName, errorMessages in errors:
      print(fieldName)
      for err in errorMessages:
        print(err)

def get_home_data():
  data = {}

  recent_10_venues = Venue.query.limit(10).all()
  recent_10_artists = Artist.query.limit(10).all()

  data['venues'] = recent_10_venues
  data['artists'] = recent_10_artists

  return data

def get_genres():
  genres = Genre.query.all()
  genre_names = []
  if genres:
    for genre in genres:
      genre_names.append(genre.name)
  
  return list(enumerate(genre_names))

def get_genres_ids(genres):
  ids = []
  for genre in genres:
    ids.append(genre.id)
  return ids

def set_venue_form_data(form, venue):
  form.genres.choices = get_genres()
  form.genres.data = get_genres_ids(venue.genres)
  form.name.data = venue.name
  form.image_link.data = venue.image_link
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.website.data = venue.website
  form.facebook_link.data = venue.facebook_link

def set_artist_form_data(form, artist):
  form.genres.choices = get_genres()
  form.genres.data = get_genres_ids(artist.genres)
  form.name.data = artist.name
  form.image_link.data = artist.image_link
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.website.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.available_from.data = artist.available_from
  form.available_to.data = artist.available_to

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

# Home
#  ----------------------------------------------------------------
#  ----------------------------------------------------------------

# List all...
#  ----------------------------------------------------------------

@app.route('/')
def index():

  return render_template('pages/home.html', data=get_home_data())

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
  form.genres.choices = get_genres()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  error = False
  form = VenueForm(request.form)
  form.genres.choices = get_genres()

  if form.validate_on_submit():
    try:
        venue = Venue(
                  name=form.name.data,
                  image_link=form.image_link.data,
                  city=form.city.data,
                  state=form.state.data,
                  address=form.address.data,
                  phone=form.phone.data,
                  seeking_talent=form.seeking_talent.data,
                  seeking_description=form.seeking_description.data,
                  website=form.website.data,
                  facebook_link=form.facebook_link.data
        )
        genres = form.genres.data
        for genre_id in genres:
          genre = Genre.query.get(genre_id)
          venue.genres.append(genre)

        db.session.add(venue)
        db.session.commit()

    except Exception as e:
      error = e
      db.session.rollback()
      traceback.print_exc()
    finally:
      db.session.close()

    if not error:
      flash('Venue ' + form.name.data + ' was successfully listed!')
    else:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

    return render_template('pages/home.html', data=get_home_data())

  else:
    log_form_errors(form.errors.items())

  return render_template('forms/new_venue.html', form=form)

#  Update...
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm()
  set_venue_form_data(form, venue)
  form.submit.name = 'Update Venue'

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  form = VenueForm(request.form)
  form.genres.choices = get_genres()

  venue = Venue.query.get(venue_id)

  if form.validate_on_submit():
    try:
        venue.name=form.name.data
        venue.image_link=form.image_link.data
        venue.city=form.city.data
        venue.state=form.state.data
        venue.address=form.address.data
        venue.phone=form.phone.data
        venue.seeking_talent=form.seeking_talent.data
        venue.seeking_description=form.seeking_description.data
        venue.website=form.website.data
        venue.facebook_link=form.facebook_link.data

        genres = form.genres.data
        for genre_id in genres:
          genre = Genre.query.get(genre_id)
          venue.genres.append(genre)

        db.session.commit()

    except Exception as e:
      error = e
      db.session.rollback()
      traceback.print_exc()
    finally:
      db.session.close()

    if not error:
      flash('Venue ' + form.name.data + ' was successfully updated!')
    else:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')

    return redirect(url_for('show_venue', venue_id=venue_id))

  else:
    log_form_errors(form.errors.items())

  return render_template('forms/edit_venue.html', form=form, venue=venue)

#  Delete...
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False

    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except Exception as e:
        error = e
        db.session.rollback()
        traceback.print_exc()
    finally:
        db.session.close()

    if error:
        return server_error(error)
    else:
        return jsonify({ 'success': True })

#  Artists
#  ----------------------------------------------------------------
#  ----------------------------------------------------------------

# List all...
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()

  return render_template('pages/artists.html', artists=artists)

# Search...
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')

  artist = Artist.query.filter(func.lower(Venue.name).contains(func.lower(search_term))).all()

  response = {
      'count': len(artist),
      'data': artist
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# Details...
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.get(artist_id)

  if artist:
    shows = Show.query.with_parent(artist).all()

    artist.available_from = artist.available_from.strftime('%Y-%m-%dT%I:%M:%S.%sZ')
    artist.available_to = artist.available_to.strftime('%Y-%m-%dT%I:%M:%S.%sZ')

    artist.past_shows = []
    artist.upcoming_shows = []
    artist.past_shows_count = 0
    artist.upcoming_shows_count = 0

    for show in shows:
      if show.start_time < datetime.today():
          show.artist_id = show.artist.id
          show.artist_name = show.artist.name
          show.venue_image_link = show.venue.image_link
          show.start_time = show.start_time.strftime('%Y-%m-%dT%I:%M:%S.%sZ')
          artist.past_shows.append(show)
      else:
          show.artist_id = show.artist.id
          show.artist_name = show.artist.name
          show.venue_image_link = show.venue.image_link
          show.start_time = show.start_time.strftime('%Y-%m-%dT%I:%M:%S.%sZ')
          artist.upcoming_shows.append(show)

    artist.past_shows_count  = len(artist.past_shows)
    artist.upcoming_shows_count = len(artist.upcoming_shows)

  return render_template('pages/show_artist.html', artist=artist)

#  Create...
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():

  form = ArtistForm()
  form.genres.choices = get_genres()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  error = False
  form = ArtistForm(request.form)
  form.genres.choices = get_genres()

  if form.validate_on_submit():
    try:
        artist = Artist(
                  name=form.name.data,
                  image_link=form.image_link.data,
                  city=form.city.data,
                  state=form.state.data,
                  phone=form.phone.data,
                  seeking_venue=form.seeking_venue.data,
                  seeking_description=form.seeking_description.data,
                  website=form.website.data,
                  facebook_link=form.facebook_link.data,
                  available_from=form.available_from.data,
                  available_to=form.available_to.data
        )
        genres = form.genres.data
        for genre_id in genres:
          genre = Genre.query.get(genre_id)
          artist.genres.append(genre)

        db.session.add(artist)
        db.session.commit()

    except Exception as e:
      error = e
      db.session.rollback()
      traceback.print_exc()
    finally:
      db.session.close()

    if not error:
      flash('Artist ' + form.name.data + ' was successfully listed!')
    else:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

    return render_template('pages/home.html', data=get_home_data())

  else:
    log_form_errors(form.errors.items())

  return render_template('forms/new_artist.html', form=form)

#  Update...
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm()
  set_artist_form_data(form, artist)
  form.submit.name = 'Update Artist'

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  form = ArtistForm(request.form)
  form.genres.choices = get_genres()

  artist = Artist.query.get(artist_id)

  if form.validate_on_submit():
    try:
        artist.name=form.name.data
        artist.image_link=form.image_link.data
        artist.city=form.city.data
        artist.state=form.state.data
        artist.phone=form.phone.data
        artist.seeking_venue=form.seeking_venue.data
        artist.seeking_description=form.seeking_description.data
        artist.website=form.website.data
        artist.facebook_link=form.facebook_link.data
        artist.available_from=form.available_from.data
        artist.available_to=form.available_to.data

        genres = form.genres.data
        for genre_id in genres:
          genre = Genre.query.get(genre_id)
          artist.genres.append(genre)

        db.session.commit()

    except Exception as e:
      error = e
      db.session.rollback()
      traceback.print_exc()
    finally:
      db.session.close()

    if not error:
      flash('Artist ' + form.name.data + ' was successfully updated!')
    else:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')

    return redirect(url_for('show_artist', artist_id=artist_id))

  else:
    log_form_errors(form.errors.items())

  return render_template('forms/edit_artist.html', form=form, artist=artist)

#  Delete...
#  ----------------------------------------------------------------
@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  error = False

  try:
      artist = Artist.query.get(artist_id)
      db.session.delete(artist)
      db.session.commit()
  except Exception as e:
      error = e
      db.session.rollback()
      traceback.print_exc()
  finally:
      db.session.close()

  if error:
    return server_error(error)
  else:
    return jsonify({ 'success': True })

#  Shows
#  ----------------------------------------------------------------
#  ----------------------------------------------------------------

#  List all...
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  shows = Show.query.order_by(Show.start_time).all()

  for show in shows:
      show.venue_name = show.venue.name
      show.artist_name = show.artist.name
      show.artist_image_link = show.artist.image_link
      show.start_time = show.start_time.strftime('%Y-%m-%dT%I:%M:%S.%sZ')

  return render_template('pages/shows.html', shows=shows)

#  Create...
#  ----------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  error = False
  form = ShowForm(request.form)

  if form.validate_on_submit():
    artist = Artist.query.get(form.artist_id.data)
    venue = Venue.query.get(form.venue_id.data)

    if not artist:
        flash('Artist not found')
        error = True
    else:
        if artist.available_from and artist.available_to:
            if form.start_time.data > artist.available_to or form.start_time.data < artist.available_from:
                error = True
                flash('Artist not available at this time, check his availability!')

    if not venue:
        flash('Venue not found!')
        error = True

    try:
        show = Show(
          start_time=form.start_time.data,
          artist_id=form.artist_id.data,
          venue_id=form.venue_id.data
        )

        db.session.add(show)
        db.session.commit()

    except Exception as e:
      error = e
      db.session.rollback()
      traceback.print_exc()
    finally:
      db.session.close()

    if not error:
      flash('Show was successfully listed!')
    else:
      flash('An error occurred. Show could not be listed.')

    return render_template('pages/home.html', data=get_home_data())

  else:
    log_form_errors(form.errors.items())

  return render_template('forms/new_show.html', form=form)

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