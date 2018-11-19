function init_bar_chart(data){
    var chart = Morris.Bar({
        element: 'bar',
        xkey: 'y',
        ykeys: ['a'],
        labels: ['Tweets'],
        resize: true,
        barColors: ['#e74c3c'],
        gridTextSize: 11
    });

    chart.setData(data);
}

function init_compare_bar_chart(data, array){
    var chart = Morris.Bar({
        element: 'bar',
        xkey: 'y',
        ykeys: ['a','b'],
        labels: array,
        resize: true,
        barColors: ['#e74c3c', '#1496BB'],
        gridTextSize: 11
    });

    chart.setData(data);
}
