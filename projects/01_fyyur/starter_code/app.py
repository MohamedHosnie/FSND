#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, and_
from flask_migrate import Migrate
import logging
import sys
import time
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='venue', lazy=True, cascade='all, delete-orphan')

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='artist', lazy=True, cascade='all, delete-orphan')

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)
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
  groups = db.session.query(
    Venue.city, 
    Venue.state
    ).group_by(
      Venue.city, 
      Venue.state
      ).all()

  data = []
  for group in groups:
    r_group = {}
    r_group['city'] = group.city
    r_group['state'] = group.state
    r_group['venues'] = db.session.query(
      Venue.id,
      Venue.name,
      func.count(Show.id).label('num_upcoming_shows')
    ).filter_by(
      city = group.city, 
      state = group.state
      ).join(Show, 
        and_(Show.start_time > datetime.now(), Venue.id == Show.venue_id),
        isouter=True
      ).group_by(
        Venue.id, 
        Venue.name
        ).all()

    data.append(r_group)
  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST', 'GET'])
def search_venues():
  response = {}
  term = request.form.get('search_term', '')
  data = []

  if term == '':
    data = db.session.query(
      Venue.id,
      Venue.name,
      func.count(Show.id).label('num_upcoming_shows')
      ).join(Show, 
        and_(Show.start_time > datetime.now(), Venue.id == Show.venue_id),
        isouter=True
      ).group_by(
        Venue.id, 
        Venue.name
        ).all()
  else:
    data = db.session.query(
      Venue.id,
      Venue.name,
      func.count(Show.id).label('num_upcoming_shows')
      ).filter(Venue.name.ilike("%"+term+"%")
      ).join(Show,
        and_(Show.start_time > datetime.now(), Venue.id == Show.venue_id),
        isouter=True
      ).group_by(
        Venue.id,
        Venue.name
        ).all()

  response['count'] = len(data)
  response['data'] = data
  return render_template('pages/search_venues.html', results=response, search_term=term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  data = db.session.query(Venue).get(venue_id)
  if data is None: abort(404)

  if data.genres is None:
    data.genres = []
  else:
    data.genres = data.genres.split(',')

  data.past_shows = db.session.query(
    Show.artist_id,
    Artist.name.label("artist_name"),
    Artist.image_link.label("artist_image_link"),
    Show.start_time
    ).join(Artist
    ).filter(
      Show.venue_id == data.id,
      Show.start_time <= datetime.now()
      ).all()
  data.upcoming_shows = db.session.query(
    Show.artist_id,
    Artist.name.label("artist_name"),
    Artist.image_link.label("artist_image_link"),
    Show.start_time
    ).join(Artist
    ).filter(
      Show.venue_id == data.id,
      Show.start_time > datetime.now()
      ).all()
  data.past_shows_count = len(data.past_shows)
  data.upcoming_shows_count = len(data.upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  form = VenueForm()
  if not form.validate_on_submit():
    flash('Validation error. Venue could not be created.', 'danger')
    return render_template('forms/new_venue.html', form=form)

  try:
    data = Venue(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      address = request.form.get('address'),
      phone = request.form.get('phone'),
      genres = ','.join(request.form.getlist('genres')),
      image_link = request.form.get('image_link'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website'),
      seeking_talent = bool(request.form.get('seeking_talent', False)),
      seeking_description = request.form.get('seeking_description'),
    )

    db.session.add(data)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + data.name + ' was successfully listed!', 'success')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + data.name + ' could not be listed.', 'danger')
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()

  if error:
    return render_template('forms/new_venue.html', form=form)
  else:
    return redirect(url_for('show_venue', venue_id = data.id))

@app.route('/venues/<int:venue_id>', methods=['DELETE', 'POST'])
def delete_venue(venue_id):
  error = False
  try:
    venue = db.session.query(Venue).get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted!', 'success')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be deleted.', 'danger')
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()

  if error:
    return redirect(url_for('show_venue', venue_id = venue_id))
  else:
    return redirect(url_for('venues'))

