function init_donut_chart(data, func) {

    var chart = Morris.Donut({
        element: 'donut',
        colors: ['#2980b9','#e74c3c'],
        data: data,
        resize: true,
        formatter: func
    });
    chart.setData(data);
}