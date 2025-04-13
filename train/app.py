from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # For flash messages

class Train:
    def __init__(self, train_id, train_name, source, destination, total_seats):
        self.train_id = train_id
        self.train_name = train_name
        self.source = source
        self.destination = destination
        self.total_seats = total_seats
        self.available_seats = total_seats

class Passenger:
    def __init__(self, name, age, gender, train_id, pnr):
        self.name = name
        self.age = age
        self.gender = gender
        self.train_id = train_id
        self.pnr = pnr

class RailwaySystem:
    def __init__(self):
        self.trains = [
            Train(101, "Express One", "Mumbai", "Delhi", 50),
            Train(102, "Superfast", "Chennai", "Kolkata", 40),
            Train(103, "Metro", "Bangalore", "Hyderabad", 30)
        ]
        self.passengers = []
        self.pnr_counter = 1000

    def get_trains(self):
        return self.trains

    def book_ticket(self, name, age, gender, train_id):
        for train in self.trains:
            if train.train_id == train_id and train.available_seats > 0:
                self.passengers.append(Passenger(name, age, gender, train_id, self.pnr_counter))
                train.available_seats -= 1
                pnr = self.pnr_counter
                self.pnr_counter += 1
                return pnr, True
        return None, False

    def cancel_ticket(self, pnr):
        for passenger in self.passengers[:]:
            if passenger.pnr == pnr:
                for train in self.trains:
                    if train.train_id == passenger.train_id:
                        train.available_seats += 1
                        break
                self.passengers.remove(passenger)
                return True
        return False

    def get_passenger(self, pnr):
        for passenger in self.passengers:
            if passenger.pnr == pnr:
                return passenger
        return None

# Initialize railway system
rs = RailwaySystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trains')
def trains():
    return render_template('trains.html', trains=rs.get_trains())

@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        train_id = int(request.form['train_id'])
        try:
            age = int(age)
            if age <= 0:
                raise ValueError
            pnr, success = rs.book_ticket(name, age, gender, train_id)
            if success:
                flash(f"Ticket booked successfully! PNR: {pnr}", "success")
                return redirect(url_for('trains'))
            else:
                flash("Booking failed! Train not found or no seats available.", "danger")
        except ValueError:
            flash("Invalid input! Please enter a valid age.", "danger")
    return render_template('book.html', trains=rs.get_trains())

@app.route('/cancel', methods=['GET', 'POST'])
def cancel():
    if request.method == 'POST':
        try:
            pnr = int(request.form['pnr'])
            if rs.cancel_ticket(pnr):
                flash(f"Ticket with PNR {pnr} canceled successfully.", "success")
            else:
                flash("PNR not found!", "danger")
            return redirect(url_for('cancel'))
        except ValueError:
            flash("Invalid input! Please enter a numeric PNR.", "danger")
    return render_template('cancel.html')

@app.route('/passenger', methods=['GET', 'POST'])
def passenger():
    passenger = None
    if request.method == 'POST':
        try:
            pnr = int(request.form['pnr'])
            passenger = rs.get_passenger(pnr)
            if not passenger:
                flash("PNR not found!", "danger")
        except ValueError:
            flash("Invalid input! Please enter a numeric PNR.", "danger")
    return render_template('passenger.html', passenger=passenger)

if __name__ == '__main__':
    app.run(debug=True)