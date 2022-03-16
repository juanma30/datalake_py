from flask import Flask

app = Flask(__name__)

import routes
import control

if __name__ == '__main__':
    app.run(debug=True)
