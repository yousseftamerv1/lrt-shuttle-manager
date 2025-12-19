"""
=============================================================================
PROJECT   : LRT Shuttle Bus Manager
AUTHOR    : Youssef Tamer
START DATE: 6 December 2025
VERSION   : 1.0.0
UNIVERSITY: SUTech Elsewedy University - Polytechnic of Egypt
=============================================================================

"""

#############################################
#                                           #
#           IMPORTS AND FUNCTIONALITY       #
#                                           #
#############################################

#Flask: the class of the framework we used to define the app and init it
#render_template: the method responsible to render the HTML Files 
#request: it's used to send data from the labels like the login 
#redirect: it's used to redirect the user into another web pages in a specific condition
#url_for: it's used if the route changes and redirect the user to the changed url by the function name
#session: a method used to save the user credintials [cookies]
#flash: send a simple message in a specific condition in the UI
from flask import Flask, render_template, request, redirect, url_for, session, flash

#SQLAlchemy: it's the ORM(Object Relational Mapper) works as a translator to use the database without knowing
# how to write queries 
from flask_sqlalchemy import SQLAlchemy
#datetime: used for get the time
#timedelta: used to have a calulations in the time
from datetime import datetime, timedelta

from os import getenv

#############################################
#                                           #
#               INIT AND CONFIG             #
#                                           #
#############################################

app = Flask(__name__) #init the flask app
app.config['SECRET_KEY'] = getenv('SECRET_KEY') #init the secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lrt_manager.db' #assigning the database the project will work in
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #to optimize the app and prevent a load in memory usage
db = SQLAlchemy(app) #init the database using the orm with the app


#############################################
#                                           #
#             DEFINE THE MODELS             #
#                                           #
#############################################

class User(db.Model): #class inherted from db.Model
    id = db.Column(db.Integer, primary_key=True) #id column [primary]
    username = db.Column(db.String(50), unique=True, nullable=False) #username column [unique, can't be empty or null]
    password = db.Column(db.String(50), nullable=False) #username column [can't be empty or null]
    role = db.Column(db.String(20), nullable=False)#role column [can't be empty or null]

class TripTemplate(db.Model):#class inherted from db.Model
    id = db.Column(db.Integer, primary_key=True)#id column [primary]
    time_str = db.Column(db.String(10), nullable=False)#time_str column [can't be empty or null]
    direction = db.Column(db.String(50), nullable=False)#direction column [can't be empty or null]
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'))#driver_id column [can't be empty or null, have a relation with user.id]
    driver = db.relationship('User', backref='templates') #add the relation between to classes, backref templates 

class Trip(db.Model):#class inherted from db.Model
    id = db.Column(db.Integer, primary_key=True)#id column [primary]
    departure_time = db.Column(db.DateTime, nullable=False) #the sceduled time column [saved as datetime, can't be empty or null]
    
    actual_arrival_time = db.Column(db.DateTime, nullable=True) #the time that the driver arrived in [saved as datetime, can't be empty or null]
    
    direction = db.Column(db.String(50), nullable=False) #direction column [can't be empty or null]
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id')) #driver_id column [can't be empty or null, have a relation with user.id]
    capacity = db.Column(db.Integer, default=14)#capacity column 
    booked_seats = db.Column(db.Integer, default=0)#booked seats column
    
    status = db.Column(db.String(20), default='Scheduled') #status column [by default: Scheduled --> Boarding --> Departed]

    driver = db.relationship('User', backref='trips') #add relation between classess, backref trips

class Booking(db.Model):#class inherted from db.Model
    id = db.Column(db.Integer, primary_key=True)#id column [primary]
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))#relation with user.id
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'))#relation with trip.id


#############################################
#                                           #
#             DAILY TRIPS METHOD            #
#                                           #
#############################################

def generate_daily_trips(): #it's used to made new trips every 24 hours, from the TripTemplate class
    today = datetime.now().date() #to see the date and time now
    templates = TripTemplate.query.all() #to save all the TripTemplate values assigned by the admin
    if not templates: return #if there is nothing in the templates return nothing

    for temp in templates: #it will loop in the templates
        try: #try block to prevent crashing
            h, m = map(int, temp.time_str.split(':')) #to change the date values form str to int
            trip_time = datetime.combine(today, datetime.min.time().replace(hour=h, minute=m)) #combine the today date with the time of the assigned trip
            
            #exists is to check the trip is already there 
            exists = Trip.query.filter_by(departure_time=trip_time, direction=temp.direction, driver_id=temp.driver_id).first() 
            
            if not exists: #if the trip is not already in the template
                new_trip = Trip(departure_time=trip_time, direction=temp.direction, driver_id=temp.driver_id) #it will make a new trip
                db.session.add(new_trip) #add the trip into the database
        except: continue #to prevent the app crash or throwing an error
    db.session.commit() #save all the changes to database



