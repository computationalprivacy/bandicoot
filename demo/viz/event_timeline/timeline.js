/***************************************************************
 CREATED FOR USE WITH DRAGGABLE BORDERS - THIS IS NOT ACTIVATED.
***************************************************************/


var daysLabelsAxis, daysTickmarksAxis, end, height, hoursAxis, hoursTickSpacing, hoursg, start, svg, weekscale, width, daysNum;
var recordTypes = d3.map();
var periodscale, sliderscale, startValue, startWeek, endWeek;
var readyForInput = false;
var leftWidth, rightWidth;

var margin = {
	top : 20,
	right : 0,
	bottom : 30,
	left : 35
};

var graphWidth = 700; // 700
var graphHeight = 160; // 153.5; // 160
width = graphWidth + margin.left + margin.right;
height = graphHeight + margin.top + margin.bottom;

var bandwidth = 4;
var granularity = 1;
var kernelHeight = 30;

yaxisHeight = 100;
var text_minutes = 20;
var axisOpacity = 0.6;
var large_tick_size = 24;
var rectHourSize = graphWidth / (7 * 8);
var slidervalue = -1;
var slidercenter_pixels;
var slider_week_width;
var daylabel_displacement = 12;
var half_a_week_in_min = 5040;

function dayDiff(date_start, date_end) {
	var dr = moment.range(date_start, date_end);
	return dr.diff('days');
}

function hourDiff(date_start, date_end) {
	var dr = moment.range(date_start, date_end);
	return dr.diff('hours');
}

function minuteDiff(date_start, date_end) {
	var dr = moment.range(date_start, date_end);
	return dr.diff('minutes');
}

function hoursFromStart(moment) {

	return hourDiff(start, moment);
}

function minFromStart(moment) {
	
	return minuteDiff(start, moment);
}


function prepareAxis() {
	function diffMinutesFromLeftSide(d) {
		var textMinutes = d.getMinutes();
		var startWeek

	}

	// Labels without tickmarks to describe the date
	daysLabelsAxis = d3.svg.axis().scale(weekscale).orient('bottom').ticks(d3.time.hour, 12).tickSize(0).tickPadding(daylabel_displacement).tickFormat(function (d) {
			var formatter;
			if (d.getHours() === 12 && minuteDiff(startWeek, moment(d)) > 180) {
				if (d.getDate() === 1 || moment(d).isSame(start, 'day')) {
					// if the month changed or it's the first label, show the month
					formatter = d3.time.format.utc('%a %d %b');
				} else {
					// else no month
					formatter = d3.time.format.utc('%a %d');
				}
				return formatter(d);
			} else {
				return null;
			}
		});

	// small tickmarks every three hours, but only label 6a and 6p
	hoursAxis = d3.svg.axis().scale(weekscale).orient('bottom').ticks(d3.time.hour, 3).tickPadding(6).tickSize(8).tickFormat(function (d) {
			var hours;
			hours = d.getHours();
			if (hours === 6) {
				return null;
				/* 	return sun; */
			} else if (hours === 18) {
				return null;
				/* return moon; */
			} else {
				return null;
			}
		});

	// draw axis below data
	hoursg = svg.append('g').classed('axis', true).classed('hours', true).classed('labeled', true).attr("transform", "translate(0.5," + yaxisHeight + ")").call(hoursAxis).style("opacity", axisOpacity);

	// Need the pixel dimensions between each tick e.g. three hours.
	hoursTickSpacing = weekscale(moment(start).add(3, 'hours').toDate()) - weekscale(start.toDate());

	// add day/night shading by adding elements to the dom for every tickmark in the hours axis.
	hourTicks = hoursg.selectAll('g.tick').insert('rect', ':first-child').attr('class', function (d, i) {
			var hours;
			hours = d.getHours();
			if (hours < 6 || hours >= 18) {
				return 'nighttime';
			} else {
				return 'daytime';
			}
		}).attr('x', 0).attr('width', hoursTickSpacing).attr('height', function (d, i) {
			return i != 7 * 8 ? 8 : 0; // remove last tick in week.. old: i != daysNum * 8 ? 8 : 0
		});

	// Larger tickmarks to denote midnights without labels
	daysTickmarksAxis = d3.svg.axis().scale(weekscale).orient('bottom').ticks(d3.time.day, 1).tickFormat('').tickSize(large_tick_size).tickPadding(6);

	// draw axes below data
	svg.append('g').classed('axis', true).classed('days', true).attr("transform", "translate(0.5," + (yaxisHeight) + ")").call(daysTickmarksAxis);
	svg.append('g').classed('axis', true).classed('days', true).classed('labeled', true).attr("transform", "translate(0.5," + (yaxisHeight) + ")").call(daysLabelsAxis).style("opacity", axisOpacity);

	// draw y-axis
	svg.append("g")
	.attr("class", "y axis")
	.attr("transform", "translate(0.5,0.0)")
	.style("opacity", axisOpacity)
	.call(yAxis);

	svg.selectAll("y_axis_vertical")
	.data(['call', 'text'])
	.enter().append("text")
	.attr("y", function (d, i) {
		return 4 + i * 45;
	}) // function(d,i) { return i+"em"})
	.attr("x", "-32")
	.style("writing-mode", "tb")
	.style("glyph-orientation-vertical", 0)
	.style("letter-spacing", -1)
	.style("opacity", axisOpacity)
	.style("font-family", "FontAwesome")
	.text(function (d, i) {
		return d;
	});
}

