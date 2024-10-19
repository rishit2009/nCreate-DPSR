from Tool import app, db, login_manager
from Tool.models import User, Club, Forum, Comment, Event, SubEvent, Submission, Skill, user_sub_event_positions
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
import os
from PIL import Image
from datetime import datetime


def get_average_color_hex(image_path):
    # Open the image
    try:
        with Image.open(image_path) as img:
            # Resize image to a smaller size for faster processing (optional)
            img = img.resize((50, 50))  # Resizing reduces the processing time
            
            # Get the pixels of the image
            pixels = img.getdata()
            
            # Initialize variables to store the sum of RGB values
            r_total = g_total = b_total = 0
            pixel_count = len(pixels)
            
            # Loop through each pixel and sum up the RGB values
            for r, g, b in pixels:
                r_total += r
                g_total += g
                b_total += b
            
            # Calculate the average RGB values
            avg_r = r_total // pixel_count
            avg_g = g_total // pixel_count
            avg_b = b_total // pixel_count
            
            # Convert the average RGB values to hex format
            avg_color_hex = "#{:02x}{:02x}{:02x}".format(avg_r, avg_g, avg_b)
            
            return avg_color_hex
    except:
        return '#eb0037'



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


@app.route('/_add-skills')
def _add_skills():
    skills = [
    # Web Development
    'HTML', 'CSS', 'JavaScript', 'React', 'Angular', 'Vue.js',
    'Bootstrap', 'Tailwind CSS', 'TypeScript', 'Sass', 'jQuery',
    'Webpack', 'Parcel', 'Node.js', 'Express.js', 'Django', 
    'Flask', 'Ruby on Rails', 'PHP', 'Laravel', 'Spring Boot', 
    'Go', 'Rust', 'SQL', 'NoSQL', 'MongoDB', 'Firebase', 
    'MySQL', 'PostgreSQL',
    
    # Data Analysis
    'Python', 'R', 'SQL', 'MATLAB', 'Pandas', 'NumPy', 'SciPy', 
    'Matplotlib', 'Seaborn', 'TensorFlow', 'PyTorch', 'Scikit-learn', 
    'Jupyter', 'Anaconda', 'Excel', 'PowerBI', 'Tableau', 'Google Analytics', 
    'Hadoop', 'Apache Spark',

    # Game Development
    'C#', 'C++', 'Java', 'Python', 'Unity', 'Unreal Engine', 
    'Godot', 'Blender', 'Maya', '3ds Max', 'Photoshop', 'Illustrator', 
    'OpenGL', 'DirectX', 'Vulkan', 'WebGL',

    # Competitive Programming
    'C++', 'Python', 'Java', 'C', 'Go', 'Rust', 'Kotlin', 
    'Swift', 'LeetCode', 'Codeforces', 'HackerRank', 'Git', 'GitHub',

    # Video Editing
    'Adobe Premiere Pro', 'Final Cut Pro', 'DaVinci Resolve', 
    'After Effects', 'Video Transitions', 'Color Grading', 
    'Motion Tracking', 'Audio Syncing', 'Storyboarding', 'Scriptwriting',

    # Design (UI/UX, Graphic Design)
    'Figma', 'Sketch', 'Adobe XD', 'InVision', 'Axure RP', 
    'Balsamiq', 'Adobe Photoshop', 'Adobe Illustrator', 
    'Adobe InDesign', 'Canva', 'CorelDRAW', 'Principle', 
    'ProtoPie', 'Framer'
]

    for skill_name in skills:
    # Check if the skill already exists
        existing_skill = Skill.query.filter_by(name=skill_name).first()
        if not existing_skill:
            skill = Skill(name=skill_name)
            db.session.add(skill)

    db.session.commit()

    return 'Success'


