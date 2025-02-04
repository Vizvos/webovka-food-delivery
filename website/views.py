from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.sql import func
import json
import os
from .models import *
from flask import current_app
from werkzeug.utils import secure_filename
from .auth import admin_required
from sqlalchemy.sql import extract
from datetime import datetime, timedelta


views = Blueprint('views', __name__)

#User section: -----------------------------------------------

@views.route('/')
def home():
    return render_template("index.html")

@views.route('/index')
def index():
    return render_template("index.html")

@views.route('/nabidka')
def nabidka():
    return render_template("nabidka.html")

@views.route('/objednat')
def objednat():
    menu_items = Food.query.all()
    return render_template("objednat.html", menu_items = menu_items)

@views.route('/profil')
def profil():
    return render_template("profil.html")

@views.route('/kosik')
def cart():
    cart =[]
    celkovaCena=0
    if current_user.is_authenticated:
        if current_user.kosik:
            for item in current_user.kosik:
                # Získání informace o množství z tabulky kosik
                cart_item = db.session.query(kosik).filter(kosik.c.uzivatel_id == current_user.id, kosik.c.food_id == item.id).first()

                if cart_item:
                    # Vynásobíme cenu položky s množstvím
                    itemPrice = item.price * cart_item.quantity
                    celkovaCena += itemPrice  # Přičítáme cenu položky k celkové ceně
                    cart.append(item)  # Přidáme položku do košíku
                else:
                    print('Položka v košíku nemá definováno množství.')
        else:
            print('Kosik je prazdny')
    else:
        print('Neprihlaseny uzivatel')

    return render_template("cart.html", cart_items=cart, celkovaCena = celkovaCena)

@views.route('/api/cart/add/<int:id>')
def add_to_cart(id):
    if current_user.is_authenticated:
        try:
            food = Food.query.get(id)
            if food:
                current_user.kosik.append(food)
                db.session.commit()
                flash("jidlo bylo pridano do kosiku")
            else:
                flash("jidlo nebylo pridano")
        except Exception as e:
            flash(f"Došlo k chybě při přřidávání do košíku: {str(e)} ", "error")
    else:
        flash("neprihlasen")
    return redirect("/objednat")

@views.route('/restaurant/order/ready/<int:id>')
def order_ready(id):
    objednavka = Objednavka.query.filter_by(id = id).first()
    doruceni = Doruceni.query.filter_by(id = objednavka.doruceni_id).first()
    doruceni.stav_objednavky = "Potvrzeno"
    db.session.commit()
    return redirect('/restaurant-orders')

@views.route('/update_cart/<int:item_id>/<int:quantity>', methods=['POST'])
def update_cart(item_id, quantity):
    if current_user.is_authenticated:
        try:
            # Zkontrolujte, zda uživatel má položku v košíku
            cart_item = db.session.query(kosik).filter_by(
                uzivatel_id=current_user.id,
                food_id=item_id
            ).first()

            if cart_item:
                # Pokud položka existuje, aktualizujte její množství
                cart_item.quantity = quantity
                db.session.commit()
                return jsonify({'message': 'Košík byl aktualizován'}), 200
            else:
                return jsonify({'message': 'Položka nenalezena v košíku'}), 404
        except Exception as e:
            return jsonify({'message': f'Chyba při aktualizaci: {str(e)}'}), 500
    else:
        return jsonify({'message': 'Nejste přihlášen'}), 401

@views.route('/api/cart/remove/<int:id>')
def remove_from_cart(id):
    food = Food.query.filter_by(id=id).first()
    if food:
        current_user.kosik.remove(food)
        db.session.commit()
    else:
        print('nenalezeno')
    return redirect("/kosik")



@views.route('/platba',methods= ['GET'])
@login_required
def platba():
    restaurants=Restaurace.query.all()
    return render_template("platba.html",restaurants=restaurants)

@views.route('/historie')
@login_required
def historie():
    orders = Objednavka.query.filter_by(uzivatel_id=current_user.id).all()
    return render_template("historie.html", orders=orders)

#Admin section: -----------------------------------------------

