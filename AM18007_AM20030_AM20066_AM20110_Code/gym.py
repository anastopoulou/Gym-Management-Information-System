# Import modules
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc

# Set up restAPI
app = Flask(__name__)  # Using Flask
app.secret_key = 'your_secret_key_here'  # And a secret no so secret key
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/gym'  # With a connection with a sql database named gym
db = SQLAlchemy(app)  # Also using SQLAlchemy


# Table request as class Request
class Request(db.Model):
    requestid = db.Column(db.Integer, primary_key=True)  # Primary Key
    username = db.Column(db.String(50), nullable=False)  # User has to enter username and a
    password = db.Column(db.String(50), nullable=False)  # Password
    first_name = db.Column(db.String(50), nullable=False)  # User has to enter a first name and a
    last_name = db.Column(db.String(50), nullable=False)  # Last name
    country = db.Column(db.String(50), nullable=False)  # For their address the user has to enter country,
    town = db.Column(db.String(50), nullable=False)  # City/ Town and
    address = db.Column(db.String(50), nullable=False)  # Address
    email = db.Column(db.String(50), nullable=False)  # User has to enter an email
    approval = db.Column(db.Boolean, nullable=True)  # The request has to be approved for the user to get access
    administrator_adminid = db.Column(db.Integer,
                                      db.ForeignKey('administrator.adminid'))  # Each request has an administrator
    users = db.relationship('User', backref='request', lazy=True)  # And is referenced in each user


# Table administrator as class Administrator
class Administrator(db.Model):
    adminid = db.Column(db.Integer, primary_key=True)  # Primary key
    username = db.Column(db.String(50), nullable=False)  # Administrator has most data similar to user
    password = db.Column(db.String(50), nullable=False)  # Like username, password, first/last name and email
    first_name = db.Column(db.String(50), nullable=False)  # In fact, most administrators were users
    last_name = db.Column(db.String(50), nullable=False)  # So the data is identical
    email = db.Column(db.String(50), nullable=False)  # While administrators can change everything, in the database
    requests = db.relationship('Request', backref='administrator', lazy=True)  # Administrators approve requests
    announcements = db.relationship('Announcement', backref='administrator', lazy=True)  # And appear in announcements


# Table announcement as class Announcements
class Announcement(db.Model):
    announceid = db.Column(db.Integer, primary_key=True)  # Primary Key
    title = db.Column(db.String(50), nullable=False)  # Title of announcement
    description = db.Column(db.String(200), nullable=False)  # Description of announcement
    date = db.Column(db.DateTime, nullable=False)  # Date published
    administrator_adminid = db.Column(db.Integer, db.ForeignKey('administrator.adminid'),
                                      nullable=False)  # Announcements are published with the information of the administrator
    discounts = db.relationship('Discount', backref='announcement',
                                lazy=True)  # Some announcements are connected to discounts


# Table diascount as class Discount
class Discount(db.Model):
    discountid = db.Column(db.Integer, primary_key=True)  # Primary key
    title = db.Column(db.String(50),
                      nullable=False)  # Title, may be used as discount code when financial aspects arise
    description = db.Column(db.String(200), nullable=False)  # Description of discount
    announcement_announceid = db.Column(db.Integer, db.ForeignKey(
        'announcement.announceid'))  # Discounts are connected with announcements
    program_programid = db.Column(db.Integer, db.ForeignKey('program.programid'))  # And a program


# Table program as class Program
# We assume that each program happens daily, and at the same time each day
class Program(db.Model):
    programid = db.Column(db.Integer, primary_key=True)  # Primary key
    title = db.Column(db.String(50), nullable=False)  # Title of program
    description = db.Column(db.String(200), nullable=False)  # Description of program
    max_capacity = db.Column(db.String(10), nullable=False)  # Maximum capacity of program
    discounts = db.relationship('Discount', backref='program', lazy=True)  # Program may be discounted
    scheduleandprograms = db.relationship('ScheduleAndProgram', backref='program',
                                          lazy=True)  # Programs connect with schedule via scheduleandprgram


# Table schedule as class Schedule
class Schedule(db.Model):
    scheduleid = db.Column(db.Integer, primary_key=True)  # Primary key
    day = db.Column(db.Date, nullable=False)  # Day of schedule
    time = db.Column(db.Time, nullable=False)  # Time od schedule
    trainer_trainerid = db.Column(db.Integer, db.ForeignKey('trainer.trainerid'))  # Trainer on duty
    scheduleandprograms = db.relationship('ScheduleAndProgram', backref='schedule',
                                          lazy=True)  # Connects with program via scheduleandprogram
    reservations = db.relationship('Reservation', backref='schedule', lazy=True)  # Appears in reservations


# Table scheduleandprogram and class ScheduleAndProgram
# In between class between schedule and program
class ScheduleAndProgram(db.Model):
    __tablename__ = 'scheduleandprogram'  # Table name because it can be confusing
    schedule_scheduleid = db.Column(db.Integer, db.ForeignKey('schedule.scheduleid'),
                                    primary_key=True)  # Primary key for schedule
    program_programid = db.Column(db.Integer, db.ForeignKey('program.programid'),
                                  primary_key=True)  # Primary key for program


# Table reservation as class reservation
class Reservation(db.Model):
    reservid = db.Column(db.Integer, primary_key=True)  # Primary key
    date = db.Column(db.DateTime, nullable=False)  # Date & Time of when the reservation was made
    cancellation = db.Column(db.Integer, nullable=True)  # State ir reservation: 1 for cancelled null for not cancelled
    user_userid = db.Column(db.Integer, db.ForeignKey('user.userid'))  # Reservations are made by user
    schedule_scheduleid = db.Column(db.Integer,
                                    db.ForeignKey('schedule.scheduleid'))  # And are referring to schedule slots


