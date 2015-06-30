
var line_diff = 0.5; // increase from zero if you want space between the call/text lines
var mark_offset = 10; // how many percent of the mark lines in each end are not used for the relationship between incoming/outgoing?
var mark_size = 7; // size of the mark on the line
var line_width_factor = 10.0 // width for the widest line

var text_links_data, call_links_data;


// Function for grabbing a specific property from an array
pluck = function (ary, prop) {
	return ary.map(function (x) {
		return x[prop]
	});
}

// Sums an array
sum = function (ary) {
	return ary.reduce(function (a, b) {
		return a + b
	}, 0);
}

maxArray = function (ary) {
	return ary.reduce(function (a, b) {
		return Math.max(a, b)
	}, -Infinity);
}

minArray = function (ary) {
	return ary.reduce(function (a, b) {
		return Math.min(a, b)
	}, Infinity);
}

var data_links;

var data_nodes;

var results = Papa.parse("links.csv", {
		header : true,
		download : true,
		dynamicTyping : true,
		delimiter : ",",
		skipEmptyLines : true,
		complete : function (results) {
			data_links = results.data;

			for (i = 0; i < data_links.length; i++) {
				total_interactions += data_links[i].source_calls
				 + data_links[i].target_calls
				 + data_links[i].source_texts
				 + data_links[i].target_texts;
				max_interactions = Math.max(max_interactions,
						data_links[i].source_calls
						 + data_links[i].target_calls
						 + data_links[i].source_texts
						 + data_links[i].target_texts)
			}

			linkedByIndex = {};

			data_links.forEach(function (d) {
				linkedByIndex[d.source + "," + d.target] = true;
			});

			dataLoaded();
		}
	});

var results = Papa.parse("nodes.csv", {
		header : true,
		download : true,
		dynamicTyping : true,
		delimiter : ",",
		skipEmptyLines : true,
		complete : function (results) {
			data_nodes = results.data;
			data_nodes.forEach(function (d, i) {
				d.radius = (i == 0) ? 20 : 10
				//d.size = (i == 0) ? 1200 : 30
				d.fill = (d.no_network_info == 1) ? "#dfdfdf" : "#a8a8a8"
			});
			dataLoaded();
		}
	});


function dataLoaded() {
	if (typeof data_nodes === "undefined" || typeof data_links === "undefined") {
		console.log("Still loading " + (typeof data_nodes === "undefined" ? 'data_links' : 'data_nodes'))
	} else {
		CreateVisualizationFromData();
		force.start()
	}
}
	
function isConnectedToOtherThanMain(a) {
	var connected = false;
	for (i = 1; i < data_nodes.length; i++) {
		if (isConnected(a, data_nodes[i]) && a.index != i) {
			connected = true;
		}
	}
	return connected;
}

function isConnected(a, b) {
	return isConnectedAsTarget(a, b) || isConnectedAsSource(a, b) || a.index == b.index;
}

function isConnectedAsSource(a, b) {
	return linkedByIndex[a.index + "," + b.index];
}

function isConnectedAsTarget(a, b) {
	return linkedByIndex[b.index + "," + a.index];
}

function isEqual(a, b) {
	return a.index == b.index;
}


function tick(e) {

	if (call_links_data.length > 0) {

		callLink
		.each(function (d) {
			d.shift_perpendicular = line_perpendicular_shift(d, 1);
			d.shift_edge = []; // outer array 
			d.shift_edge.push(line_radius_shift_to_edge(d, 0));
			d.shift_edge.push(line_radius_shift_to_edge(d, 1));
			d.x1 = d.source.x - d.shift_perpendicular[0] + d.shift_edge[0][0];
			d.y1 = d.source.y - d.shift_perpendicular[1] + d.shift_edge[0][1];
			d.x2 = d.target.x - d.shift_perpendicular[0] + d.shift_edge[1][0];
			d.y2 = d.target.y - d.shift_perpendicular[1] + d.shift_edge[1][1];
		})
		.attr("x1", function (d) {
			return d.x1
		})
		.attr("y1", function (d) {
			return d.y1;
		})
		.attr("x2", function (d) {
			return d.x2;
		})
		.attr("y2", function (d) {
			return d.y2;
		});
		callLink.each(function (d, i) {
			applyGradient(this, "call", d, i)
		});

	}

	if (text_links_data.length > 0) {

		textLink
		.each(function (d) {
			d.shift_perpendicular = line_perpendicular_shift(d, -1);
			d.shift_edge = [];
			d.shift_edge.push(line_radius_shift_to_edge(d, 0));
			d.shift_edge.push(line_radius_shift_to_edge(d, 1));
			d.x1 = d.source.x - d.shift_perpendicular[0] + d.shift_edge[0][0];
			d.y1 = d.source.y - d.shift_perpendicular[1] + d.shift_edge[0][1];
			d.x2 = d.target.x - d.shift_perpendicular[0] + d.shift_edge[1][0];
			d.y2 = d.target.y - d.shift_perpendicular[1] + d.shift_edge[1][1];
		})
		.attr("x1", function (d) {
			return d.x1
		})
		.attr("y1", function (d) {
			return d.y1;
		})
		.attr("x2", function (d) {
			return d.x2;
		})
		.attr("y2", function (d) {
			return d.y2;
		});
		textLink.each(function (d, i) {
			applyGradient(this, "text", d, i)
		});

		node
		.attr("transform", function (d) {
			return "translate(" + d.x + "," + d.y + ")";
		});

	}
}

