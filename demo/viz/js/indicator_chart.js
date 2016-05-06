import React from 'react'
import d3 from 'd3'
import ReactDOM from 'react-dom'
import c3 from 'c3'

import { meta_indicators, flatten } from "./utils"


const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

export default class IndicatorChart extends React.Component {
  constructor(props) {
    super(props)
    this.chart = null
    this.chart_id = "chart_" + props.id

    this.state = {
      name: this.props.name,
      filter: [null, null],
      groupby: "day-of-week",
    }

    this.handleAggregateChange = this.handleAggregateChange.bind(this)
  }

  postfix() {
    let unit = meta_indicators[this.state.name].unit
    return (unit == "second" ? "s" : "") + (unit == "percent" ? "%" : "")
  }

  componentDidMount() {
    function format_week(d) {
      let d_end = d3.time.week.offset(d3.time.saturday(d), 1)

      let format = d3.time.format("%a %d %b %Y")
      let format_fst = d3.time.format("%a %d %b %Y");
      let same_year = d.getFullYear() == d_end.getFullYear(),
          same_month = d.getMonth() == d_end.getMonth()

      if(same_year){
        if(same_month) format_fst = d3.time.format("%a %d")
        else format_fst = d3.time.format("%a %d %b")
      } else
        format_fst = format
      
      return format_fst(d) + " &#8212; " + format(d_end)
    }

    let total_height = document.getElementById(this.chart_id).parentElement.parentElement.parentElement.offsetHeight

    this.chart = c3.generate({
      bindto: '#' + this.chart_id,
      data: this._c3_data(),
      legend: { show: false },
      size: { height: total_height / 2 - 50 },

      tooltip: {
        format: {
          title: (x) => (this.state.groupby == "day-of-week" ? days[x] : format_week(x)),
          value: (v) => d3.round(v, 2) + this.postfix(),
          name: (name) =>  meta_indicators[this.state.name].agg == "mean" ? "Average value" : "Total value"
        }
      }
    });

    this.componentDidUpdate()
  }

  componentDidUpdate() {
    if(this.state.groupby == "day-of-week") {
      this.chart.internal.loadConfig({
        axis: {
          x: {
            tick: {
              format: (i) => days[i],
              culling: {},
            },
            type: 'category'
          }
        }
      })
    } else {
      this.chart.internal.loadConfig({
        axis: {
          x: {
            tick: {
              culling: { max: 7},
              format: '%Y-%m-%d'
            },
            type: 'timeseries',
          }
        }
      })
    }

    this.chart.load(this._c3_data())
  }

  _c3_data() {
    const day_of_week = d3.time.format("%w")
    const day_format = d3.time.format("%Y-%m-%d")
    const week_agg = d3.time.week

    let indicator = this.props.indicators[this.state.name]
    let agg_function = (meta_indicators[this.state.name].agg == "mean") ? d3.mean : d3.sum

    let entries = d3.zip(this.props.timescale, indicator)
    if(this.state.filter[0] != null)
      entries = entries.filter((d) => this.state.filter[0] <= d[0] && d[0] < this.state.filter[1])

    let is_distribution = meta_indicators[this.state.name].type == 'distribution'
    function rollup(i) {
      if(is_distribution)
        return agg_function(flatten(i.map((j) => j[1]))) || 0
      else
        return agg_function(i.map((j) => j[1])) || 0
    }

    let nest = d3.nest()
      .key((d) => this.state.groupby == "day-of-week" ? day_of_week(d[0]) : day_format(week_agg(d[0])))
      .rollup(rollup)
      .entries(entries)

    let c3_data = {
      x: 'date',
      columns: [
        ['date'].concat(nest.map((i) => i.key)),
        ['indicator'].concat(nest.map((i) => i.values))
      ],
      types: { indicator: this.state.groupby == "day-of-week" ? "bar" : "area-step"},
      xFormat: "%Y-%m-%d"
    }
    return c3_data;
  }

  handleAggregateChange(event) {
    this.setState({groupby: event.target.value})
  }

  render() {
    return (<div className="graph">
              <p>Indicators / { meta_indicators[this.state.name].description }</p>
              <div className="aggregate-select">
                <select onChange={this.handleAggregateChange}>
                  <option value="day-of-week">by week</option>
                  <option value="all-time">all time range</option>
                </select>
              </div>
              <div id={this.chart_id}></div>
            </div>);
  }
}