# Table user as class User
class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True)  # Primary key
    username = db.Column(db.String(50),
                         nullable=False)  # Same as request, users get credentials, like username and password,
    first_name = db.Column(db.String(50), nullable=False)  # Their full (first/last) name,
    last_name = db.Column(db.String(50), nullable=False)  # Their address, country and town
    country = db.Column(db.String(50), nullable=False)  # And are contacted via their email
    town = db.Column(db.String(50), nullable=False)  # All this information is identical with the request they made
    address = db.Column(db.String(50), nullable=False)  # And it can't change, unless an admin wants to do it
    email = db.Column(db.String(50), nullable=False)  # While the username is unique
    password = db.Column(db.String(50),
                         nullable=False)  # The database and this restAPI will be working with the userid
    request_requestid = db.Column(db.Integer, db.ForeignKey('request.requestid'))  # Each user has an approved request
    reservations = db.relationship('Reservation', backref='user', lazy=True)  # Some users make reservations


# Table trainer as class Trainer
class Trainer(db.Model):
    trainerid = db.Column(db.Integer, primary_key=True)  # Primary key
    first_name = db.Column(db.String(50), nullable=False)  # Trainers have basic information
    last_name = db.Column(db.String(50), nullable=False)  # Their name
    email = db.Column(db.String(50), nullable=False)  # And their email
    schedules = db.relationship('Schedule', backref='trainer', lazy=True)  # Trainers appear in schedule slots


# Fishing function: reservation data
def get_user_reservations_by_username(username, use):
    # Find the user id to identify the user in the system
    find_user = (
        db.session.query(User.userid)  # Select userid
        .filter(User.username == username)  # By username
        .subquery()  # Information of the query will be used below
    )
    # Get information about reservations
    first_draft_data = (
        db.session.query(
            Reservation.reservid,  # Select reserveid
            Reservation.date,  # Select time&date the reservation was made
            Reservation.cancellation,  # Select cancellation status: 1 for cancelled null for active
            Schedule.day,  # Select date of appointment
            Schedule.time,  # Select time of appointment
            Program.title,  # Select title of program
            Trainer.first_name,  # Select trainer full name first
            Trainer.last_name  # And last
        )
        .join(find_user,
              find_user.c.userid == Reservation.user_userid)  # Find reservations made by user using query above
        .join(Schedule, Reservation.schedule_scheduleid == Schedule.scheduleid)  # Connect reservation with schedule
        .join(Trainer, Schedule.trainer_trainerid == Trainer.trainerid)  # Connect trainer with schedule
        .join(ScheduleAndProgram,
              Schedule.scheduleid == ScheduleAndProgram.schedule_scheduleid)  # Connect schedule and program
        .join(Program, ScheduleAndProgram.program_programid == Program.programid)  # Via scheduleandprogram
        .order_by(  # The data of the query will be arranged in descending order by
            desc(Reservation.date),  # Reservation time stumps
            desc(Schedule.day),  # Date of appointment when in a tie
            desc(Schedule.time)  # Time of appointment when in a tie
        )
        .all()  # Get all entries available
    )
    if use == 1:  # If the target is active reservations
        # Get current time stumps, separated by
        current_date = datetime.now().date()  # Date
        current_time = datetime.now().time()  # And time
        first_draft_data = [
            entry for entry in first_draft_data  # Alter the first draft data to only include
            if ((entry[3] > current_date)  # Appointments that are on a later date
                or ((entry[3] == current_date)  # Appointments that are the same day are today
                    and (entry[4] > current_time)))  # But at a later time
               and (entry[2] is None)  # Appointments that haven't been cancelled
        ]
        first_draft_data = sorted(  # Then to rearrange the data
            first_draft_data,  # Select first draft
            key=lambda entry: (entry[3], entry[4]),
            # Arrange the draft in ascending order by schedule date and then time
            reverse=True  # Reverse the line to be in descending order
        )
    if first_draft_data:  # If first draft has data
        formed_data = [  # Form the data in an appropriate form
            {
                'Reservation_reservid': entry[0],
                'Reservation_date': entry[1],
                'Reservation_cancellation': 'Yes' if entry[2] else 'No',
                'Schedule_day': entry[3],
                'Schedule_time': entry[4],
                'Program_title': entry[5],
                'Trainer_first_name': entry[6],
                'Trainer_last_name': entry[7],
            } for entry in first_draft_data
        ]
        return formed_data  # Return the formed data
    else:
        return None  # If no data have been found, return none


# Fishing function: announcement data
def get_announcements_data():
    # Get announcement information
    first_draft_data = (
        db.session.query(
            Announcement.title,  # For announcements, select title,
            Announcement.description,  # Description and
            Announcement.date,  # Date
            Discount.title,  # For discounts select title and
            Discount.description,  # description
            Program.title  # Select title of program associated with discount
        )
        .outerjoin(Discount,
                   Announcement.announceid == Discount.announcement_announceid)  # Get all announcements, but find also those that have discounts
        .outerjoin(Program, Discount.program_programid == Program.programid)  # For the discounts, find program
        .order_by(desc(Announcement.date))  # Arrange the data on descending order by announcement date
        .all()  # Get all entries
    )
    if first_draft_data:  # If first draft has data
        formed_data = [  # Form the data in an appropriate form
            {
                'Announcement_title': entry[0],
                'Announcement_description': entry[1],
                'Announcement_date': entry[2],
                'Discount_title': entry[3] if entry[3] is not None else '',  # Not all announcements will be linked to
                # a discount
                'Discount_description': entry[4] if entry[4] is not None else '',
                # In that case, these values are black
                'Program_title': entry[5] if entry[5] is not None else ''
            } for entry in first_draft_data
        ]
        return formed_data  # Return the formed data
    else:
        return None  # If no data have been found, return none


