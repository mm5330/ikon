$(document).ready(function(){
    updateScoreboard()
    $(document).on("click", "#year1" , function() {
        buttonClick(1)
    })
    $(document).on("click", "#year2" , function() {
        buttonClick(2)
    })
    $(document).on("click", "#equals" , function() {
        buttonClick(3)
    })
    $(document).on("click", "#idk" , function() {
        buttonClick(4)
    })
})

function updateScoreboard()
{
    $("#scoreboard").html("")
    for (var i=0; i<users.length && i<11; i++)
    {
        var wrapped = wrapUser(users[i], i)
        $("#scoreboard").append(wrapped)
    }
}

function wrapUser(user, index)
{
    var name = user["name"]
    score=user["score"]
    if (index==0)
    {
        var wrap = '<div id="firstplace"> <img class = "icon" src ="https://www.nhlbi.nih.gov/sites/default/files/styles/square_crop/public/2017-12/genericavatar_55.png?itok=XOsJyktf">'+name+'<span style="float:right">'+score+' points</span></div>'
        return wrap
    }
    else if (index==1 || index==2)
    {
        var wrap = '<div class="secondthird"> <img class = "icon" src ="https://www.nhlbi.nih.gov/sites/default/files/styles/square_crop/public/2017-12/genericavatar_55.png?itok=XOsJyktf">'+name+'<span style="float:right">'+score+' points</span></div>'
        return wrap
    }
    else
    {
        var wrap = '<div class="scorers"> <img class = "icon" src ="https://www.nhlbi.nih.gov/sites/default/files/styles/square_crop/public/2017-12/genericavatar_55.png?itok=XOsJyktf">'+name+'<span style="float:right">'+score+' points</span></div>'
        return wrap
    }
}

function buttonClick(button)
{
    var buttonPressed = {"button": button,
                        "year1": $("#year1").text().replace(/\s/g,''),
                        "year2": $("#year2").text().replace(/\s/g,'')}
    $.ajax({
        type: "POST",
        url: "/button",
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(buttonPressed),
        success: function(result){
            year1=result["year1"]
            year2=result["year2"]
            users=result["users"]
            userScore=result["score"]
            name=result["name"]
            voted=result["voted"]
            satChecker=result["satChecker"]
            stationChecker=result["stationChecker"]
            votesChecker=result["votesChecker"]
            $("#year1").text(year1)
            $("#year2").text(year2)
            $("#points").text(userScore)
            updateScoreboard()
            if (voted){
                $("#none").addClass("hidden")
                $("#satImage").addClass("hidden")
                $("#stationImage").addClass("hidden")
                $("#userImage").addClass("hidden")
                $("#match").removeClass("hidden")
                if(satChecker){
                    $("#satImage").removeClass("hidden")
                }
                if(stationChecker){
                    $("#stationImage").removeClass("hidden")
                }
                if(votesChecker){
                    $("#userImage").removeClass("hidden")
                }
                if(!satChecker && !stationChecker && !votesChecker)
                {
                    $("#none").removeClass("hidden")
                }
            }
            else{
                $("#match").addClass("hidden")
                $("#none").addClass("hidden")
                $("#satImage").addClass("hidden")
                $("#stationImage").addClass("hidden")
                $("#userImage").addClass("hidden")
            }
        },
        error: function(request, status, error){
            console.log("Error");
            console.log(request)
            console.log(status)
            console.log(error)
        }
    })
}