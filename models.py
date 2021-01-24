import dateutil.parser
import babel
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Show Table


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)

    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id'))

    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'))

    start_time = db.Column(db.DateTime, nullable=True,
                           default="2021-01-23 21:36:22")


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
    genres = db.Column(db.ARRAY(db.String(50)))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.Text)

    # shows relation
    shows = db.relationship('Show', backref='venues', lazy=True)

    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}>'


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

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_venue = db.Column(db.Boolean)
    website = db.Column(db.String(500))
    seeking_description = db.Column(db.Text)

    # shows relation
    shows = db.relationship('Show', backref='artists', lazy=True)

    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
