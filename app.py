from Tool import app, db, login_manager
from Tool.models import User, Club, Forum, Comment, Event, SubEvent, Submission
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/null-club')
def null_club():
    nc = Club(name='null', description = 'null')
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
        desc = request.form['description']

        new_user = User(name=name, email=email, password=passw, description = desc)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        if 'profile_pic' not in request.files:
            flash('No file part')
            print('No file part')
            print('Request files:', request.files)
            return redirect(request.url)

        file = request.files['profile_pic']
    
        if file.filename == '':
            flash('No selected file')
            print('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
        # Assuming you want to use the user's ID for the filename
            filename = f"{new_user.id}.{file.filename.rsplit('.', 1)[1].lower()}"  # Adjust extension as needed
            filepath = ('Tool/static/images/users/'+ filename)
            file.save(filepath)

            new_user.profile_pic = '../static/images/users/' + filename  # Save the file path to the user's profile
            db.session.commit()

            
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


@app.route('/user/<uid>')
@login_required
def user_profile(uid):
    user = db.session.get(User, uid)
    club = db.session.get(Club, user.club_id)
    print(user.profile_pic)
    return render_template('user.html', user = user, club = club)


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

@app.route('/cancel-request/<cid>', methods=['POST'])
@login_required
def cancel_request_club(cid):
    club = db.session.get(Club, cid)
    if current_user in club.requesters:
        club.requesters.remove(current_user)
        current_user.add_notification(f'You have canceled your request to join {club.name}')
        return True
    return False

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
        return False
    
    user = db.session.get(User, uid)
    if user not in club.requesters:
        return False
    
    prev_club = db.session.get(Club, user.club_id)
    prev_club.members.remove(user)
    if user in prev_club.managers:
        prev_club.managers.remove(user)
    

    user.club_id = club.id
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


    user.club_id = 1
    
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

    current_user.club_id = 1
    current_user.add_notification(f'You have left {club.name}')
    db.session.commit()
    return redirect(url_for('view_clubs'))


@app.route('/create-club', methods=['POST'])
@login_required
def create_club():

    prev_club = db.session.get(Club, current_user.club_id)
    prev_club.members.remove(current_user)
    if current_user in prev_club.managers:
        prev_club.managers.remove(current_user)
    


    name = request.form['name']
    club = Club(name=name)
    club.managers.append(current_user)
    club.members.append(current_user)
    current_user.club_id = club.id
    db.session.add(club)
    db.session.commit()

    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = club.id
        filepath = os.path.join('static/images/clubs', filename)
        file.save(filepath)
        club.profile_pic = filepath
        db.session.commit()


    return redirect(url_for('club', cid=club.id))


@app.route('/test')
def test():
    see_events()  # Corrected call
    return render_template('test.html')


def see():
    clubs = Club.query.all()
    for i in clubs:
        print(i)
        print("MEMBERS", i.members)
        print("Managers", i.managers)
        print("requesters", i.requesters)


def see_events():
    events = Event.query.all()
    for event in events:
        print(event.name)
        for sub in event.sub_events:
            print('   ', sub.name, ' : ', sub.participant_count, sub.registered_users)



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



@app.route('/events')
@login_required
def view_events():
    events = Event.query.all()

    return render_template('events.html', events = events)


@app.route('/event/<eid>')
@login_required
def event(eid):
    event = db.session.get(Event, eid)
    return render_template('event.html', event = event)


@app.route('/create-event', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'GET':
        managed_clubs = current_user.managed_club
        return render_template('create_event.html', managed_clubs=managed_clubs)
    elif request.method == 'POST':
        club_id = current_user.club_id
        club = db.session.get(Club, club_id)
        if current_user not in club.managers:
            current_user.add_notification('You must be a manager to create an event')
            return redirect(url_for('index'))
        event_name = request.form['event_name']
        event = Event(name=event_name, host_id=club_id)
        db.session.add(event)
        db.session.commit() 

        sub_event_count = 0
        for key, value in request.form.items():
            if key.startswith('sub_event_name_'):
                sub_event_count += 1
                sub_event_name = value
                sub_event_participants = request.form[f'sub_event_participants_{sub_event_count}']

                sub_event = SubEvent(
                    event_id=event.id,
                    name=sub_event_name,
                    participant_count=sub_event_participants
                )
                db.session.add(sub_event)
        db.session.commit()
        return redirect(url_for('view_events'))
    

@app.route('/register-event/<eid>', methods = ['GET', 'POST'])
@login_required
def register_event(eid):
    event = db.session.get(Event, eid)
    club = db.session.get(Club, current_user.club_id)
    if request.method == 'GET':
        return render_template('register_event.html', event = event, club = club)
    elif request.method == 'POST':
        if current_user not in club.managers:
            current_user.add_notification('You must be a manager of a club to register')
            return redirect(url_for('index'))
        for sube in event.sub_events:
            for i in range(sube.participant_count):
                participant_id = request.form.get(f'sub_event_{sube.id}_participant_{i+1}')
                if participant_id :
                    pcpt = db.session.get(User, participant_id)
                    sube.registered_users.append(pcpt)
                    pcpt.add_notification(f'You have been registered for {sube.name} at {event.name}.')
        current_user.add_notification(f'Succesfully registered for {event.name}. You may edit you submission at the registration page before the registration ends')
        return redirect(url_for('index'))
    

@app.route('/submit/<eid>/<sid>', methods = ['GET', 'POST'])
def submit(eid, sid):
    event = db.session.get(Event, eid)
    s_event = db.session.get(SubEvent, sid)
    if request.method == 'GET':
        if (current_user not in s_event.registered_users):
            current_user.add_notification('You must be registered for an event to submit.')
            return redirect(url_for('index'))
        return render_template('submit.html', event = event, sub_event = s_event)
    if request.method == 'POST':
        sub_link = request.form['submission_link']
        sub = Submission(
            club_id = current_user.club_id,
            sub_event_id = s_event.id,
            submission_link = sub_link
        )

        db.session.add(sub)
        db.session.commit()


        return redirect(url_for('index'))


@app.route('/declare-result/<eid>', methods = ['GET', 'POST'])
@login_required
def declare_result(eid):
    event = db.session.get(Event, eid)
    if request.method == 'GET':
        return render_template('declare_reesult.html')
    elif request.method == 'POST':
        club = db.session.get(Club, current_user.club_id)
        if current_user.club_id != event.host_id:
            return redirect(url_for('index'))
        if current_user not in club.managers:
            current_user.add_notification('You must be a manager of the host club to declare results')
            return redirect(url_for('index'))
        
        for sub_event in event.sub_events:
            # Set the club IDs for the winners from the form data
            sub_event.first_place_club_id = request.form.get(f'sub_event_{sub_event.id}_first')
            sub_event.second_place_club_id = request.form.get(f'sub_event_{sub_event.id}_second')
            sub_event.third_place_club_id = request.form.get(f'sub_event_{sub_event.id}_third')

            # Notify the first place users
            first_users = User.query.filter(
                User.club_id == sub_event.first_place_club_id,
                User.registered_sub_events.contains(sub_event)
            ).all()

            for user in first_users:
                user.add_notification(f'Congratulations! You have won 1st position in {sub_event.name} at {event.name}')

            # Notify the second place users
            second_users = User.query.filter(
                User.club_id == sub_event.second_place_club_id,
                User.registered_sub_events.contains(sub_event)
            ).all()

            for user in second_users:
                user.add_notification(f'Congratulations! You have won 2nd position in {sub_event.name} at {event.name}')

            # Notify the third place users
            third_users = User.query.filter(
                User.club_id == sub_event.third_place_club_id,
                User.registered_sub_events.contains(sub_event)
            ).all()

            for user in third_users:
                user.add_notification(f'Congratulations! You have won 3rd position in {sub_event.name} at {event.name}')

            db.session.commit()

        for mn in club.managers:
            mn.add_notification(f'{current_user.name} declared results for {event.name}. It may be changed before the results declaration date from the same page.')

        return redirect(url_for('index'))
            




        
        
     


if __name__ == '__main__':
    app.run(debug=True)
