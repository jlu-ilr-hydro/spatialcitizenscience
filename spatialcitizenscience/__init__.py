__version__ = '2022.01.31a0'
import os

if __name__ == "__main__":
    from .app import app
    os.environ['FLASK_DEBUG'] = 1
    app.run(debug=True)  # server neustart bei Veraenderungen wird vermieden

