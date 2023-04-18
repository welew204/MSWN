import os

from flask import Flask

from flask_cors import CORS


def create_app(test_config=None):
    # create and config the app
    app = Flask(__name__, instance_relative_config=True)

    db_string = os.environ.get('DB')

    CORS(app, origins='*')
    app.config.from_mapping(
        # replace the filename string w/ a variable puled from os.environ('database')
        # just add simDB to the /instances file, then the environ variable points to the right one
        # this should be overidden w/ random value when deploying for security
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, db_string)

    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test_config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/health")
    def health():
        return "<h1>Health check!</h1>"
        # what else could I have RUN here that exposes some good stuff??

    with app.app_context():
        from . import f_db
        f_db.init_app(app)

        from . import add_mover
        add_mover.add_user_to_app(app)

        from . import simulate_workout
        simulate_workout.run_simulated_CARs(app)
        simulate_workout.run_simulated_workout(app)

        from . import crud_bp
        app.register_blueprint(crud_bp.bp)
        app.add_url_rule('/', endpoint='index')

        return app
