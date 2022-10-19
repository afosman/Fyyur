# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()


# class Venue(db.Model):
#     __tablename__ = 'Venue'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     city = db.Column(db.String(120))
#     state = db.Column(db.String(120))
#     address = db.Column(db.String(120))
#     phone = db.Column(db.String(120))
#     image_link = db.Column(db.String(500))
#     facebook_link = db.Column(db.String(120))

#     # TODO: implement any missing fields, as a database migration using Flask-Migrate
#     website_link = db.Column(db.String(500), nullable=True)
#     seeking_talent = db.Column(db.Boolean, default=False, nullable=True)
#     seeking_description = db.Column(db.String(500), nullable=True)
    
#     shows = db.relationship('Show', backref='venue', lazy=True)
#     genres = db.Column(db.String(120))
    
    
#     def __repr__(self):
#       return f'<Venue id={self.id}, name={self.name}, state={self.state}, city={self.city}>'


# class Artist(db.Model):
#     __tablename__ = 'Artist'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     city = db.Column(db.String(120))
#     state = db.Column(db.String(120))
#     phone = db.Column(db.String(120))
#     # genres = db.Column(db.String(120))
#     image_link = db.Column(db.String(500))
#     facebook_link = db.Column(db.String(120))

#     # TODO: implement any missing fields, as a database migration using Flask-Migrate
#     website_link = db.Column(db.String(120), nullable=True)
#     seeking_venue = db.Column(db.Boolean, default=False, nullable=True)
#     seeking_description = db.Column(db.String(500),nullable=True)
    
#     shows = db.relationship('Show', backref='artist', lazy=True)
#     # venues = db.relationship('Venue', secondary=artists_venues, backref=db.backref('artists', lazy=True))
#     genres = db.Column(db.String(120))
    
#     def __repr__(self):
#       return f'<Artist id={self.id}, name={self.name}, state={self.state}, city={self.city}>'


# # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# class Show(db.Model):
#     __tablename__ = 'Show'
#     id = db.Column(db.Integer, primary_key=True)
#     start_time = db.Column(db.DateTime(timezone=True), nullable=False)
#     venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
#     artist_id  = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False) 
    
#     def __repr__(self):
#       return f'<Show id={self.id}, start_time={self.start_time}, venue_id={self.venue_id}, artist_id={self.artist_id}>'



