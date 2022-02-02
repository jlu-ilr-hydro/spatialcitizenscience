__version__ = '2022.01.31a0'
import os
from .app import create_app

if __name__ == "__main__":
    app = create_app()
    os.environ['FLASK_DEBUG'] = 1
    app.run(debug=True)  # server neustart bei Veraenderungen wird vermieden

