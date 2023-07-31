from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Saransh'
app.config['MYSQL_DB'] = 'flask_app'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Secret key for sessions
app.secret_key = 'your_secret_key'

# Route to display the home page
@app.route('/')
def home():
    return render_template('lander_page.html')

# Route to display the analysis page
@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

# Route to display the prediction page
@app.route('/prediction')
def prediction():
    return render_template('prediction.html')

# Route to display the page for booking tickets
@app.route('/baytickets', methods=['GET', 'POST'])
def baytickets():
    if request.method == 'POST':
        # Process signup form data and store in the database
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
        mysql.connection.commit()
        cur.close()

    return render_template('baytickets.html')

# Route to display the login page and handle user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('book_tickets'))  # Redirect to index if already logged in

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = mysql.connection
        cursor = connection.cursor()

        # Check if the credentials match in the database
        cursor.execute("SELECT id FROM users WHERE username = %s AND password = %s",
                       (username, password))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:
            # Store the user ID in the session for future authentication
            session['user_id'] = user['id']  # Use 'id' key to get the user_id from the 'user' dictionary
            return redirect(url_for('baytickets'))  # Redirect to index page after login
        else:
            # Show error message if the user is not found
            return "Login failed. Invalid username or password."

    return render_template('login.html')

# Route to display the signup page and handle user signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        connection = mysql.connection
        cursor = connection.cursor()

        # Create the users table if it doesn't exist
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, "
                       "username VARCHAR(255) UNIQUE NOT NULL, "
                       "email VARCHAR(255) UNIQUE NOT NULL, "
                       "password VARCHAR(255) NOT NULL)")

        # Check if the username is already taken
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            cursor.close()
            connection.close()
            return "Username already taken. Please choose a different username."

        # Insert the new user into the database
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                       (username, email, password))
        connection.commit()

        cursor.close()
        connection.close()

        # Redirect to the login page after successful signup
        return redirect(url_for('login'))

    return render_template('signup.html')

# Route to display the forum page with threads
@app.route('/forum')
def forum():
    # Fetch and display data from the threads table in MySQL
    cur = mysql.connection.cursor()
    cur.execute('SELECT id, title, description FROM threads')  # Fetch the id, title, and description columns
    threads = cur.fetchall()
    cur.close()

    return render_template('forum.html', threads=threads)  # Pass the fetched data to the template

# Route to create a new thread and handle form submission
@app.route('/thread', methods=['GET', 'POST'])
def thread():
    if request.method == 'POST':
        # Process form data and store the new thread description and title in the database
        title = request.form['title']
        description = request.form['description']

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO threads (title, description) VALUES (%s, %s)', (title, description))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('forum'))

    return render_template('thread.html')

# Route to add a new thread and handle form submission (Alternate version)
@app.route('/add_thread', methods=['POST'])  # Specify 'POST' method for handling form submission
def add_thread():
    if request.method == 'POST':
        # Process form data and store the new thread description and title in the database
        title = request.form['title']
        description = request.form['description']

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO threads (title, description) VALUES (%s, %s)', (title, description))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('forum'))

    # If accessed directly, redirect back to the thread.html page (or you can render the template here)
    return redirect(url_for('thread'))

@app.route('/book_tickets', methods=['GET', 'POST'])
def book_tickets():
    cur = mysql.connection.cursor()
    cur.execute('SELECT seat_number FROM available_seats WHERE seat_status = %s', ('available',))
    available_seats = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        # Process ticket booking form data and store in database
        first_name = request.form['first_name']
        seat_number = int(request.form['seat_number'])

        # Check if the user is logged in
        if 'user_id' in session:
            user_id = session['user_id']

            cur = mysql.connection.cursor()

            # Check if the selected seat is available
            cur.execute('SELECT seat_status FROM available_seats WHERE seat_number = %s', (seat_number,))
            result = cur.fetchone()

            if result and result['seat_status'] == 'available':
                # Insert booked ticket into booked_tickets table
                cur.execute('INSERT INTO booked_tickets (user_id, name, seat_number) VALUES (%s, %s, %s)', (user_id, first_name, seat_number))

                # Update seat status to 'notavailable' in available_seats table
                cur.execute('UPDATE available_seats SET seat_status = %s WHERE seat_number = %s', ('notavailable', seat_number))

                mysql.connection.commit()
                cur.close()

                return redirect(url_for('my_tickets'))

    return render_template('book_tickets.html', available_seats=available_seats)

@app.route('/book_ticket', methods=['POST'])
def book_ticket():
    if request.method == 'POST':
        # Process ticket booking form data and store in database
        first_name = request.form['first_name']
        seat_number = int(request.form['seat_number'])

        # Check if the user is logged in
        if 'user_id' in session:
            user_id = session['user_id']

            cur = mysql.connection.cursor()

            # Check if the selected seat is available
            cur.execute('SELECT seat_status FROM available_seats WHERE seat_number = %s', (seat_number,))
            result = cur.fetchone()

            if result and result['seat_status'] == 'available':
                # Insert booked ticket into booked_tickets table
                cur.execute('INSERT INTO booked_tickets (user_id, name, seat_number) VALUES (%s, %s, %s)', (user_id, first_name, seat_number))

                # Update seat status to 'notavailable' in available_seats table
                cur.execute('UPDATE available_seats SET seat_status = %s WHERE seat_number = %s', ('notavailable', seat_number))

                mysql.connection.commit()
                cur.close()

    return redirect(url_for('book_tickets'))

# Route to display the booked tickets for the current user
@app.route('/my_tickets')
def my_tickets():
    if 'user_id' in session:
        # Fetch booked tickets for the current user
        user_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM booked_tickets WHERE user_id = %s', (user_id,))
        booked_tickets = cur.fetchall()
        cur.close()

        return render_template('mytickets.html', booked_tickets=booked_tickets)

    # If user is not logged in, redirect to login page
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
