$(document).ready(function(){
    updateScoreboard()
    if (finished){
        $("#year1").prop('disabled', true)
        $("#year2").prop('disabled', true)
        $("#equals").prop('disabled', true)
        $("#idk").prop('disabled', true)
        $("#match").removeClass("hidden")
        $("#match").text("You have responded to all pairs of years!")
    }
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
        var wrap = '<div id="firstplace">'+name+'<span style="float:right">'+score+' points</span></div>'
        return wrap
    }
    else if (index==1 || index==2)
    {
        var wrap = '<div class="secondthird">'+name+'<span style="float:right">'+score+' points</span></div>'
        return wrap
    }
    else
    {
        var wrap = '<div class="scorers">'+name+'<span style="float:right">'+score+' points</span></div>'
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
            checker1=result["checker1"]
            checker2=result["checker2"]
            checker3=result["checker3"]
            checker4=result["checker4"]
            finished=result["finished"]
            $("#year1").text(year1)
            $("#year2").text(year2)
            $("#points").text(userScore)
            updateScoreboard()
            if(finished)
            {
                $("#none").addClass("hidden")
                $("#farmingdale").addClass("hidden")
                $("#laguardia").addClass("hidden")
                $("#teterboro").addClass("hidden")
                $("#votesDiv").addClass("hidden")
                $("#year1").prop('disabled', true)
                $("#year2").prop('disabled', true)
                $("#equals").prop('disabled', true)
                $("#idk").prop('disabled', true)
                $("#match").removeClass("hidden")
                $("#match").text("You have responded to all pairs of years!")
            }
            else if (voted && !finished){
                $("#none").addClass("hidden")
                $("#farmingdale").addClass("hidden")
                $("#laguardia").addClass("hidden")
                $("#teterboro").addClass("hidden")
                $("#votesDiv").addClass("hidden")
                $("#match").removeClass("hidden")
                if(checker1){
                    $("#farmingdale").removeClass("hidden")
                }
                if(checker2){
                    $("#laguardia").removeClass("hidden")
                }
                if(checker3){
                    $("#teterboro").removeClass("hidden")
                }
                if(checker4){
                    $("#votesDiv").removeClass("hidden")
                }
                if(!checker1 && !checker2 && !checker3 && !checker4)
                {
                    $("#none").removeClass("hidden")
                }
            }
            else{
                $("#match").addClass("hidden")
                $("#none").addClass("hidden")
                $("#farmingdale").addClass("hidden")
                $("#laguardia").addClass("hidden")
                $("#teterboro").addClass("hidden")
                $("#votesDiv").addClass("hidden")
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