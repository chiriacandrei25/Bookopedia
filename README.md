# Description
### Bookopedia

Bookopedia is a social network that offers readers the possibility to record and share their progress, such as what books they have read, have been reading or wish to read next.
They also can discover similar books to one of their favorites through the recommendation system.

## Installation
### Dependencies
- Python Flask
- SQL Alchemy
- Flask SocketIO
- Flask BCrypt
- Flask Login
- Flask Mail
- Flask WTForms
- Pickle
- Pandas
- SKLearn

The libraries can be installed on Windows, Ubuntu 16.04 and macOS via pip:
```
pip install Flask
pip install SQLAlchemy
pip install flask-socketio
pip install flask-bcrypt
pip install flask-login
pip install flask-mail
pip install flask-wtforms
pip install pickle
pip install pandas
pip install sklearn
```

### Testing the Installation
You can test that you have correctly installed the app by running the following command:

```
python run.py
```

## Using Bookopedia
### Register

In the registration page there are 5 mandatory fields that must be filled in: first name, last name, email, password and password confirmation. If one of the fields is not filled in or invalid, a suggestive message will be displayed next to it. If successful, the user is redirected to the login page. <br/> <br/>
![](https://github.com/chiriacandrei25/Bookopedia/blob/master/Register.PNG)<br/><br/>
On the login page, the user must fill in the email and password fields, which are verified in the database. To facilitate future logging, the user has the option to check the "Remember me" field, so his credentials are retained after the session expires. If successful, the user is redirected to the main page.<br/><br/>
![](https://github.com/chiriacandrei25/Bookopedia/blob/master/Login.PNG)<br/><br/>
The central area, called the news area, contains the actions taken by users in our friends list, sorted from newest to oldest. There are two types of news: adding a book to a shelf and writing a review.<br/><br/>
![](https://github.com/chiriacandrei25/Bookopedia/blob/master/New%20Feed.PNG)<br/><br/>
An important page is a user's profile page. It contains on the left the profile picture of the user, and in the center his name, together with the title of Administrator if applicable.<br/><br/>
![](https://github.com/chiriacandrei25/Bookopedia/blob/master/User_Profile_1.PNG)<br/><br/>
The notifications icon is dropdown, and when pressed, all notifications specific to the current user are displayed. These notifications are updated in real time when another user appreciates or comments on a news item or a review of the current user. Similar to this, we have icons with friend requests and messages from other users.<br/><br/>
![](https://github.com/chiriacandrei25/Bookopedia/blob/master/Notifications.PNG)<br/>