# Fishing function: program information
def get_daily_program_data(db_session, this_day, username=None):
    # Get the programs scheduled for the day with their first appearance times
    first_draft_data = (
        db_session.query(  # For each program
            Program.programid,  # Find the programid
            Program.title,  # The title
            Program.description,  # The description
            Schedule.time,  # The time
            Program.max_capacity  # And the maximum capacity
        )
        .join(ScheduleAndProgram,
              Program.programid == ScheduleAndProgram.program_programid)  # Connect schedule and program
        .join(Schedule, ScheduleAndProgram.schedule_scheduleid == Schedule.scheduleid)  # Via scheduleandprogram
        .group_by(Program.programid)  # Group by programid
        .order_by(func.min(Schedule.time).asc())  # Arrange by time
    )
    if first_draft_data:  # If the first draft has data
        formed_data = [  # Form the data in an appropriate form
            {
                'program_id': entry[0],
                'name': entry[1],
                'description': entry[2],
                'time': str(entry[3]),
                'max_capacity': entry[4],
                'remaining_capacity': find_availability(entry[0], this_day),
                # Available spots in the program on that day
                'user_reserved': user_reserv_exists(username, this_day, entry[0]) if username else False,
                # If username is provided, see if user has a reservation
                'first_name': find_trainer(entry[0], this_day, 0),  # Find the trainer info
                'last_name': find_trainer(entry[0], this_day, 1),  # Find the trainer info
                'is_current_time_past': (
                        this_day > datetime.now().date() or
                        (this_day == datetime.now().date() and
                         datetime.strptime(str(entry[3]), '%H:%M:%S').time() > datetime.now().time())
                )  # If we're looking at today, this condition tells us if the program has happened yet
            }
            for entry in first_draft_data
        ]
        return formed_data  # Returned the formed data
    else:
        return None  # If no data have been found, return none


# Use function: Get the availability of a program at a desired date
def find_availability(program_id, date):
    # Find the capacity of a program
    capacity = (
        db.session.query(Program.max_capacity)  # Select max_capacity
        .filter(Program.programid == program_id)  # Found by programid
        .scalar()  # Get integer number back
    )
    # We only include active reservations for this program on this day. 
    reservations = (
        db.session.query(Reservation)  # Select reserveid
        .join(Schedule, Reservation.schedule_scheduleid == Schedule.scheduleid)  # Connect reservations with schedule
        .join(ScheduleAndProgram,
              Schedule.scheduleid == ScheduleAndProgram.schedule_scheduleid)  # Connect schedule and program
        .join(Program, ScheduleAndProgram.program_programid == Program.programid)  # Via scheduleandprogram
        .filter(Program.programid == program_id)  # Only include reservations for this program
        .filter(Schedule.day == date)  # For this day
        .filter(Reservation.cancellation.is_(None))  # And only the active reservations
        .all()  # Get all entries related
    )
    return int(capacity) - int(len(reservations))  # User can only make a reservation if there is space


# Use function: See if user has made a reservation for a program at a date
def user_reserv_exists(username, date, program):
    reservations = (
        db.session.query(Reservation)  # Select reserveid
        .join(Schedule, Reservation.schedule_scheduleid == Schedule.scheduleid)  # Connect reservations with schedule
        .join(ScheduleAndProgram,
              Schedule.scheduleid == ScheduleAndProgram.schedule_scheduleid)  # Connect schedule and program
        .join(Program, ScheduleAndProgram.program_programid == Program.programid)  # Via scheduleandprogram 
        .join(User, Reservation.user_userid == User.userid)  # Connect reservation to users
        .filter(Program.programid == program)  # Find reservation via program
        .filter(User.username == username)  # Find user by username
        .filter(Schedule.day == date)  # For this day
        .filter(Reservation.cancellation.is_(None))  # And only the active reservations
        .all()  # Get all entries related
    )
    return int(len(reservations)) == 0  # The user has no reservation this day


# Use function: Find the trainer on schedule
def find_trainer(program_id, date, info):
    first_draft_data = (
        db.session.query(  # Find Trainer information
            Trainer.first_name,  # This includes first
            Trainer.last_name  # And last name
        )
        .join(Schedule, Schedule.trainer_trainerid == Trainer.trainerid)  # Connect schedule and trainer
        .join(ScheduleAndProgram,
              Schedule.scheduleid == ScheduleAndProgram.schedule_scheduleid)  # Connect schedule and program
        .join(Program, ScheduleAndProgram.program_programid == Program.programid)  # Via scheduleandprogram 
        .filter(Schedule.day == date)  # Only for a certain day
        .filter(ScheduleAndProgram.program_programid == program_id)  # And for a certain program
        .all()  # Get all entries related
    )
    trainers = [{'first_name': first_name, 'last_name': last_name} for first_name, last_name in
                first_draft_data]  # Form the data
    if info == 0:  # Return the information
        return trainers[0]['first_name'] if trainers else None
    elif info == 1:
        return trainers[0]['last_name'] if trainers else None
    else:
        return None


# Set up function: home page
@app.route('/', methods=['GET'])
def get_home_information_data():
    return render_template('home.html')  # Set up page


# Set up function: User panel page
@app.route('/user', methods=['GET'])
def get_user_information_data():
    announcements = get_announcements_data()  # Get announcement information
    username = session['username'] # get the username of the currently logged in user
    reservations = get_user_reservations_by_username(username, 1)  # Get all active reservations
    return render_template('user.html', announcements=announcements, reservations=reservations,username=username)  # Set up page


# Button function: Cancel reservation by reserveid
# Accessed by button in user.html
@app.route('/user/cancel_reservation/<int:Reservation_reservid>', methods=['POST'])
def cancel_reservation(Reservation_reservid):
    # Find the reservation picked
    this_reservation = (
        db.session.query(
            Reservation.cancellation,  # Select cancellation status
            Schedule.day,  # Select day of reservation
            Schedule.time  # Select time of reservation
        )
        .join(Schedule, Reservation.schedule_scheduleid == Schedule.scheduleid)  # Connect reservation and schedule
        .filter(Reservation.reservid == Reservation_reservid)  # Find the reservation by reserveid
        .first()  # pick the first entry
    )
    if this_reservation:  # Reservation was presented to user, so it should exist, just in case
        current_datetime = datetime.now()  # Get current timestamps
        reservation_datetime = datetime.combine(this_reservation[1],
                                                this_reservation[2])  # Compile schedule data in a datetime format
        cancellation_window = timedelta(hours=2)  # Select cancellation window
        # For a reservation to be cancelled 3 conditions need to be met
        if (reservation_datetime > current_datetime  # The appointment has to be in the future
                and (reservation_datetime - current_datetime) > cancellation_window  # But not less than 2 hours later
                and this_reservation[
                    0] != 1):  # And the reservation needs to be active; this is a failsafe, if reservation was
            # picked was active
            # Make the query
            Reservation.query.filter_by(reservid=Reservation_reservid).update(
                {'cancellation': 1})  # Change cancellation status to 1, as in cancelled
            db.session.commit()  # Commit alteration query
            flash(
                'You have successfully cancelled this reservation')  # Send Message to alert for the successful alteration
        else:
            # At least 1 of 3 conditions haven't been met
            # Send error message to indicate the condition that wasn't met
            if not reservation_datetime > current_datetime:  # The user wants to time travel
                flash('Sorry, looks like the appointment has passed')
            elif not (reservation_datetime - current_datetime) > cancellation_window:  # User can no longer cancel
                flash('Sorry, looks like the grace period has passed, you will not be allowed to cancel')
            else:  # The reservation is inactive
                flash('Good news, your reservation has already been cancelled')
    else:
        flash(
            'Sorry, the reservation you want to cancel can not be found')  # In the unlikely case of a reservation not existing, send message to alert for problem
    return redirect('/user')  # Redirect back to user panel page


