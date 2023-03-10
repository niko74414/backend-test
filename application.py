from src.settings import application
from src.scripts.routes import base_blueprint

application.register_blueprint(base_blueprint)

if __name__ == '__main__':
    application.run()