@views.route('/admin_approval')
@admin_required
def admin_approval():
    return render_template("admin_approval.html")

@views.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    return render_template("admin_dashboard.html")

@views.route('/admin_manage')
@admin_required
def admin_manage():
    couriers = Uzivatel.query.filter_by(role_typ='deliveryGuy')
    restaurants = Restaurace.query.all()
    return render_template("admin_manage.html", couriers=couriers, restaurants=restaurants)

@views.route('/admin_statistics')
@admin_required
def admin_statistics():
    # Celkový příjem
    total_revenue = db.session.query(db.func.sum(Objednavka.cena)).scalar()

    # Příjem za posledních 5 dní
    today = datetime.today()
    five_days_ago = today - timedelta(days=5)
    recent_revenue = db.session.query(
        db.func.date(Objednavka.datum_objednani).label('day'),
        db.func.sum(Objednavka.cena).label('revenue')
    ).filter(
        Objednavka.datum_objednani >= five_days_ago
    ).group_by(
        db.func.date(Objednavka.datum_objednani)
    ).order_by(
        db.func.date(Objednavka.datum_objednani).desc()
    ).all()

    return render_template(
        "admin_statistics.html", 
        total_revenue=total_revenue, 
        recent_revenue=recent_revenue
    )

@views.route('/admin/smazat/<int:id>')
def adminSmazat(id):
    restaurant = Restaurace.query.get_or_404(id)
    db.session.delete(restaurant)
    db.session.commit()
    return redirect("/admin_manage")

@views.route('/admin/upravit/<int:id>')
def adminUpravit():
    
    return redirect("/admin_manage")
#Courier section: -----------------------------------------------



@views.route('/courier_orders', methods=['GET'])
def courier_orders():
    orders = Objednavka.query.all()
    return render_template("courier_orders.html", orders=orders)

@views.route('/accept-order/<int:id>', methods=['POST','GET'])
def accept_order(id):
    order = Doruceni.query.filter_by(id = id).first()
    order.stav_objednavky = "přijato kuryrem"
    order.poslicek_id = current_user.id
    db.session.commit()
    if order:
        db.session.commit()
        flash(f"Objednávka #{id} byla přijata.", category='success')
    else:
        flash("Objednávka nebyla nalezena.", category='error')

    return redirect(url_for('views.courier_orders'))

@views.route('/leave-order/<int:id>', methods=['POST','GET'])
def order_leave(id):
    order = Doruceni.query.filter_by(id = id).first()
    order.stav_objednavky = "Potvrzeno"
    order.poslicek_id = 0
    db.session.commit()
    return redirect(url_for('views.courier_orders'))

@views.route('/complete-order/<int:id>', methods=['POST','GET'])
def order_complete(id):
    order = Doruceni.query.filter_by(id = id).first()
    order.stav_objednavky = "Dorucena"
    db.session.commit()
    return redirect(url_for('views.courier_orders'))


# Endpoint pro menu
@views.route("/api/menu")
def weeklyMenu():
    weekly_menu_data = Food.query.all()
    weekly_menu_list = [{
        "name": item.name,
        "description": item.description,
        "image": item.image,
        "price": item.price
    } for item in weekly_menu_data]
    return jsonify(weekly_menu_list)

#Endpoint pro týdenní menu
@views.route("/api/weeklyMenu")
def Menu():
    restaurants = Restaurace.query.all()
    result = []

    for restaurant in restaurants:
        print(f"Zpracovává se restaurace: {restaurant.nazev}")  # Debug výstup
        restaurant_data = {
            "restaurant_name": restaurant.nazev,
            "menu": []
        }
        userRestaurant = Uzivatel.query.filter_by(email = restaurant.email).first()

        for item in userRestaurant.nabidka:
            restaurant_data["menu"].append({
                    "name": item.name,
                    "description": item.description,
                    "image": item.image,
                    "price": item.price
                })
        result.append(restaurant_data)

    print(f"Výsledek: {result}")  # Debug výstup
    return jsonify(result)
 

