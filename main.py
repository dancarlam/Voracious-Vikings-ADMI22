#importing libraries needed


from flask import Flask, render_template

#Creates flask app
app = Flask(__name__)

#creates a route for the flask app
@app.route('/')
def root():
    
    # returns the final HTML template 
    return render_template('index.html')
    

if __name__ == '__main__':
    
    #127.0.0.1 = loop back port(port of own computer)
    app.run(host='127.0.0.1', port=8080, debug=True)
    #Waits for request, port directs traffic to particular process
