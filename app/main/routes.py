from app.main import bp
from flask import render_template, redirect
from flask_login import login_required

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')

@bp.route('/club')
@login_required
def club_index():
    return render_template('clubs/club_list.html')