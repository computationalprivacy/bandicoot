import React from 'react'
import d3 from 'd3'
import ReactDOM from 'react-dom'


export default class TimeScaleBrush extends React.Component {
  constructor(props) {
    super(props)
    this.chart = null
    this.chart_id = "chart_" + props.id

    this.svg = null
    this.brush = null

    this.intervals = {}
    this.updateBrush.bind(this)
  }


  updateBrush(new_extent) {
    this.svg.select(".brush").transition()
      .duration(250)
      .call(this.brush.extent(new_extent))
      .call(this.brush.event);

    this.props.onBrush(new_extent);
  }

  updateNamedBrush(name) {
    this.updateBrush(this.intervals[name])
  }

  componentDidMount() {
    let el = ReactDOM.findDOMNode(this)

    let margin = {top: 5, right: 20, bottom: 20, left: 0},
        width = el.offsetWidth - margin.left - margin.right,
        height = 80 - margin.top - margin.bottom;

    let svg = d3.select(el).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
          .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    this.svg = svg

    svg.append("rect")
      .attr("class", "grid-background")
      .attr("width", width)
      .attr("height", height)

    let small_interval = d3.time.month,
        large_interval = d3.time.year

    if(this.props.timescale.length < 52 * 7) {
      small_interval = d3.time.week
      large_interval = d3.time.month
    }

    let timescale_by_chunk = this.props.timescale.map(small_interval)
    let min_max = d3.extent(timescale_by_chunk) // First and last

    this.intervals = {
      'all': [null, null],
      'last_week': [d3.time.week.offset(min_max[1], -1), min_max[1]],
      'last_month': [d3.time.month.offset(min_max[1], -1), min_max[1]]
    }

    let x = d3.time.scale()
      .domain(min_max)
      .range([0, width])

    let brush = d3.svg.brush()
      .x(x)
      .extent([null, null])
      .on("brushend", brushended)
    this.brush = brush

    let onBrush = this.props.onBrush

    function brushended() {
      if (!d3.event.sourceEvent) return; // only transition after input
      let extent0 = brush.extent(),
          extent1 = extent0.map(small_interval.round);

      // if empty when rounded, use floor & ceil instead
      if (extent1[0] >= extent1[1]) {
        extent1[0] = small_interval.floor(extent0[0]);
        extent1[1] = small_interval.ceil(extent0[1]);
      }

      d3.select(this).transition()
        .duration(250)
        .call(brush.extent(extent1))
        .call(brush.event);

      if(onBrush) onBrush(extent1)
    }

    // Ticks by week
    svg.append("g")
      .attr("class", "x grid")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.svg.axis()
          .scale(x)
          .orient("bottom")
          .ticks(small_interval)
          .tickSize(-height)
          .tickFormat(""))

    // X axis with months
    svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.svg.axis()
        .scale(x)
        .orient("bottom")
        .ticks(large_interval)
        .tickPadding(0))
    .selectAll("text")
      .attr("x", 6)
      .style("text-anchor", null);

    // Selector brush
    svg.append("g")
      .attr("class", "brush")
      .call(brush)
      .call(brush.event)
      .selectAll("rect")
      .attr("height", height)
  }

  render() {
    return (<div id={this.chart_id}></div>);
  }
}
