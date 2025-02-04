from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from functools import wraps


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    
    if request.method =='POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = Uzivatel.query.filter_by(email=email).first()
        if user:
            if password == user.password:
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                if user.role_typ =='admin':
                    return redirect(url_for("views.admin_dashboard"))
                elif user.role_typ == 'restaurant':
                    return redirect(url_for("views.edit_homepage"))
                elif user.role_typ == 'deliveryGuy':
                    return redirect(url_for("views.courier_orders"))
                else:
                    return redirect(url_for('views.index'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
            
    return render_template("login.html")
    

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():
    if request.method  == 'POST':
        f_email= request.form.get('email')
        f_firstName = request.form.get('firstName')
        f_lastName = request.form.get('lastName')
        f_password1 = request.form.get('password1')
        f_password2 = request.form.get('password2')

        user = Uzivatel.query.filter_by(email=f_email).first()
        if user:
            flash('Email already exist.', category='error')

        elif len(f_email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(f_firstName) < 2:
            flash('First name must be greater than 1 characters.', category='error')
        elif len(f_lastName) < 2:
            flash('First name must be greater than 1 characters.', category='error')
        elif f_password1 != f_password2:
            flash('Passwords don\'t match.', category='error')
        elif len(f_password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = Uzivatel(email=f_email, firstName=f_firstName, lastName=f_lastName, password=f_password1, role_typ = 'user')
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created', category='success')
            return redirect(url_for('views.index'))

    return render_template("register.html")
    
    
@auth.route('/restaurant/register', methods=['GET', 'POST'])
def restaurant_register():
    if request.method  == 'POST':
        f_email= request.form.get('email')
        name = request.form.get('nazev')
        phone = request.form.get('phone')
        adresa = request.form.get('adresa')
        f_password1 = request.form.get('password1')
        f_password2 = request.form.get('password2')

        user = Uzivatel.query.filter_by(email=f_email).first()
        if user:
            flash('Email already exist.', category='error')

        elif len(f_email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(phone) < 2:
            flash('First name must be greater than 1 characters.', category='error')
        elif f_password1 != f_password2:
            flash('Passwords don\'t match.', category='error')
        elif len(f_password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_restaurant = Restaurace(email=f_email, nazev=name, telefon=phone,adresa=adresa, password=f_password1)
            new_user = Uzivatel(email=f_email, firstName=name, lastName=adresa, password=f_password1, role_typ = 'restaurant')
            db.session.add(new_restaurant)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created', category='success')
            return redirect(url_for('auth.restaurant_register'))

    return render_template('restaurant_register.html')

@auth.route('/courier/register')
def courierRegister():
    if request.method  == 'POST':
        f_email= request.form.get('email')
        f_firstName = request.form.get('firstName')
        f_lastName = request.form.get('lastName')
        f_password1 = request.form.get('password1')
        f_password2 = request.form.get('password2')

        user = Uzivatel.query.filter_by(email=f_email).first()
        if user:
            flash('Email already exist.', category='error')

        elif len(f_email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(f_firstName) < 2:
            flash('First name must be greater than 1 characters.', category='error')
        elif len(f_lastName) < 2:
            flash('First name must be greater than 1 characters.', category='error')
        elif f_password1 != f_password2:
            flash('Passwords don\'t match.', category='error')
        elif len(f_password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = Uzivatel(email=f_email, firstName=f_firstName, lastName=f_lastName, password=f_password1, role_typ = 'deliveryGuy')
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created', category='success')
            return redirect(url_for('views.index'))
    return render_template('register_poslicek.html')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Musíte být přihlášený jako admin, abyste měli přístup k této stránce.", "error")
            return redirect(url_for('auth.login'))
        if current_user.role_typ != 'admin':
            flash("Nemáte oprávnění k přístupu na tuto stránku.", "error")
            return redirect(url_for('views.index'))
        return f(*args, **kwargs)
    return decorated_function

