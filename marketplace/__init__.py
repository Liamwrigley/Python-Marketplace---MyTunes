import os
import datetime

# uncomment for heroku
# import psycopg2


#import flask - from the package import class
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .util.filters import datetimeformat, excerpt

db=SQLAlchemy()

#create a function that creates a web application
# a web server will run this web application
def create_app():

    app=Flask(__name__)  # this is the name of the module/package that is calling this app
    app.debug=True
    app.secret_key='supersecretkey'
    #set the app configuration data

    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///marketplace.sqlite'

    # uncomment for Heroku
    # app.config['SQLALCHEMY_DATABASE_URI']= os.environ['DATABASE_URL']
    # conn = psycopg2.connect(DATABASE_URL, sslmode='require')

    #initialize db with flask app
    db.init_app(app)

    bootstrap = Bootstrap(app)

    #initialize the login manager
    login_manager = LoginManager()

    #set the name of the login function that lets user login
    # in our case it is auth.login (blueprintname.viewfunction name)
    login_manager.login_view='auth.login'
    login_manager.init_app(app)

    #create a user loader function takes userid and returns User
    #from .models import User, Listing  # importing here to avoid circular references
    from .models import User, Listing
    from flask_login import current_user
    @login_manager.user_loader
    def load_user(user_id):
       return User.query.get(int(user_id))

    # Error handing - passes through error code and template forms based on code
    @app.errorhandler(Exception)
    def handle_error(e):
        return render_template("error.html", error=e.code)

    @app.context_processor
    def get_genres():
        genres = Listing.query.with_entities(Listing.genre).filter(Listing.available==True).order_by(Listing.genre.desc()).distinct()
        years = Listing.query.with_entities(Listing.release_year).filter(Listing.available==True).order_by(Listing.release_year.desc()).distinct()
        return dict(nav_genres=genres, nav_years=years)

    #importing views module here to avoid circular references
    # a commonly used practice.
    from . import views
    app.register_blueprint(views.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    from .listings import bp
    app.register_blueprint(bp)

    app.jinja_env.filters['datetimeformat'] = datetimeformat
    app.jinja_env.filters['excerpt'] = excerpt

    return app
