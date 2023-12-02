from flask import Flask, render_template, url_for, request, flash, redirect, session, logging
from flask_mysqldb import MySQL
from data import Patients
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


app = Flask(__name__)
app.secret_key = "hello"


app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "Qlfsat2017"
app.config['MYSQL_DB'] = "patients"
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

Patients = Patients()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/new", methods=['POST', 'GET'])
def new():
    if request.method == 'POST':
        
        user = request.form["name"]
        sexo = request.form['sexo']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO patients(nome, bairro) VALUES (%s, %s)", (user, sexo))
        mysql.connection.commit()
        cur.close()
        flash("gravado com sucesso !")
        return redirect(url_for("index"))

    else:
        return render_template("newPatient.html")

@app.route("/list")
def list():
    return render_template("list_patients.html", patients = Patients)

@app.route("/patient/<string:id>/")
def patient(id):
    return render_template("patient.html", id=id)

@app.route("/tratamento")
def tratamento():
    
    return render_template("tratamentos.html")

@app.route("/log", methods=['GET', 'POST'])
def log():
    if request.method == 'POST':

        #get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        #create cursor
        cur=mysql.connection.cursor()

        #get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", 
        [username])
        

        if result > 0:
            #get stored hash
            data = cur.fetchone()
            password = data['password']

            #compare passwords
            if sha256_crypt.verify(password_candidate, password):
                #passed
                session['Logged_in'] = True
                session['username'] = username

                flash('Você esta logado!', 'success')
                return redirect(url_for('list'))

            else:
                error = "Login incorreta!"
                return render_template('loginPage.html', error=error)
            
            #close the connexion
            cur.close()
        
        else:
            error = "Username nâo encontrado!"
            return render_template('loginPage.html', error=error)

    return render_template("LoginPage.html")

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=3, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.equal_to('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form=RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        print(name)

        #create cursor

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
        #commit
        mysql.connection.commit()
        #close
        cur.close()
        flash('You are now registered and can log in', 'success')

        return redirect(url_for('log'))

    return render_template("register.html", form=form)

#check if user logged in
def estoudentro(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'Logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Não autoizado, por favor login', 'danger')
            return redirect(url_for('log'))
    return wrap


@app.route('/logout')
def logout():
    session.clear()
    flash('Você está agora desconectado!', 'success')
    return redirect(url_for('log'))

if __name__ == "__main__":
    app.run(debug=True)