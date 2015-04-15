

// Some code used from http://chriszetter.com/voronoi-map/examples/uk-supermarkets/ , which has the following license.

/*	The MIT License (MIT)
	
Copyright (c) 2014 Chris Zetter

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. */

voronoiMap = function (map, link_antennna, link_transitions, layerControl) {
	var points = [],
	transitions = [],
	lastSelectedPoint;
	var readyToDraw = false;

	var line_width_factor = 3;
	var pointDist = 5;
	var colorScale;

	var voronoi = d3.geom.voronoi()
		.x(function (d) {
			return d.x;
		})
		.y(function (d) {
			return d.y;
		});

	
	var drawWithLoading = function (e) {
		draw();
		/* d3.select('#loading').classed('visible', true);
		if (e && e.type == 'viewreset') {
			d3.select('#overlay').remove();
		}
		setTimeout(function () {
			draw();
			d3.select('#loading').classed('visible', false);
		}, 0); */
	}

	var svg;
	var bounds;
	var topLeft;
	var bottomRight;
	var existing;
	var drawLimit;

	var findCoordsForLinePoints = function (transition) {
		var idArray = pluck(points, 'id');
		var indexSource = idArray.indexOf(transition.source);
		var indexTarget = idArray.indexOf(transition.target);

		x1 = points[indexSource].x;
		y1 = points[indexSource].y;
		x2 = points[indexTarget].x;
		y2 = points[indexTarget].y;

		theta = Math.atan2(y2 - y1, x2 - x1);
		thetaOpposite = theta + Math.PI;

		x1 += pointDist * Math.cos(theta)
		y1 += pointDist * Math.sin(theta)
		x2 += pointDist * Math.cos(thetaOpposite)
		y2 += pointDist * Math.sin(thetaOpposite)

		return String(x1 + ',' + y1 + ',' + x2 + ',' + y2);
	}

	var draw = function () {

		d3.select('#overlay').remove();
		d3.selectAll("polyline").remove();

		bounds = map.getBounds();
		
		topLeft = map.latLngToLayerPoint(bounds.getNorthWest());
		bottomRight = map.latLngToLayerPoint(bounds.getSouthEast());
		drawLimit = bounds.pad(200);
		readyToDraw = true;
		
		existing = d3.set();
		
		colorScale = d3.scale.quantize()
			.domain([0, maxInteractions])
			.range(colorbrewer.Blues[9].slice(1, 6));

		svg = d3.select(map.getPanes().overlayPane).append("svg")
			.attr('id', 'overlay')
			.attr("class", "leaflet-zoom-hide")
			.style("width", map.getSize().x + 'px')
			.style("height", map.getSize().y + 'px')
			.style("margin-left", topLeft.x + "px")
			.style("margin-top", topLeft.y + "px");

		filteredPoints = points.filter(function (d) {
				var latlng = new L.LatLng(d.latitude, d.longitude);

				if (!drawLimit.contains(latlng)) {
					return false
				};

				var point = map.latLngToLayerPoint(latlng); //map.latLngToContainerPoint(latlng) // map.latLngToLayerPoint(latlng);

				key = point.toString();
				if (existing.has(key)) {
					return false
				};
				existing.add(key);

				d.x = point.x;
				d.y = point.y;
				return true;
			});
			
		//console.log(filteredPoints[0].x);
		//console.log(filteredPoints[0].y);

		voronoi(filteredPoints).forEach(function (d) {
			d.point.cell = d;
		});

		var g = svg.append("g")
			.attr("transform", "translate(" + (-topLeft.x) + "," + (-topLeft.y) + ")");

		var svgPoints = g.attr("class", "points")
			.selectAll("g")
			.data(filteredPoints)
			.enter().append("g")
			.attr("class", "point");

		var buildPathFromPoint = function (point) {
			//console.log(point)
			return "M" + point.cell.join("L") + "Z";
		}

		svgPoints.append("path")
		.attr("class", "point-cell")
		.attr("d", buildPathFromPoint)
		.style("stroke", "grey") // "gainsboro"
		.style("stroke-width", 2.5)
		.style('fill', function (d) {
			return interactionGradient(d)
		})
		.style('opacity', 0.8);

		svgPoints.append("circle")
		.attr("transform", function (d) {
			return "translate(" + d.x + "," + d.y + ")";
		})
		.style('fill', function (d) {
			return d.interactions > 0 ? 'white' : 'transparent';
		})
		.attr("r", 3.5);

		if (typeof transitions !== 'undefined') {

			filteredTransitions = transitions

				var gLines = svg.append("g")
				.attr("transform", "translate(" + (-topLeft.x) + "," + (-topLeft.y) + ")");

			var svgLines = gLines.attr("class", "points")
				.selectAll("g")
				.data(filteredTransitions)
				.enter().append("g")
				.attr("class", "point");

			svgLines.append("polyline")
			.style("stroke", "slategray")
			.style("fill", "none")
			.style("stroke-width", function (d) {
				return (d.amount + meanTransitions) / (maxTransitions + meanTransitions) * line_width_factor
			}) // scaled so even few transitions are visible
			.attr("points", function (d) {
				return findCoordsForLinePoints(d)
			});

			drawLegend();

		}
	}

	function drawLegend() {

		var g_legend = svg.append("g")
			.attr("class", "key")
			.attr("transform", "translate(50, 50)");

		var background;
		var legendWidth = 400;

		var x = d3.scale.linear()
			.domain([0, 1])
			.range([0, legendWidth]);

		ran = colorbrewer.Blues[9].slice(1, 6);
		len = ran.length;

		dom = [1 / len, 2 / len, 3 / len, 4 / len, 5 / len, 1];

		var threshold = d3.scale.threshold()
			.domain(dom)
			.range(ran);

		g_legend.selectAll("backgroundRect")
		.data([1])
		.enter().append("rect")
		.attr("x", "12.5")
		.attr("y", "12.5")
		.attr("height", 50)
		.attr("width", legendWidth + 25)
		.style("fill", "white")
		.style("stroke", "black")
		.style("stroke-width", 0.5);

		g_legend.selectAll("legendRect")
		.data(threshold.range().map(function (colorScale) {
				var d = threshold.invertExtent(colorScale);
				if (d[0] == null)
					d[0] = x.domain()[0];
				if (d[1] == null)
					d[1] = x.domain()[1];
				return d;
			}))
		.enter().append("rect")
		.attr("height", 10)
		.attr("y", "25")
		.attr("x", function (d) {
			return x(d[0]) + 25;
		})
		.attr("width", function (d) {
			return x(d[1]) - x(d[0]);
		})
		.style("fill", function (d) {
			return threshold(d[0]);
		})
		.style("opacity", 0.8);

		var formatPercent = d3.format(".0%"),
		formatNumber = d3.format(".0f");

		var xAxis = d3.svg.axis()
			.scale(x)
			.orient("bottom")
			.tickSize(13)
			.tickValues(dom)
			.tickFormat("");

		g_legend.selectAll("text")
		.data(dom, function (d) {
			return d
		})
		.call(function (d) {
			d.enter().append("text")
		})
		.attr("y", "45")
		.attr("x", function (d, i) {
			return (legendWidth / len * (i + 0.5)) + 25
		})
		.style("text-anchor", "middle")
		.text(function (d, i) {
			return formatNumber(i * maxInteractions / len + 1) + "-" + formatNumber((i + 1) * maxInteractions / len);
		});

	}

	function interactionGradient(d) {
		color = "rgba(255,255,255,0.5)"; // 'white'

		if (d.interactions > 0) {
			color = colorScale(d.interactions);
		}

		return color;
	}

	var mapLayer = {
		onAdd : function (map) {
			map.on('viewreset moveend', drawWithLoading);
			drawWithLoading();
		},
		onRemove : function (map) {
			d3.select('#overlay').remove();
		}
	};

	var maxInteractions = 0;
	var maxTransitions = 0;

	// Function for grabbing a specific property from an array
	pluck = function (ary, prop) {
		return ary.map(function (x) {
			return x[prop]
		});
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

	// Sums an array
	sumArray = function (ary) {
		return ary.reduce(function (a, b) {
			return a + b
		}, 0);
	}

	function setMap() {
		intCount = pluck(points, 'interactions');
		int_min = ss.quantile(intCount, 0.9);

		enoughInteractionsPoints = points.filter(function (d) {
				return d.interactions > int_min;
			});
		latitude = pluck(enoughInteractionsPoints, 'latitude');
		longitude = pluck(enoughInteractionsPoints, 'longitude');

		minLat = Math.min(minArray(latitude));
		maxLat = Math.max(maxArray(latitude));

		minLong = Math.min(minArray(longitude));
		maxLong = Math.max(maxArray(longitude));

		map.fitBounds([[maxLat + 0.05, minLong - 0.05], [minLat - 0.05, maxLong + 0.05]]);
	}
	

	d3.csv(link_antennna, function (csv) {
		points = csv;
		points.forEach(function (point) {
			point.interactions = parseInt(point.interactions);
		})
		maxInteractions = Math.max(maxArray(pluck(points, 'interactions')));

		setMap();
		map.addLayer(mapLayer);
		//layerControl.addOverlay(mapLayer, 'Voronoi');
	})

	d3.csv(link_transitions, function (csv) {
		transitions = csv;
		transitions.forEach(function (transition) {
			transition.amount = parseInt(transition.amount);
		})
		maxTransitions = Math.max(maxArray(pluck(transitions, 'amount')));
		meanTransitions = sumArray(pluck(transitions, 'amount')) / transitions.length;

		drawWithLoading();
	})

}