var parseDate = d3.time.format("%d-%m-%Y %H:%M").parse;

function cleanAxisWindow() {
	svg.selectAll(".axis").remove()
	svg.selectAll("text").remove()
	svg.selectAll(".bar").remove()
	svg.selectAll(".handle").remove()
	//svg.selectAll(".greyedArea").remove()
	//svg.selectAll(".kde").remove()
	//svg.selectAll(".greyedAreaBorders").remove()
	//svg.selectAll(".whiteSelectionArea").remove()
	//svg.selectAll(".slider").remove()

}

function initializeStaticWindow() {

	svg = d3.select("body").append("svg")
		.attr("id", "svgID")
		.attr("width", width)
		.attr("height", height)
		.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	// set types of records for y-axis
	recordTypes.set("inc_call", {
		label : "in",
		color : "#438DCA",
		order : 1
	});
	recordTypes.set("out_call", {
		label : "out",
		color : "#245A76",
		order : 2
	});
	recordTypes.set("inc_text", {
		label : "in",
		color : "#70C05A",
		order : 3
	});
	recordTypes.set("out_text", {
		label : "out",
		color : "#326B26",
		order : 4
	});

	records = records.sort(function (a, b) {
			return recordTypes.get(b.type).order - recordTypes.get(a.type).order;
		});

	y.domain(records.map(function (d) {
			return d.type;
		}));

}

function defineScales() {

	records.forEach(function (d, i) {
		if (i == 0) {
			start = d.time;
			end = d.time;
		} else {
			start = moment.min(start, d.time);
			end = moment.max(end, d.time);
		}
	});

	start = moment(start).startOf('day');
	end = moment(end).startOf('day').add(1, 'days');

	// Turn into pure dates
	daysNum = dayDiff(start, end);

	// kernel slider
	slider_week_width = (7 / daysNum) * graphWidth;
	sliderscale = d3.time.scale().nice(d3.time.day).domain([start.toDate(), end.toDate()]).range([0, graphWidth]).clamp(true);
	records.forEach(function (d) {
		d.time_from_start = hoursFromStart(d.time)
	});

	slidervalue = moment(start).add(half_a_week_in_min, 'minutes');
	
	leftBorder  = 0;
	rightBorder = slider_week_width;
	slidercenter_pixels = slider_week_width/2;
}

function updateWeekScale() {

	startWeek = sliderscale.invert(leftBorder);
	endWeek   = sliderscale.invert(rightBorder);
	weekscale = d3.time.scale().nice(d3.time.day).domain([startWeek, endWeek]).range([0, graphWidth]);

}

