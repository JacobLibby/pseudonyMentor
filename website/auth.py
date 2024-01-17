from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Admin, Mentor, Mentee, Connections
# from .models import School, Company
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import sqlalchemy
import sqlalchemy.sql
from sqlalchemy import create_engine, engine, MetaData, Table, Column, String, select, inspect, Integer, String, ForeignKey, and_, or_, join
from sqlalchemy.orm import sessionmaker, relationship, query, join
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

auth = Blueprint('auth', __name__)
Base = declarative_base()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                user_id = User.query.filter_by(email=email).first().id

                type_of_user = User.query.filter_by(email=email).first().type_of_user

                if type_of_user == "Mentee":
                    sendQuery = Mentor.query.filter(id!=user_id).all()
                    # print("SENDQUERY!!!!" + str(sendQuery))
                elif type_of_user == "Mentor":
                    sendQuery = Mentee.query.filter(id!=user_id).all()
                else: #type_of_user == 'Admin'
                    sendQuery = User.query.all()
                

                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)

                # return redirect(url_for('views.home'), sendQuery=sendQuery, type_of_user=type_of_user, user_id=user_id)
                session['type_of_user'] = str(type_of_user)
                session['userid'] = str(user_id)
                session['sendQuery'] = str(sendQuery)
                return redirect(url_for('views.home')) # , type_of_user=type_of_user, user_id=user_id, sendQuery=sendQuery

            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    type_of_user = current_user.type_of_user
    current_user_specifics = User.query.filter_by(id = current_user.id).first()
    if type_of_user == "Mentee":
        check_users = Mentor.query.filter(id!=current_user.id).all()
        current_mentee = Mentee.query.filter_by(id=current_user.id).first()
        current_user_specifics = current_mentee
    elif type_of_user == "Mentor":
        check_users = Mentee.query.filter(id!=current_user.id).all()
        current_mentor = Mentor.query.filter_by(id=current_user.id).first()
        current_user_specifics = current_mentor
    else:
        check_users = Users.query.all()
        current_admin = Admin.query.filter_by(id=current_user.id).first()
        current_user_specifics = current_admin
        

    if request.method == 'POST':

        ## DELETE ACCOUNT?
        wants_to_delete = request.form.get("DELETE")
        if wants_to_delete:
            print("     H EEH EH EH EHE HE they wanna delete: " + str(wants_to_delete))
        
            verify_callsign = request.form.get("verify_callsign")
            print("VERIFY: " + str(verify_callsign))
            userVar = User.query.filter(User.id==current_user_specifics.id).first()
            userCallsign = userVar.callsign
            check_str = "verify_" + userCallsign
            if verify_callsign == userCallsign:
                

                # delete account
                if type_of_user == "Mentor":
                    # find all connections that include this user
                    delconn = Connections.query.filter(Connections.mentorID==current_user_specifics.id).all()
                    for eachdelconn in delconn:
                        db.session.delete(eachdelconn)

                    db.session.delete(current_mentor)
                elif type_of_user == "Mentee":
                    # find all connections that include this user
                    delconn = Connections.query.filter(Connections.menteeID==current_user_specifics.id).all()
                    for eachdelconn in delconn:
                        db.session.delete(eachdelconn)

                    db.session.delete(current_mentee)

                elif type_of_user == "Admin":
                    db.session.delete(current_admin)
                db.session.delete(current_user)

                #delete any connections that involve this account VvV

                db.session.commit()

                #send back to sign_up.html page
                return redirect(url_for('auth.login'))
                flash("Account deleted successfully", category='success')
            else:
                flash("Incorrect callsign, did not delete account", category='error')


            



        new_email = request.form.get('new_email')
        if new_email:
            if len(new_email) < 4:
                flash('Email must be greater than 3 characters.', category='error') 
            else: # valid email
                #change email to new_email
                current_user.email = new_email
                # db.session.commit()

        new_callsign = request.form.get('new_callsign')
        if new_callsign:
            if len(new_callsign) < 2:
                flash('Call-Sign must be greater than 1 character.', category='error')
            else: # valid call-sign
                # change call-sign to new_call-sign
                current_user.callsign = new_callsign
                # db.session.commit()

        # new_password = generate_password_hash(request.form.get('new_password'), method='sha256')
        new_password = request.form.get('new_password')
        if new_password:
            if len(new_password) < 7:
                flash('Password must be atleast 7 characters.', category='error')
            else: # valid password
                # change password to new_password
                current_user.password = generate_password_hash(new_password,method='sha256')
                # db.session.commit()

        # # # MENTEE # # #
        if type_of_user == 'Mentee':
            current_mentee = Mentee.query.filter_by(id=current_user.id).first()
            new_major = request.form.get('new_major')
            if new_major:
                current_mentee.major = new_major
                # db.session.commit()
            new_gradyear = request.form.get('new_gradyear')
            if new_gradyear:
                current_mentee.grad_year = new_gradyear
                # db.session.commit()
            new_bio = request.form.get('new_bio')
            if new_bio:
                current_mentee.bio = new_bio
                # db.session.commit()
            new_currentschool = request.form.get('new_currentschool')
            if new_currentschool:
                current_mentee.current_school = new_currentschool
            current_user_specifics = current_mentee

        # # # MENTOR # # #
        elif type_of_user == 'Mentor':
            current_mentor = Mentor.query.filter_by(id=current_user.id).first()
            new_major = request.form.get('new_major')
            if new_major:
                current_mentor.major = new_major
                # db.session.commit()
            new_gradyear = request.form.get('new_gradyear')
            if new_gradyear:
                current_mentor.grad_year = new_gradyear
                # db.session.commit()
            new_bio = request.form.get('new_bio')
            if new_bio:
                current_mentor.bio = new_bio
                # db.session.commit()
            new_position = request.form.get('new_position')
            if new_position:
                current_mentor.position = new_position
            new_levelofeducation = request.form.get('new_levelofeducation')
            if new_levelofeducation:
                current_mentor.levelOfEducation = new_levelofeducation
            current_user_specifics = current_mentor
        # # # ADMIN # # #
        elif type_of_user =='Admin':
            current_user_specifics = Admin.query.filter_by(id=current_user.id).first()
            pass
        db.session.commit()


        # accept connection
        for each in check_users:
            offer_conn = request.form.get(str(each.id))
            print("THIS USER CHECKING: " + str(each))
            if offer_conn:
                # CONNECT WITH USER
                print("USER: " + str(current_user.id) + " REQUESTED TO CONNECT WITH USER: " + str(each.id))
                if type_of_user == 'Mentor':
                        now = datetime.now()
                        new_connection = Connections.query.filter(and_(Connections.mentorID==current_user.id, Connections.menteeID==each.id, Connections.id_sentBy==each.id)).first()
                        if new_connection:
                            print("found something !! ! ! ! ! ! : " + str(new_connection))
                        new_connection.date_accepted = now
                        # db.session.add(new_connection)
                        db.session.commit()
                        flash('Connection Request accepted!', category='success')
                elif type_of_user == 'Mentee':
                        now = datetime.now()
                        new_connection = Connections.query.filter(and_(Connections.menteeID==current_user.id, Connections.mentorID==each.id, Connections.id_sentBy==each.id))
                        new_connection.date_accepted = now
                        db.session.commit()
                        flash('Connection Request accepted!', category='success')
   

        # deny connection
        for each in check_users:
            offer_conn = request.form.get(str(each.id) + "deny")
            print("THIS USER DENYING: " + str(each))
            if offer_conn:
                # CONNECT WITH USER
                print("USER: " + str(current_user.id) + " DENIED TO CONNECT WITH USER: " + str(each.id))
                if type_of_user == 'Mentor':
                        delconn = Connections.query.filter(Connections.mentorID==current_user_specifics.id).filter(Connections.menteeID==each.id).first()
                        db.session.delete(delconn)

                        db.session.commit()
                        flash('Connection Request denied!', category='success')
                elif type_of_user == 'Mentee':
                        delconn = Connections.query.filter(Connections.menteeID==current_user_specifics.id).filter(Connections.mentorID==each.id).first()
                        db.session.delete(delconn)
                        db.session.commit()
                        flash('Connection Request denied!', category='success')

        # delete connection
        for each in check_users:
            offer_conn = request.form.get(str(each.id) + "delete")
            print("THIS USER DENYING: " + str(each))
            if offer_conn:
                # CONNECT WITH USER
                print("USER: " + str(current_user.id) + " DENIED TO CONNECT WITH USER: " + str(each.id))
                if type_of_user == 'Mentor':
                        delconn = Connections.query.filter(Connections.mentorID==current_user_specifics.id).filter(Connections.menteeID==each.id).first()
                        db.session.delete(delconn)
                        db.session.commit()
                        flash('Connection Deleted!', category='success')
                elif type_of_user == 'Mentee':
                        delconn = Connections.query.filter(Connections.menteeID==current_user_specifics.id).filter(Connections.mentorID==each.id).first()
                        db.session.delete(delconn)
                        db.session.commit()
                        flash('Connection Deleted!', category='success')
   
   
    # query to send to html
    
    if type_of_user == 'Mentor':
        sendquery = Mentor.query.filter_by(id=current_user.id).first()
        # joined = User.join(Mentor, User.c.id == Mentor.c.id).filter_by(id=current_user.id).first()
        joined = db.session.query(User).join(Mentor, User.id == Mentor.id).filter_by(id=current_user.id).first()
        # specific_connections = db.session.query(Connections, Mentee).filter(Connections.menteeID == Mentee.id).filter(Connections.mentorID == current_user.id)
        # specific_connections = Connections.query.join(Mentee, Connections.menteeID == Mentee.id).all()
        specific_connections = db.session.query(Connections,Mentee).join(Mentee, Connections.menteeID == Mentee.id).filter(Connections.id_sentBy != current_user.id).all()
        verified_connections = db.session.query(Connections,Mentee).join(Mentee, Connections.menteeID == Mentee.id).filter(or_(Connections.id_sentBy == current_user.id, Connections.id_sentBy != current_user.id and Connections.date_accepted != None)).all()
        print("PLEASE WORK!!!!    : " + str(verified_connections))
    elif type_of_user == 'Mentee':
        sendquery = Mentee.query.filter_by(id=current_user.id).first()
        # joined = User.join(Mentee, User.c.id == Mentee.c.id).filter_by(id=current_user.id).first()
        joined = db.session.query(User).join(Mentee, User.id == Mentee.id).filter_by(id=current_user.id).first()
        specific_connections = Connections.query.join(Mentor, Connections.menteeID == Mentor.id).all()
        verified_connections = db.session.query(Connections,Mentor).join(Mentor, Connections.mentorID == Mentor.id).filter(or_(Connections.id_sentBy == current_user.id, Connections.id_sentBy != current_user.id and Connections.date_accepted != None)).all()

    elif type_of_user == 'Admin':
        sendquery = Admin.query.filter_by(id=current_user.id).first()
        # joined = User.join(Admin, User.c.id == Admin.c.id).filter_by(id=current_user.id).first()
        # joined = User.join(Mentor, User.c.id == Mentor.c.id).filter_by(id=current_user.id).first()
        specific_connections = Connections.query.all()

    print(str( db.session.query(Connections,Mentee).join(Mentee, Connections.menteeID == Mentee.id)))
    print(str(specific_connections))
    for eachconnection, eachmentee in specific_connections:
        print ("CONN: " + str(eachconnection))
        print (str(eachconnection.date_sent))
        print ("MENT: " + str(eachmentee))
        print (str(eachmentee.grad_year))
        print ("")


    return render_template("profile.html", user=current_user, sendquery=sendquery, type_of_user=type_of_user, joined=joined, current_user_specifics=current_user_specifics, specific_connections=specific_connections, verified_connections=verified_connections)




