## Description of Database
This database will allow mentors and mentees to login and view a database of other users to connect with, and send a connection request to other users. If the request is accepted, both users with be sent an email of eachothers' emails for them to then communicate via.

General steps to start using database:
1) create an account using sign up page
2) add personal information on profile page
3) begin looking for mentors/mentees and request to connect by clicking on their blue "Connect" button
4) await for users to accept your request, or accept other users' requests to connect on profile page
5) view all connections on profile page (and view emails of confirmed connections)

Additional tools:

Profile Page
    * Edit personal information
    * Delete account on the bottom by putting in your call-sign for verification
    * Deny incoming requests to connect
    * Delete connections

Home
    * By clicking on "Pending", you can rescind your connection request

## Running The App

```bash
pip install -r requirements.txt
```

```bash
python main.py
```

## Viewing The App

Go to `http://127.0.0.1:5000`


## Notes

I am currently in the process of pre-populating the database, so that functionalities such as finding other mentees/mentors is more effective out of the box
