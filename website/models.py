from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

kosik = db.Table('kosik',
    db.Column('uzivatel_id', db.Integer, db.ForeignKey('uzivatel.id')),
    db.Column('food_id', db.Integer, db.ForeignKey('food.id')),
    db.Column('quantity', db.Integer, default=1)  
)

nabidka = db.Table('nabidka',
    db.Column('uzivatel_id', db.Integer, db.ForeignKey('uzivatel.id')),
    db.Column('food_id', db.Integer, db.ForeignKey('food.id')), 
)

objednani = db.Table('objednani',
    db.Column('objednavka_id', db.Integer, db.ForeignKey('objednavka.id')),
    db.Column('jidlo.id', db.Integer, db.ForeignKey('food.id'))
    )

class Uzivatel(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    firstName = db.Column(db.String(150))
    lastName = db.Column(db.String(150))
    password = db.Column(db.String(150))
    role_typ = db.Column(db.String(150), db.ForeignKey('role.typ_role'))
    dorucene_objednavky = db.relationship('Objednavka')
    kosik = db.relationship('Food', secondary = kosik, backref='kosik')
    nabidka = db.relationship('Food', secondary = nabidka, backref='nabidka')

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(255), nullable = False)
    objednavka_id = db.Column(db.Integer, db.ForeignKey('objednavka.id'))

class Restaurace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nazev = db.Column(db.String(150))
    email  = db.Column(db.String(150))
    telefon = db.Column(db.String(150))
    adresa = db.Column(db.String(150))
    password = db.Column(db.String(150))

class Doruceni(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stav_objednavky = db.Column(db.String(150), default = "Čeká na zpracování")
    doruceni_adresa = db.Column(db.String(255),nullable = True)
    uzivatel_id = db.Column(db.Integer, db.ForeignKey('uzivatel.id'))
    poslicek_id = db.Column(db.Integer, db.ForeignKey('uzivatel.id'))
    
    
class Objednavka(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datum_objednani = db.Column(db.DateTime(timezone=True), default=func.now())
    cena = db.Column(db.Float())
    zpusob_platby = db.Column(db.String(150))
    uzivatel_id = db.Column(db.Integer, db.ForeignKey('uzivatel.id'))
    doruceni_id = db.Column(db.Integer, db.ForeignKey('doruceni.id'))
    restaurace_id = db.Column(db.Integer, db.ForeignKey('restaurace.id'))  
    foods = db.relationship('Food')
    doruceni = db.relationship('Doruceni', backref='objednavky', foreign_keys=[doruceni_id])
    restaurace = db.relationship('Restaurace', backref='objednavky', foreign_keys=[restaurace_id])  


class Role(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    typ_role = db.Column(db.String(150), nullable = False)
    uzivatele = db.relationship('Uzivatel')