#  Update Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = db.session.query(Venue).get(venue_id)
  if venue is None:
    abort(400)

  if venue.genres is None:
    venue.genres = []
  else:
    venue.genres = venue.genres.split(',')
    
  form = VenueForm(obj=venue)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False

  venue = db.session.query(Venue).get(venue_id)
  if venue is None:
    abort(400)

  form = VenueForm()
  if not form.validate_on_submit():
    flash('Validation error. Venue could not be updated.', 'danger')
    return render_template('forms/edit_venue.html', form=form, venue=venue)

  try:
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.genres = ','.join(request.form.getlist('genres'))
    venue.image_link = request.form.get('image_link')
    venue.facebook_link = request.form.get('facebook_link')
    venue.website = request.form.get('website')
    venue.seeking_talent = bool(request.form.get('seeking_talent', False))
    venue.seeking_description = request.form.get('seeking_description')

    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully updated!', 'success')
  except:
    db.session.rollback()
    flash('An error occurred. Venue could not be updated.', 'danger')
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()

  if error:
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  else:
    return redirect(url_for('show_venue', venue_id = venue_id))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = db.session.query(
      Artist.id,
      Artist.name,
      func.count(Show.id).label('num_upcoming_shows')
      ).join(Show, 
        and_(Show.start_time > datetime.now(), Artist.id == Show.artist_id),
        isouter=True
      ).group_by(
        Artist.id, 
        Artist.name
        ).all()
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST', 'GET'])
def search_artists():
  response = {}
  term = request.form.get('search_term', '')
  data = []

  if term == '':
    data = db.session.query(
      Artist.id,
      Artist.name,
      func.count(Show.id).label('num_upcoming_shows')
      ).join(Show,
        and_(Show.start_time > datetime.now(), Artist.id == Show.artist_id),
        isouter=True
      ).group_by(
        Artist.id, 
        Artist.name
        ).all()
  else:
    data = db.session.query(
      Artist.id,
      Artist.name,
      func.count(Show.id).label('num_upcoming_shows')
      ).filter(Artist.name.ilike("%"+term+"%")
      ).join(Show,
        and_(Show.start_time > datetime.now(), Artist.id == Show.artist_id),
        isouter=True
      ).group_by(
        Artist.id, 
        Artist.name
        ).all()

  response['count'] = len(data)
  response['data'] = data
  return render_template('pages/search_artists.html', results=response, search_term=term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  data = db.session.query(Artist).get(artist_id)
  if data is None: abort(404)

  if data.genres is None:
    data.genres = []
  else:
    data.genres = data.genres.split(',')

  data.past_shows = db.session.query(
    Show.venue_id,
    Venue.name.label("venue_name"),
    Venue.image_link.label("venue_image_link"),
    Show.start_time
    ).join(Venue
    ).filter(
      Show.artist_id == data.id,
      Show.start_time <= datetime.now()
      ).all()
  data.upcoming_shows = db.session.query(
    Show.venue_id,
    Venue.name.label("venue_name"),
    Venue.image_link.label("venue_image_link"),
    Show.start_time
    ).join(Venue
    ).filter(
      Show.artist_id == data.id,
      Show.start_time > datetime.now()
      ).all()
  data.past_shows_count = len(data.past_shows)
  data.upcoming_shows_count = len(data.upcoming_shows)

  return render_template('pages/show_artist.html', artist=data)

#  Create Artists
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  form = ArtistForm()
  if not form.validate_on_submit():
    flash('Validation error. Artist could not be created.', 'danger')
    return render_template('forms/new_artist.html', form=form)

  try:
    data = Artist(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      phone = request.form.get('phone'),
      genres = ','.join(request.form.getlist('genres')),
      image_link = request.form.get('image_link'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website'),
      seeking_venue = bool(request.form.get('seeking_venue', False)),
      seeking_description = request.form.get('seeking_description'),
    )

    db.session.add(data)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + data.name + ' was successfully listed!', 'success')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + data.name + ' could not be listed.', 'danger')
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()

  if error:
    return render_template('forms/new_artist.html', form=form)
  else:
    return redirect(url_for('show_artist', artist_id = data.id))

@app.route('/artists/<int:artist_id>', methods=['DELETE', 'POST'])
def delete_artist(artist_id):
  error = False
  try:
    artist = db.session.query(Artist).get(artist_id)
    db.session.delete(artist)
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully deleted!', 'success')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + artist.name + ' could not be deleted.', 'danger')
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()

  if error:
    return redirect(url_for('show_artist', artist_id = artist_id))
  else:
    return redirect(url_for('artists'))

#  Update Artists
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = db.session.query(Artist).get(artist_id)
  if artist is None:
    abort(400)

  if artist.genres is None:
    artist.genres = []
  else:
    artist.genres = artist.genres.split(',')

  form = ArtistForm(obj=artist)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False

  artist = db.session.query(Artist).get(artist_id)
  if artist is None:
    abort(400)

  form = ArtistForm()
  if not form.validate_on_submit():
    flash('Validation error. Artist could not be updated.', 'danger')
    return render_template('forms/edit_artist.html', form=form, artist=artist)

  try:
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = ','.join(request.form.getlist('genres'))
    artist.image_link = request.form.get('image_link')
    artist.facebook_link = request.form.get('facebook_link')
    artist.website = request.form.get('website')
    artist.seeking_venue = bool(request.form.get('seeking_venue', False))
    artist.seeking_description = request.form.get('seeking_description')

    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully updated!', 'success')
  except:
    db.session.rollback()
    flash('An error occurred. Artist could not be updated.', 'danger')
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()
  
  if error:
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  else:
    return redirect(url_for('show_artist', artist_id = artist_id))


#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  # displays list of shows at /shows

  data = db.session.query(
    Show.venue_id,
    Venue.name.label("venue_name"),
    Show.artist_id,
    Artist.name.label("artist_name"),
    Artist.image_link.label("artist_image_link"),
    Show.start_time
  ).join(Venue).join(Artist).all()

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  form = ShowForm()
  if not form.validate_on_submit():
    flash('Validation error. Show could not be listed.', 'danger')
    return render_template('forms/new_show.html', form=form)

  artist = db.session.query(Artist).get(request.form.get('artist_id'))
  venue = db.session.query(Venue).get(request.form.get('venue_id'))

  if artist is None or venue is None:
    flash('You entered a wrong Artist or Venue ID.', 'danger')
    return render_template('forms/new_show.html', form=form)

  try:
    data = Show(
      start_time = request.form.get('start_time')
    )

    data.artist = artist
    data.venue = venue

    db.session.add(data)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!', 'success')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.', 'danger')
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()
  
  if error:
    return render_template('forms/new_show.html', form=form)
  else:
    return redirect(url_for('shows'))


#  Error Handling
#  ----------------------------------------------------------------
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
