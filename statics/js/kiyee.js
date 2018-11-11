$(function () {
    $("a[role='menuitem").click(function () {$(".dropdown-toggle").text($(this).text());$(".dropdown-toggle").css("color", "white");});
    $("[data-addRole='nopresentation").click(function () {$(".dropdown-toggle").css("color", "grey");});
    $( ".wiki-folding-trg" ).click(function() {var folder = $(this).parent().find("> .wiki-folding");folder.toggle('fold');});
  })
function moveindex(seq,tag){
  var scrolloff = $(tag).eq(seq).offset();
  $('html ,body').animate({scrollTop : scrolloff.top}, 1000);}
