

// Some code used from http://codepen.io/idan/pen/xejuD, which uses the MIT license (see https://blog.codepen.io/legal/licensing/).

/*	The MIT License (MIT)
	
Copyright (c) Idan Gazit

Permission is hereby granted, free of charge, to any person 
obtaining a copy of this software and associated documentation 
files (the "Software"), to deal in the Software without restriction,
 including without limitation the rights to use, copy, modify, 
merge, publish, distribute, sublicense, and/or sell copies of 
the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall 
be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES 
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
DEALINGS IN THE SOFTWARE. */



// visualization parameters
var text_minutes = 20;
var axisOpacity = 0.6;
var large_tick_size = 24;
var rectHourSize = graphWidth / (7 * 8);
var daylabel_displacement = 12;
var half_a_week_in_min = 5040;

// slider variables
var sliderscale, startWeek, endWeek;
/* var leftWidth, rightWidth, leftBorder, rightBorder; */
var slidervalue_left, slidervalue_right;
var sliderborder_translate = 0.5;
var sliderborder_area_width = 8;
/* var slidercenter_pixels; */

// window
var margin = {
	top : 20,
	right : 10,
	bottom : 30,
	left : 35
};
var graphWidth = 700;
var graphHeight = 160;
var width = graphWidth + margin.left + margin.right;
var height = graphHeight + margin.top + margin.bottom;
var yaxisHeight = 100;

// kernel density plot
var bandwidth = 5;
var granularity = 1;
var kernelHeight = 30;

// visualization global variables
var daysLabelsAxis, daysTickmarksAxis, hoursAxis, hoursTickSpacing, hoursg, start, end, svg, weekscale, shownTicks, records;
var recordTypes = d3.map();
var readyForInput = false;
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
var parseDate = d3.time.format("%d-%m-%Y %H:%M").parse;

var results = Papa.parse("timeseries.csv", {
		header : true,
		download : true,
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
			drawGraphOutline();
			initializeScaler();
			updateWeekScale();
			prepareAxis();
			visualizeData();
			

			readyForInput = true;
		}
	});

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
	var daysNum = dayDiff(start, end);

	// kernel slider
	var slider_week_width = (7 / daysNum) * graphWidth;
	sliderscale = d3.time.scale().nice(d3.time.day).domain([start.toDate(), end.toDate()]).range([0, graphWidth]).clamp(true);
	records.forEach(function (d) {
		d.time_from_start = hoursFromStart(d.time)
	});

	slidervalue_left = sliderscale(moment(start));
	slidervalue_right = sliderscale(moment(start).add(7, 'days'));
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

