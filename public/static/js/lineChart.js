function init_likes_line_chart(data){

var chart = Morris.Line({
    element: 'likesLineChart',
    xkey: 'y',
    ykeys: ['a'],
    labels: ['Likes','dislikes'],
    pointFillColors: ['#e74c3c']
});

chart.setData(data);
}

function init_retweets_line_chart(data){

var chart = Morris.Line({
    element: 'retweetLineChart',
    xkey: 'y',
    ykeys: ['a'],
    labels: ['Retweets'],
    pointFillColors: ['#e74c3c'],
});

chart.setData(data);
}

function init_compare_likes_line_chart(data, array){

var chart = Morris.Line({
    element: 'compareLikesLineChart',
    xkey: 'y',
    ykeys: ['a','b'],
    labels: array,
    lineColors: ['#1496BB', '#AD2A1A']
});

chart.setData(data);
}

function init_compare_retweets_line_chart(data, array){

var chart = Morris.Line({
    element: 'compareRetweetLineChart',
    xkey: 'y',
    ykeys: ['a','b'],
    labels: array,

    lineColors: ['#1496BB', '#AD2A1A']
});

chart.setData(data);
}

