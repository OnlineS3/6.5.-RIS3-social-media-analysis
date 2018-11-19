function init_word_count(words_dict){
var fill = d3.scale.category20();
var color = d3.scale.ordinal().range(["#66c2a5","#fc8d62","#8da0cb","#e78ac3","#a6d854"]);
var my_dim = document.getElementById("word-cloud-header").clientWidth;
var layout = d3.layout.cloud()
    .size([my_dim, my_dim])
    .words(words_dict
    )
    .padding(5)
    .rotate(function() { return 0; })
    .font("Impact")
    .fontSize(function(d) { return d.size; })
    .on("end", draw);

    layout.start();

    function draw(words) {
      d3.select("div.wordCloud").append("svg")
          .attr("width", layout.size()[0])
          .attr("height", layout.size()[1])
        .append("g")
          .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
        .selectAll("text")
          .data(words)
        .enter().append("text")
          .style("font-size", function(d) { return d.size + "px"; })
          .style("font-family", "Impact")
          .style("fill", function(d) { return color(Math.random() * (color.length)); })
          .attr("text-anchor", "middle")
          .attr("transform", function(d) {
            return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
          })
          .text(function(d) { return d.text; });
    }
}