@views.route('/create-order', methods=['POST', 'GET'])
@login_required
def create_order():
    try:
        # Získání dat z formuláře
        address = request.form.get('address')
        payment_method = request.form.get('payment_method')
        restaurace_id = request.form.get('restaurant_id')  # Přidání restaurace

        # Validace vstupu
        if not address or not payment_method or not restaurace_id:
            flash('Chybí potřebné údaje!', category='error')
            return redirect(url_for('views.cart'))

        # Kontrola, zda restaurace existuje
        restaurace = Restaurace.query.get(restaurace_id)
        if not restaurace:
            flash('Zvolená restaurace neexistuje.', category='error')
            return redirect(url_for('views.cart'))

        # Debug výpis: kontrola restaurace
        print(f"Restaurace přiřazená k objednávce: ID={restaurace.id}, Název={restaurace.nazev}")

        # Vytvoření záznamu doručení
        new_doruceni = Doruceni(
            doruceni_adresa=address,
            uzivatel_id=current_user.id,
            poslicek_id=0
        )
        db.session.add(new_doruceni)
        db.session.commit()

        # Spočítání celkové ceny košíku
        cart_items = current_user.kosik
        total_price = sum([item.price for item in cart_items])

        # Vytvoření objednávky
        new_order = Objednavka(
            datum_objednani=func.now(),
            cena=total_price,
            zpusob_platby=payment_method,
            uzivatel_id=current_user.id,
            doruceni_id=new_doruceni.id,
            restaurace_id=restaurace_id  # Propojení s restaurací
        )
        db.session.add(new_order)

        # Debug výpis: kontrola objednávky
        print(f"Nová objednávka vytvořena: ID={new_order.id}, Restaurace_ID={new_order.restaurace_id}")

        # Přidání položek z košíku do objednávky
        for item in cart_items:
            new_order.foods.append(item)

        # Vyprázdnění košíku
        current_user.kosik.clear()
        db.session.commit()

        flash('Objednávka byla úspěšně vytvořena!', category='success')
        return redirect(url_for('views.historie'))

    except Exception as e:
        print(f"Chyba při vytváření objednávky: {str(e)}")  # Debugging
        flash(f'Chyba: {str(e)}', category='error')
        return redirect(url_for('views.cart'))





#Restaurant section: -----------------------------------------------

@views.route('/restaurant/menus')
@login_required
def view_menus():
    menus = Food.query.all()
    nabidkas = current_user.nabidka
    return render_template('view_menus.html', menus=menus, nabidkas = nabidkas)

@views.route('/restaurant/menu/add/<int:id>')
@login_required
def add_item_toMenu(id):
    currentRestaurant = Restaurace.query.filter_by(email=current_user.email).first()
    food = db.session.query(Food).filter(Food.id == id).first()
    current_user.nabidka.append(food)
    db.session.commit()
    return redirect('/restaurant/menus')

@views.route('/restaurant/menu/remove/<int:id>')
@login_required
def remove_item_fromMenu(id):
    food = Food.query.filter_by(id=id).first()
    if food:
        current_user.nabidka.remove(food)
        db.session.commit()
    else:
        print('nenalezeno')
    return redirect('/restaurant/menus')


@views.route('/restaurant/menu/add', methods=['GET', 'POST'])
@login_required
def add_menu_item():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        category = request.form.get('category')
        image = request.form.get('image')

        new_item = Food(
            name=name,
            description=description,
            price=price,
            category=category,
            image=image
        )
        db.session.add(new_item)
        db.session.commit()
        flash("Jídlo bylo úspěšně přidáno!", "success")
        return redirect(url_for('views.view_menus'))

    return render_template('add_menu_item.html')

