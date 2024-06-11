from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservas.db'
db = SQLAlchemy()
migrate = Migrate()
db.init_app(app)
migrate.init_app(app, db)

class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False)
    cantidad_personas = db.Column(db.Integer, nullable=False)

CAPACIDAD_RESTAURANTE = 50  # Asignacion de cantidad total de mesas del Restaurante

# Función para verificar la disponibilidad de mesas
def verificar_disponibilidad(fecha, cantidad_personas):
    reservas_exist = Reserva.query.filter_by(fecha=fecha).all()
    total_personas_reservadas = sum(reserva.cantidad_personas for reserva in reservas_exist)
    total_personas = total_personas_reservadas + cantidad_personas
    if total_personas <= CAPACIDAD_RESTAURANTE:
        return True
    else:
        return False

# Función para generar horarios disponibles
def generar_horarios_disponibles():
    horarios = []
    hora_actual = datetime.now().replace(minute=0, second=0, microsecond=0)
    for _ in range(14):  # Generar horarios para las próximas 24 horas
        horarios.append(hora_actual.strftime('%H:%M'))
        hora_actual += timedelta(hours=1)
    return horarios

# Ruta para la página principal
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d')
        hora = request.form['hora']
        cantidad_personas = int(request.form['cantidad_personas'])
        fecha_hora = datetime.combine(fecha, datetime.strptime(hora, '%H:%M').time())
        # Verificar disponibilidad de mesas
        if verificar_disponibilidad(fecha_hora, cantidad_personas):
            # Crear reserva si hay disponibilidad
            nueva_reserva = Reserva(fecha=fecha_hora, cantidad_personas=cantidad_personas)
            db.session.add(nueva_reserva)
            db.session.commit()
            return redirect('/')
        else:
            return "Lo sentimos, no hay mesas disponibles para esa fecha y hora."
    else:
        horarios_disponibles = generar_horarios_disponibles()
        return render_template('index.html', horarios=horarios_disponibles)

# Ruta para ver las reservas existentes
@app.route('/reservas')
def ver_reservas():
    lista_reservas = Reserva.query.all()
    return render_template('reservas.html', reservas=lista_reservas)

# Ruta para modificar una reserva existente
@app.route('/reservas/<int:id>/modificar', methods=['GET', 'POST'])
def modificar_reserva(id):
    reserva = Reserva.query.get_or_404(id)
    if request.method == 'POST':
        reserva.fecha = datetime.combine( datetime.strptime(request.form['fecha'], '%Y-%m-%d'), datetime.strptime(request.form['hora'],'%H:%M').time())
        reserva.cantidad_personas = int(request.form['cantidad_personas'])
        db.session.commit()
        return redirect('/reservas')
    else:
        return render_template('modificar_reserva.html', reserva=reserva)

# Ruta para cancelar una reserva existente
@app.route('/reservas/<int:id>/cancelar', methods=['POST'])
def cancelar_reserva(id):
    reserva = Reserva.query.get_or_404(id)
    db.session.delete(reserva)
    db.session.commit()
    return redirect('/reservas')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    
    app.run(debug=True)