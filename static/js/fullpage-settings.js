$(document).ready(function() {
    $("#header, #footer").animate({height:"8%"}, 2000, 'swing');
    $('#fullpage').fullpage({
        verticalCentered: false,
        sectionsColor : ['black', '#88abaf'],
        anchors:[],
        scrollingSpeed: 600,
        navigation: false,
        navigationPosition: 'right',
        navigationTooltips: ['Home', 'Networking'],
        slidesNavigation: true,
        slidesNavPosition: 'bottom',
        css3: false,
        paddingTop: '3em',
        paddingBottom: '10px',
        keyboardScrolling: true,

    });
});