#############################################
#                                           #
#                   ROUTES                  #
#                                           #
#############################################

@app.route('/') #the route of the root
def index(): return redirect(url_for('login')) #redirect into the login website

@app.route('/login', methods=['GET', 'POST']) #the route of the login page - get[to render the html page], post[to get the data from the user]
def login():#the login funciton
    if request.method == 'POST': #if the request method is post[get the data from the user] 
        user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first() #to check from the user credintials
        if user: #if the user is exists
            session['user_id'] = user.id #saving the user_id in the session [cookies]
            session['role'] = user.role #saving the user.role in the session [cookies]
            session['username'] = user.username #saving the user.username in the session [cookies]
            if user.role == 'admin': return redirect(url_for('admin_dashboard')) #if the user is admin it will redirect into the admin page
            elif user.role == 'driver': return redirect(url_for('driver_dashboard'))#if the user is admin it will redirect into the driver page
            else: return redirect(url_for('student_dashboard'))#if the user is admin it will redirect into the student page
        else:#if the user credintials don't match
            flash('Invalid credentials', 'danger') #it will throw a message and say 'Invalid credentials'
    return render_template('login.html') #render the login.html page

@app.route('/logout') #the route of the logout
def logout():#the logout funciton
    session.clear()#clear all the cookies
    return redirect(url_for('login'))#redirect you to login.html page



@app.route('/admin') #the route of the admin
def admin_dashboard():#the admin dashboard function
    if session.get('role') != 'admin': return redirect(url_for('login')) #security check before rendering the admin dashboard
    #render the admin.html page and then send the templates to the admin.html file to view all the trip and also get the users with driver roles to select them into the trip
    return render_template('admin.html', templates=TripTemplate.query.order_by(TripTemplate.time_str).all(), drivers=User.query.filter_by(role='driver').all())

@app.route('/admin/add', methods=['POST']) #the route of adding new trip -- to get data from the admin
def add_template():#the add function
    if session.get('role') != 'admin': return redirect(url_for('login')) #security check before rendering
    #saving the trip info into the ram
    db.session.add(TripTemplate(direction=request.form['direction'], time_str=request.form['time_str'], driver_id=request.form['driver_id']))
    db.session.commit() #saving the changes into the database
    generate_daily_trips() #using the function generate_daily_trips to sync a new trip added
    return redirect(url_for('admin_dashboard')) #render the admin.html

@app.route('/admin/delete/<int:id>') #the route of deleting a trip -- using the dynamic format
def delete_template(id):#the delete function
    if session.get('role') != 'admin': return redirect(url_for('login'))#security check before rendering
    temp = TripTemplate.query.get(id) #to search for this trip template in TripTemplate class
    if temp: #if the trip is there
        
        today = datetime.now().date() #saving the time of the date now
        try: #to check without crashing the program
            h, m = map(int, temp.time_str.split(':')) #to change the time from str to int
            trip_time = datetime.combine(today, datetime.min.time().replace(hour=h, minute=m)) #to combine them into date and time 
            #check if the trip is scheduled
            t = Trip.query.filter_by(departure_time=trip_time, direction=temp.direction, driver_id=temp.driver_id, status='Scheduled').first()
            if t: #if it's scheduled
                Booking.query.filter_by(trip_id=t.id).delete() #delete all the bookings in this trip
                db.session.delete(t) #then delete the trip itself
        except: pass #continue even if there is an error
        db.session.delete(temp) #delete the temp object
        db.session.commit() #then save everything into the database
    return redirect(url_for('admin_dashboard')) #redirect you into the admin dashboard



@app.route('/driver') #the route of the driver
def driver_dashboard():#the driver dashboard method
    if session.get('role') != 'driver': return redirect(url_for('login')) #security check before rendering the diver dashboard
    generate_daily_trips()#sync to confirm if there is any trips
    start_of_day = datetime.combine(datetime.now().date(), datetime.min.time()) #to get the zero hour
    
    #filtering the driver trips [check of the driver id - to check only his assigned trips]
    # also by the day of the trip - today
    # also filter only the scheduled or boarding trips to be seen in the driver dashboard
    my_trips = Trip.query.filter(
        Trip.driver_id == session['user_id'],
        Trip.departure_time >= start_of_day,
        Trip.status.in_(['Scheduled', 'Boarding']) 
    ).order_by(Trip.departure_time).all() 
    
    return render_template('driver.html', trips=my_trips) #render the driver.html page and also return with it my_trips

