/**
 * Created by simonhutton on 03/09/2014.
 */

window.StatsView = Backbone.View.extend({
    initialize: function () {
        this.render();
    },

    template: _.template($('#stats-view-template').html()),

    render: function(){
        this.$el.html(this.template(this.model));

        this.chartEl = this.$el.find('.download-type-chart');

        var ctx = this.chartEl.get(0).getContext("2d");

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
                data: this.model.fileTypeFrequencies
            }
        ]};

        new Chart(ctx).Bar(data);

        return this;
    },

    className: 'stat-section'
});


window.App = Backbone.View.extend({
    initialize: function (){

        this.fetchData();
    },

    el: $("body"),

    statsListEl: $("#stat-sections-container"),

    fetchData: function(){
        var that = this;

        $.get( "statistics-data", function( data ) {

            var response = jQuery.parseJSON(data);

            that.statsListEl.empty();

            _.each(response, function(statDataItem){
                var view = new StatsView({model: statDataItem});

                that.statsListEl.append(view.el);
            });
        });
    }
});

$(document).ready(function(){
    window.App = new App();
});