function initializeScaler() {

	/* updateBorderWidth();
	moveBorders(); */

	var whiteSelectionData = [{
			x : slidervalue_left,
			width : slidervalue_right - slidervalue_left
		}
	]

	svg.selectAll("whiteSelection")
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

	var greyAreaData = [{
			x : 0,
			width : 0.01,
			side : "leftGrey",
			visibility : "visible"
		}, {
			x : slidervalue_right,
			width : graphWidth - slidervalue_right,
			side : "rightGrey",
			visibility : "visible"
		}
	]

	svg.selectAll("greyArea")
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

	
	var borderLineData = [{
			x : 0 + sliderborder_translate,
			side : "leftBorderLine"
		}, {
			x : slidervalue_right + sliderborder_translate,
			side : "rightBorderLine"
		}
	]

	svg.selectAll("borderLine")
	.data(borderLineData)
	.enter().append('line')
	.attr("x1", function (d) {
		return d.x;
	})
	.attr("x2", function (d) {
		return d.x;
	})
	.attr("y1", graphHeight - kernelHeight - 1)
	.attr("y2", graphHeight + 1)
	.attr("class", function (d) {
		return d.side;
	});

	var borderEllipseData = [{
			cx : 0 + sliderborder_translate,
			side : "leftBorderEllipse"
		}, {
			cx : slidervalue_right + sliderborder_translate,
			side : "rightBorderEllipse"
		}
	]

	svg.selectAll("ellipse")
	.data(borderEllipseData)
	.enter().append('ellipse')
	.attr("cx", function (d) {
		return d.cx;
	})
	.attr("cy", graphHeight - kernelHeight / 2)
	.attr("rx", 5)
	.attr("ry", 8)
	.attr("class", function (d) {
		return d.side;
	});

	var borderRectData = [{
			cx : 0 + sliderborder_translate,
			side : "leftBorderRect",
			width : 3,
			height : 5
		}, {
			cx : slidervalue_right + sliderborder_translate,
			side : "rightBorderRect",
			width : 3,
			height : 5
		}
	]

	svg.selectAll("borderRect")
	.data(borderRectData)
	.enter().append('rect')
	.attr("x", function (d) {
		return d.cx - d.width / 2;
	})
	.attr("y", function (d) {
		return graphHeight - kernelHeight / 2 - d.height / 2;
	})
	.attr("width", function (d) {
		return d.width;
	})
	.attr("height", function (d) {
		return d.height;
	})
	.attr("class", function (d) {
		return d.side;
	});

	var borderAreaData = [{
			x : slidervalue_left - sliderborder_area_width / 2,
			width : sliderborder_area_width,
			side : "leftBorderArea",
			visibility : "visible"
		}, {
			x : slidervalue_right - sliderborder_area_width / 2,
			width : sliderborder_area_width,
			side : "rightBorderArea",
			visibility : "visible"
		}
	]

	svg.selectAll("borderSelectArea")
	.data(borderAreaData)
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
	}).call(dragBorder);

}

function updateWeekScale() {

	startWeek = sliderscale.invert(slidervalue_left);
	endWeek   = sliderscale.invert(slidervalue_right);
	shownDays = dayDiff(startWeek, endWeek)
	weekscale = d3.time.scale().nice(d3.time.day).domain([startWeek, endWeek]).range([0, graphWidth]);

}

