## iKON Admin Page

### Overview
iKON Admin Page is a web application developed for iKON game administrators.
It provides a user-friendly interface for the administrators to create and customize their iKON deployments.

Using the Admin Page, the administrators can define new deployments or edit existing ones for different localities,
which includes selecting language scripts, choosing satellites and weather stations as data sources, 
and creating their own location lists for collecting user demographic information. 
While there are data provided for many options, the administrators may upload their own satellite and weather station data.
These new data sources will be available to other administrators once uploaded. 
The Admin Page also allows the administrators to customize the provided language scripts.

Besides, the Admin Page also provides a dashboard for each deployment,
which visualizes user engagement statistics and allows the administrators to monitor their deployments in real time.
Along with the dashboard, the administrators can download all user responses gathered and perform their own analysis.
(Note: The downloadable data will not contain information violating user privacy, such as phone number, unless authorized by the users.)

The changes made through the Admin Page will be reflected immediately on the iKON game.
However, to ensure the best experience for the players, it is highly recommended that
the administrators finalize their design choices for the deployments before releasing them to the players.


### Run on local machine
- Run terminal commands under the iKONadmin directory
  1. `pip3 install -r requirements.txt` to set up the environment
  2. `python admin.py` to run the program
- The webpage will be hosted on http://127.0.0.1:5100/ unless otherwise specified.
- Login credentials: 
  - username: test1, password: 123456
  - username: test2, password: 123456
    

### Some notes
- Once a deployment has been created, there will be 10 "fake users" generated with various scores and automatically added to the deployments.
  This is to help with the situation where an actual player entered the game in the early stage and
  does not see any other player, which may demotivate the player.
- When submitting edited language scripts, everything in the JSON editor must be expanded.
  Otherwise, the content will not be saved properly.
    

### Future works
- Security: Add an authorization step when redirecting to each page 
  (e.g. make sure the user logged in is the owner deployment when accessing dashboard)
- Language script: Add a function by which the administrator can alter the distribution of language configurations among players.
- Dashboard: Many improvements can be made, including maps, more useful statistics and charts, etc.
- Testing: Add a logging system and some tests.


### References
- Datta Able Flask: https://appseed.us/admin-dashboards/flask-dashboard-dattaable
- Apache Echarts: https://echarts.apache.org/en/index.html


Author: Hongfei Chen<br>
Contact: hc3222@columbia.edu

Last updated: May 21, 2021