from app.clubs import bp
from flask import render_template, flash, redirect, url_for, request
from urllib.parse import urlparse
from flask_login import login_required
from flask_login import current_user, login_user, logout_user
from app.models import User, Club, ClubMembership
from app import db
from .forms import ClubForm

@bp.route('/create_club', methods=['GET', 'POST'])
@login_required
def create_club():
    form = ClubForm()
    if form.validate_on_submit():
        club = Club(name=form.name.data, owner_id=current_user.id)
        db.session.add(club)
        db.session.commit()
        flash('Club created successfully.', 'success')
        return redirect(url_for('main.index'))
    return render_template('clubs/club_create.html', form=form)

@bp.route('/join_club/<int:club_id>', methods=['POST'])
@login_required
def join_club(club_id):
    club = Club.query.get(club_id)
    if club:
        if current_user not in club.members:
            club.members.append(current_user)
            db.session.commit()
            flash('You have joined the club.', 'success')
        else:
            flash('You are already a member of this club.', 'warning')
    return redirect(url_for('main.index'))

@bp.route('/club_list', methods=['GET','POST'])
@login_required
def club_list():
    clubs = Club.query.all()
    return render_template('clubs/club_list.html', clubs=clubs)

@bp.route('/club_index/<int:club_id>', methods=['GET','POST'])
@login_required
def club_index(club_id):
    club = Club.query.get(club_id)
    return render_template('clubs/club_index.html', club=club)