function prepareAxis() {

	function diffMinutesFromLeftSide(d) {
		var textMinutes = d.getMinutes();
		var startWeek

	}

	// Labels without tickmarks to describe the date
	daysLabelsAxis = d3.svg.axis().scale(weekscale).orient('bottom').ticks(d3.time.hour, 12).tickSize(0).tickPadding(daylabel_displacement).tickFormat(function (d) {
			var formatter;
			if (minuteDiff(startWeek, moment(d)) > 180 && minuteDiff(moment(d), endWeek) > 180) { // remove text crossing the edges
				if (d.getHours() === 12) {
					if ((d.getDate() === 1 || moment(d).isSame(start, 'day')) && shownDays < 16) {
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
	var hourTicks = hoursg.selectAll('g.tick');
	
	//hourTicks.filter(':not(:last-child)').insert('rect', ':first-child').attr('class', function (d, i) {
	//hourTicks.insert('rect', ':not(:last-child)').attr('class', function (d, i) {
	hourTicks.insert('rect', ':first-child').attr('class', function (d, i) {
			var hours;
			hours = d.getHours();
			if (hours < 6 || hours >= 18) {
				return 'nighttime';
			} else {
				return 'daytime';
			}
		}).attr('x', 0).attr('width', hoursTickSpacing).attr('height', 8);

	/* function (d, i) {
	return i != daysNum * 8 ? 8 : 0; // remove last tick in week..
	}); */

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
		length = d.type == "inc_text" || d.type == "out_text" ? text_minutes : d.call_duration/60;
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
	// clip sides
	.style("opacity", function (d) {
		return (weekscale(d.time) < 0 || weekscale(d.time) > graphWidth) ? 0.0 : 1.0;
	});

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
	.attr("x1", graphWidth + 0.5)
	.attr("x2", graphWidth + 0.5)
	.attr("y1", 0)
	.attr("y2", graphHeight + 1)
	.attr("stroke-width", 1)
	.attr("stroke", "black");
}

function updateVisualization() {

	if (readyForInput) {

		cleanAxisWindow();
		updateWeekScale();
		prepareAxis();
		visualizeData();
	}
}

function cleanAxisWindow() {
	svg.selectAll(".axis").remove()
	svg.selectAll("text").remove()
	svg.selectAll(".bar").remove()
	svg.selectAll(".handle").remove()
}

function updateBorder(x, whichBorder) {

	svg.selectAll(whichBorder.concat("Area"))
	.each(function (d) {
		d.x = x - sliderborder_area_width / 2
	})
	.attr("x", x - sliderborder_area_width / 2);

	// translate visuals slightly to fit graph
	x = x + sliderborder_translate

		svg.selectAll(whichBorder.concat("Line"))
		.attr("x1", x)
		.attr("x2", x);

	svg.selectAll(whichBorder.concat("Ellipse"))
	.attr("cx", x);

	svg.selectAll(whichBorder.concat("Rect"))
	.attr("x", function (d) {
		return x - d.width / 2
	});
}

function updateGreyArea(x, width, whichGrey) {

	width = Math.max(width, 0.01);

	svg.selectAll(whichGrey)
	.attr("x", x)
	.attr("width", width)
	.each(function (d) {
		d.x = x
	})
	.each(function (d) {
		d.width = width
	});

}

// Function for grabbing a specific property from an array
pluck = function (ary, prop) {
	return ary.map(function (x) {
		return x[prop]
	});
}

function checkBordersMoreThanWeekApart(d, slider_drag) {

	if (d.side == "leftBorderArea") {
		temp_left = d.x + slider_drag + sliderborder_area_width / 2;
		temp_right = slidervalue_right;
	} else {
		temp_left = slidervalue_left;
		temp_right = d.x + slider_drag + sliderborder_area_width / 2;
	}

	left_date = sliderscale.invert(temp_left);
	right_date = sliderscale.invert(temp_right);

	num_days = dayDiff(left_date, right_date);
	
	return (num_days >= 4 && num_days <= 18);

}

var dragBorder = d3.behavior.drag()
	.on('drag', function (d) {

		slider_drag = d3.event.dx;

		/* Hitting edges of graph? */
		if (d.x + sliderborder_area_width / 2 + slider_drag < 0) {
			d.x = -sliderborder_area_width / 2;
		} else if (d.x + sliderborder_area_width / 2 + slider_drag > graphWidth) {
			d.x = graphWidth - sliderborder_area_width / 2;
		} else {
			/* Borders too close to each other? */
			if (checkBordersMoreThanWeekApart(d, slider_drag))
				d.x += slider_drag;
		}

		if (d.side == "leftBorderArea") {
			slidervalue_left = d.x + sliderborder_area_width / 2;
		} else {
			slidervalue_right = d.x + sliderborder_area_width / 2;
		}

		updateScalerObjects();
		updateVisualization();

	});

var dragSelection = d3.behavior.drag()
	.on('drag', function (d) {

		slider_drag = d3.event.dx;

		/* Hitting edges of graph? */
		if (d.x + slider_drag < 0) {
			d.x = 0;
		} else if (d.x + d.width + slider_drag > graphWidth) {
			d.x = graphWidth - d.width;
		} else {
			d.x += slider_drag;
		}

		slidervalue_left = d.x;
		slidervalue_right = d.x + d.width;

		updateScalerObjects();
		updateVisualization();

	});

function updateScalerObjects() {

	svg.selectAll(".whiteSelectionArea")
	.attr("width", slidervalue_right - slidervalue_left)
	.attr("x", slidervalue_left)
	.each(function (d) {
		d.x = slidervalue_left
	})
	.each(function (d) {
		d.width = slidervalue_right - slidervalue_left
	});

	updateGreyArea(0, slidervalue_left, ".leftGrey");
	updateBorder(slidervalue_left, ".leftBorder");

	updateGreyArea(slidervalue_right, graphWidth - slidervalue_right, ".rightGrey");
	updateBorder(slidervalue_right, ".rightBorder");

}

function inputData(d) {
	d.time = parseDate(d.time);
	return d;
}

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
