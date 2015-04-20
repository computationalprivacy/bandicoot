var line_diff = 0.5;  // increase from zero if you want space between the call/text lines
var mark_offset = 10; // how many percent of the mark lines in each end are not used for the relationship between incoming/outgoing?
var mark_size = 5;    // size of the mark on the line

var legendRectSize = 9; // 18
var legendSpacing = 5; // 4
var recordTypes = [];
var legend;
var legendDrawn = false;

var text_links_data, call_links_data;

// colors for the different parts of the visualization
recordTypes.push({
	text : "call",
	color : "#438DCA",
	legendtype: "legend_rect"
});

recordTypes.push({
	text : "text",
	color : "#70C05A",
	legendtype: "legend_rect"
});

recordTypes.push({
	text : "balance",
	color : "#245A76",
	legendtype: "legend_rect"
});

recordTypes.push({
	text : "in network",
	color : "#a8a8a8",
	legendtype: "legend_circle"
});

recordTypes.push({
	text : "out of network",
	color : "#dfdfdf",
	legendtype: "legend_circle"
});

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
                total_interactions += data_links[i].inc_calls
                                                            + data_links[i].out_calls
                                                            + data_links[i].inc_texts
                                                            + data_links[i].out_texts;
                max_interactions = Math.max(max_interactions,
                                                                        data_links[i].inc_calls
                                                                        + data_links[i].out_calls
                                                                        + data_links[i].inc_texts
                                                                        + data_links[i].out_texts)
            }

            //console.log(total_interactions);
            //console.log(max_interactions);

            linkedByIndex = {};

            data_links.forEach(function (d) {
                linkedByIndex[d.source + "," + d.target] = true;
                //linkedByIndex[d.source.index + "," + d.target.index] = true;
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
                d.size = (i == 0)? 200 : 30
                d.fill = (d.no_network_info == 1)? "#dfdfdf": "#a8a8a8"
            });
            dataLoaded();
        }
    });

function node_radius(d) {
    return Math.pow(40.0 * ((d.index == 0) ? 200 : 30), 1 / 3);
}
function node_radius_data(d) {
    return Math.pow(40.0 * d.size, 1 / 3);
}

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
            d.lpf1 = line_perpendicular_shift(d, 1)
            d.lrste = []
            d.lrste.push(line_radius_shift_to_edge(d, 0))
            d.lrste.push(line_radius_shift_to_edge(d, 1))
        })
        .attr("x1", function (d) {
            return d.source.x - d.lpf1[0] + d.lrste[0][0];
        })
        .attr("y1", function (d) {
            return d.source.y - d.lpf1[1] + d.lrste[0][1];
        })
        .attr("x2", function (d) {
            return d.target.x - d.lpf1[0] + d.lrste[1][0];
        })
        .attr("y2", function (d) {
            return d.target.y - d.lpf1[1] + d.lrste[1][1];
        });
        callLink.each(function (d, i) {
            applyGradient(this, "call", d, i)
        });

            }

    if (text_links_data.length > 0) {

                textLink
        .each(function (d) {
            d.lpfNeg1 = line_perpendicular_shift(d, -1);
            d.lrste = [];
            d.lrste.push(line_radius_shift_to_edge(d, 0));
            d.lrste.push(line_radius_shift_to_edge(d, 1));
        })
        .attr("x1", function (d) {
            return d.source.x - d.lpfNeg1[0] + d.lrste[0][0];
        })
        .attr("y1", function (d) {
            return d.source.y - d.lpfNeg1[1] + d.lrste[0][1];
        })
        .attr("x2", function (d) {
            return d.target.x - d.lpfNeg1[0] + d.lrste[1][0];
        })
        .attr("y2", function (d) {
            return d.target.y - d.lpfNeg1[1] + d.lrste[1][1];
        });
        textLink.each(function (d, i) {
            applyGradient(this, "text", d, i)
        });

        node
        .attr("transform", function (d) {
            return "translate(" + d.x + "," + d.y + ")";
        });

            }

    if (force.alpha() < 0.05 && legendDrawn == false)
        drawLegend();

    }