function applyGradient(line, interaction_type, d, i) {

	var self = d3.select(line);

	var current_gradient = self.style("stroke");

	if (current_gradient.match("http")) {
		var parts = current_gradient.split("/");
		current_gradient = parts[-1];
	} else {
		current_gradient = current_gradient.substring(4, current_gradient.length - 1);
	}

	var new_gradient_id = "lg" + interaction_type + d.source.index + '_' + d.target.index; // + getRandomInt();


	var mid_offset = 0;
	var standardColor = "";

	if (interaction_type == "call") {
		mid_offset = d.source_calls / (d.source_calls + d.target_calls);
		standardColor = "#438DCA";
	} else {
		mid_offset = d.source_texts / (d.source_texts + d.target_texts);
		standardColor = "#70C05A";
	}

	lineLengthCalculation = function (x, y, x0, y0) {
		return Math.sqrt((x -= x0) * x + (y -= y0) * y);
	};

	lineLength = lineLengthCalculation(d.x1, d.y1, d.x2, d.y2);	
	
	if (lineLength >= 0.1) {
		var mark_size_percent = (mark_size / lineLength) * 100;

		// scale offset so it will hit the ends, but never beyond them.
		mid_offset = mid_offset * 100;
		mid_offset = mid_offset*(1 - mark_size_percent/100) + mark_size_percent/2;
		
		var _offsetBegin = Math.round(mid_offset - mark_size_percent * 0.5) + "%";
		var _offsetEnd = Math.round(mid_offset + mark_size_percent * 0.5) + "%";

		var defsUpdate = defs.selectAll("#" + new_gradient_id)
			.data([{
						/* x1 : d.source.px,
						y1 : d.source.py,
						x2 : d.target.px,
						y2 : d.target.py */
						x1 : d.x1,
						y1 : d.y1,
						x2 : d.x2,
						y2 : d.y2
					}
				]);

		var defsEnter = defsUpdate.enter().append("linearGradient")
			.attr("id", new_gradient_id)
			.attr("gradientUnits", "userSpaceOnUse");

		var defsUpdateEnter = defsUpdate
			.attr("x1", function (d) {
				return d.x1
			})
			.attr("y1", function (d) {
				return d.y1
			})
			.attr("x2", function (d) {
				return d.x2
			})
			.attr("y2", function (d) {
				return d.y2
			});
			
		var stopsUpdate = defsUpdateEnter.selectAll("stop")
			.data([{
						offset : "0%",
						color : standardColor,
						opacity : "1"
					}, {
						offset : _offsetBegin,
						color : standardColor,
						opacity : "1"
					}, {
						offset : _offsetBegin,
						color : standardColor,
						opacity : "1"
					}, {
						offset : _offsetBegin,
						color : "#245A76",
						opacity : "1"
					}, {
						offset : _offsetEnd,
						color : "#245A76",
						opacity : "1"
					}, {
						offset : _offsetEnd,
						color : standardColor,
						opacity : "1"
					}, {
						offset : _offsetEnd,
						color : standardColor,
						opacity : "1"
					}, {
						offset : "100%",
						color : standardColor,
						opacity : "1"
					}
				]);

		stopsEnter = stopsUpdate.enter().append("stop");

		stopsUpdateEnter = stopsUpdate
			.attr("offset", function (d) {
				return d.offset;
			})
			.attr("stop-color", function (d) {
				return d.color;
			})
			.attr("stop-opacity", function (d) {
				return d.opacity;
			});

		self.style("stroke", "url(#" + new_gradient_id + ")");
	}

}

var linkedByIndex;

var width = $(window).width();
var height = $(window).height();

var svg = d3.select("body").append("svg")
	.attr("width", width)
	.attr("height", height);

var force;
var callLink;
var textLink;
var link;
var node;
var defs;
var marker;
var total_interactions = 0;
var max_interactions = 0;

