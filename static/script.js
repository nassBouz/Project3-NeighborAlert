$(document).ready(function () {
// hamburger bar drop down and show me all nav links
  $(".fas.fa-bars").click(function() {
    // debugger;
    console.log(`hamburger menu clicked`);
    // grab the nav container and toggle to show/hide
    $(".nav-wrapper-flex").toggle();
    $(".hamburger-nav-bar").toggle();
  });

  $( "#signin" ).click( function() {
    $( "#signin-form" ).toggle( 'slow' );
  });

  $( "#signup" ).click( function() {
    $( "#signup-form" ).toggle( 'slow' );
  });
}); // end of (document).ready