import os
from flask import (
    Blueprint, flash, render_template, request, url_for, redirect
)
from .models import Listing,User #add Comment back later
from .forms import ListingForm #add comment form later
from . import db
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import app

#create a blueprint
bp = Blueprint('listing', __name__, url_prefix='/listing')


#-------------------------------------------------------------------

#-----/show/id-----
#create a page that will show the details fo the destination
@bp.route('/<int:id>')
def show(id):
  listing = Listing.query.filter_by(id=id).first()
  # cform = CommentForm()
  user = User.query.filter_by(id=listing.owner_id).first()
  return render_template('listings/show.html', listing=listing, user=user) #, form=cfor
#-----/show/id-----END

#-----/my_listings-----
#Shows all listings belonging to current user
@bp.route('/my_listings')
@login_required   #decorator between the route and view function
def my_listings():
  listing = Listing.query.filter_by(owner_id=current_user.id).all()
  return render_template('listings/currently-listed.html', listing=listing)
#-----/my_listings-----END

#-----/create-----
@bp.route('/create', methods = ['GET', 'POST'])
@login_required   #decorator between the route and view function
def create():
  listing_form = ListingForm()
  if listing_form.validate_on_submit():
    # on successful validation add data
    listing = Listing(name=listing_form.name.data,
                artist=listing_form.artist.data,
                description=listing_form.description.data,
                image=('/static/listing_images/' + listing_form.image.data.filename),
                price=listing_form.price.data,
                genre=listing_form.genre.data,
                owner_id=current_user.id)

    if request.method == 'POST':
      f = listing_form.image.data
      f.save(os.path.join('marketplace\\static\\listing_images', secure_filename(f.filename)))

    # push to db
    db.session.add(listing)
    db.session.commit()

    flash('Successfully created new listing', 'success')

    #redirect to created listing
    return redirect(url_for('listing.show', id=listing.id))

  return render_template('listings/create.html', form=listing_form, heading='Create Listing')
#-----/create-----END

#-----/edit/id-----
@bp.route('/edit/<int:id>', methods = ['GET', 'POST'])
@login_required   #decorator between the route and view function
def edit(id):
  listing = Listing.query.filter_by(id=id).first()

  #check if current user is poster of listing
  if (current_user.id == listing.owner_id):
    listing_form = ListingForm()
    if listing_form.validate_on_submit():
      listing.name=listing_form.name.data
      listing.artist=listing_form.artist.data
      listing.description=listing_form.description.data
      listing.image=('/static/listing_images/' + listing_form.image.data.filename)
      listing.price=listing_form.price.data
      listing.genre=listing_form.genre.data
      listing.owner_id=current_user.id

      if request.method == 'POST':
        f = listing_form.image.data
        f.save(os.path.join('marketplace\\static\\listing_images', secure_filename(f.filename)))

      # update db
      db.session.commit()

      flash('Successfully edited listing', 'success')

      #redirect to created listing
      return redirect(url_for('listing.show', id=id))
  else:
    return redirect(url_for('listing.show', id=id))

  return render_template('listings/create.html', form=listing_form, heading='Edit Listing')
#-----/edit/id-----END

# @bp.route('/<destination>/comment', methods = ['GET', 'POST'])
# @login_required
# def comment(destination):
#     form = CommentForm()
#     #get the destination object associated to the page and the comment
#     destination_obj = Destination.query.filter_by(id=destination).first()
#     if form.validate_on_submit():
#       #read the comment from the form
#       comment = Comment(text=form.text.data,
#                         destination=destination_obj, user=current_user)
#       #here the back-referencing works - comment.destination is set
#       # and the link is created
#       db.session.add(comment)
#       db.session.commit()

#       #flashing a message which needs to be handled by the html
#       flash('Your comment has been added', 'success')
#     # using redirect sends a GET request to destination.show
#     return redirect(url_for('destination.show', id=destination))
