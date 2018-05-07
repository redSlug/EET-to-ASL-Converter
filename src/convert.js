$(document).ready(function(){
  console.log("page loaded");
  $("#converterForm").submit(function(e){
    e.preventDefault();
    convertEetToASL();
  });
})




function convertEetToASL(e) {
  let subject = $("#eetSubject").val();
  $("#aslSubject").val(subject);
  let object = $("#eetObject").val();
  $("#aslObject").val(object);
  let verb = $("#eetVerb").val();
  $("#aslVerb").val(verb);
  let time = $("#eetTime").val();
  $("#aslTime").val(time);
}
