from app import db, Venue, Show, Artist

ven_data_1={
	"name": "The Musical Hop",
	"genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
	"address": "1015 Folsom Street",
	"city": "San Francisco",
	"state": "CA",
	"phone": "+233778909876",
	"website_link": "https://www.themusicalhop.com",
	"facebook_link": "https://www.facebook.com/TheMusicalHop",
	"seeking_talent": True,
	"seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
	"image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
}
 
  
ven_data_2={
	"name": "The Dueling Pianos Bar",
	"genres": ["Classical", "R&B", "Hip-Hop"],
	"address": "335 Delancey Street",
	"city": "New York",
	"state": "NY",
	"phone": "+145787598768",
	"website_link": "https://www.theduelingpianos.com",
	"facebook_link": "https://www.facebook.com/theduelingpianos",
	"seeking_talent": False,
	"image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
}
 

venue1 = Venue(**ven_data_1) 
venue2 = Venue(**ven_data_2) 

db.session.add(venue1)
db.session.add(venue2)
db.session.commit()

 
artist_data_1={
	"name": "Guns N Petals",
	"genres": ["Rock n Roll"],
	"city": "San Francisco",
	"state": "CA",
	"phone": "+145678908678",
	"website_link": "https://www.gunsnpetalsband.com",
	"facebook_link": "https://www.facebook.com/GunsNPetals",
	"seeking_venue": True,
	"seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
	"image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
}

artist_data_2={
	"name": "Matt Quevedo",
	"genres": ["Jazz"],
	"city": "New York",
	"state": "NY",
	"phone": "+8890876535790",
	"facebook_link": "https://www.facebook.com/mattquevedo923251523",
	"seeking_venue": False,
	"image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80", 
}

artist1 = Artist(**artist_data_1)
artist2 = Artist(**artist_data_2)
  
  
db.session.add(artist1)
db.session.add(artist2)
db.session.commit()  
 

 
show_data_1 = {
  "venue_id": venue1.id,
  "artist_id": artist1.id,
  "start_time": "2019-05-21T21:30:00.000Z"
}
    
show_data_2 = {
  "artist_id": venue1.id,
  "venue_id": artist2.id,
  "start_time": "2035-05-21T21:30:00.000Z"
}

show_data_3 = {
  "artist_id": artist1.id,
  "venue_id": venue1.id,
  "start_time": "2022-12-21T21:30:00.000Z"
}

show_data_4 = {
  "artist_id": artist2.id,
  "venue_id": venue1.id,
  "start_time": "2025-05-21T21:30:00.000Z"
}

show_data_5 = {
  "artist_id": artist2.id,
  "venue_id": venue2.id,
  "start_time": "2015-05-21T21:30:00.000Z"
}

show_data_6 = {
  "artist_id": artist1.id,
  "venue_id": venue2.id,
  "start_time": "2022-08-21T21:30:00.000Z"
}


	
show1 = Show(**show_data_1)
show2 = Show(**show_data_2)
show3 = Show(**show_data_3)
show4 = Show(**show_data_4)
show5 = Show(**show_data_5)
show6 = Show(**show_data_6)

  
db.session.add(show1)
db.session.add(show2)
db.session.add(show3)
db.session.add(show4)
db.session.add(show5)
db.session.add(show6)
db.session.commit()
  