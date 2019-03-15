from flask import (Blueprint, render_template, flash, request, redirect, url_for,
                   current_app)

user = Blueprint('user', __name__)


@user.route('/profile')
def profile():
    social = current_app.extensions['social']
    return render_template(
        'user/profile.html',
        #content='Profile Page',
        #twitter_conn=social.twitter.get_connection(),
        #facebook_conn=social.facebook.get_connection()
        #foursquare_conn=social.foursquare.get_connection()
        )