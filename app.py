from flask import Flask, render_template, request, redirect
import pymysql

app = Flask(__name__)

# MySQL Config
db = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="bus_app"
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    source = request.form['source']
    destination = request.form['destination']
    cursor = db.cursor()
    cursor.execute("SELECT * FROM buses WHERE source=%s AND destination=%s", (source, destination))
    buses = cursor.fetchall()
    return render_template('search.html', buses=buses)

@app.route('/book/<int:bus_id>', methods=['GET', 'POST'])
def book(bus_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM buses WHERE id=%s", (bus_id,))
    bus = cursor.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        seats = int(request.form['seats'])

        if bus[5] >= seats:
            cursor.execute("INSERT INTO bookings (bus_id, name, email, seats) VALUES (%s, %s, %s, %s)",
                           (bus_id, name, email, seats))
            cursor.execute("UPDATE buses SET seats_available = seats_available - %s WHERE id=%s", (seats, bus_id))
            db.commit()
            return redirect('/mybookings')
        else:
            return "Not enough seats available."

    return render_template('book.html', bus=bus)

@app.route('/mybookings')
def mybookings():
    cursor = db.cursor()
    cursor.execute("""
        SELECT b.id, bu.source, bu.destination, bu.date, bu.time, b.seats, bu.fare, b.name 
        FROM bookings b 
        JOIN buses bu ON b.bus_id = bu.id
    """)
    bookings = cursor.fetchall()
    return render_template('bookings.html', bookings=bookings)

if __name__ == '__main__':
    app.run(debug=True)