function initializeScaler() {

	updateBorderWidth();
	moveBorders();

	
 
	var whiteSelectionData = [{
			x : 0,
			width : 1
		}
	]

	svg.selectAll("rect")
	.data(whiteSelectionData)
	.enter().append('rect')
	.attr("x", function (d) {
		return d.x;
	})
	.attr("y", graphHeight - kernelHeight - 1)
	.attr("width", function (d) {
		return d.width;
	})
	.attr("height", kernelHeight + 2)
	.attr("class", "whiteSelectionArea")
	.call(dragSelection);
	
	
	var greyAreaData = [
	{x : 0, width: 10, side: "bugfix", visibility: "hidden"}, {x : 0, width: 10, side: "leftGrey", visibility: "visible"}, {x : rightBorder, width: 10, side: "rightGrey", visibility: "visible"}
	]
	
	svg.selectAll("rect")
	.data(greyAreaData)
	.enter().append('rect')
	.attr("x", function (d) {
		return d.x;
	})
	.attr("y", graphHeight - kernelHeight - 1)
	.attr("width", function (d) {
		return d.width;
	})
	.attr("visibility", function (d) {
		return d.visibility;
	})
	.attr("height", kernelHeight + 2)
	.attr("class", function (d) {
		return d.side;
	});
	
	var borderData = [
	{x : 0, side: "leftBorder"}, {x : rightBorder, side: "rightBorder"}
	]

	svg.selectAll("line")
	.data(borderData)
	.enter().append('line')
	.attr("x1", function (d) {
		return d.x - 2;
	})
	.attr("x2", function (d) {
		return d.x - 2;
	})
	.attr("y1", graphHeight - kernelHeight - 1)
	.attr("y2", graphHeight + 1)
	.attr("class", function (d) {
		return d.side;
	});
	//.call(dragBorder);
	
}


function updateBorder(x, whichBorder) {

	svg.selectAll(whichBorder)
	.attr("x1", x)
	.attr("x2", x)
	/* .attr("x1", x - 1)
	.attr("x2", x - 1) */;

}

function updateGreyArea(x, width, whichGrey) {

	width = Math.max(width, 1)

	svg.selectAll(whichGrey)
	.attr("x", x)
	.attr("width", width);

}

function updateBorderWidth() {
	
	
	leftWidth  = slidercenter_pixels - leftBorder;
	rightWidth = rightBorder - slidercenter_pixels;
}

function moveBorders() {

	
	
	slidercenter_pixels = sliderscale(slidervalue);
	leftBorder  =  slidercenter_pixels - leftWidth;
	rightBorder = slidercenter_pixels + rightWidth;
	
}

function drawScaler() {

	
	svg.selectAll(".whiteSelectionArea")
	.attr("width", rightBorder - leftBorder)
	.attr("x", leftBorder);

	// clamp borders
	if (leftBorder > 1.5) {		
		updateBorder(leftBorder, ".leftBorder");
		updateGreyArea(0, leftBorder-1.5, ".leftGrey");
	}
	else {	
		updateBorder(1.5, ".leftBorder");
		updateGreyArea(0, 0, ".leftGrey");
	}
	
	if (rightBorder < graphWidth - 1.5) {		
		updateBorder(rightBorder, ".rightBorder");
		updateGreyArea(rightBorder, graphWidth-rightBorder, ".rightGrey");
	}
	else {	
		updateBorder(graphWidth, ".rightBorder");
		updateGreyArea(graphWidth, 0, ".rightGrey");
	}
	
	
	
}

function drawKernelDensity() {

	// extract only timestamps
	timestamps = pluck(records, 'time_from_start');

	// create kernel
	kde = science.stats.kde().sample(timestamps);
	var kernel_output = kde.bandwidth(bandwidth)(d3.range(0, hoursFromStart(end), granularity));
	kernel_output = pluck(kernel_output, 1)
		var kernel_max = ss.quantile(kernel_output, 0.975);

	// scales to transform data
	kernel_scale_x = d3.scale.linear().domain([0, hoursFromStart(end)]).range([0, graphWidth]);
	kernel_scale_y = d3.scale.linear().domain([0, kernel_max]).range([0, kernelHeight]).clamp(true);

	var line = d3.svg.line()
		.x(function (d) {
			return kernel_scale_x(d[0]);

		})
		.y(function (d) {
			return graphHeight - kernel_scale_y(d[1]);
		});

	svg.selectAll("kde")
	.data([bandwidth])
	.enter().append("path")
	.attr("d", line(kde.bandwidth(bandwidth)(d3.range(0, hoursFromStart(end), granularity))))
	.attr("stroke", "#438DCA");

}

function drawGraphOutline() {
	svg.append("line")
	.attr("x1", 0.5)
	.attr("x2", 0.5)
	.attr("y1", 0)
	.attr("y2", graphHeight + 1)
	.attr("stroke-width", 1)
	.attr("stroke", "black");

	svg.append("line")
	.attr("x1", graphWidth - 0.5)
	.attr("x2", graphWidth - 0.5)
	.attr("y1", 0)
	.attr("y2", graphHeight + 1)
	.attr("stroke-width", 1)
	.attr("stroke", "black");
}

