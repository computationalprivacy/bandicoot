import React from 'react'
import d3 from 'd3'
import ReactDOM from 'react-dom'


export default class NetworkChart extends React.Component {
  constructor(props) {
    super(props)
    this.chart = null
    this.chart_id = "chart_" + props.id
    this.state = {extent: [null, null]}
  }

  shouldComponentUpdate(nextProps, nextState) {
    // Stop calling gravity() if the extent is the same
    if (nextState.extent == this.state.extent)
      return false
    else
      return true
  }

  componentDidUpdate() {
    const format = d3.time.format("%Y-%m-%d")

    this.props.network.forEach((d, i) => {
      d.count = d.values.filter((i) => {
        if (this.state.extent[0] == null) return true;
        return (format.parse(i[0]) >= this.state.extent[0]) && (format.parse(i[0]) <= this.state.extent[1]);
      }).length
    })
    let extent = d3.max(this.props.network, (d) => d.count) // On local count
    let radius_scale = d3.scale.pow().exponent(0.8).domain([0, extent]).range([2, 30]),
        color_scale = radius_scale.copy().range(["#7fcdbb", "#2c7fb8"])

    this.props.network.forEach((d) => d.r = radius_scale(d.count))

    let node = this.svg.selectAll("circle")
      .data(this.props.network)

    node
      .transition()
      .duration(400)
      .style("fill", (d, i) => d.count == 0 ? "#eee" : color_scale(d.count))
      .attr("r", (d) => d.r)

    this.updateTopThree()
    if(this.force) this.force.start()
  }

  updateTopThree() {
    var n = this.props.network.sort((a, b) => b.count - a.count)

    this.refs.top0.innerHTML = n[0].key + " (" + n[0].count + ")"
    this.refs.top1.innerHTML = n[1].key + " (" + n[1].count + ")"
    this.refs.top2.innerHTML = n[2].key + " (" + n[2].count + ")"
  }

  componentDidMount() {
    let el = ReactDOM.findDOMNode(this)

    let margin = {top: 15, right: 0, bottom: 15, left: 15},
        headerHeight = 140,
        width = el.offsetWidth - margin.left - margin.right,
        height = el.parentNode.offsetHeight - margin.top - margin.bottom - headerHeight;

    this.svg = d3.select(el).append("svg")
      .attr("width", width)
      .attr("height", height)
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    let layout_gravity = 0.5,
        charge = (d) => - 2.5 * Math.pow(d.r, 2),
        friction = 0.3

    this.componentDidUpdate()

    this.force = d3.layout.force()
      .gravity(layout_gravity)
      .charge(charge)
      .friction(friction)
      .nodes(this.props.network)
      .size([width, height])
      .on("tick", tick)

    let tooltip = d3.select("body")
      .append("div")
      .style("position", "absolute")
      .style("z-index", "10")
      .style("visibility", "hidden")
      .style("color", "white")
      .style("padding", "8px")
      .style("background-color", "rgba(0, 0, 0, 0.75)")
      .style("border-radius", "6px")
      .style("font", "12px sans-serif")
      .text("tooltip")

    this.node = this.svg.selectAll(".nodes")
      .data(this.props.network)
      .enter().append("circle")
        .attr("class", "node")
        .attr("cx", (d) => d.x)
        .attr("cy", (d) => d.y)
        .attr("r", (d) => d.r)
        .on("mouseover", function(d) {
          tooltip.text(d.key + " : " + d.count);
          tooltip.style("visibility", "visible");
        })
        .on("mousemove", () =>
          tooltip.style("top", (d3.event.pageY - 10) + "px").style("left", (d3.event.pageX + 10) + "px")
        )
        .on("mouseout", () => tooltip.style("visibility", "hidden"))

    let self = this // debug
    function tick(e) {
      self.node
        // .each(gravity(e.alpha * 0.5))
        .each(collide(0.2))

      self.node.attr("cx", function(d) { return d.x; })
          .attr("cy", function(d) { return d.y; });
    }

    function collide(k) {
      let q = d3.geom.quadtree(this.props.network);

      return function(node) {
        let nr = node.r * 1.2 + 5, // with padding
            nx1 = node.x -nr,
            nx2 = node.x +nr,
            ny1 = node.y -nr,
            ny2 = node.y +nr;

        q.visit(function(quad,x1,y1,x2,y2) {
          if (quad.point && (quad.point !== node )) {
            let x = node.x - quad.point.x,
              y = node.y-quad.point.y,
              l = x*x+y*y,
              r = nr + quad.point.r;

            if (l<r*r) {
              l = ((l = Math.sqrt(l)) - r) / l * k;
              node.x -= x *= l;
              node.y -= y *= l;
              quad.point.x += x;
              quad.point.y += y;
            }
          }
          return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
        });
      };
    }

    collide = collide.bind(this)
    this.componentDidUpdate()

  }

  render() {
    return <div id={this.chart_id}>
      <div className="top-box">
        <p className="legend">Top 3 users</p>
        <ol>
          <li ref="top0"></li>
          <li ref="top1"></li>
          <li ref="top2"></li>
        </ol>
      </div>
      <p>Ego network</p>
    </div>
  }
}