function CreateVisualizationFromData() {

	function chargeForNode(d, i) {
		// main node
		if (i == 0) {
			return -25000;
		}
		// contains other links
		else if (isConnectedToOtherThanMain(d)) {
			return -2000;
		} else {
			return -1200;
		}
	}

	// initial placement of nodes prevents overlaps
	var xOffset = 10000;
	var yOffset = 0;
	var central_x = width / 2;
	var central_y = height / 2;

	data_nodes.forEach(function (d, i) {
		if (i != 0) {
			connected = isConnectedToOtherThanMain(d);
			data_nodes[i].x = connected ? central_x + xOffset : central_x - xOffset;
			data_nodes[i].y = connected ? central_y + yOffset : central_y - yOffset;
		} else {
			data_nodes[i].x = central_x;
			data_nodes[i].y = central_y;
		}
	})

	force = d3.layout.force()
		.nodes(data_nodes)
		.links(data_links)
		.charge(function (d, i) {
			return chargeForNode(d, i)
		})
		.friction(0.6) // 0.6
		.gravity(0.4) // 0.6
		.size([width, height])
		.start() //initialise alpha
		.stop();

	call_links_data = data_links.filter(function (d) {
			return (d.source_calls + d.target_calls > 0)
		});
	text_links_data = data_links.filter(function (d) {
			return (d.source_texts + d.target_texts > 0)
		});

	//UPDATE
	callLink = svg.selectAll(".call-line")
		.data(call_links_data)
		//ENTER
		callLink.enter().append("line")
		.attr('class', 'call-line');
	//EXIT
	callLink.exit().remove;

	//UPDATE
	textLink = svg.selectAll(".text-line")
		.data(text_links_data)
		//ENTER
		textLink.enter().append("line")
		.attr('class', 'text-line');
	//EXIT
	textLink.exit().remove;

	//UPDATE
	node = svg.selectAll(".node")
		.data(data_nodes)
		//ENTER
		node.enter().append("g")
		.attr("class", "node")
		.append("circle")
		.attr("r", function(d) {return d.radius;} )
		.style("fill", function (d) {
			return (d.index == 0) ? "#ffffff" : d.fill;
		})
		.style("stroke", function (d) {
			return (d.index == 0) ? "#8C8C8C" : "#ffffff";
		})

	//EXIT
	node.exit().remove;

	defs = !(defs && defs.length) ? svg.append("defs") : defs;

	marker = svg.selectAll('marker')
		.data([{
					refX : 6 + 7,
					refY : 2,
					markerWidth : 6,
					markerHeight : 4
				}
			])
		.enter().append("marker")
		.attr("id", "arrowhead")
		.attr("refX", function (d) {
			return d.refX
		})
		.attr("refY", function (d) {
			return d.refY
		})
		.attr("markerWidth", function (d) {
			return d.markerWidth
		})
		.attr("markerHeight", function (d) {
			return d.markerHeight
		})
		.attr("orient", "auto")
		.append("path")
		.attr("d", "M 0,0 V 4 L6,2 Z");

		$('.node').tipsy({
			gravity: 'w',
			html: true,
			title: function() {
			var d = this.__data__, name = d.name;
			return name;
		}
	});
		
	if (text_links_data.length > 0) {
		//UPDATE + ENTER
		textLink
		.style("stroke-width", function stroke(d) {
			return text_width(d)
		})
		.each(function (d, i) {
			applyGradient(this, "text", d, i)
		});
	}

	if (call_links_data.length > 0) {
		//UPDATE + ENTER
		callLink
		.style("stroke-width", function stroke(d) {
			return call_width(d)
		})
		.each(function (d, i) {
			applyGradient(this, "call", d, i)
		});
	}

	force
	.on("tick", tick);

}


function call_width(d) {
	return (d.source_calls + d.target_calls) / max_interactions * line_width_factor;
}

function text_width(d) {
	return (d.source_texts + d.target_texts) / max_interactions * line_width_factor;
}

function total_width(d) {
	return (d.source_calls + d.target_calls + d.source_texts + d.target_texts) / max_interactions * line_width_factor + line_diff;
}

function line_perpendicular_shift(d, direction) {
	theta = getAngle(d);
	theta_perpendicular = theta + (Math.PI / 2) * direction;

	lineWidthOfOppositeLine = direction == 1 ? text_width(d) : call_width(d);
	shift = lineWidthOfOppositeLine / 2;

	var delta_x = (shift + line_diff) * Math.cos(theta_perpendicular);
	var delta_y = (shift + line_diff) * Math.sin(theta_perpendicular);

	return [delta_x, delta_y];

}

function line_radius_shift_to_edge(d, which_node) { // which_node = 0 if source, = 1 if target

	theta = getAngle(d);
	theta = (which_node == 0) ? theta : theta + Math.PI; // reverse angle if target node
	radius = (which_node == 0) ? d.source.radius : d.target.radius; // node_radius(d.source) : node_radius(d.target); // d.source and d.target refer directly to the nodes (not indices)
	//radius -= 2; // add stroke width

	var delta_x = radius * Math.cos(theta);
	var delta_y = radius * Math.sin(theta);

	return [delta_x, delta_y];

}

function getAngle(d) {
	rel_x = d.target.x - d.source.x;
	rel_y = d.target.y - d.source.y;
	return theta = Math.atan2(rel_y, rel_x);
}