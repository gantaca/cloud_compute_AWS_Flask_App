from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this!

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('register.html')

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

        c.execute("INSERT INTO users (username, password, firstname, lastname, email, address) VALUES (?, ?, ?, ?, ?, ?)",
                  (username, password, firstname, lastname, email, address))

        conn.commit()
        conn.close()

        session['username'] = username
        return redirect(url_for('profile', username=username))
    return render_template('register.html')

@app.route('/profile/<username>')
def profile(username):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    #Extra Credit -- Word Count.
    word_count = session.get('word_count',0)

    return render_template('profile.html', user=user,word_count=word_count)

@app.route('/login')
def login():
    return render_template('login.html')

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
        session['username'] = username
        return redirect(url_for('profile', username=username))
    else:
        return "Invalid login credentials"

    @app.route('/upload', methods=['POST'])
    def upload_file():
        if 'file' not in request.files:
            return "No file part"

        file = request.files['file']

        if file.filename == '':
            return "No selected file"

        if file:
            filename = "limerick.txt"  # Fixed filename
            filepath = os.path.join("/tmp", filename)  #Temporary file in /tmp
            file.save(filepath)

            # Calculate word count
            with open(filepath, 'r') as f:
                content = f.read()
                word_count = len(content.split())

            session['word_count'] = word_count

            return redirect(url_for('profile', username=session.get('username')))

        return "File upload failed"
    @app.route('/download')
    def download_file():
        filename = "limerick.txt"
        filepath = os.path.join("/tmp", filename)
        return send_from_directory("/tmp", filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)