@app.route('/driver/toggle/<int:id>') #route of the toggle action
def toggle_status(id):#function of the toggle action
    if session.get('role') != 'driver': return redirect(url_for('login')) #security check before doing the action
    trip = Trip.query.get(id) #saving the trip info
    
    if trip: #if it's exists
        if trip.status == 'Scheduled': #if it's still in scheduleed
            trip.status = 'Boarding' #change it to boarding
            trip.actual_arrival_time = datetime.now() #start a timer now
            
        elif trip.status == 'Boarding':#if it's still in boarding
            trip.status = 'Departed' #change it to departed
            
        db.session.commit() #save all the changes to database
    return redirect(url_for('driver_dashboard')) #redirect to driver.html page



@app.route('/student') #route of the student
def student_dashboard():#function of the student dashboard
    if session.get('role') != 'student': return redirect(url_for('login'))#security check before rendering the student dashboard
    generate_daily_trips() #to sync and confirm if there is any trips
    
    now = datetime.now() #time now
    #filter to show the trips by the time [trips that still scheduled]
    # and also union the with the boardin trips 
    trips = Trip.query.filter(
        Trip.departure_time > now, #still in the near future
        Trip.status == 'Scheduled'
    ).union(
        Trip.query.filter(Trip.status == 'Boarding')
    ).order_by(Trip.departure_time).all()
    
    #save all the booking made by the user
    my_bookings = [b.trip_id for b in Booking.query.filter_by(user_id=session['user_id']).all()]
    
   
    trips_data = [] #list to save the trips data
    for t in trips:#looping the trips data
        target_time = t.departure_time #the time of of departure that saved in the object
        timer_type = 'arrival' #the arival time that sent to the js file
        
        if t.status == 'Boarding' and t.actual_arrival_time: #if the driver is arrived and now boarding and there is a value in actual arrival time
            target_time = t.actual_arrival_time + timedelta(minutes=20) #start a timer [20 minutes]
            timer_type = 'departure' #change the timer type to departure and send it to the js file
            
        #appending the trip data
        trips_data.append({
            'obj': t,
            'target_time': target_time,
            'timer_type': timer_type
        })
    #render the student.html and send with it the trip data and the bookings
    return render_template('student.html', trips_data=trips_data, my_bookings=my_bookings) 

@app.route('/student/book/<int:id>') #route of the book action
def book_seat(id):#function of book action
    if session.get('role') != 'student': return redirect(url_for('login'))#security check before doing the action
    trip = Trip.query.get(id) #fetching the data of the targeted trip
    user_id = session['user_id'] #getting the user id from the session
    
    existing = Booking.query.filter_by(user_id=user_id, trip_id=id).first() #filter the data and see it will return it or it will be none
    
    if existing: #if it's exists
        trip.booked_seats -= 1 #it will remove one seats as booked
        db.session.delete(existing) #remove the existing from the session
    else:#if not exists

        can_book = False #flag variable to check if the student can book or not
        if trip.status == 'Boarding': #if it's boarding
            can_book = True #the student can book
        else: #if it's not boarding
            diff = (trip.departure_time - datetime.now()).total_seconds() / 60 #calculate the diffrence
            if 0 < diff <= 5: #if diffrence between the 0 and 5 minutes
                can_book = True #the student can book
        
        #if the flag can_book is true and the booked seats are smaller than the capacity
        if can_book and trip.booked_seats < trip.capacity: 
            trip.booked_seats += 1 #add it to the booked seats
            db.session.add(Booking(user_id=user_id, trip_id=id)) #add to the session a new row of the booked ticket
            flash('Seat Booked!', 'success') #send message that the booking is done
        else: #if not
            flash('Cannot book right now.', 'warning') #send a message that the booking is not available
            
    db.session.commit() #save all the changes into the database
    return redirect(url_for('student_dashboard')) #redirect you into the student dashboard



#############################################
#                                           #
#               MAIN FUNCTION               #
#                                           #
#############################################

if __name__ == '__main__': #if __name__ attribute is equal "__main__" - that means that the file ran directly not imported
    with app.app_context(): #with app context
        db.create_all() #if the database is deleted or not created create it
        if not User.query.first(): #if there is no users in the database
            db.session.add(User(username='admin', password='123', role='admin')) #adding the admin user
            db.session.add(User(username='driver1', password='123', role='driver')) #adding the driver user
            db.session.add(User(username='student', password='123', role='student')) #adding the student user
            db.session.commit() #save all the changes
    app.run(debug=True, host='0.0.0.0') #start the app