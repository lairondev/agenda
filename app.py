'''from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
db = SQLAlchemy(app)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time= db.Column(db.Time, nullable=False)
    event_details = db.Column(db.String(200), nullable=False)
    
class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_vehicles = db.Column(db.Integer, nullable=False, default=3)  # Define o número total de veículos disponíveis
    available_vehicles = db.Column(db.Integer, nullable=False, default=3)

with app.app_context():
    db.create_all()
    # Inicializa a frota com um número fixo de veículos, caso não exista um registro.
    if not Vehicle.query.first():
        initial_fleet = Vehicle(total_vehicles=3, available_vehicles=3)
        db.session.add(initial_fleet)
        db.session.commit()



def get_calendar_data(year, month):
    """Retorna os dias do mês com seus dias da semana corretos (real)."""
    first_day = date(year, month, 2)  # Primeiro dia do mês
    start_weekday = first_day.weekday()  # Dia da semana (0=segunda-feira, 1=terça-feira, ..., 6=domingo)
    
    # Número de dias no mês
    num_days = (date(year, month % 12 + 1, 1) - first_day).days  # Total de dias no mês
    days = list(range(1, num_days + 2) )# Lista de dias do mês

    # Adiciona espaços vazios antes do primeiro dia, com base no dia da semana de `first_day`
    days_before = [None] * start_weekday  # Espaços vazios até o primeiro dia
    calendar_days = days_before + days  # Junta os espaços vazios e os dias do mês

    # Divide os dias em semanas (7 dias por semana)
    weeks = [calendar_days[i:i + 7] for i in range(0, len(calendar_days), 7)]
    return weeks



@app.route('/')
def index():
    cars = Vehicle.query.first()
    
    today = date.today()
    # Carrega a frota atual
    fleet = Vehicle.query.first()

    # Carrega reservas do mês atual
    bookings = Booking.query.filter(
        Booking.start_date >= today.replace(day=1)
    ).all()

    # Define dias como indisponíveis caso os veículos estejam esgotados
    unavailable_days = {b.start_date.day for b in bookings if fleet.available_vehicles <= 0}

    # Gera o calendário
    weeks = get_calendar_data(today.year, today.month)
    
        # Nomes dos mêses formatado por extenso
    if today.month == 1:
        nome_mes = "Janeiro"
    elif today.month == 2:
        nome_mes = "Fevereiro"
    elif today.month == 3:
        nome_mes = "Março"
    elif today.month == 4:
        nome_mes = "Abril"
    elif today.month == 5:
        nome_mes = "Maio"
    elif today.month == 6:
        nome_mes = "Junho"
    elif today.month == 7:
        nome_mes = "Julho"
    elif today.month == 8:
        nome_mes = "Agosto"
    elif today.month == 9:
        nome_mes = "Setembro"
    elif today.month == 10:
        nome_mes = "Outubro"
    elif today.month == 11:
        nome_mes = "Novembro"
    elif today.month == 12:
        nome_mes = "Dezembro"

    return render_template('index.html', weeks=weeks, unavailable_days=unavailable_days, today=today, mes=today.month, nome_mes=nome_mes, cars=cars.available_vehicles)


@app.route('/book/<int:day>', methods=['GET', 'POST'])
def book(day):
    if request.method == 'POST':
        start_date = request.form['start_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        event_details = request.form['event_details']

        # Carrega a frota atual
        fleet = Vehicle.query.first()

        # Verifica se há veículos disponíveis
        if fleet.available_vehicles > 0:
            # Salva o agendamento no banco de dados
            booking = Booking(
                start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
                start_time=datetime.strptime(start_time, '%H:%M').time(),
                end_time=datetime.strptime(end_time, '%H:%M').time(),
                event_details=event_details
            )
            db.session.add(booking)
            
            # Atualiza a disponibilidade de veículos
            fleet.available_vehicles -= 1
            db.session.commit()
            
            flash('Solicitação de transporte realizada com sucesso!')
            return redirect(url_for('index'))
        else:
            flash('Não há veículos disponíveis para essa data.')
            return redirect(url_for('index'))

    selected_date = date(date.today().year, date.today().month, day)
    return render_template('booking_form.html', selected_date=selected_date)


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.start()
    app.run(debug=True)
'''

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
db = SQLAlchemy(app)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time= db.Column(db.Time, nullable=False)
    event_details = db.Column(db.String(200), nullable=False)
    returned = db.Column(db.Boolean, default=False)  # Novo campo para indicar se o veículo foi retornado

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_vehicles = db.Column(db.Integer, nullable=False, default=3)
    available_vehicles = db.Column(db.Integer, nullable=False, default=3)

with app.app_context():
    db.create_all()
    if not Vehicle.query.first():
        initial_fleet = Vehicle(total_vehicles=3, available_vehicles=3)
        db.session.add(initial_fleet)
        db.session.commit()

def get_calendar_data(year, month):
    first_day = date(year, month, 2)
    start_weekday = first_day.weekday()
    num_days = (date(year, month % 12 + 1, 1) - first_day).days
    days = list(range(1, num_days + 2))
    days_before = [None] * start_weekday
    calendar_days = days_before + days
    weeks = [calendar_days[i:i + 7] for i in range(0, len(calendar_days), 7)]
    return weeks

@app.route('/')
def index():
    cars = Vehicle.query.first()
    today = date.today()
    fleet = Vehicle.query.first()
    
    # Filtrar apenas eventos agendados para o dia atual
    bookings = Booking.query.filter(Booking.start_date == today).all()
    
    unavailable_days = {b.start_date.day for b in Booking.query.filter(Booking.start_date >= today.replace(day=1)).all() if fleet.available_vehicles <= 0}
    
    weeks = get_calendar_data(today.year, today.month)
    nome_mes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"][today.month - 1]

    return render_template('index.html', weeks=weeks, unavailable_days=unavailable_days, 
                           today=today, mes=today.month, nome_mes=nome_mes, cars=cars.available_vehicles, bookings=bookings)



@app.route('/book/<int:day>', methods=['GET', 'POST'])
def book(day):
    if request.method == 'POST':
        start_date = request.form['start_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        event_details = request.form['event_details']
        
        fleet = Vehicle.query.first()
        selected_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        today = date.today()

        if selected_date == today:
            if fleet.available_vehicles > 0:
                fleet.available_vehicles -= 1
            else:
                flash('Não há veículos disponíveis para essa data.')
                return redirect(url_for('index'))
        
        booking = Booking(
            start_date=selected_date,
            start_time=datetime.strptime(start_time, '%H:%M').time(),
            end_time=datetime.strptime(end_time, '%H:%M').time(),
            event_details=event_details
        )
        
        db.session.add(booking)
        db.session.commit()
        
        flash('Solicitação de transporte realizada com sucesso!')
        return redirect(url_for('index'))

    selected_date = date(date.today().year, date.today().month, day)
    return render_template('booking_form.html', selected_date=selected_date)

@app.route('/return/<int:booking_id>', methods=['POST'])
def return_vehicle(booking_id):
    booking = Booking.query.get(booking_id)
    fleet = Vehicle.query.first()
    
    if booking and not booking.returned:
        booking.returned = True
        fleet.available_vehicles += 1
        db.session.commit()
        flash('Veículo marcado como retornado.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.start()
    app.run(debug=True)