# Set up function: Services for users
@app.route('/userServices', methods=['GET'])
def get_services_information_by_user():
    this_day = datetime.now().date()  # Get current date
    daily_plan = get_daily_program_data(db.session, this_day)  # Get program information
    return render_template('userServices.html', daily_plan=daily_plan)  # Set up page


# Set up function: Reservation history of user
@app.route('/userReservations', methods=['GET'])
def get_reservations_by_user():
    username = session['username']
    reservations = get_user_reservations_by_username(username, 0)  # Get all reservations made by user
    return render_template('userReservations.html', reservations=reservations)  # Set up page


# Set up function: Login page
@app.route('/login', methods=['GET'])
def user_login():
    return render_template('login.html')  # Set up page


@app.route('/page_login', methods=['POST'])
def login():
    username = request.form.get('username') # get username from the form
    password = request.form.get('password') # get password from the form
    is_admin = Administrator.query.filter_by(username=username).first() # find the first admin with this username
    is_user = User.query.filter_by(username=username).first() # find the first user with this username
    session['username'] = username # 

    # go to admin or user page
    if is_admin and is_user:
        flash('You are admin and user. Select in which page you want to go.')
        show = True 
        return render_template('login.html',show=show)
    elif is_admin and is_admin.password == password:
        return redirect('/main_admin')
    elif is_user and is_user.password == password:
        return redirect('/user')
    else:
        flash('Failed to recognise the account.Please check your credentials.')
        return redirect('/login')


# Set up function: Register page
@app.route('/register', methods=['GET'])
def user_register():
    return render_template('register.html')  # Set up page


# Make new user request
# Button function: add a request made by the user
# Accessed by button in register.html
@app.route('/new_request', methods=['POST'])
def new_request():
    get_admin = (db.session.query(Administrator.adminid).first())
    adminId = get_admin.adminid # Find adminid for the default admin
    user_request = Request(  # Make information packet
        requestid=Request.query.count() + 1,  # Primary key
        username=request.form.get('username'),
        password=request.form.get('password'),
        first_name=request.form.get('fname'),
        last_name=request.form.get('lname'),
        country=request.form.get('country'),
        town=request.form.get('city'),
        address=request.form.get('address'),
        email=request.form.get('email'),
        administrator_adminid=adminId  # Default admin
    )
    user_exists = User.query.filter_by(username=user_request.username).first()  # Username needs to be unique in users
    admin_exists = Administrator.query.filter_by(username=user_request.username).first()  # And to be sure, in admins too
    if user_exists or admin_exists:
        flash('Username already exists')
    else:
        db.session.add(user_request)
        db.session.commit()  # Add the request
        flash(
            'You have successfully made a request for registration in our gym website. Wait for your request to be approved')  # Tell user to wait for approval
    return redirect('/register')


# Set up function: Services for non-users
@app.route('/homeServices', methods=['GET'])
def get_services_information():
    this_day = datetime.now().date()  # Get current date
    daily_plan = get_daily_program_data(db.session, this_day)  # Get program information
    return render_template('services.html', daily_plan=daily_plan)  # Set up page


# Set up function: Make reservation page
@app.route('/makeReservation', methods=['GET', 'POST'])
def make_reservation():
    if request.method == 'POST':  # In this case, the function is called by the make reservation page, so the user has added a date
        this_day_str = request.form.get('this_day')  # Get date by user
        current_date = datetime.now().date()  # Find current date
        try:
            this_day = datetime.strptime(this_day_str, '%Y-%m-%d').date()  # Convert string to date
        except ValueError:
            flash('Sorry, You need to provide a valid date')  # Send message to user to alert the user of the problem
            return redirect('/makeReservation')  # Redirect to makeReservation page
    else:
        this_day = datetime.now().date()  # If user hasn't added a date, get today
        current_date = this_day
    username = session['username']
    daily_plan = get_daily_program_data(db.session, this_day, username)  # Get program information
    date_number, start_date, end_date = find_the_day(this_day)  # Find the week being referred to
    return render_template('userMakeReservation.html',
                           daily_plan=daily_plan,
                           date=this_day,
                           sunday=(date_number <= 6),
                           can_reserve=find_cancellations(start_date, end_date, username),
                           date_valid=(current_date <= this_day))  # Set up page


# Use function: Find week by date.
def find_the_day(date):
    day = date.isoweekday()  # The number of day in a week
    start_date = date - timedelta(days=day - 1)  # Find the first day of the week
    end_date = date + timedelta(days=6 - day)  # Find the last day of the week
    return day, start_date, end_date  # Return information to add_reservation


# Use function: Get a week and see how many cancellations a user has had
def find_cancellations(start_date, end_date, username):
    # Find the user id to identify the user in the system
    find_user = (
        db.session.query(User.userid)  # Select userid
        .filter(User.username == username)  # Found by username
        .subquery()  # Use the data in the query below
    )
    # Cancellations are defined by the day the reservation was booked for
    # Find cancellations made by user
    week_cancellations = (
        db.session.query(Reservation.cancellation)  # Get cancellations
        .join(find_user, find_user.c.userid == Reservation.user_userid)  # Match Reservations with user
        .join(Schedule, Reservation.schedule_scheduleid == Schedule.scheduleid)  # Match reservations and schedules
        .filter(Schedule.day >= start_date)  # Reservation was made for after the end of the week
        .filter(Schedule.day <= end_date)  # Reservations are made for before the end of the week
        .filter(Reservation.cancellation == 1)  # If reservation has been cancelled, it will have value 1
        .all()  # Don't get information, but count the entries
    )
    return int(len(week_cancellations)) < 2  # User can make up to 2 cancellations


