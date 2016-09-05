# Elections-R-Us
## Week 5 project for Code Fellows Seattle PY 401


Elections-R-Us is a portal for voters looking for more information on prospective candidates up for election.
Elections-R-Us will serve information to voters based on their geographical location. It will present voters
with candidates based on their geographical location and their voting history where applicable. It will pull
from a wide variety of publicly available sources.


## Team Members:
- Jeffrey Russell
- Crystal Lessor
- Justin Lange
- Jeff Torres

## Setup
1. Clone this repo
2. Install (into a virtual environment!): `pip install -e .[testing]`
3. Run `createdb elections_r_us`
4. Edit your new environment's activate script, adding this line:
`export DATABASE_URL=postgres:///elections_r_us`
5. Run `init_db development.ini`
6. Run `pserve development.ini`