@app.route('/register', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        passw = request.form['password']
        desc = request.form['description']

        new_user = User(name=name, email=email, password=passw, description=desc)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        selected_skills = request.form.getlist('skills')

        for skill_data in selected_skills:
            if skill_data.isdigit():
                skill = db.session.get(Skill, int(skill_data))
            else:
                skill = Skill.query.filter_by(name=skill_data).first()
                if not skill:
                    skill = Skill(name=skill_data)
                    db.session.add(skill)
                    db.session.commit()
            new_user.skills.append(skill)

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
            # Ensure the directory exists
            user_image_dir = 'Tool/static/images/users/'
            os.makedirs(user_image_dir, exist_ok=True)  # Create the directory if it doesn't exist
            
            filename = f"{new_user.id}.{file.filename.rsplit('.', 1)[1].lower()}"
            filepath = os.path.join(user_image_dir, filename)  # Construct the full file path
            file.save(filepath)

            new_user.banner_color = get_average_color_hex(filepath)
            new_user.profile_pic = f'../static/images/users/{filename}'  # Save the file path to the user's profile
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
    if not user : return url_for('index')
    club = db.session.get(Club, user.club_id)
    achs = []
    if user.won_sub_events:
        for sube in user.won_sub_events:
            pos = db.session.query(user_sub_event_positions.c.position).filter_by(
                user_id=user.id, sub_event_id=sube.id
            ).scalar()
            ename = db.session.query(Event, sube.event_id).first().name
            pos_dict = {1 : '1st', 2 : '2nd', 3 : '3rd'}
            achs.append(f'Achieved {pos_dict[pos]} postion at {sube.name} at {ename}')
    else :
        achs = ['Theres nothing here yet :( ']

    return render_template('user.html', user = user, club = club, achievements = achs)


@app.route('/clear_notif/<uid>', methods=['POST'])
def _clear_notifs(uid):
    user = db.session.get(User, uid)
    if user:
        user.clear_notifications()  # Assuming this method clears notifications
        db.session.commit()  # Commit the transaction if necessary
        return jsonify({'success': True, 'message': 'Notifications cleared successfully.'}), 200
    else:
        return jsonify({'success': False, 'message': 'User not found.'}), 404

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

    won_sub_events = db.session.query(
        SubEvent, user_sub_event_positions.c.position
    ).join(
        user_sub_event_positions, SubEvent.id == user_sub_event_positions.c.sub_event_id
    ).join(
        User, User.id == user_sub_event_positions.c.user_id
    ).filter(
        User.club_id == cid  # Filter by the club ID
    ).all()


    return render_template('club.html', club=club, wse = won_sub_events)




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

@app.route('/manage-club/<cid>')
@login_required
def manage_club(cid):
    club = db.session.get(Club, cid)
    if current_user not in club.managers:
        return redirect(url_for('index'))
    return render_template('manage_club.html' , club = club)


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
    db.session.add(current_user)
    db.session.commit()
    print(current_user.club_id)
    return redirect(url_for('clubs'))

 
@app.route('/create-club', methods=['POST', 'GET'])
@login_required
def create_club():
    if request.method == 'GET':
        return render_template('create_club.html')
    
    elif request.method == 'POST':
        # Remove the user from their previous club (if they had one)
        prev_club = db.session.get(Club, current_user.club_id)
        if prev_club:
            prev_club.members.remove(current_user)
            if current_user in prev_club.managers:
                prev_club.managers.remove(current_user)

        # Get form data
        name = request.form['name']
        description = request.form['description']
        email = request.form['email']

        # Create a new club and associate the current user as a manager and member
        club = Club(name=name, description=description, email=email)
        club.managers.append(current_user)
        club.members.append(current_user)
        db.session.add(club)
        db.session.commit()

        # Handle file upload for the profile picture
        if 'profile_pic' not in request.files:
            print('No file part')
            return redirect(request.url)
        
        file = request.files['profile_pic']
        
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            user_image_dir = 'Tool/static/images/clubs/'
            os.makedirs(user_image_dir, exist_ok=True) 
            filename = (f"{club.id}.{file.filename.rsplit('.', 1)[1].lower()}")
            filepath = os.path.join('Tool/static/images/clubs/', filename)
            
            # Save the file to the desired path
            file.save(filepath)
            
            # Update the club's profile_pic field
            club.profile_pic = '../static/images/clubs/' + filename
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
    forum = Forum.query.get_or_404(fid)

    # Get the comment content from the AJAX request
    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({'success': False, 'error': 'No content provided'}), 400

    # Create a new comment
    comment = Comment(
        forum_id=forum.id,
        user_id=current_user.id,
        content=content,
        datetime=datetime.now()  
    )

    # Save the comment to the database
    db.session.add(comment)
    db.session.commit()

    # Return the comment as JSON response
    return jsonify({
        'success': True,
        'comment': {
            'content': comment.content,
            'datetime': comment.datetime.strftime('%d %B, %I:%M %p')
        },
        'user': {
            'username': current_user.name,
            'profile_pic' : current_user.profile_pic
        }
    })


@app.route('/create-forum', methods=['GET', 'POST'])
@login_required
def create_forum():
    if request.method == 'GET':
        return render_template('create_forum.html') 
    elif request.method == 'POST':
        name = request.form['name']
        desc = request.form['description']
        forum = Forum(name=name, description=desc)
        forum.members.append(current_user)
        db.session.add(forum)
        db.session.commit()

        if 'profile_pic' not in request.files:
            print('No file part')
            return redirect(request.url)
        
        file = request.files['profile_pic']
        
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            user_image_dir = 'Tool/static/images/forums/'
            os.makedirs(user_image_dir, exist_ok=True) 
            filename = (f"{forum.id}.{file.filename.rsplit('.', 1)[1].lower()}")
            filepath = os.path.join('Tool/static/images/forums/', filename)
            
            # Save the file to the desired path
            file.save(filepath)
            
            # Update the club's profile_pic field
            forum.profile_pic = '../static/images/forums/' + filename
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
    host_club = db.session.get(Club, event.host_id)
    return render_template('event.html', event = event, host = host_club)


@app.route('/create-event', methods=['GET', 'POST'])
@login_required
def create_event():
    club_id = current_user.club_id
    club = db.session.get(Club, club_id) 
    if request.method == 'GET':
        if current_user not in club.managers:
            current_user.add_notification('You must be a manager to create an event')
            return redirect(url_for('index'))

        return render_template('create_event.html')
    
    elif request.method == 'POST':

        for key, value in request.form.items():
            print(key, value) 
        
        
        # Event Details
        event_name = request.form['event_name']
        event_description = request.form['event_description']
        brochure_link = request.form['brochure']

        # Convert date inputs to Python datetime objects
        registration_end_date = datetime.strptime(request.form.get('date1'), '%Y-%m-%d')
        prompts_date = datetime.strptime(request.form.get('date2'), '%Y-%m-%d')
        submission_date = datetime.strptime(request.form.get('date3'), '%Y-%m-%d')
        event_date = datetime.strptime(request.form.get('date4'), '%Y-%m-%d')

        # Create Event Object
        event = Event(
            name=event_name,
            host_id=club_id,
            description=event_description,
            brochure_link=brochure_link,
            registration_end_date=registration_end_date,
            prompts_date=prompts_date,
            submission_date=submission_date,
            event_date=event_date
        )

        db.session.add(event)
        db.session.commit()

        # Sub-Event Details
        sub_event_count = 0
        for key, value in request.form.items():
            if key.startswith('sub_event_name_'):
                sub_event_count += 1
                sub_event_name = value
                sub_event_participants = request.form[f'sub_event_participants_{sub_event_count}']
                sub_event_description = request.form[f'description_{sub_event_count}']
                sub_event_mode = request.form[f'mode_{sub_event_count}']  # Online, Offline, Hybrid
                sub_event_type = request.form[f'type_{sub_event_count}']  # Submission, No Submission
                
                # Determine if submission-based
                is_submission_based = True if sub_event_type == "Submission" else False

                # Create SubEvent Object
                sub_event = SubEvent(
                    event_id=event.id,
                    name=sub_event_name,
                    participant_count=sub_event_participants,
                    description=sub_event_description,
                    event_type=sub_event_mode.lower(),
                    is_submission_based=is_submission_based
                )

                db.session.add(sub_event)

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
            user_image_dir = 'Tool/static/images/events/'
            os.makedirs(user_image_dir, exist_ok=True) 
        # Assuming you want to use the user's ID for the filename
            filename = f"{event.id}.{file.filename.rsplit('.', 1)[1].lower()}"  # Adjust extension as needed
            filepath = ('Tool/static/images/events/'+ filename)
            file.save(filepath)
            
            event.profile_pic = '../static/images/events/' + filename  # Save the file path to the user's profile
            db.session.commit()

        
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
        current_user.add_notification(f'Succesfully registered for {event.name}')
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
    club = db.session.get(Club, current_user.club_id)
    if request.method == 'GET':
        if current_user.club_id != event.host_id:
            current_user.add_notification('You must be a manager of the host club to declare results')
            return redirect(url_for('index'))
        if current_user not in club.managers:
            current_user.add_notification('You must be a manager of the host club to declare results')
            return redirect(url_for('index'))
        return render_template('declare_result.html', event= event)
    elif request.method == 'POST':
    
        
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
                user.won_sub_events.append({
                'sub_event_id': sub_event.id,
                'position': 1
                })


            # Notify the second place users
            second_users = User.query.filter(
                User.club_id == sub_event.second_place_club_id,
                User.registered_sub_events.contains(sub_event)
            ).all()

            for user in second_users:
                user.add_notification(f'Congratulations! You have won 2nd position in {sub_event.name} at {event.name}')
                user.won_sub_events.append({
                'sub_event_id': sub_event.id,
                'position': 2
                })

            # Notify the third place users
            third_users = User.query.filter(
                User.club_id == sub_event.third_place_club_id,
                User.registered_sub_events.contains(sub_event)
            ).all()

            for user in third_users:
                user.add_notification(f'Congratulations! You have won 3rd position in {sub_event.name} at {event.name}')
                user.won_sub_events.append({
                'sub_event_id': sub_event.id,
                'position': 3
                })

            db.session.commit()

        for mn in club.managers:
            mn.add_notification(f'{current_user.name} declared results for {event.name}. It may be changed before the results declaration date from the same page.')

        return redirect(url_for('index'))
            

@app.route('/search_skills')
def search_skills():
    query = request.args.get('q')
    skills = Skill.query.filter(Skill.name.ilike(f'%{query}%')).all()
    return jsonify([{'id': skill.id, 'name': skill.name} for skill in skills])



@app.route('/learn')
@login_required
def learn():
    return render_template('learn.html')
        
@app.route('/learn/cp')
@login_required
def learncp():
    return render_template('learncp.html')

@app.route('/learn/webd')
@login_required
def learnwebd():
    return render_template('learnwebd.html')

@app.route('/learn/av')
@login_required
def learnav():
    return render_template('learnav.html')
        
     


if __name__ == '__main__':
    app.run(debug=True)

# %%