// Function for grabbing a specific property from an array
pluck = function (ary, prop) {
	return ary.map(function (x) {
		return x[prop]
	});
}

function moveSpecificBorder(d) {

	current_x = parseFloat(svg.selectAll(".".concat(d.side)).attr("x1"));
	current_x += d3.event.dx;
	
	//current_x = d3.mouse(this)[0];
		
		
	if (d.side == "leftBorder")
	{
		leftBorder = current_x;
	}
	else {
		rightBorder = current_x;
	}
	
}

var dragBorder = d3.behavior.drag()
.on('drag', function (d) {
		
		moveSpecificBorder(d);
		
		
		
		updateVisualization();

	});

var dragSelection = d3.behavior.drag()
	.on('drag', function (d) {
	
		//d.x = leftBorder;
		d.x += d3.event.dx;
		
		if (d.x < 0) {
			d.x = 0;
		}
		//d.y += d3.event.dy;
		
		slidervalue = sliderscale.invert(d.x);
		

		
		leftWidthDate = sliderscale.invert(leftWidth);
		leftWidthMin  = minFromStart(leftWidthDate);
		
		rightWidthDate = sliderscale.invert(rightWidth);
		rightWidthMin  = minFromStart(rightWidthDate);
		
		slidervalue = moment(slidervalue).add(leftWidthMin, 'minutes');
		
		// clamp
		if (minuteDiff(start, slidervalue) < leftWidthMin && d3.event.dx < 0) {
			slidervalue = moment(start).add(leftWidthMin, 'minutes');
			d.x = 0;
		}
		else if (minuteDiff(slidervalue, end) < rightWidthMin && d3.event.dx > 0) {
			slidervalue = moment(end).subtract(rightWidthMin, 'minutes');
			d.x = leftBorder;
		}
		
		updateBorderWidth();
		moveBorders();

		
		d3.select(this)
		.attr('x', d.x);
		
		updateVisualization();

	});

function updateVisualization() {
	
			if (readyForInput) {

			cleanAxisWindow();
			updateWeekScale();
			prepareAxis();
			visualizeData();
			//drawKernelDensity();
			drawScaler();
			//drawGraphOutline();
		}
}
	
function inputData(d) {
	d.time = parseDate(d.time);
	return d;
}

var y = d3.scale.ordinal()
	.rangeRoundBands([yaxisHeight, 0], 0.3);

var yAxis = d3.svg.axis()
	.scale(y)
	.orient("left")
	.outerTickSize(0)
	.tickFormat(function (d, i) {
		return recordTypes.get(d).label;
	});

var colorOf = d3.scale.category10();

var records;

var results = Papa.parse("timeseries.csv", {
		header : true,
		download : true, // is needed even for local files as this interprets the input value as a path instead of simply the data
		dynamicTyping : true,
		delimiter : ",",
		skipEmptyLines : true,
		complete : function (results) {
			records = results.data;
			records.forEach(function (d) {
				d.time = parseDate(d.time);
				d.time = moment(d.time);
			});

			
			
			initializeStaticWindow();
			
			defineScales();
			drawKernelDensity();
			initializeScaler();
			updateWeekScale();
			prepareAxis();
			visualizeData();
			drawGraphOutline();
			drawScaler();
			
			readyForInput = true;
		}
	});

function visualizeData() {

	svg.selectAll(".bar")
	.data(records)
	.enter().append("rect")
	.attr("class", "bar")
	.attr("y", function (d) {
		return y(d.type);
	})
	.attr("height", y.rangeBand())
	.attr("x", function (d) {
		return weekscale(d.time);
	})
	.attr("width", function (d) {
		// set texts to a fixed length (and make calls minimum length)
		length = d.type == "inc_text" || d.type == "out_text" ? text_minutes : d.call_duration / 60;
		if (length < text_minutes) {
			length = text_minutes;
		}

		// find length of call on time scale by finding length between start and start + call_duration
		var rect_width = weekscale(moment(start).add(length, 'minutes').toDate()) - weekscale(start.toDate());
		return rect_width;
	})
	.style("fill", function (d) {
		return recordTypes.get(d.type).color;
	})
	// clip left side
	.style("opacity", function (d) {
		return weekscale(d.time) < 0 ? 0.0 : 1.0;
	});

}