# Úprava jídla
@views.route('/restaurant/menu/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_menu_item(item_id):
    item = Food.query.get_or_404(item_id)
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.description = request.form.get('description')
        item.price = request.form.get('price')
        item.category = request.form.get('category')
        item.image = request.form.get('image')
        db.session.commit()
        flash("Jídlo bylo úspěšně upraveno!", "success")
        return redirect(url_for('views.view_menus'))

    return render_template('edit_menu_item.html', item=item)


@views.route('/restaurant/menu/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_menu_item(item_id):
    item = Food.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Jídlo bylo odstraněno.", "success")
    return redirect(url_for('views.view_menus'))

@views.route('/restaurant/dashboard')
@login_required
def restaurant_dashboard():
    return render_template('restaurant_dashboard.html')

@views.route('/restaurant-orders', methods=['GET'])
@login_required
def restaurant_orders():
    if current_user.role_typ != 'restaurant':
        flash('Nemáte oprávnění k přístupu na tuto stránku.', category='error')
        return redirect(url_for('views.index'))

    restaurace = Restaurace.query.filter_by(email=current_user.email).first()

    if not restaurace:
        flash('Vaše restaurace nebyla nalezena.', category='error')
        return redirect(url_for('views.index'))
    orders = Objednavka.query.filter_by(restaurace_id=restaurace.id).all()

    # Debugging:
    print(f"Restaurace ID: {restaurace.id}, Název: {restaurace.nazev}")
    for order in orders:
        print(f"Objednávka ID: {order.id}, Cena: {order.cena}, Restaurace ID: {order.restaurace_id}")
    return render_template('restaurant_orders.html', orders=orders)




@views.route('/restaurant/orders/status')
@login_required
def restaurant_order_status():
    orders = Objednavka.query.all()  
    return render_template('restaurant_order_status.html', orders=orders)


@views.route('/restaurant/edit_homepage', methods=['GET', 'POST'])
@login_required
def edit_homepage():
  
    homepage_text = get_homepage_text()  # Například z databáze
    return render_template('edit_homepage.html', homepage_text=homepage_text)

@views.route('/restaurant/update_texts', methods=['POST'])
@login_required
def update_texts():
    new_text = request.form.get('homepage_text')

    if new_text:
        # Uložit nový text (do souboru nebo databáze)
        save_homepage_text(new_text)
        flash("Text na hlavní stránce byl úspěšně aktualizován.", "success")
    else:
        flash("Text nebyl aktualizován. Zkuste to znovu.", "error")

    return redirect(url_for('views.edit_homepage'))

@views.route('/restaurant/update_image', methods=['POST'])
@login_required
def update_image():
    if 'image' not in request.files:
        flash("Nebyl vybrán žádný soubor.", "error")
        return redirect(url_for('views.edit_homepage'))

    file = request.files['image']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.root_path, 'static/images/', filename)
        file.save(filepath)

        # Aktualizace v databázi nebo přepsání aktuálního obrázku
        update_homepage_image(filepath)

        flash("Obrázek byl úspěšně aktualizován.", "success")
    else:
        flash("Nepovolený formát souboru.", "error")

    return redirect(url_for('views.edit_homepage'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}
    
    
def get_homepage_text():
    filepath = os.path.join(current_app.root_path, 'data/homepage_text.txt')
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    return "Přidejte text o Vaší restauraci..."

def save_homepage_text(new_text):
    filepath = os.path.join(current_app.root_path, 'data/homepage_text.txt')
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(new_text)

def update_homepage_image(filepath):
    
    pass


@views.route('/restaurant/orders', methods=['GET'])
def restaurant_orders_overview():
    orders = Objednavka.query.all()
    return render_template('restaurant_orders.html', orders=orders)



@views.route('/order-details/<int:order_id>', methods=['GET'])
@login_required
def order_details(order_id):
    order = Objednavka.query.filter_by(id=order_id, uzivatel_id=current_user.id).first()

    if not order:
        flash('Objednávka nebyla nalezena.', category='error')
        return redirect(url_for('views.historie'))

    return render_template('order_details.html', order=order)

@views.route('/restaurant-order-detail/<int:order_id>', methods=['GET'])
@login_required
def restaurant_order_detail(order_id):
    # Načtení objednávky
    order = Objednavka.query.filter_by(id=order_id).first()

    if not order:
        flash('Objednávka nebyla nalezena.', category='error')
        return redirect(url_for('views.restaurant_orders'))

    return render_template(
        'restaurant_order_detail.html',
        order=order
    )