# Button function: make reservation by programid and date
# Accessed by button in userMakeReservations.html
@app.route("/add_reservation/<int:program_id>/<string:date>", methods=['POST'])
def add_reservation(program_id, date):
    # Date is currently a string. Turn it into datetime
    date = datetime.strptime(date, '%Y-%m-%d')  # Convert date string to datetime object
    date = date.date()
    username = session['username']
    if date:  # If date has been filled and converted
        # Find the week this date is a part of
        this_day, start_date, end_date = find_the_day(
            date)  # Results are the day or the current date (Monday is 1 and Sunday is 7), the monday of that week
        # and the saturday of that week; The last two are in a date format
        # For the user to make a reservation the following conditions need to be met
        # The below conditions are a failsafe
        # The way the page is set up should not give the user the option to make a reservation anyway
        if (find_cancellations(start_date, end_date, username)  # The users haven't cancelled 3 appointments this week
                and this_day <= 6  # The user can't make a reservation on a sunday
                and (find_availability(program_id, date) > 0)  # The program has to have space
                and (check_schedule(date,
                                    program_id) == 1)  # If we're looking at today, this condition tells us if the program has happened yet
                and user_reserv_exists(username, date, program_id)):
            # To make a reservation, find the schedule that corresponds with the information given
            scheduleId = (
                db.session.query(Schedule.scheduleid)  # Select scheduleid
                .join(ScheduleAndProgram,
                      Schedule.scheduleid == ScheduleAndProgram.schedule_scheduleid)  # Connect schedule with program
                .join(Program, ScheduleAndProgram.program_programid == Program.programid)  # Via scheduleandprogram
                .filter(Program.programid == program_id)  # Find the entry by the program
                .filter(Schedule.day == date)  # And the date
                .scalar()  # Return an integer number
            )
            if scheduleId:  # If admin has made the schedule needed
                # Find the user id to identify the user in the system
                find_user = (
                    db.session.query(User.userid)  # Select userid
                    .filter(User.username == username)  # By username
                    .scalar()  # This query will be an integer number
                )
                # Make reservation entry
                # For ease of planing, we assume that a program only happens ones daily
                reservation = Reservation(
                    reservid=Reservation.query.count() + 1,  # Primary key, find how many reservation exists and add 1
                    date=datetime.now(),  # Get current timestamp
                    cancellation=None,  # Reservation has been cancelled yet
                    user_userid=find_user,  # Userid, as provided by the session
                    schedule_scheduleid=scheduleId  # Scheduleid, as found above by program id and date
                )
                # Create query to add reservation
                db.session.add(reservation)  # Query to add the above reservation
                db.session.commit()  # Committing the query
                flash("You have successfully made a reservation")  # Send message to alert user
            else:
                # Schedules are managed and added by admin some don't exist yet
                flash(
                    'Sorry, the program your looking for has not been scheduled for this date yet')  # Send message to alert for problem
        else:
            # For at least 1 of 4 conditions, reservation could not be made
            # Send error message to indicate the condition that wasn't met
            if not find_cancellations(start_date, end_date,
                                      username):  # The user has cancelled 3 appointments this week
                flash('Sorry, you have achieved to maximum amount of cancellation this week')
            elif not this_day <= 6:  # The user can't make a reservation on a sunday
                flash('Sorry, unfortunately, our gym is closed at sundays')
            elif not find_availability(program_id, date):  # The program doesn't have space
                flash('Sorry, this program is booked solid this day')
            elif not user_reserv_exists(username, date, program_id):  # The user already has a reservation
                flash('Sorry, you already have a reservation')
            elif check_schedule(date, program_id) == 3:
                flash('Sorry, no matching schedule found for the given program and date')
            elif check_schedule(date, program_id) == 2:
                flash('Sorry, the program has passed')
            elif check_schedule(date, program_id) == 4:
                flash('Sorry, the selected date is in the past.')
    return redirect('/makeReservation')  # Redirect to reservation page, regardless of outcome of reservation


# Use function: See if a user can make a reservation today
def check_schedule(date, program_id):
    # Get current date and time
    current_date = datetime.now().date()
    current_time = datetime.now().time()
    if date > current_date:
        return 1  # Date is in the future
    elif date == current_date:
        # Date is today, check if time is later than current time
        this_schedule = (
            db.session.query(
                Schedule.time  # Find the time the program is on
            )
            .join(ScheduleAndProgram,
                  Schedule.scheduleid == ScheduleAndProgram.schedule_scheduleid)  # Connect schedule and program
            .join(Program, ScheduleAndProgram.program_programid == Program.programid)  # Via scheduleandprogram
            .filter(Program.programid == program_id)  # Find the program
            .filter(Schedule.day == date)  # On the day needed
            .first()
        )  # Find the time the program in on that day
        if this_schedule:
            program_time = this_schedule[0]  # Schedule was found, this get the time 
            if program_time > current_time:
                return 1  # The program time is later than the current time
            else:
                return 2  # The program time has already passed.
        else:
            return 3  # No matching schedule found for the given program_id and date
    else:
        return 4  # The date has passed


# Admin home page
@app.route('/main_admin', methods=['GET'])
def main_admin():
    username = session['username']
    return render_template('main_admin.html',username=username)  # Set up page


# Admin users page
@app.route('/main_users', methods=['GET'])
def main_users():
    return render_template('main_users.html')  # Set up page


# Admin requests page
@app.route('/main_requests', methods=['GET'])
def main_requests():
    return render_template('main_requests.html')  # Set up page


