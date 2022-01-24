from .webinterface import app
import os

if __name__ == "__main__":
    os.environ['FLASK_DEBUG'] = 1
    app.run(debug=True)  # server neustart bei Veraenderungen wird vermieden