function applyGradient(line, interaction_type, d, i) {

        var self = d3.select(line);

    var current_gradient = self.style("stroke");
    //current_gradient = current_gradient.substring(4, current_gradient.length - 1);

    if (current_gradient.match("http")) {
        var parts = current_gradient.split("/");
        current_gradient = parts[-1];
    } else {
        current_gradient = current_gradient.substring(4, current_gradient.length - 1);
    }

    var new_gradient_id = "lg" + interaction_type + d.source.index + '_' + d.target.index; // + getRandomInt();

    var from = d.source.size < d.target.size ? d.source : d.target;
    var to = d.source.size < d.target.size ? d.target : d.source;

    var mid_offset = 0;
    var standardColor = "";

    if (interaction_type == "call") {
        mid_offset = d.inc_calls / (d.inc_calls + d.out_calls);
        standardColor = "#438DCA";
    } else {
        mid_offset = d.inc_texts / (d.inc_texts + d.out_texts);
        standardColor = "#70C05A";
    }


    mid_offset = mid_offset * 100;
    mid_offset = mid_offset * 0.6 + 20; // scale so it doesn't hit the ends

    lineLengthCalculation = function (x, y, x0, y0) {
        return Math.sqrt((x -= x0) * x + (y -= y0) * y);
    };

    lineLength = lineLengthCalculation(from.px, from.py, to.px, to.py);

    if (lineLength >= 0.1) {
        var mark_size_percent = (mark_size / lineLength) * 100,
                _offsetDiff = Math.round(mid_offset - mark_size_percent / 2) + "%",
                _offsetSum = Math.round(mid_offset + mark_size_percent / 2) + "%",

            defsUpdate = defs.selectAll("#" + new_gradient_id)
            .data([{
                x1: from.px,
                y1: from.py,
                x2: to.px,
                y2: to.py
        }]),

            defsEnter = defsUpdate.enter().append("linearGradient")
                .attr("id", new_gradient_id)
                .attr("gradientUnits", "userSpaceOnUse"),

            defsUpdateEnter = defsUpdate
                .attr("x1", function (d) { return d.x1 })
                .attr("y1", function (d) { return d.y1 })
                .attr("x2", function (d) { return d.x2 })
                .attr("y2", function (d) { return d.y2 }),

            stopsUpdate = defsUpdateEnter.selectAll("stop")
                .data([{
                    offset: "0%",
                    color: standardColor,
                    opacity: "1"
                }, {
                    offset: _offsetDiff,
                    color: standardColor,
                    opacity: "1"
                }, {
                    offset: _offsetDiff,
                    color: standardColor,
                    opacity: "1"
                }, {
                    offset: _offsetDiff,
                    color: "#245A76",
                    opacity: "1"
                }, {
                    offset: _offsetSum,
                    color: "#245A76",
                    opacity: "1"
                }, {
                    offset: _offsetSum,
                    color: standardColor,
                    opacity: "1"
                }, {
                    offset: _offsetSum,
                    color: standardColor,
                    opacity: "1"
                }, {
                    offset: "100%",
                    color: standardColor,
                    opacity: "1"
                }
                ]),

                stopsEnter = stopsUpdate.enter().append("stop")

            stopsUpdateEnter = stopsUpdate
            .attr("offset", function (d) {
                return d.offset;
            })
            .attr("stop-color", function (d) {
                return d.color;
            })
            .attr("stop-opacity", function (d) {
                return d.opacity;
            })

        self.style("stroke", "url(#" + new_gradient_id + ")")

        //current_gradient && defs.select(current_gradient).remove();
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

    data_nodes.forEach(function(d, i) {
        if (i != 0) {
            connected = isConnectedToOtherThanMain(d);
            data_nodes[i].x = connected ? central_x + xOffset : central_x - xOffset;
            data_nodes[i].y = connected ? central_y + yOffset : central_y - yOffset;
        }
        else {data_nodes[i].x = central_x; data_nodes[i].y = central_y;}})

    force = d3.layout.force()
        .nodes(data_nodes)
        .links(data_links)
        .charge(function (d, i) {
            return chargeForNode(d, i)
        })
        .friction(0.6) // 0.6
        .gravity(0.4) // 0.6
        .size([width, height])
        .start()    //initialise alpha
        .stop();

    call_links_data = data_links.filter(function(d) {
        return (d.inc_calls + d.out_calls > 0)});
    text_links_data = data_links.filter(function(d) {
        return (d.inc_texts + d.out_texts > 0)});

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
            .attr("r", node_radius)
            .style("fill", function (d) {
                return (d.index == 0) ? "#ffffff" : d.fill;
            })
            .style("stroke", function (d) {
                return (d.index == 0) ? "#8C8C8C" : "#ffffff";
            });

    //EXIT
    node.exit().remove;

    defs = !(defs && defs.length) ? svg.append("defs") : defs;

    marker = svg.selectAll('marker')
        .data([{refX: 6+7, refY: 2, markerWidth: 6, markerHeight: 4}])
    .enter().append("marker")
        .attr("id", "arrowhead")
        .attr("refX", function (d) { return d.refX })
        .attr("refY", function (d) { return d.refY })
        .attr("markerWidth", function (d) { return d.markerWidth })
        .attr("markerHeight", function (d) { return d.markerHeight })
        .attr("orient", "auto")
        .append("path")
            .attr("d", "M 0,0 V 4 L6,2 Z");

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

function drawLegend() {

	legendDrawn = true;
	var node_px = pluck(data_nodes, 'px');
	var node_py = pluck(data_nodes, 'py');
	var nodeLayoutRight  = Math.max(maxArray(node_px));
	var nodeLayoutBottom = Math.max(maxArray(node_py));
	
	legend = svg.selectAll('.legend')
		.data(recordTypes)
		.enter()
		.append('g')
		.attr('class', 'legend')
		.attr('class', function(d) {return d.legendtype})
		.attr('transform', function (d, i) {
			var rect_height = legendRectSize + legendSpacing;
			var offset = rect_height * (recordTypes.length-1);
			var horz = nodeLayoutRight + 15; /*  - 2*legendRectSize; */
			var vert = nodeLayoutBottom + (i * (rect_height)) - offset;
			return 'translate(' + horz + ',' + vert + ')';
		});

	svg.selectAll('.legend_rect')
	.append('rect')
	.attr('width', legendRectSize)
	.attr('height', legendRectSize)
	.style('fill', function (d) {
		return d.color
	})
	.style('stroke', function (d) {
		return d.color
	});
	
	svg.selectAll('.legend_circle')
	.append('circle')
	.attr('r', legendRectSize/2)
	.style('fill', function (d) {
		return d.color
	})
	.style('stroke', function (d) {
		return d.color
	})
	.attr('transform', 'translate('+legendRectSize/2+','+(legendRectSize/2+1.1)+')');

	legend.append('text')
	.attr('x', legendRectSize + legendSpacing)
	.attr('y', legendRectSize - legendSpacing + 6)
	.text(function (d) {
		return d.text;
	})
	.style('fill', '#757575');

}

var line_width_factor = 10.0 // width for the widest line

function call_width(d) {
    return (d.inc_calls + d.out_calls) / max_interactions * line_width_factor;
}

function text_width(d) {
    return (d.inc_texts + d.out_texts) / max_interactions * line_width_factor;
}

function total_width(d) {
    return (d.inc_calls + d.out_calls + d.inc_texts + d.out_texts) / max_interactions * line_width_factor + line_diff;
}

function line_perpendicular_shift(d, direction) {
    theta = getAngle(d);
    theta_perpendicular = theta + (Math.PI / 2) * direction;

    lineWidthOfOppositeLine = direction == 1 ? text_width(d) : call_width(d);
    shift = lineWidthOfOppositeLine / 2;

    delta_x = (shift + line_diff) * Math.cos(theta_perpendicular)
    delta_y = (shift + line_diff) * Math.sin(theta_perpendicular)

    return [delta_x, delta_y]

}

function line_radius_shift_to_edge(d, which_node) { // which_node = 0 if source, = 1 if target

    theta = getAngle(d);
    theta = (which_node == 0) ? theta : theta + Math.PI; // reverse angle if target node
    radius = (which_node == 0) ? node_radius(d.source) : node_radius(d.target) // d.source and d.target refer directly to the nodes (not indices)
    radius -= 2; // add stroke width

    delta_x = radius * Math.cos(theta)
        delta_y = radius * Math.sin(theta)

        return [delta_x, delta_y]

}

function getAngle(d) {
    rel_x = d.target.x - d.source.x;
    rel_y = d.target.y - d.source.y;
    return theta = Math.atan2(rel_y, rel_x);
}