#  Get a list of all users
@app.route('/users_list', methods=['GET'])
def users_list():
    users = User.query.all()  # Get all users from database

    if not users:
        flash("No users found.")  # No users found

    formed_data = [  # Form the data
        {
            'User_userid': user.userid,
            'User_username': user.username,
            'User_first_name': user.first_name,
            'User_last_name': user.last_name,
            'User_country': user.country,
            'User_town': user.town,
            'User_address': user.address,
            'User_email': user.email
        }
        for user in users
    ]
    return render_template('users_list.html', users=formed_data)  # Render the template


# Show the Update User form
@app.route('/update_user_info', methods=['GET'])
def show_update_user_info():
    return render_template('update_user.html') # Render the template


# Update user information
@app.route('/update_user_info_action', methods=['POST'])
def update_user_info():
    update_choice = request.form.get('update_choice')  # Get the update choice from the form
    new_info = request.form.get('new_info')  # Get the new information from the form
    userid = request.form.get('userid') # Get the User ID from the form

    user = User.query.get(userid)  # Get the user from the database

    if not user:
        flash("User does not exist.")
    else:   # Update the user attribute based on the update choice
        if update_choice == 'username':
            user.username = new_info
        elif update_choice == 'first_name':
            user.first_name = new_info
        elif update_choice == 'last_name':
            user.last_name = new_info
        elif update_choice == 'country':
            user.country = new_info
        elif update_choice == 'town':
            user.town = new_info
        elif update_choice == 'address':
            user.address = new_info
        elif update_choice == 'email':
            user.email = new_info
        else:
            user.password = new_info

        db.session.commit()  # Commit the changes to the database
        flash('User information has been updated successfully!')  # Success message

    return redirect('/update_user_info')  # Redirect to main Update User page


# Show the Delete User form
@app.route('/delete_user', methods=['GET'])
def show_delete_user():
    return render_template('delete_user.html') # Render the template


# Delete User
@app.route('/delete_user_action', methods=['GET', 'POST'])
def delete_user():
    userid = request.form.get('userid') # Get the User ID from the form
    user = User.query.get(userid)  # Get the user from the database

    if not user:
        flash("User does not exist.")
        return redirect('/delete_user')  # Redirect to main page

    if request.method == 'POST':
        db.session.delete(user)  # Delete the user from the database
        db.session.commit()  # Commit the changes
        flash('User has been deleted successfully!')  # Flash success message

    return redirect('/delete_user')  # Redirect to the main Delete User page


# Show the Make User Admin form
@app.route('/make_user_admin', methods=['GET'])
def show_make_user_admin():
    return render_template('change_user_role.html') # Render the template


# Make User Admin
@app.route('/make_user_admin_action', methods=['GET', 'POST'])
def make_user_admin():
    userid = request.form.get('userid') # Get the User ID from the form
    user = User.query.get(userid)  # Get the user from the database

    if not user:
        flash("User does not exist.")
        return redirect('/make_user_admin')  # Redirect to main page

    if request.method == 'POST':

        max_adminid = db.session.query(func.max(Administrator.adminid)).scalar() or 0
        new_adminid = max_adminid + 1 # In case there is no Admin

        while Administrator.query.filter_by(adminid=new_adminid).first():
            new_adminid += 1

        new_admin = Administrator(  # Create new administrator
            adminid=new_adminid,
            username=user.username,
            password=user.password,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email
        )

        db.session.add(new_admin)
        db.session.commit()  # Commit the change to the database

        flash('User has been granted admin privileges successfully!')  # Flash success message

    return redirect('/make_user_admin')  # Redirect to the main Change User Role page


# Process Requests
@app.route('/pending_requests', methods=['GET'])
def pending_requests():
    requests = Request.query.filter(Request.approval == None).all()  # Filter requests with approval=NULL  # Get new requests from the database

    if not requests:
        flash("There are no pending requests.")

    formed_data = [  # Form the data
        {
            'Request_requestid': request_entry.requestid,
            'Request_username': request_entry.username,
            'Request_first_name': request_entry.first_name,
            'Request_last_name': request_entry.last_name,
            'Request_country': request_entry.country,
            'Request_town': request_entry.town,
            'Request_address': request_entry.address,
            'Request_email': request_entry.email
        }
        for request_entry in requests
    ]
    return render_template('pending_requests.html', requests=formed_data)  # Render the template


# Approve a request
@app.route('/approve_request/<int:Request_requestid>', methods=['GET', 'POST'])
def approve_request(Request_requestid):
    request_obj = Request.query.get(Request_requestid)  # Get the request from the database

    username = session['username']
    find_adminid = (
        db.session.query(Administrator.adminid)  # Select userid
        .filter(Administrator.username == username)  # By username
        .scalar()  # This query will be an integer number
    )
    request_obj.administrator_adminid=find_adminid  # Set the ID of the admin that approved the request

    if request.method == 'POST':

        max_userid = db.session.query(func.max(User.userid)).scalar() or 0
        new_userid = max_userid + 1 # In case there is no User

        while User.query.filter_by(userid=new_userid).first():
            new_userid += 1

        new_user = User(  # Create new user
            userid=new_userid,
            username=request_obj.username,
            first_name=request_obj.first_name,
            last_name=request_obj.last_name,
            country=request_obj.country,
            town=request_obj.town,
            address=request_obj.address,
            email=request_obj.email,
            password=request_obj.password,
            request_requestid=request_obj.requestid
        )

        db.session.add(new_user)
        request_obj.approval = 1 # Mark request as approved
        db.session.commit()  # Commit the changes to the database

        flash("Request approved successfully!")  # Flash success message
    return redirect('/pending_requests')


# Reject a request
@app.route('/reject_request/<int:Request_requestid>', methods=['POST'])
def reject_request(Request_requestid):
    request_obj = Request.query.get(Request_requestid)  # Get the request from the database

    username = session['username']
    find_adminid = (
        db.session.query(Administrator.adminid)  # Select userid
        .filter(Administrator.username == username)  # By username
        .scalar()  # This query will be an integer number
    )
    request_obj.administrator_adminid=find_adminid  # Set the ID of the admin that approved the request

    request_obj.approval = 0 # Mark request as rejected
    db.session.commit()  # Commit

    flash("Request rejected successfully.")  # Flash success message
    return redirect('/pending_requests')  # Render the template


