# Filename: app.py
from flask import Flask # import Flask in Python
app = Flask(__name__) # creates an instance of a Flask app
@app.route('/') # route called by user
def index(): # function called by '/' route
    return render_template('index.html')
app.run(host='0.0.0.0', port=8000) # starts the web app at port 8000
