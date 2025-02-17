from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os # Import the os module

app = Flask(__name__)
app.secret_key = "hr123"  # Change this to a strong, random key

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

# Route for the registration page
@app.route('/')
def index():
    return render_template('register.html')

# Route for handling registration form submission
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        address = request.form['address']

        conn = get_db_connection()
        c = conn.cursor()

        # Insert data into the database
        c.execute("INSERT INTO users (username, password, firstname, lastname, email, address) VALUES (?, ?, ?, ?, ?, ?)",
                  (username, password, firstname, lastname, email, address))

        conn.commit()
        conn.close()

        session['username'] = username  # Store username in session for redirect

        return redirect(url_for('profile', username=username))
    return render_template('register.html')

# Route for displaying user profile
@app.route('/profile/<username>')
def profile(username):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return render_template('profile.html', user=user)

# Route for the login page
@app.route('/login')
def login():
    return render_template('login.html')

# Route for handling the login form submission
@app.route('/auth', methods=['POST'])
def auth():
    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        session['username'] = username # Store username in session
        return redirect(url_for('profile', username=username))
    else:
        return "Invalid login credentials"

# Extra Credit: File Upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    if file:
        filename = "limerick.txt"  # Fixed filename for simplicity
        filepath = os.path.join("/tmp", filename)  # Store in /tmp
        file.save(filepath)

        # Calculate word count
        with open(filepath, 'r') as f:
            content = f.read()
            word_count = len(content.split())

        session['word_count'] = word_count
        return redirect(url_for('profile', username=session.get('username')))

    return "File upload failed"

# Route to download the uploaded file (Extra Credit)
@app.route('/download')
def download_file():
    filename = "limerick.txt"
    filepath = os.path.join("/tmp", filename)
    return send_from_directory("/tmp", filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80) # Ensure it listens on port 80