@app.route('/trainers', methods=['GET', 'POST'])
def get_trainers():
    if request.method == 'POST':
        # Retrieve trainer information from the form
        trainer_id = request.form['trainerID']
        first_name = request.form['trainerFirstName']
        last_name = request.form['trainerLastName']
        email = request.form['trainerEmail']

        # Create a new Trainer object
        new_trainer = Trainer(trainerid=trainer_id, first_name=first_name, last_name=last_name, email=email)

        try:
            # Add the new trainer to the database
            db.session.add(new_trainer)
            db.session.commit()
            flash('Trainer added successfully', 'success')
        except Exception as e:
            # Handle exceptions and rollback changes if an error occurs
            print(f"Error adding trainer: {e}")
            db.session.rollback()
            flash('Error adding trainer. Please try again.', 'error')

    else:  # Handle GET request
        trainers = Trainer.query.all()
        return render_template('admin_trainers.html', trainers=trainers)

    # If it's a GET request, retrieve trainers from the database
    trainers = Trainer.query.all()
    return render_template('admin_trainers.html', trainers=trainers)


@app.route('/trainers/update_trainer_info/action', methods=['POST'])
def update_trainer():
    # Get information from the form
    new_info = request.form.get('newInfo')
    trainerid = request.form.get('trainerid')
    update_choice = request.form.get('update_choice')

    # Retrieve the trainer from the database
    trainer = Trainer.query.get(trainerid)

    if not trainer:
        flash("Trainer does not exist.")
    else:
        # Update the corresponding attribute based on the choice
        if update_choice == 'first_name':
            trainer.first_name = new_info
        elif update_choice == 'last_name':
            trainer.last_name = new_info
        elif update_choice == 'email':
            trainer.email = new_info
        else:
            flash("Invalid update choice.")

        db.session.commit()  # Commit the changes to the database
        flash('Trainer information has been updated successfully!')  # Success message

    return redirect('/trainers')  # Redirect to the main Trainers page


@app.route('/trainers/delete_trainer_info/action', methods=['POST'])
def delete_trainer():
    trainerid = request.form.get('trainerid')  # Get the Trainer ID from the form

    trainer = Trainer.query.get(trainerid)  # Get the trainer from the database

    if not trainer:
        flash("Trainer does not exist.")
    else:
        # Get all schedules associated with the trainer
        schedules = Schedule.query.filter_by(trainer_trainerid=trainerid).all()

        # Delete related records in the 'scheduleandprogram' table
        for schedule in schedules:
            ScheduleAndProgram.query.filter_by(schedule_scheduleid=schedule.scheduleid).delete()

        # Delete related records in the 'reservation' table
        for schedule in schedules:
            Reservation.query.filter_by(schedule_scheduleid=schedule.scheduleid).delete()

        # Delete associated schedules
        Schedule.query.filter_by(trainer_trainerid=trainerid).delete()

        # Delete the trainer from the database
        db.session.delete(trainer)
        db.session.commit()  # Commit the changes to the database
        flash('Trainer has been deleted successfully!')  # Success message

    return redirect('/trainers')  # Redirect to the main Trainers page


from datetime import datetime

@app.route('/announcements', methods=['GET', 'POST'])
def get_announcements():
    if request.method == 'POST':
        # Retrieve announcement information from the form
        administrator_adminid = request.form['administrator_adminid']
        announceid = request.form['announceid']
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']

        # Create a new Announcement object
        new_announc = Announcement(administrator_adminid=administrator_adminid, announceid=announceid, title=title, description=description, date=date)

        try:
            # Add the new announcement to the database
            db.session.add(new_announc)
            db.session.commit()
            flash('Announcement added successfully', 'success')
        except Exception as e:
            # Handle exceptions and rollback changes if an error occurs
            print(f"Error adding announcement: {e}")
            db.session.rollback()
            flash('Error adding announcement. Please try again.', 'error')

    else:  # Handle GET request
        announcements = Announcement.query.all()
        return render_template('admin_announcement.html', announcements=announcements)

    # If it's a GET request, retrieve announcements from the database
    announcements = Announcement.query.all()
    return render_template('admin_announcement.html', announcements=announcements)


@app.route('/announcements/update_announcement_info/action', methods=['POST'])
def update_announcement():
    # Get information from the form
    new_info = request.form.get('newInfo')
    announceid = request.form.get('announceid')
    update_choice = request.form.get('update_choice')

    # Retrieve the announcement from the database
    announcement = Announcement.query.get(announceid)

    if not announcement:
        flash("Announcement does not exist.")
    else:
        # Update the corresponding attribute based on the choice
        if update_choice == 'title':
            announcement.title = new_info
        elif update_choice == 'description':
            announcement.description = new_info
        elif update_choice == 'date':
            announcement.date = new_info
        else:
            flash("Invalid update choice.")

        db.session.commit()
        flash('Announcement information has been updated successfully!')

    return redirect('/announcements')


@app.route('/announcements/delete_announcement_info/action', methods=['POST'])
def delete_announcement():
    announceid = request.form.get('announcementIdDelete')

    announcement = Announcement.query.get(announceid)

    if not announcement:
        flash("Announcement does not exist.")
    else:
        # Delete the announcement
        db.session.delete(announcement)
        db.session.commit()

        flash('Announcement has been deleted successfully!')

    return redirect('/announcements')


@app.route('/discounts', methods=['GET', 'POST'])
def get_discounts():
    if request.method == 'POST':
        # Retrieve discount information from the form
        announcement_announceid = int(request.form['announcement_announceid'])
        description = request.form['description']
        discountid = int(request.form['discountid'])
        program_programid = int(request.form['program_programid'])
        title = request.form['title']

        # Create a new Discount object
        new_discount = Discount(
            announcement_announceid=announcement_announceid,
            description=description,
            discountid=discountid,
            program_programid=program_programid,
            title=title
        )

        try:
            # Add the new discount to the database
            db.session.add(new_discount)
            db.session.commit()
            flash('Discount added successfully', 'success')
        except Exception as e:
            # Handle exceptions and rollback changes if an error occurs
            print(f"Error adding discount: {e}")
            db.session.rollback()
            flash('Error adding discount. Please try again.', 'error')

    # Handle GET request
    discounts = Discount.query.all()
    return render_template('admin_discount.html', discounts=discounts)


