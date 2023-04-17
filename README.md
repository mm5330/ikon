# iKON SMS & Web Versions

This directory contains both the SMS (Texting) version and the web version of the iKON project
in the folders "iKONSMSVersion" and "iKONWebVersion" respectively.
(The other folders are the older versions of the application.)
The code is still a work in progress, but all the basic functionalities have been implemented.
Below are the instructions for setting up both version respectively.

### Environment Setup
- As both versions require connection to IRI postgres database, you would need to be part of IRI's network
to have access, i.e. connect to IRI VPN
- Using a virtual environment is preferred though not required.
- Under the root directory, run `pip install -r requirements.txt` to load all the packages.


### SMS Version
- The main file of the sms version is "kon.py" under "iKONSMSVersion" directory.
- The followings are the configurations needed to run the sms version locally:
    - Set up your Twilio account (contact Max to get a proper account under "IRI FIST")
    - Run `./ngrok http 5000` to start tunneling, where "5000" is the port number the flask app running on. 
    ngrok would provide a forwarding address for your localhost. 
    (You can download ngrok from https://ngrok.com/download)
    - In Debugger / Webhook & Email Triggers, set the webhook to
    "<forwarding_address_by_ngrok>/sms" (e.g. http://d978fead6bfb.ngrok.io/sms)
    - In Phone Numbers / Manage Numbers / Active Numbers, select the number whose friendly name is "KON".
    In the Messaging section, set the webhook of both "A MESSAGE COMES IN" and "PRIMARY HANDLER FAILS"
    to "<forwarding_address_by_ngrok>/sms" (same as above).
- Finally, run `python kon.py` under the "KONSMSVersion" directory.
- Send (on your own mobile phone) an entry code (e.g. **NYNYN**) to the number for KON (+1 646 766 9995)
- Text "**Bye**" when you want to end the session or restart.
- Note that the messages are not case-sensitive.


### Web Version
- *The web version is currently unavailable because of unfinished database related updates*
- The latest version the web version is under the directory "iKONWebVersion".
- Run `python kon.py`. Visit "http://127.0.0.1:5100/" on your local browser.
- No other setup needed.


### Localization
- Each deployment has its own language scripts for both the web version and the sms version.
- To modify the current scripts or enable a new language script, use the "Script" table in the database.
  - The "content" column contains the json string of the script in which all the keys in "script_en.json" must be included.
  - The "version" column indicates whether the script is for "web" or "sms" version.
- The process currently can only be done from backend. Future versions will incorporate
this as a part of admin page.


### Future Work
- Code cleanup (Completed)
- An administration page for the web version, which would allow admins to define their own deployment. (Main task for Spring 2021)
- Integrate the actual satellite and weather station data from the design engine database. (Spring 2021)
- Try to resolve the latency issue caused by querying the database. (Partially completed, will get back to this when the integration with design engine database is finished)
- UI/UX improvement (e.g. intro/starting page showing the description of iKON project)


Author: Hongfei Chen

Contact: hc3222@columbia.edu

Updated on Feb 24, 2021