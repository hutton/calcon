/**
 * Created by simonhutton on 03/09/2014.
 */

$(document).ready(function(){
    var ctx = $("#myChart").get(0).getContext("2d");

    var data = {
    labels: ['csv', 'xlsx', 'html', 'xml', 'pdf', 'json', 'txt', 'tsv'],
    datasets: [
        {
            label: "My First dataset",
            fillColor: "rgba(151,187,205,0.2)",
            strokeColor: "rgba(151,187,205,1)",
            pointColor: "rgba(151,187,205,1)",
            pointStrokeColor: "#fff",
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(151,187,205,1)",
            data: [65, 59, 80, 81, 56, 55, 40]
        }
    ]};

    var myLineChart = new Chart(ctx).Bar(data);
});
