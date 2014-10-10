$(document).ready(function() {
    $("#header, #footer").animate({height:"10%"}, 2000, 'swing');
    $('#fullpage').fullpage({
        verticalCentered: false,
        sectionsColor : ['black', '#88abaf', '#99b089', '#b08d89'],
        anchors:[],
        scrollingSpeed: 600,
        navigation: true,
        navigationPosition: 'right',
        navigationTooltips: ['Home', 'Development','Networking', 'Cafe & Membership'],
        slidesNavigation: true,
        slidesNavPosition: 'top',
        css3: false,
        paddingTop: '3em',
        paddingBottom: '10px',
        keyboardScrolling: true,

    });
});
