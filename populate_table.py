from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Saransh' 
app.config['MYSQL_DB'] = 'flask_app'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Create the available_seats table with 100 initial vacant seats
def create_available_seats_table():
    cur = mysql.connection.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS available_seats (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    seat_number INT NOT NULL,
                    seat_status VARCHAR(20) NOT NULL)''')

    # Check if the table is already populated
    cur.execute('SELECT COUNT(*) FROM available_seats')
    count = cur.fetchone()
    
    if count is not None and count['COUNT(*)'] == 0:
        # If the table is empty, insert 100 initial vacant seats
        seats = [(i, 'available') for i in range(1, 101)]
        cur.executemany('INSERT INTO available_seats (seat_number, seat_status) VALUES (%s, %s)', seats)

    mysql.connection.commit()
    cur.close()

if __name__ == '__main__':
    with app.app_context():
        create_available_seats_table()
