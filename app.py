#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
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
#----------------------------------------------------------------------------#
from config import SQLALCHEMY_DATABASE_URI
from flask_migrate import Migrate
from models import db, Artist, Venue, Show


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')


# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

db.init_app(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    venues = []
    prev_city, prev_state = None, None
    time_now = datetime.now().strftime('%Y-%m-%d %H:%S:%M')

    for v in Venue.query.order_by(Venue.city, Venue.state).all():
        # Querying all shows of the current venue
        upcoming_shows = Show.query.filter(Show.venue_id == v.id).filter(
            Show.start_time > time_now).all()

        # Checking for duplicate city, state pairs
        if prev_city != None and prev_state != None:
            if v.city != prev_city or v.state != prev_state:
                # If new city, state pair is queried, append the prev pair
                data.append({
                    "city": prev_city,
                    "state": prev_state,
                    "venues": venues
                })

                venues = []

            venues.append({
                "id": v.id,
                "name": v.name,
                "num_upcoming_shows": len(upcoming_shows)
            })

        prev_city, prev_state = v.city, v.state

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    keyword = request.form.get('search_term')
    findings = Venue.query.filter(
        Venue.name.ilike("%{}%".format(keyword))).all()

    response = {"count": len(findings)}
    response["data"] = []
    time_now = datetime.now().strftime('%Y-%m-%d %H:%S:%M')

    for f in findings:
        upcoming_shows = Show.query.filter(Show.venue_id == f.id).filter(
            Show.start_time > time_now).all()

        response["data"].append({
            "id": f.id,
            "name": f.name,
            "num_upcoming_shows": len(upcoming_shows)
        })

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    time_now = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
    v = Venue.query.filter(Venue.id == venue_id).first()

    # PAST SHOWS DATA
    past_shows = Show.query.join(Artist).filter(Show.venue_id == v.id).filter(
        Show.start_time < time_now).all()
    past_shows_data = []
    for p in past_shows:
        past_shows_data.append({
            "artist_id": p.artists.id,
            "artist_name": p.artists.name,
            "artist_image_link": p.artists.image_link,
            "start_time": str(p.start_time)
        })

    # UPCOMING SHOWS DATA
    upcoming_shows = Show.query.join(Artist).filter(Show.venue_id == v.id).filter(
        Show.start_time > time_now).all()
    upcoming_shows_data = []
    for u in upcoming_shows:
        upcoming_shows_data.append({
            "artist_id": u.artists.id,
            "artist_name": u.artists.name,
            "artist_image_link": u.artists.image_link,
            "start_time": str(u.start_time)
        })

    data = {
        "id": v.id,
        "name": v.name,
        "genres": v.genres,
        "address": v.address,
        "city": v.city,
        "state": v.state,
        "phone": v.phone,
        "website": v.website,
        "facebook_link": v.facebook_link,
        "seeking_talent": v.seeking_talent,
        "seeking_description": v.seeking_description,
        "image_link": v.image_link,
        "past_shows": past_shows_data,
        "upcoming_shows": upcoming_shows_data,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')
    website = request.form.get('website')

    try:
        v = Venue(
            name=name, city=city, state=state,
            address=address, phone=phone, genres=genres,
            facebook_link=facebook_link, seeking_talent=True if(
                seeking_talent == "Yes") else False,
            seeking_description=seeking_description, website=website
        )
        db.session.add(v)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] +
              ' was successfully listed!')

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
        flash('An error occurred. Venue ' +
              form.name.data + ' could not be listed.')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
        # TODO: Complete this endpoint for taking a venue_id, and using
        # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    v = Venue.query.filter(Venue.id == venue_id).first()
    db.session.delete(v)
    db.session.commit()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = []

    for a in Artist.query.all():
        data.append({
            "id": a.id,
            "name": a.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    keyword = request.form.get('search_term')
    findings = Artist.query.filter(
        Artist.name.ilike("%{}%".format(keyword))).all()

    response = {"count": len(findings)}
    response["data"] = []
    time_now = datetime.now().strftime('%Y-%m-%d %H:%S:%M')

    for f in findings:
        upcoming_shows = Show.query.filter(Show.venue_id == f.id).filter(
            Show.start_time > time_now).all()

        response["data"].append({
            "id": f.id,
            "name": f.name,
            "num_upcoming_shows": len(upcoming_shows)
        })

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    time_now = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
    a = Artist.query.filter(Artist.id == artist_id).first()

    # PAST SHOWS DATA
    past_shows = Show.query.join(Venue).filter(Show.artist_id == a.id).filter(
        Show.start_time < time_now).all()
    past_shows_data = []
    for p in past_shows:
        past_shows_data.append({
            "venue_id": p.venues.id,
            "venue_name": p.venues.name,
            "venue_image_link": p.venues.image_link,
            "start_time": str(p.start_time)
        })

    # UPCOMING SHOWS DATA
    upcoming_shows = Show.query.join(Venue).filter(Show.artist_id == a.id).filter(
        Show.start_time > time_now).all()
    upcoming_shows_data = []
    for u in upcoming_shows:
        upcoming_shows_data.append({
            "venue_id": u.venues.id,
            "venue_name": u.venues.name,
            "venue_image_link": u.venues.image_link,
            "start_time": str(u.start_time)
        })

    data = {
        "id": a.id,
        "name": a.name,
        "genres": a.genres,
        "city": a.city,
        "state": a.state,
        "phone": a.phone,
        "website": a.website,
        "facebook_link": a.facebook_link,
        "seeking_venue": a.seeking_venue,
        "seeking_description": a.seeking_description,
        "image_link": a.image_link,
        "past_shows": past_shows_data,
        "upcoming_shows": upcoming_shows_data,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    # TODO: populate form with fields from artist with ID <artist_id>
    a = Artist.query.filter(Artist.id == artist_id).first()

    artist = {
        "id": a.id,
        "name": a.name,
        "genres": a.genres,
        "city": a.city,
        "state": a.state,
        "phone": a.phone,
        "website": a.website,
        "facebook_link": a.facebook_link,
        "seeking_venue": a.seeking_venue,
        "seeking_description": a.seeking_description,
        "image_link": a.image_link
    }

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.filter(Artist.id == artist_id).first()

    name = request.form.get('name')
    city = request.form.get('city')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website')
    seeking_venue = request.form.get('facebook_link')
    seeking_description = request.form.get('seeking_description')

    artist.name = name
    artist.city = city
    artist.phone = phone
    artist.genres = genres
    artist.facebook_link = facebook_link
    artist.website = website
    artist.seeking_venue = True if(
        seeking_venue == "Yes") else False
    artist.seeking_description = seeking_description

    db.session.commit()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    # TODO: populate form with values from venue with ID <venue_id>
    v = Venue.query.filter(Venue.id == venue_id).first()

    venue = {
        "id": v.id,
        "name": v.name,
        "genres": v.genres,
        "address": v.address,
        "city": v.city,
        "state": v.state,
        "phone": v.phone,
        "website": v.website,
        "facebook_link": v.facebook_link,
        "seeking_talent": v.seeking_talent,
        "seeking_description": v.seeking_description,
        "image_link": v.image_link
    }

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.filter(Venue.id == venue_id).first()

    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')

    venue.name = name
    venue.city = city
    venue.state = state
    venue.address = address
    venue.phone = phone
    venue.genres = genres
    venue.facebook_link = facebook_link
    venue.website = website
    venue.seeking_talent = True if(
        seeking_talent == "Yes") else False
    venue.seeking_description = seeking_description

    db.session.commit()

    return redirect(url_for('show_venue', venue_id=venue_id))

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

    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website')
    seeking_venue = request.form.get('seeking_venue')
    seeking_description = request.form.get('seeking_description')

    try:
        a = Artist(
            name=name, city=city, state=state,
            phone=phone, genres=genres,
            facebook_link=facebook_link, website=website, seeking_venue=True if(
                seeking_venue == "Yes") else False, seeking_description=seeking_description
        )

        db.session.add(a)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    except:
        flash('An error occurred. Artist ' +
              form.name.data + ' could not be listed.')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    shows = Show.query.join(Venue).join(Artist).all()
    data = []

    for s in shows:
        data.append({
            "venue_id": s.venues.id,
            "venue_name": s.venues.name,
            "artist_id": s.artist_id,
            "artist_name": s.artists.name,
            "artist_image_link": s.artists.image_link,
            "start_time": str(s.start_time)
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    try:
        a_id = request.form.get('artist_id')
        v_id = request.form.get('venue_id')
        start_time = request.form.get('start_time')

        s = Show(artist_id=a_id, venue_id=v_id, start_time=start_time)
        db.session.add(s)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed!')

    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Show could not be listed.')
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
