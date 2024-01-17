from flask import Blueprint, render_template, request, flash, jsonify, redirect, session
from flask_login import login_required, current_user
from .models import User, Admin, Mentor, Mentee, Connections
# from .models import School, Company
from . import db
import json
from sqlalchemy import or_, and_
import sqlalchemy
from datetime import datetime
import flask_sqlalchemy
from sqlalchemy.orm import join

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # try:
    userid = session.get('userid', None)
    # sendQuery = session.get('sendQuery', None)
    type_of_user = session.get('type_of_user', None)
    if type_of_user == "Mentee":
        sendQuery = Mentor.query.filter(id!=current_user.id).all()
        # print("SENDQUERY!!!!" + str(sendQuery))
    elif type_of_user == "Mentor":
        sendQuery = Mentee.query.filter(id!=current_user.id).all()
    else: #type_of_user == 'Admin'
        sendQuery = User.query.all()

    if type_of_user == 'Mentor':
        accepted_connections = Connections.query.filter(and_(Connections.mentorID==userid,Connections.date_accepted != None)).all()
        unaccepted_connections = Connections.query.filter(and_(Connections.mentorID==userid,Connections.date_accepted == None)).all()
        users_connections = Connections.query.filter(Connections.menteeID==current_user.id).all()
        specific_connections = Connections.query.join(Mentee, Connections.menteeID == Mentee.id).all()
        # specific_connections = db.session.query(Connections).join(Mentee).all()
        # specific_connections = db.session.query(Connections,Mentee, (Connections.menteeID == Mentee.id and Connections.mentorID == current_user.id)).select_from(Connections).join(Mentee).all()
        # specific_connections = db.session.query(Connections,Mentee).select_from(Connections).join(Mentee).filter(and_(Connections.menteeID == Mentee.id, Connections.mentorID == current_user.id)).all()
        # accepted_connections = connection_table.query.filter(and_(mentorID==userid,date_accepted!=null)).all()
    elif type_of_user == 'Mentee':
        accepted_connections = Connections.query.filter(and_(Connections.menteeID==userid,Connections.date_accepted != None)).all()
        unaccepted_connections = Connections.query.filter(and_(Connections.menteeID==userid,Connections.date_accepted != None)).all()
        users_connections = Connections.query.filter(Connections.mentorID==current_user.id).all()
        specific_connections = Connections.query.join(Mentor, Connections.menteeID == Mentor.id).all()

        # specific_connections = db.session.query(Connections, Mentor, onclause=None).select_from(Connections).join(Mentor).all()  

        # specific_connections = db.session.query(Connections,Mentor).select_from(Connections).join(Mentor).filter(and_(Connections.mentorID == Mentor.id, Connections.menteeID == current_user.id)).all()

        # connection_table = Connections.query.filter_by(menteeID=userid).all()
    # else: Allow admins to see connections
    #     connection_table = Connections.query.filter_by()
    else: # type_of_user == 'Admin'
        accepted_connections = Connections.query.filter(Connections.date_accepted != None).all()
        unaccepted_connections = Connections.query.filter(Connections.date_accepted == None).all()
        users_connections = Connections.query.all()
        specific_connections = Connections.query.all()
    # print("    VVvvVvvVv SEND QUERY: VvVvVVvvV")
    # print(sendQuery)
    # arr = list(sendQuery)
    # arr.remove('[')
    # arr.remove(']')
    # length = len(arr)
    # new = ""
    # for x in range(0,len(arr)):
    #     if arr[x] != ' ':
    #         new += arr[x]
        
        
    # new = new.split(',')
    # sendQuery = new
    # print(sendQuery[0])
    print ("SPECIFIC CONNETIONS:")
    print(str(specific_connections))
    i = 1
    for eachconn in specific_connections:
        print("**" + str(i) + " : " + str(eachconn))
        i += 1
    print ("UP HERE ^^^")

    # user_id = int(userid)
    user_id = current_user.id
    type_of_user = type_of_user
    check_users = User.query.all()

    if type_of_user == "Mentee":
        sendQuery = Mentor.query.filter(id!=user_id).all()
        #print("SENDQUERY!!!!" + str(sendQuery))
        check_users = Mentor.query.all()

    elif type_of_user == "Mentor":
        sendQuery = Mentee.query.filter(id!=user_id).all()
        check_users = Mentee.query.filter(id!=user_id).all()
    else: #type_of_user == 'Admin'
        sendQuery = User.query.all()
        accesslevel = session.get('levelofaccess', None)
        menteeQuery = Mentee.query.all()
        mentorQuery = Mentor.query.all()

    
    if request.method == 'POST':
        for each in check_users:
            offer_conn = request.form.get(str(each.id))
            print("THIS USER CHECKING: " + str(each))
            if offer_conn:
                # CONNECT WITH USER
                print("USER: " + str(current_user.id) + " REQUESTED TO CONNECT WITH USER: " + str(each.id))
                if type_of_user == 'Mentor':
                    checking_double = Connections.query.filter(and_(Connections.mentorID==current_user.id, Connections.menteeID == each.id)).first()
                    if checking_double:
                        print("HEY YOU ALREADY DID THAT")
                        flash('Connection Request has been deleted', category='success')
                        # delete that ish
                        db.session.delete(checking_double)
                        db.session.commit()
                        pass
                    else: # is not duplicate, actually add connection
                        now = datetime.now()
                        new_connection = Connections(mentorID=current_user.id, menteeID=each.id, date_sent=now, id_sentBy=current_user.id)
                        db.session.add(new_connection)
                        db.session.commit()
                        flash('Connection Request Sent to user!', category='success')
                elif type_of_user == 'Mentee':
                    checking_double = Connections.query.filter(and_(Connections.mentorID == each.id, Connections.menteeID == current_user.id)).first()
                    if checking_double:
                        print("HEY YOU ALREADY DID THAT")
                        flash('Connection Request has been deleted', category='success')
                        # delete that ish
                        db.session.delete(checking_double)
                        db.session.commit()
                        pass
                    else: # is not duplicate, actually add cionnection
                        now = datetime.now()
                        new_connection = Connections(menteeID=current_user.id, mentorID=each.id, date_sent=now, id_sentBy=current_user.id)
                        db.session.add(new_connection)
                        db.session.commit()
                        flash('Connection Request Sent to user!', category='success')

            else:
                print("NOTHIN")
        # if len(note) < 1:
        #     flash('Note is too short!', category='error')
        # else:
        #     new_note = Note(data=note, user_id=current_user.id)
        #     db.session.add(new_note)
        #     db.session.commit()
        #     flash('Note added!', category='success')
            ##
            # testquery = User.query.all()
            # for eachUser in testquery:
            #     print("Type of user: " + eachUser.type_of_user + " Email: " + eachUser.email, " UserID: " + str(eachUser.id)) ################################### TESTING PURPOSES

            

            ##
    connections_table = Connections.query.all()
    menteeQuery = Mentee.query.filter(Mentee.id.isnot(current_user.id)).all()
    mentorQuery = Mentor.query.filter(or_(Mentor.id > current_user.id, Mentor.id < current_user.id))
    totalMentee = Mentee.query.all()
    # allMentees = menteeQuery.statement.execute().fetchall()
    # for eachMentee in menteeQuery:
    #     print("mentee: " + eachMentee.callsign + " ID: " + str(eachMentee.id))
    print("current User ID:" + str(current_user.id))
    if type_of_user == 'Admin':
        return render_template("home.html", user_id=userid, sendQuery=sendQuery, user=current_user, type_of_user=type_of_user, levelofaccess=accesslevel, menteeQuery=menteeQuery, mentorQuery=mentorQuery)

    else:
        return render_template("home.html", user_id=userid, sendQuery=sendQuery, user=current_user, type_of_user=type_of_user, accepted_connections=accepted_connections, connections_table=connections_table, users_connections=users_connections, specific_connections=specific_connections)
    # except:
        # return render_template("tryloggingin.html")

# @views.route('/delete-note', methods=['POST'])
# def delete_note():
#     note = json.loads(request.data)
#     noteId = note['noteId']
#     note = Note.query.get(noteId)
#     if note:
#         if note.user_id == current_user.id:
#             db.session.delete(note)
#             db.session.commit()

#     return jsonify({})