@app.route('/discounts/update_discount_info/action', methods=['POST'])
def update_discount():
    # Get information from the form
    new_info = request.form.get('newInfo')
    discountid = request.form.get('discountid')
    update_choice = request.form.get('update_choice')

    # Retrieve the discount from the database
    discount = Discount.query.get(discountid)

    if not discount:
        flash("Discount does not exist.")
    else:
        # Update the corresponding attribute based on the choice
        if update_choice == 'title':
            discount.title = new_info
        elif update_choice == 'description':
            discount.description = new_info
        elif update_choice == 'program_programid':
            discount.program_programid = new_info
        else:
            flash("Invalid update choice.")

        db.session.commit()
        flash('Discount information has been updated successfully!')

    return redirect('/discounts')


@app.route('/discounts/delete_discount_info/action', methods=['POST'])
def delete_discount():
    discountid = request.form.get('discountIdDelete')

    discount = Discount.query.get(discountid)

    if not discount:
        flash("Discount does not exist.")
    else:
        # Delete the discount
        db.session.delete(discount)
        db.session.commit()

        flash('Discount has been deleted successfully!')

    return redirect('/discounts')


@app.route('/schedule', methods=['GET', 'POST'])
def get_schedules():
    if request.method == 'POST':
        # Retrieve schedule information from the form
        scheduleid = request.form['scheduleid']
        day = request.form['day']
        time = request.form['time']
        trainer_trainerid = request.form['trainerid']

        program_id = request.form['program_id']

        # Create a new Schedule object
        new_sched = Schedule(scheduleid=scheduleid, day=day, time=time, trainer_trainerid=trainer_trainerid)

        try:
            # Add the new schedule to the database
            db.session.add(new_sched)
            db.session.commit()

            # Create an entry in the ScheduleAndProgram table
            schedule_and_program = ScheduleAndProgram(schedule_scheduleid=new_sched.scheduleid, program_programid=program_id)
            db.session.add(schedule_and_program)
            db.session.commit()

            flash('Schedule added successfully', 'success')
        except Exception as e:
            # Handle exceptions and rollback changes if an error occurs
            print(f"Error adding schedule: {e}")
            db.session.rollback()
            flash('Error adding schedule. Please try again.', 'error')

    # Handle GET request
    schedules = Schedule.query.all()
    programs = Program.query.all()
    return render_template('admin_schedule.html', schedules=schedules, programs=programs)


@app.route('/schedule/update_schedule_info/action', methods=['POST'])
def update_schedule():
    # Get information from the form
    new_info = request.form.get('newInfo')
    scheduleid = request.form.get('scheduleid')
    update_choice = request.form.get('update_choice')

    # Retrieve the schedule from the database
    schedule = Schedule.query.get(scheduleid)

    if not schedule:
        flash("Schedule does not exist.")
    else:
        # Update the corresponding attribute based on the choice
        if update_choice == 'day':
            schedule.day = new_info
        elif update_choice == 'time':
            schedule.time = new_info
        elif update_choice == 'trainerid':
            schedule.trainer_trainerid = new_info
        else:
            flash("Invalid update choice.")

    db.session.commit()
    flash('Schedule information has been updated successfully!')

    return redirect('/schedule')


@app.route('/schedule/delete_schedule_info/action', methods=['POST'])
def delete_schedule():
    scheduleid = request.form.get('scheduleIdDelete')

    schedule = Schedule.query.get(scheduleid)

    if not schedule:
        flash("Schedule does not exist.")
    else:
        schedule = Schedule.query.get(scheduleid)
        # Delete related records in scheduleandprogram table
        ScheduleAndProgram.query.filter_by(schedule_scheduleid=scheduleid).delete()
        # Now, delete the schedule itself
        db.session.delete(schedule)
        db.session.commit()

        # Delete the schedule
        db.session.delete(schedule)
        db.session.commit()

        flash('Schedule has been deleted successfully!')

    return redirect('/schedule')


@app.route('/programs', methods=['GET', 'POST'])
def get_programs():
    if request.method == 'POST':
        # Retrieve program information from the form
        programid = request.form['programid']
        title = request.form['title']
        description = request.form['description']
        max_capacity = request.form['maxCapacity']

        # Create a new Program object
        new_program = Program(programid=programid, title=title, description=description, max_capacity=max_capacity)

        try:
            # Add the new program to the database
            db.session.add(new_program)
            db.session.commit()
            flash('Program added successfully', 'success')
        except Exception as e:
            # Handle exceptions and rollback changes if an error occurs
            print(f"Error adding program: {e}")
            db.session.rollback()
            flash('Error adding program. Please try again.', 'error')

    else:  # Handle GET request
        programs = Program.query.all()
        return render_template('admin_classes.html', programs=programs)

    # If it's a GET request, retrieve programs from the database
    programs = Program.query.all()
    return render_template('admin_classes.html', programs=programs)


@app.route('/programs/update_program_info/action', methods=['POST'])
def update_program():
    # Get information from the form
    new_info = request.form.get('newInfo')
    programid = request.form.get('programid')
    update_choice = request.form.get('update_choice')

    # Retrieve the program from the database
    program = Program.query.get(programid)  # Fix variable name

    if not program:
        flash("Program does not exist.")
    else:
        # Update the corresponding attribute based on the choice
        if update_choice == 'title':
            program.title = new_info
        elif update_choice == 'description':
            program.description = new_info
        elif update_choice == 'max_capacity':
            program.max_capacity = new_info
        else:
            flash("Invalid update choice.")

        db.session.commit()
        flash('Program information has been updated successfully!')

    return redirect('/programs')


from sqlalchemy.orm import joinedload

@app.route('/programs/delete_program_info/action', methods=['POST'])
def delete_program():
    programid = request.form.get('programIdDelete')

    program = Program.query.get(programid)

    if not program:
        flash("Program does not exist.")
    else:
        # Delete the program
        db.session.delete(program)
        db.session.commit()

        flash('Program has been deleted successfully!')
        
    return redirect('/programs')


# Function to run the app
if __name__ == '__main__':
    app.run(debug=True)
