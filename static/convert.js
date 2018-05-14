$(document).ready(function(){
  console.log("page loaded");
  $("#convertButton").click(function(e){
    e.preventDefault();
    convertEetToASL();
  });

  $("#convertParagraphButton").click(function(e){
    e.preventDefault();
    getTokens();
  });
})


function convertEetToASL(e) {
    let subject = $("#eetSubject").val();
    $("#aslSubject").html(subject);
    let object = $("#eetObject").val();
    $("#aslObject").html(object);
    let verb = $("#eetVerb").val();
    $("#aslVerb").html(verb);
    let time = $("#eetTime").val();
    $("#aslTime").html(time);
    $( "#top" ).removeClass( "collapse" )
}


function setNewSentence(d) {
    let times = (d.times.length ? "Time: " + d.times.join() + ", " : "");
    let objects = (d.objects.length ? "Object: " + d.objects.join() + ", " : "");
    let subjects = (d.subjects.length ? "Subject: " + d.subjects.join() + ", ": "");
    let verbs = (d.verbs.length ? "Verb: " + d.verbs.join() + "" : "");
    $("#bottomConverted").html($("#bottomConverted").html() +  times +  objects +  subjects +  verbs + "<br />");
}


function getTokens(e) {
    $.ajax({
    url: "get_tosv_sentence",
    type: "POST",
    data: JSON.stringify($("#eetParagraph").val()),
    contentType: "application/json",
    complete: function(data){
            $("#bottomConverted").html("");
            data.responseJSON.forEach(setNewSentence);
            $( "#bottom" ).removeClass( "collapse" );
        }
    });
}
