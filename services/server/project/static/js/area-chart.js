function chart(data) {

	var keys = Object.keys(data[0]).slice(1);
	var parseTime = d3.timeParse("%Y-%m-%d"),
		formatDate = d3.timeFormat("%Y-%m-%d"),
		bisectDate = d3.bisector(d => d.date).left,
		formatValue = d3.format(",.0f");

	data.forEach(function(d) {
		d.date = parseTime(d.date);
		return d;
	})
	var svg = d3.select("#chart"),
        margin = {top: 15, right: 35, bottom: 15, left: 50},
		width = parseInt(d3.select('body').style('width'), 10)  - margin.left - margin.right,
		height = parseInt(d3.select('body').style('height'), 10) - margin.top - margin.bottom;
    if(width > 1000){
        var width = 850
    }
    else{
        var width = width - 50
    }
	var x = d3.scaleTime()
		.rangeRound([margin.left, width - margin.right])
		.domain(d3.extent(data, d => d.date))

	var y = d3.scaleLinear()
		.rangeRound([height - margin.bottom, margin.top]);

	var z = d3.scaleOrdinal(d3.schemeCategory10);

	var line = d3.line()
		.curve(d3.curveCardinal)
		.x(d => x(d.date))
		.y(d => y(d.degrees));

	svg.append("g")
		.attr("class","x-axis")
		.attr("transform", "translate(0," + (height - margin.bottom) + ")")
		.call(d3.axisBottom(x).tickFormat(d3.timeFormat("%b")));

	svg.append("g")
		.attr("class", "y-axis")
		.attr("transform", "translate(" + margin.left + ",0)");

	var focus = svg.append("g")
		.attr("class", "focus")
		.style("display", "none");

	focus.append("line").attr("class", "lineHover")
		.style("stroke", "#999")
		.attr("stroke-width", 1)
		.style("shape-rendering", "crispEdges")
		.style("opacity", 0.5)
		.attr("y1", -height)
		.attr("y2",0);

	focus.append("text").attr("class", "lineHoverDate")
		.attr("text-anchor", "middle")
		.attr("font-size", 12);

	var overlay = svg.append("rect")
		.attr("class", "overlay")
		.attr("x", margin.left)
		.attr("width", width - margin.right - margin.left)
		.attr("height", height)

	update(d3.select('#selectbox').property('value'), 0);

	function update(input, speed) {

		var copy = keys.filter(f => f.includes(input))

		var cities = copy.map(function(id) {
			return {
				id: id,
				values: data.map(d => {return {date: d.date, degrees: +d[id]}})
			};
		});

		y.domain([
			d3.min(cities, d => d3.min(d.values, c => c.degrees)),
			d3.max(cities, d => d3.max(d.values, c => c.degrees))
		]).nice();

		svg.selectAll(".y-axis").transition()
			.duration(speed)
			.call(d3.axisLeft(y).tickSize(-width + margin.right + margin.left))

		var city = svg.selectAll(".cities")
			.data(cities);

		city.exit().remove();

		city.enter().insert("g", ".focus").append("path")
			.attr("class", "line cities")
			.style("stroke", d => z(d.id))
			.merge(city)
		.transition().duration(speed)
			.attr("d", d => line(d.values))

		tooltip(copy);
	}

	function tooltip(copy) {

		var labels = focus.selectAll(".lineHoverText")
			.data(copy)

		labels.enter().append("text")
			.attr("class", "lineHoverText")
			.style("fill", d => z(d))
			.attr("text-anchor", "start")
			.attr("font-size",12)
			.attr("dy", (_, i) => 1 + i * 2 + "em")
			.merge(labels);

		var circles = focus.selectAll(".hoverCircle")
			.data(copy)

		circles.enter().append("circle")
			.attr("class", "hoverCircle")
			.style("fill", d => z(d))
			.attr("r", 2.5)
			.merge(circles);

		svg.selectAll(".overlay")
			.on("mouseover", function() { focus.style("display", null); })
			.on("mouseout", function() { focus.style("display", "none"); })
			.on("mousemove", mousemove);

		function mousemove() {

			var x0 = x.invert(d3.mouse(this)[0]),
				i = bisectDate(data, x0, 1),
				d0 = data[i - 1],
				d1 = data[i],
				d = x0 - d0.date > d1.date - x0 ? d1 : d0;

			focus.select(".lineHover")
				.attr("transform", "translate(" + x(d.date) + "," + height + ")");

			focus.select(".lineHoverDate")
				.attr("transform",
					"translate(" + x(d.date) + "," + (height + margin.bottom) + ")")
				.text(formatDate(d.date));

			focus.selectAll(".hoverCircle")
				.attr("cy", e => y(d[e]))
				.attr("cx", x(d.date));

			focus.selectAll(".lineHoverText")
				.attr("transform",
					"translate(" + (x(d.date)) + "," + height / 2.5 + ")")
				.text(e => e + " " + "º" + formatValue(d[e]));

			x(d.date) > (width - width / 4)
				? focus.selectAll("text.lineHoverText")
					.attr("text-anchor", "end")
					.attr("dx", -10)
				: focus.selectAll("text.lineHoverText")
					.attr("text-anchor", "start")
					.attr("dx", 10)
		}
	}

	var selectbox = d3.select("#selectbox")
		.on("change", function() {
			update(this.value, 750);
		})
}