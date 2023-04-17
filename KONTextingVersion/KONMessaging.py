from twilio.rest import Client
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# count = 0
# Your Account SID from twilio.com/console
account_sid = "sid"
# Your Auth Token from twilio.com/console
auth_token  = "auth"

client = Client(account_sid, auth_token)

comparisons = ["Which year was better - Reply: 1 for 2003, 2 for 2012, 3 for Same, 4 for I Don't Know",
 "Which year was better - Reply: 1 for 2004, 2 for 2009, 3 for Same, 4 for I Don't Know",
  "Which year was better - Reply: 1 for 2009, 2 for 2015, 3 for Same, 4 for I Don't Know",
  "Which year was better - Reply: 1 for 2002, 2 for 2010, 3 for Same, 4 for I Don't Know",
 "Which year was better - Reply: 1 for 2005, 2 for 2009, 3 for Same, 4 for I Don't Know",
  "Which year was better - Reply: 1 for 2007, 2 for 2015, 3 for Same, 4 for I Don't Know"]
count = 0
winner = []
# count = 0

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    print(body)
    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    if body == "1":
        
        msg = resp.message("Congrats, you matched with satelite A")
    # Add a picture message
        msg.media("https://www.iconfinder.com/icons/3088386/download/png/512")

    elif body == "2":
        resp.message("You didn't match with anyone")

    elif body == "3":
        resp.message("You didn't match with anyone")
    
    elif body == "4":
        resp.message("That's ok. Lets move on!")

    elif body == "Start":
        resp.message("Welcome to KON!")

    global winner
    winner.append(body)
    global count
    # sendMessage(count)
    resp.message(comparisons[count])
    count = count + 1
    return str(resp)

def sendMessage(intcount):
    client.messages.create(
        to="+16468756700", 
        from_="+18024594058",
        body=comparisons[intcount])
    print(winner[intcount])

# sendMessage(count)

if __name__ == "__main__":
    app.run(debug=True)


    