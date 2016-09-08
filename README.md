# Elections-R-Us
____  
## Week 5 Project September 2016
## Code Fellows Seattle Python 401


Elections-R-Us is a portal for Washington State voters seeking more information on candidates and referendums being considered for the upcoming election. Employing the Google Civic Information API,  Elections-R-Us delivers information to voters based on their entered address. The application provides secure registration and log-in allowing storage and retrieval of voting preferences. 

## Team Members
- Justin Lange
- Crystal Lessor
- Jeffery Russell
- Jeff Torres

## Deployment on Heroku

http://elections-r-us.herokuapp.com/

## Technologies
- Python 3.5
- Pyramid
- Jinja2
- Material Design Bootstrap 3
- SQLAlchemy


## Setup
1. Clone this repo
2. Create a new virtual environment
3. Run `createdb elections_r_us`
4. Edit your new environment's activate script, adding this line:
`export DATABASE_URL=postgres:///elections_r_us`
5. Activate and install:
```pip install -U pip setuptools -e .[testing]```
6. Run `init_db development.ini`
7. Run `pserve development.ini`