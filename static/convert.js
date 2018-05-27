$(document).ready(function(){
  console.log("page loaded");
  $("#convertParagraphButton").click(function(e){
    e.preventDefault();
    getTokens();
  });
})


const doc = document;

function setSentence(s) {
    let times = (s.times.length ? "Time: " + s.times.join() + ", " : "");
    let objects = (s.objects.length ? "Object: " + s.objects.join() + ", " : "");
    let subjects = (s.subjects.length ? "Subject: " + s.subjects.join() + ", ": "");
    let verbs = (s.verbs.length ? "Verb: " + s.verbs.join() + "" : "");
    $("#sentencesConverted").html($("#sentencesConverted").html() +  times +  objects +  subjects +  verbs + "<br />");
    debugger
}

function setVideo(v) {
    let video_container = document.createElement("div")
    video_container.classList.add("d-inline-block")

    let video_description = document.createElement("a")
    video_description.innerText = v[0]
    video_description.classList.add("row")
    video_description.classList.add("m-2")
    video_description.href = v[2]

    let video_iframe = document.createElement("iframe")
    video_iframe.src = v[1]
    video_iframe.classList.add("row")
    video_iframe.classList.add("m-2")
    video_iframe.width = 325
    video_iframe.height = 230

    let videos = document.querySelector("#signVideos")
    video_container.appendChild(video_description)
    video_container.appendChild(video_iframe)
    videos.appendChild(video_container)
}

function getTokens(e) {
    $.ajax({
    url: "get_tosv_sentence",
    type: "POST",
    data: JSON.stringify($("#eetParagraph").val()),
    contentType: "application/json",
    complete: function(data){

            // add and show sentences
            let sentences = document.querySelector("#sentencesConverted")
            data.responseJSON['sentences'].forEach(setSentence);
            $("#sentences").removeClass( "collapse" );

            // clear out previous videos and hide
            let signVideos = document.querySelector("#signVideos")
            $("#videos").addClass( "collapse" );
             while (signVideos.firstChild) {
                signVideos.removeChild(signVideos.firstChild)
            }

            // populate new videos and show
            data.responseJSON['videos'].forEach(setVideo);
            if (data.responseJSON['videos'].length > 0) {
                $("#videos").removeClass( "collapse" );
            }
        }
    });
}
