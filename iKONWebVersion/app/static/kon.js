//first functions when the game.html is sent to the browser. Updates scoreboard and allows each button to be clicked (or touched on mobile) to enact the buttonClick function
$(document).ready(function(){
    updateScoreboard()
    $(document).on("click", "#year1" , function(e) {
        $("#popup-message").css("display", "block");
        e.preventDefault();
        e.stopImmediatePropagation();
        buttonClick(1)
    })
    $(document).on("click", "#year2" , function(e) {
        $("#popup-message").css("display", "block");
        e.preventDefault();
        e.stopImmediatePropagation();
        buttonClick(2)
    })
    $(document).on("click", "#equals" , function(e) {
        $("#popup-message").css("display", "block");
        e.preventDefault();
        e.stopImmediatePropagation();
        buttonClick(3)
    })
    $(document).on("click", "#idk" , function(e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        buttonClick(4)
    })
})


//takes the top 10 of the users list, which is sent from the python backend, and wraps each user in html to be added to the scoreboard
function updateScoreboard()
{
    $("#scoreboard").html("")
    for (var i=0; i<users.length && i<11; i++)
    {
        var wrapped = wrapUser(users[i], i)
        $("#scoreboard").append(wrapped)
    }
}

//user wrapping in html function - based off place in leaderboard
function wrapUser(user, index)
{
    var name = user["name"]
    score=user["score"]
    if (index==0)
    {
        var wrap = '<div id="firstplace"><img class = "icon" src ="../static/images/generic_avatar.png">'+name+'<span style="float:right">'+score+' points</span></div>'
        return wrap
    }
    else if (index==1 || index==2)
    {
        var wrap = '<div class="secondthird"><img class = "icon" src ="../static/images/generic_avatar.png">'+name+'<span style="float:right">'+score+' points</span></div>'
        return wrap
    }
    else
    {
        var wrap = '<div class="scorers"><img class = "icon" src ="../static/images/generic_avatar.png">'+name+'<span style="float:right">'+score+' points</span></div>'
        return wrap
    }
}

//function to send vote from user to backend 
function buttonClick(button)
{
    var buttonPressed = {"button": button,
                        "year1": $("#year1").text().replace(/\s/g,''),
                        "year2": $("#year2").text().replace(/\s/g,'')}
                        //sends which button user chose and the years after removing whitespace
    //ajax request
    $.ajax({
        type: "POST",
        url: "/button",
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(buttonPressed),
        //on success:
        success: function(result){
            // close pop up window
            $("#popup-message").css("display", "none");

            //creating variables for all the return values
            year1=result["year1"]
            year2=result["year2"]
            users=result["users"]
            userScore=result["score"]
            name=result["name"]
            voted=result["voted"]
            satChecker=result["satChecker"]
            stationChecker=result["stationChecker"]
            votesChecker=result["voteChecker"]

            let stationName = result["stationName"]
            let satName = result["satName"]
            let voteCount = result["voteCount"]

            let script_dict = result["script_dict"]

            //setting buttons value to new years and updating user's score and scoreboard
            $("#year1").text(year1)
            $("#year2").text(year2)
            $("#points").text(userScore)
            updateScoreboard(users)
            
            //if the user doesn't say they don't know:
            if (voted){
                //hides the responses from last time and makes sure "You matched with:" is not hidden 
                $("#none").addClass("hidden")
                $("#satImage").addClass("hidden")
                $("#stationImage").addClass("hidden")
                $("#userImage").addClass("hidden")
                $("#match").removeClass("hidden")

                //if user correctly answered the year based on satellite, station or user data, the information is shown
                if(satChecker){
                    $("#satellite").html(script_dict["satellite_matched"] + "<br>" + satName)
                    $("#satImage").removeClass("hidden")
                }
                if(stationChecker){
                    $("#station").html(script_dict["station_matched"] + "<br>" + stationName)
                    $("#stationImage").removeClass("hidden")
                }
                if(votesChecker){
                    $("#userNumbers").html(script_dict["user_matched"] + "<br>" + voteCount)
                    $("#userImage").removeClass("hidden")
                }

                //if none of the data matches with user's answer, user is told they matched with no data
                if(!satChecker && !stationChecker && !votesChecker)
                {
                    $("#none").removeClass("hidden")
                }
            }
            else{
                //if user says they don't know, every response is hidden
                $("#match").addClass("hidden")
                $("#none").addClass("hidden")
                $("#satImage").addClass("hidden")
                $("#stationImage").addClass("hidden")
                $("#userImage").addClass("hidden")
            }
        },
        //in case of error
        error: function(request, status, error){
            console.log("Error");
            console.log(request)
            console.log(status)
            console.log(error)
        }
    })
}