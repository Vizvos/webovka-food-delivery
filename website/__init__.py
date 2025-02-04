from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from datetime import datetime
import pytz

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ajdasdfäsdf-¨-a¨sdfa2asfa312a'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # Blueprinty
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Modely databáze
    from .models import Uzivatel, Role, Restaurace, Objednavka, Food, Doruceni

    with app.app_context():
        # Vytvoření tabulek v databázi
        db.create_all()

        # Naplnění databáze jídelním lístkem
        db.session.query(Food).delete()  # Smazání stávajících dat
        db.session.commit()

        extended_menu = [
            {"name": "Svíčková na smetaně", "description": "Tradiční česká svíčková omáčka s hovězím masem, houskovými knedlíky a brusinkami.", "image": "static/images/svica.jpg", "category": "maso", "price": 250 },
            {"name": "Vepřo knedlo zelo", "description": "Vepřová pečeně s houskovým knedlíkem a dušeným kysaným zelím.", "image": "static/images/veproknedlozelo.jpg", "category": "maso", "price": 220 },
            {"name": "Kuřecí řízek s bramborovým salátem", "description": "Klasický smažený kuřecí řízek podávaný s bramborovým salátem.", "image": "static/images/rizek_salat.jpg", "category": "maso", "price": 180 },
            {"name": "Guláš s houskovým knedlíkem", "description": "Hovězí guláš s cibulí, česnekem a paprikou podávaný s houskovými knedlíky.", "image": "static/images/gulas_s_knedlikem.jpg", "category": "maso", "price": 200},
            {"name": "Koprová omáčka s hovězím masem", "description": "Koprová omáčka na smetaně, hovězí maso a houskový knedlík.", "image": "static/images/kopr_omacka.jpg", "category": "maso", "price": 190 },
            {"name": "Špagety Carbonara", "description": "Italské špagety s krémovou omáčkou, pancettou a parmazánem.", "image": "static/images/spagety_carbonara.jpg", "category": "maso;testoviny", "price": 210 },
            {"name": "Hovězí burger s hranolky", "description": "Šťavnatý hovězí burger v domácí housce, podávaný s hranolky.", "image": "static/images/burger_hranolky.jpg","category": "maso", "price": 230 },
            {"name": "Pizza Margherita", "description": "Pizza s rajčatovým základem, mozzarellou a čerstvou bazalkou.", "image": "static/images/pizza_margherita.jpg","category": "vegetarianske", "price": 190 },
            {"name": "Caesar salát", "description": "Čerstvý římský salát s kuřecím masem, krutony a parmazánem.", "image": "static/images/caesar_salat.jpg","category": "vegetarianske;salat", "price": 170 },
            {"name": "Losos na grilu", "description": "Grilovaný losos s bylinkovým máslem a pečenými brambory.", "image": "static/images/losos_gril.jpg","category": "maso", "price": 270},
            {"name": "Krémová brokolicová polévka", "description": "Hustá polévka z čerstvé brokolice, smetany a sýra.", "image": "static/images/brokolicova_polevka.jpg","category": "vegetarianske;polevka", "price": 60},
            {"name": "Palačinky s čokoládou", "description": "Lahodné palačinky plněné čokoládovým krémem, podávané s ovocem.", "image": "static/images/palacinky_cokolada.jpg","category": "desert", "price": 150 },
            {"name": "Vegetariánská pizza", "description": "Pizza s rajčatovým základem, čerstvou zeleninou a mozzarellou.", "image": "static/images/vegetarianska_pizza.jpg","category": "vegetarianske", "price": 200},
            {"name": "Houbové rizoto", "description": "Krémové rizoto s lesními houbami a parmazánem.", "image": "static/images/houbove_rizoto.jpg","category": "vegetarianske", "price": 190 },
            {"name": "Pstruh na másle", "description": "Grilovaný pstruh podávaný s citronem a dušenou zeleninou.", "image": "static/images/pstruh_na_masle.jpg","category": "maso", "price": 250 },
            {"name": "Rajská omáčka s hovězím masem", "description": "Tradiční rajská omáčka s houskovými knedlíky a hovězím masem.", "image": "static/images/rajska_omacka.jpg","category": "maso;polevka", "price": 200},
            {"name": "Ovocný dort", "description": "Domácí dort s čerstvým ovocem a šlehačkou.", "image": "static/images/ovocny_dort.jpg","category": "desert", "price": 160 },
            {"name": "Smažený sýr s hranolky", "description": "Klasický smažený sýr podávaný s hranolky a tatarskou omáčkou.", "image": "static/images/smazeny_syr.jpg","category": "vegetarianske", "price": 180 },
            {"name": "Zeleninový wrap", "description": "Lehký wrap plněný čerstvou zeleninou, sýrem a jogurtovou omáčkou.", "image": "static/images/zeleninovy_wrap.jpg","category": "vegetarianske", "price": 120 }
        ]

        for item in extended_menu:
            new_food = Food(name=item["name"], description=item["description"], image=item["image"],category=item["category"], price=item["price"])
            db.session.add(new_food)

        roles = {
            "admin": Role(typ_role="admin"),
            "deliveryGuy": Role(typ_role="deliveryGuy"),
            "user": Role(typ_role="user"),
            "restaurant": Role(typ_role="restaurant")
        }

        for typ, role in roles.items():
            existing_role = Role.query.filter_by(typ_role=typ).first()
            if not existing_role:
                db.session.add(role)

        # Kontrola a přidání administrátora
        existing_admin = Uzivatel.query.filter_by(email="admin@admin").first()
        existing_restaurant1 = Restaurace.query.filter_by(email="1@restaurace").first()
        existing_zamestnanec1 = Uzivatel.query.filter_by(email="1@restaurace").first()
        existing_restaurant2 = Restaurace.query.filter_by(email="2@restaurace").first()
        existing_zamestnanec2 = Uzivatel.query.filter_by(email="2@restaurace").first()
        existing_restaurant3 = Restaurace.query.filter_by(email="3@restaurace").first()
        existing_zamestnanec3 = Uzivatel.query.filter_by(email="3@restaurace").first()
        existing_user = Uzivatel.query.filter_by(email="user@user").first()
        existing_delivery_guy = Uzivatel.query.filter_by(email="delivery@delivery").first()

        # Vytvoření admina
        if not existing_admin:
            new_admin = Uzivatel(
                email="admin@admin",
                firstName="admin",
                lastName="admin",
                password="admin",
                role_typ="admin"
            )
            db.session.add(new_admin)
        # Vytvoření uživatele
        if not existing_user:
            new_user = Uzivatel(
                email="user@user",
                firstName="user",
                lastName="user",
                password="user",
                role_typ="user"
            )
            db.session.add(new_user)
        # Vytvoření Poslička
        if not existing_delivery_guy:
            new_delivery_guy = Uzivatel(
                email="delivery@delivery",
                firstName="delivery",
                lastName="delivery",
                password="delivery",
                role_typ="deliveryGuy"
            )
            db.session.add(new_delivery_guy)
        # Vytvoření Zaměstnanců a restauraci
        if not existing_zamestnanec1:
            new_1zamestnanec = Uzivatel(
                email="1@restaurace",
                firstName="1",
                lastName="1",
                password="1",
                role_typ="restaurant"
            )
            db.session.add(new_1zamestnanec)

        if not existing_restaurant1:
            new_1restaurace = Restaurace(
                nazev = "Restaurace1",
                email  = "1@restaurace",
                telefon = "111111111",
                adresa = "restaurace1adresa",
                password = "1",
            )
            db.session.add(new_1restaurace)

        if not existing_zamestnanec2:
            new_2zamestnanec = Uzivatel(
                email="2@restaurace",
                firstName="2",
                lastName="2",
                password="2",
                role_typ="restaurant"
            )
            db.session.add(new_2zamestnanec)

        if not existing_restaurant2:
            new_2restaurace = Restaurace(
                nazev = "Restaurace2",
                email  = "2@restaurace",
                telefon = "222222222",
                adresa = "restaurace2adresa",
                password = "2",
            )
            db.session.add(new_2restaurace)

        if not existing_zamestnanec3:
            new_3zamestnanec = Uzivatel(
                email="3@restaurace",
                firstName="3",
                lastName="3",
                password="3",
                role_typ="restaurant"
            )
            db.session.add(new_3zamestnanec)

        if not existing_restaurant3:
            new_3restaurace = Restaurace(
                nazev = "Restaurace3",
                email  = "3@restaurace",
                telefon = "333333333",
                adresa = "restaurace3adresa",
                password = "3",
            )
            db.session.add(new_3restaurace)

        db.session.commit()

    # Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Uzivatel.query.get(int(id))


    @app.template_filter('to_cz_time')
    def to_cz_time(value):
        """Převod UTC času na čas v ČR (CET/CEST)."""
        if value:
            utc_time = value.replace(tzinfo=pytz.UTC)
            cz_time = utc_time.astimezone(pytz.timezone('Europe/Prague'))
            return cz_time.strftime('%d.%m.%Y %H:%M')
        return value

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')



