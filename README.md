# login-app2.7
functional on py2 but not py3

# login-app

1.) Download the zip of login-app from this link: 
(python3) https://github.com/bmdatl/login-app 
(python2) https://github.com/bmdatl/login-app2.7

2.) Open terminal. 
	2.1) if pip is not already installed, type: sudo easy_install pip
	
3.) Type: sudo pip install virtualenv

4.) Type: cd downloads/login-app-master (or cd downloads/login-app2.7-master)

5.) For python3, type: virtualenv -p python3 venv 
	5.1) For python2, type: virtualenv venv
	
6.) Type: source venv/bin/activate

7.) Type: pip install -r requirements.txt

8.) Type: python app.py

9.) To use the app, go to your browser and enter localhost:5000


to check out the database:

in terminal, in the login-app-master directory, type sqlite3 database.db

to see stored users:

select * from users;