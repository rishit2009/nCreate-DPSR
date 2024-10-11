from Tool import app, db, login_manager
from Tool.models import User, Club, Forum, Comment
from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/null-club')
def null_club():
    nc = Club(name='null')
    db.session.add(nc)
    db.session.commit()
    return 'Added successfully'


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        passw = request.form['password']
        new_user = User(name=name, email=email, password=passw)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        passw = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(passw):
            login_user(user)
        return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/clubs')
@login_required
def view_clubs():
    clubs = Club.query.all()
    return render_template('all_clubs.html', clubs=clubs)


@app.route('/request/<cid>', methods=['POST'])
@login_required
def request_club(cid):
    club = db.session.get(Club, cid)
    club.requesters.append(current_user)
    current_user.add_notification(f'Requested to join {club.name}')
    db.session.commit()
    return redirect(url_for('view_clubs'))


@app.route('/club/<cid>')
@login_required
def club(cid):
    club = db.session.get(Club, cid)
    return render_template('club.html', club=club)


@app.route('/accept/<uid>/<cid>', methods=['POST'])
@login_required
def accept(uid, cid):
    club = db.session.get(Club, cid)
    if current_user not in club.managers:
        return redirect(url_for('index'))
    
    user = db.session.get(User, uid)
    if user not in club.requesters:
        return redirect(url_for('index'))

    club.members.append(user)
    club.requesters.remove(user)
    user.add_notification(f'You have been accepted to {club.name}')
    db.session.commit()
    return redirect(url_for('view_clubs'))


@app.route('/reject/<uid>/<cid>', methods=['POST'])
@login_required
def reject(uid, cid):
    club = db.session.get(Club, cid)
    if current_user not in club.managers:
        return redirect(url_for('index'))

    user = db.session.get(User, uid)
    if user not in club.requesters:
        return redirect(url_for('index'))

    club.requesters.remove(user)
    user.add_notification(f'You have been rejected from {club.name}')
    db.session.commit()
    return redirect(url_for('view_clubs'))


@app.route('/promote/<uid>/<cid>', methods=['POST'])
@login_required
def promote(uid, cid):
    club = db.session.get(Club, cid)
    if current_user not in club.managers:
        return redirect(url_for('index'))

    user = db.session.get(User, uid)
    if user not in club.members:
        return redirect(url_for('index'))

    club.managers.append(user)
    user.add_notification(f'You have been promoted to manager in {club.name}')
    db.session.commit()
    return redirect(url_for('view_clubs'))


@app.route('/demote/<uid>/<cid>', methods=['POST'])
@login_required
def demote(uid, cid):
    club = db.session.get(Club, cid)
    if current_user not in club.managers:
        return redirect(url_for('index'))

    user = db.session.get(User, uid)
    if user not in club.managers:
        return redirect(url_for('index'))

    club.managers.remove(user)
    user.add_notification(f'You are no longer a manager in {club.name}')
    db.session.commit()
    return redirect(url_for('view_clubs'))


@app.route('/remove/<uid>/<cid>', methods=['POST'])
@login_required
def remove(uid, cid):
    club = db.session.get(Club, cid)
    if current_user not in club.managers:
        return redirect(url_for('index'))

    user = db.session.get(User, uid)
    if user not in club.members:
        return redirect(url_for('index'))

    club.members.remove(user)

    if user in club.managers:
        club.managers.remove(user)
    
    user.add_notification(f'You are no longer a member of {club.name}')
    db.session.commit()
    return redirect(url_for('view_clubs'))


@app.route('/leave/<cid>', methods=['POST'])
@login_required
def leave(cid):
    club = db.session.get(Club, cid)

    if current_user in club.managers:
        club.managers.remove(current_user)
        club.members.remove(current_user)
    elif current_user in club.members:
        club.members.remove(current_user)
    else:
        return redirect(url_for('index'))

    current_user.add_notification(f'You have left {club.name}')
    db.session.commit()
    return redirect(url_for('view_clubs'))


@app.route('/create-club', methods=['POST'])
@login_required
def create_club():
    name = request.form['name']
    club = Club(name=name)
    club.managers.append(current_user)
    club.members.append(current_user)
    db.session.add(club)
    db.session.commit()
    return redirect(url_for('club', cid=club.id))


@app.route('/test')
def test():
    see_forums()  # Corrected call
    return render_template('test.html')


@app.route('/forums')
@login_required
def view_forums():
    forums = Forum.query.all()
    return render_template('forums.html', forums = forums)

@app.route('/forum/<fid>')
@login_required
def view_forum(fid):
    forum = db.session.get(Forum, fid)
    if not forum:
        # Handle case where forum does not exist
        return "Forum not found", 404
    comments = Comment.query.filter_by(forum_id=forum.id).all()
    return render_template('forum.html', forum=forum, comments=comments)


@app.route('/join-forum/<fid>', methods=['POST'])
@login_required
def join_forum(fid):
    forum = db.session.get(Forum, fid)
    if not forum:
        return "Forum not found", 404
    forum.members.append(current_user)
    db.session.commit()
    return redirect(url_for('view_forum', fid=fid))


@app.route('/comment/<fid>', methods=['POST'])
@login_required
def comment(fid):
    content = request.form['comment']
    if not content:
        return "Comment cannot be empty", 400
    
    comment = Comment(content=content, forum_id=fid, user_id=current_user.id)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('view_forum', fid=fid))


@app.route('/create-forum', methods=['GET', 'POST'])
@login_required
def create_forum():
    if request.method == 'GET':
        return render_template('create_forum.html')
    elif request.method == 'POST':
        name = request.form['name']
        forum = Forum(name=name)
        forum.members.append(current_user)
        db.session.add(forum)
        db.session.commit()
        return redirect(url_for('view_forum', fid=forum.id))


def see_forums():
    forums = Forum.query.all()
    for forum in forums:  # Corrected from 'for forum in forum'
        print(forum.name)
        print('Members:', forum.members)
        print('Comments:', forum.comments)






if __name__ == '__main__':
    app.run(debug=True)
