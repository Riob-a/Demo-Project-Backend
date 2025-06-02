#!/usr/bin/env python3

from models import db, User, Artwork, Contact
from flask import Flask
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Drop all tables and recreate them to ensure a clean slate
    db.drop_all()
    db.create_all()

    # Seed Users
    user1 = User(username="john_doe", email="john@example.com")
    user1.set_password("password123")
    user2 = User(username="jane_doe", email="jane@example.com")
    user2.set_password("password456")

    # Add users to the session
    db.session.add_all([user1, user2])

    # Seed Artworks with new images
    artworks =[ 
    Artwork(
        name="Raging Fury",
        email="artist1@example.com",
        style="animated",
        image_url="https://i.pinimg.com/originals/db/5a/54/db5a547a554cfaebfcb48aa1e8462918.gif",
        description="Description of this piece"
    ),

     Artwork(
        name="StandART II",
        email="artist2@example.com",
        style="animated",
        image_url="https://i.pinimg.com/originals/47/51/a5/4751a5150b14cab7056a8a0d72576e5a.gif",
        description="nosce te ipsum"
    ),

    Artwork(
        name="lh3.googleusercontent.com",
        email="artist3@example.com",
        style="animated",
        image_url="https://i.pinimg.com/originals/b2/d7/fd/b2d7fddd6261a9fcd9327645ded6209f.gif",
        description="Description of artwork 3"
    ),

    Artwork(
        name="BUCK",
        email="artist4@example.com",
        style="animated",
        image_url="https://i.pinimg.com/originals/99/ee/d3/99eed3289b336e484f5b4bb182630d36.gif",
        description="BUCK is a global creative company that brings brands, stories, and experiences to life through art, design, and technology."
    ),

    Artwork(
        name="Lights 0NN",
        email="artist5@example.com",
        style="animated",
        image_url="https://i.pinimg.com/originals/a3/7e/48/a37e48e6e5e0edb1b2ffbee6a73fbd59.gif",
        description="Description of artwork 5"
    ),

    Artwork(
        name="Freeform Portland",
        email="artist6@example.com",
        style="animated",
        image_url="https://i.pinimg.com/originals/91/04/aa/9104aa39381fec0c1fb54346e3700ddc.gif",
        description="Description of artwork 6"
    ),

    Artwork(
        name="Richard Brandão",
        email="artist7@example.com",
        style="static",
        image_url="https://i.pinimg.com/564x/e1/12/ce/e112cec116c02f617870067cbed7649a.jpg",
        description="69 Artworks by Richard Brandão, Saatchi Art Artist"
    ),

    Artwork(
        name="Pictoplasma",
        email="artist8@example.com",
        style="animated",
        image_url="https://i.pinimg.com/originals/48/3f/be/483fbebfa30d9d506715307a9de897b1.gif",
        description="I'm watching you! Pictoplasma #CharacterStareDown entry"
    ),

    Artwork(
        name="A-na5/ｱ_ﾅ",
        email="artist9@example.com",
        style="animated",
        image_url="https://i.pinimg.com/originals/91/56/64/9156644ae1ddcbc1756330c5f25ef067.gif",
        description="Flowtype"
    ),

    # Regular Artworks
    Artwork(
        name="Muted f-1",
        email="artist10@example.com",
        style="static",
        image_url="https://i.pinimg.com/enabled_hi/564x/5d/bd/00/5dbd006f8a7323e95215c70712e79d29.jpg",
        description="Speed of green"
    ),

    Artwork(
        name="Perspective",
        email="artist11@example.com",
        style="static",
        image_url="https://i.pinimg.com/enabled_hi/564x/ff/72/9d/ff729d47356e1c9d83eb210318a3b2a8.jpg",
        description="Soy tantas personas, emociones susurrando un mismo nombre"
    ),

    Artwork(
        name="A-I",
        email="artist12@example.com",
        style="static",
        image_url="https://i.pinimg.com/enabled_hi/564x/dd/9e/6b/dd9e6b3417414eff234c837202bc02ca.jpg",
        description="AI theme"
    ),

    Artwork(
        name="Halftone",
        email="artist13@example.com",
        style="static",
        image_url="https://i.pinimg.com/736x/8b/d7/b8/8bd7b883b210468739db1bff92822dbf.jpg",
        description="close-up of stacked halftone overlays on a BMW"
    ),

    Artwork(
        name="Smoking Kills 1",
        email="artist14@example.com",
        style="static",
        image_url="https://i.pinimg.com/736x/0a/18/27/0a1827e9238aaf70a295153757c1a393.jpg",
        description="smoking kills michael schumacher"
    ),

    Artwork(
        name="Smoking Kills 2",
        email="artist15@example.com",
        style="static",
        image_url="https://i.pinimg.com/enabled_hi/564x/ab/68/86/ab68861f180d341161e5e69082b9d974.jpg",
        description="Smoking kills"
    ),

    Artwork(
        name="911",
        email="artist16@example.com",
        style="static",
        image_url="https://i.pinimg.com/enabled_hi/564x/12/c2/25/12c225b47a96bf8b2fdb62811caff5a3.jpg",
        description="Description of artwork 7"
    ),

    Artwork(
        name="Speedster posterwork",
        email="artist17@example.com",
        style="static",
        image_url="https://i.pinimg.com/enabled_hi/564x/9c/fe/01/9cfe017fd0ad40807f79fead11415e3d.jpg",
        description="Speedster"
    ),
]

    # Add all artworks to the session
    db.session.add_all(artworks)

    # Seed Contacts
    contacts = [
        Contact(
            name="Alice Smith",
            email="alice@example.com",
            message="Interested in your artwork collection!"
        ),
        Contact(
            name="Bob Johnson",
            email="bob@example.com",
            message="Could you provide more details on your art styles?"
        )
    ]

    # Add contacts to the session
    db.session.add_all(contacts)
    db.session.commit()

    # Commit all data to the database
    db.session.commit()

    print("Database seeded with users, artworks, and contacts successfully!")