@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    defaultLevelOfAccess = 1
    if request.method == 'POST':
        # get all important information from sign-up form
        email = request.form.get('email')
        callsign = request.form.get('callsign')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        type_of_user = request.form.get('type_of_user')
        userEmail = email

        # get user's id to verify the same ID is used in Mentor/Mentee/Admin table
        user = User.query.filter_by(email=email).first()

        # exception handling
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(callsign) < 2:
            flash('Call-Sign must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif type_of_user == 'Admin' and password1 != 'Admin123':
            flash('Restricted Access', category='error')
        else:
            # no exceptions, begin adding new user
            if type_of_user == 'Admin' or type_of_user == 'Mentor' or type_of_user == 'Mentee':
                

                


                # statement = text("SELECT id FROM user WHERE email=:email")
                # statement = statement.columns(User.id, User.email)
                # newestID = db.session.query(User.id, User.email).from_statement(statement).params(email=userEmail).all()
                # print("****newestID: "+ str(newestID))
                new_user = User(email=email, password=generate_password_hash(password1, method='sha256'), type_of_user=type_of_user, callsign=callsign)
                db.session.add(new_user)
                db.session.commit()


                engine = create_engine("sqlite:///database.db",connect_args={"check_same_thread": False}, poolclass=StaticPool)

                # idRec = database.execute("SELECT * FROM user ORDER BY id")
                # print(idRec[0].id)

                user_id = User.query.filter_by(email=email).first().id
                # print("HERE VV")
                # print(user_id)
                # # print(userID.id)
                # print("HERE ^^")


                """
                if type_of_user == "Mentee":
                    sendQuery = Mentee.query.filter(email!=email).all()
                elif type_of_user == "Mentor":
                    sendQuery = Mentor.query.filter(email!=email).all()
                else: #type_of_user == 'Admin'
                    sendQuery = User.query.all()
                """



                """
                connection = engine.connect()
                stmt = 'SELECT * FROM user'
                results = connection.execute(stmt).fetchall()
                print(results)
                """

                """
                #engine = create_engine("dburl://user:pass@database/schema")
                metadata = MetaData(bind=None)
                table = Table(
                    'user', 
                    metadata, 
                    autoload=True, 
                    autoload_with=engine
                )

                stmt = select([
                    table.columns.id]
                )
                # .where(and_(
                #     table.columns.column1 == 'filter1', 
                #     table.columns.column2 == 'filter2'   
                # )

                connection = engine.connect()
                results = connection.execute(stmt).fetchall()
                for row in results:
                    print(row)
                print("SHOULD BE HERE!!!! ^^")
                """



                # engine = create_engine("sqlite:///database.db", echo=True)

                # connection = engine.raw_connection()
                # try:
                #     cursor = connection.cursor()
                #     cursor.execute("select * from User") # ; select * from table2")
                #     results_one = cursor.fetchall()
                #     # cursor.nextset()
                #     # results_two = cursor.fetchall()
                #     print("****HERE: " + str(results_one))
                #     cursor.close()
                # except:
                #     print("******IT DIDNT WORK")
                # finally:
                #     connection.close()


                # with engine.begin() as conn:
                #     qry = sqlalchemy.text("SELECT * FROM user WHERE id>5")
                #     resultset = conn.execute(qry)
                #     results_as_dict = resultset.mappings().all()
                #     print("        VVvvVvvVv HERE IT IS VvVvVV")
                #     print(results_as_dict)
                #     """
                #     [{'FirstName': 'Gord', 'LastName': 'Thompson'}, 
                #     {'FirstName': 'Bob', 'LastName': 'Loblaw'}]
                #     """




                


                # inspector = inspect(engine)
                # for table_name in inspector.get_table_names():
                #     for column in inspector.get_columns(table_name):
                #         print("***Column: %s" % column['name'])



                # print("****new_user: " + str(new_user))
                # newID = User.query.filter(User.email==userEmail)
                # print("****newID: " + str(newID))
                # newID2 = select([User.id]).where(User.email==userEmail)
                # print("****newID2: "+ str(newID2))

                # with sqlite3.connect("database.db",check_same_thread=False) as con:
                #     cur = con.cursor()
                #     cur.execute("SELECT id FROM user WHERE user.email= (?)",(email))
                #     con.commit()

                #engine = create_engine("sqlite:///database.db", echo=True)

                # Base.metadata.create_all(bind=engine)
                
                # metadata = MetaData(engine) ######
                # metadata = MetaData()
                # users = Table('User', metadata, Column('id', Integer, primary_key=True), Column('type_of_user', String(100)), Column('email', String(150), unique=True), Column('password', String(150)))
                # users = Table('User', metadata, autoload=True, autoload_with=engine)

                # metadata.create_all(engine) #####

                # conn = engine.connect()
                # conn = engine.raw_connection()
                
                #s = select([users]) # .where(User.email==userEmail) # << error w user and user


                # s = select([User])
                # print("s: " + str(s))
                # precursor = conn.cursor()
                # result = conn.execute(s).fetch()
                # print(result)
                # cursor = conn.cursor()
                # print("result: " + str(result))
                # for row in result:
                    # print("*** * * *ROW: " + row)
                # print("****PRECURSOR: " + str(precursor))
                # print("****CURSOR: " + str(cursor))


                """
                metadata = MetaData()
                # users = Table('User', metadata, Column('id', Integer, primary_key=True), Column('type_of_user', String(100)), Column('email', String(150), unique=True), Column('password', String(150)))
                users = Table('User', metadata, autoload=True, autoload_with=engine)

                metadata.create_all(engine) #####

                conn = engine.connect()
                # conn = engine.raw_connection()
                
                #s = select([users]) # .where(User.email==userEmail) # << error w user and user


                s = select([User])
                print("s: " + str(s))
                # precursor = conn.cursor()
                result = conn.execute(s).fetch()
                print(result)
                # cursor = conn.cursor()
                print("result: " + str(result))
                for row in result:
                    print("*** * * *ROW: " + row)
                # print("****PRECURSOR: " + str(precursor))
                # print("****CURSOR: " + str(cursor))


                """



                # Session = sessionmaker(bind=engine)
                # session = Session()
                # trial1 = session.query(User).all()
                # for everyUser in trial1:
                #     print("User: " + everyUser.email + " ID: " + everyUser.id)
                # trial2 = session.query(User.id).where(User.email==email)
                # print("trial2: " + str(trial2))
                 



                #add .where to select statement and then add id to insert below ###################################################################################################################################
                # select id from users where user.email = email

                # select * from ____ where user.id != id



                # userID = cur.execute('SELECT id FROM User WHERE email=:email')
                # print(userID)
                if type_of_user == 'Admin':
                    new_user2 = Admin(id = int(user_id), callsign=callsign, levelOfAccess=int(defaultLevelOfAccess)) # id=int(result[0])
                elif type_of_user == 'Mentor':
                    new_user2 = Mentor(id = int(user_id))
                elif type_of_user == 'Mentee':
                    new_user2 = Mentee(id = int(user_id))
                # print("new_user.id: " + str(newID) + " new_user2.id: " + str(new_user2.id))
                
                db.session.add(new_user2)
                db.session.commit()
                login_user(new_user, remember=True)
                flash('Account created!', category='success')
                if type_of_user == "Mentee":
                    sendQuery = Mentor.query.filter(id!=user_id).all()
                    # print("SENDQUERY!!!!" + str(sendQuery))
                elif type_of_user == "Mentor":
                    sendQuery = Mentee.query.filter(id!=user_id).all()
                else: #type_of_user == 'Admin'
                    sendQuery = User.query.all()
                    accesslevel = Admin.query.filter_by(id=user_id).first().levelOfAccess
                    session['levelofaccess'] = str(accesslevel)
                print("INSERT INTO User (email,password,type_of_user)" + '\n' + "VALUES (" + email + "," + password1 + "," + type_of_user + ")")
                if type_of_user == 'Admin':
                    session['type_of_user'] = str(type_of_user)
                    # print("THIS IS IT BOIZZZZZ !!!11!!`~~~~~``~~~~~~~~`~~" + str(type_of_user))
                    session['userid'] = str(user_id)
                    session['sendQuery'] = str(sendQuery)
                    session['levelofaccess'] = str(defaultLevelOfAccess)
                    print("INSERT INTO " + type_of_user + " (callsign,levelOfAccess)" + '\n' + "VALUES (" + callsign + "," + str(defaultLevelOfAccess) + ")")
                    return redirect(url_for('views.home'))
                    # return redirect(url_for('views.home', type_of_user=type_of_user, user_id=user_id, level_of_access=levelOfAccess))

                else:
                    print("INSERT INTO " + type_of_user + " (callsign)" + '\n' + "VALUES (" + callsign + ")")

                session['type_of_user'] = str(type_of_user)
                # print("THIS IS IT BOIZZZZZ !!!11!!`~~~~~``~~~~~~~~`~~" + str(type_of_user))
                session['userid'] = str(user_id)
                session['sendQuery'] = str(sendQuery)
                # print("* * **  CHECK IT HERE V.vV>v.vV>v * * ** ")
                # print(sendQuery)
                # print(" -- - -- - - -- -")

                # return redirect(url_for('views.home', type_of_user=type_of_user, user_id=user_id, sendQuery=sendQuery)) # return redirect(url_for('views.home') )
                return redirect(url_for('views.home')) # return redirect(url_for('views.home') )

            else:
                flash('Unkown Error, try selecting valid type of user', category='error')

            

    return render_template("sign_up.html", user=current_user)




"""
{% if type_of_user == 'Admin' %}
    <h2 align="center">Mentors</h2>
    <table style="width:100%" border="1" align="center">
    <tr>
      <th>Graduation Year</th>
      <th>Major</th>
      <th>Position</th>
      <th>Bio</th>
    </tr>   
    {% for each in mentorQuery %}
    <!-- {% if (each.grad_year != None and each.grad_year != "NONE") or (each.major != None and each.major != "NONE") or (each.position != None and each.position != "NONE") or (each.bio != None and each.bio != "NONE") %} -->
        <tr>
          <td>{{ each.grad_year }}</td>
          <td>{{ each.major }}</td>
          <td>{{ each.position }}</td>
          <td>{{ each.bio }}</td>
        </tr>
      <!-- {% endif %} -->
    {% endfor %}
  </table>
  <br> <br> <br>
  <h2 align="center">Mentees</h2>
  <table style="width:100%" border="1" align="center">
    <tr>
      <th>Graduation Year</th>
      <th>Major</th>
      <th>Current School</th>
      <th>Bio</th>
    </tr>
    {% for each in menteeQuery %}
    <!-- {% if (each.grad_year != None and each.grad_year != "NONE") or (each.major != None and each.major != "NONE") or (each.current_school != None and each.current_school != "NONE") or (each.bio != None and each.bio != "NONE") %} -->
    <tr>
      <td>{{ each.grad_year }}</td>
      <td>{{ each.major }}</td>
      <td>{{ each.current_school }}</td>
      <td>{{ each.bio }}</td>
    </tr>
    <!-- {% endif %} -->
    {% endfor %}
    </table>
    {% endif %}
"""