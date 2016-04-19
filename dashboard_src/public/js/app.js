import React from 'react'
import d3 from 'd3'
import ReactDOM from 'react-dom'
import c3 from 'c3'

import TimeScaleBrush from "./timescale_brush"
import IndicatorChart from "./indicator_chart"
import NetworkChart from "./network"
import { meta_indicators, flatten } from "./utils"

class ControlPanel extends React.Component {
  render() {
    let click = (i) => (() => this.props.onClick(i))

    let props = this.props;
    function nb(indicator, legend, classes) {
      return React.createElement("span", {
        onClick: click(indicator),
        className: classes
      }, props[indicator] + " " + legend);
    }

    function simple_block(name, legend, postfix, classes) {
      let displayed_value = (props[name] == null || isNaN(props[name])) ? "/" : (String(props[name]) + (postfix || ''));

      return <div className={"nav-block " + classes}>
          <p className="number" onClick={click(name)}>{displayed_value}</p>
          <p className="legend">{legend}</p>
        </div>
    }

    let plural_form = (g) => g + 's' // Currently simple :)

    return (
      <nav className="nav-inner-panel">
        {simple_block('nb_all', "interactions in " + props.number_of_bins + " " + plural_form(props.groupby), '', 'large')}

        <div className="nav-block">
          <p onClick={click("nb_inc_all")} className="number">{props.nb_inc_all} <span className="label">incoming</span></p>
          <p className="legend">{nb("nb_inc_call", "calls", "label call")} and {nb("nb_inc_text", "texts", "label text")}</p>
        </div>

        <div className="nav-block">
          <p onClick={click("nb_out_all")} className="number">{props.nb_out_all} <span className="label">outgoing</span>
          </p>
          <p className="legend">{nb("nb_out_call", "calls", "label call")} and {nb("nb_out_text", "texts", "label text")}</p>
        </div>

        {simple_block('call_duration', 'average call duration', 's', 'separator')}
        {simple_block('percent_initiated_interactions', 'initiated interactions', '%')}
        {simple_block('percent_initiated_conversations', 'initiated conversations', '%', 'separator')}
        {simple_block('response_rate', 'response rate', '%')}
        {simple_block('percent_nocturnal', 'at night', '%')}
        {simple_block('balance_of_contacts', 'balance of contacts', '%')}
      </nav>
    )
  }
}


class Dashboard extends React.Component {
  constructor(props) {
    super(props)
    this.state = {last_chart: null}
  }

  handleUpdate(name) {
    let chart = (this.state.last_chart == this.refs.top_graph) ?
                this.refs.bottom_graph : this.refs.top_graph

    chart.setState({name: name})
    this.setState({last_chart: chart})
  }

  handleBrush(time_filter) {
    this.refs.top_graph.setState({filter: time_filter})
    this.refs.bottom_graph.setState({filter: time_filter})
    this.refs.network.setState({extent: time_filter})
  }

  handleNamedBrush (e) {
    let selection = e.target.dataset.key;
    this.refs.timescale.updateNamedBrush(selection)
  }

  render() {
    let boundUpdate = (i) => { this.handleUpdate(i) }
    let boundBrush = (i) => { this.handleBrush(i) }
    let boundNamedBrush = (i) => { this.handleNamedBrush(i) }

    return <div className="dashboard-container">
      <section className="main-panel">
        <section className="viz-panel">
          <section className="section-panel left-panel">
            <NetworkChart ref="network" id="network" width={500} height={500}
                          network={this.props.network} />
          </section>
          <section className="section-panel right-panel">
            <IndicatorChart ref="top_graph" id="top"
                            indicators={this.props.indicators}
                            timescale={this.props.timescale}
                            name={"nb_all"} />
            <IndicatorChart ref="bottom_graph" id="bottom"
                            indicators={this.props.indicators}
                            timescale={this.props.timescale}
                            name={"percent_nocturnal"} />
          </section>
        </section>
        <section className="section-selector">
          <div className="mini-group">
            <p data-key="all" onClick={boundNamedBrush}>All time range</p>
            <p data-key="last_month" onClick={boundNamedBrush}>Last month</p>
            <p data-key="last_week" onClick={boundNamedBrush}>Last week</p>
          </div>
          <div id="timescale-selector">
            <TimeScaleBrush ref="timescale" id="week-brush"
                            timescale={this.props.timescale}
                            onBrush={boundBrush} />
          </div>
        </section>
      </section>
      <nav className="nav-panel" id="nav-panel">
        <ControlPanel {...this.props.stats} onClick={boundUpdate}/>
      </nav>
    </div>
  }
} 


d3.json("data/bc_export.json", (error, data) => {
  if (error) return console.warn(error);

  let format = d3.time.format("%Y-%m-%d")
  let timescale = data.me.date_range.map(format.parse)
  let indicators = data.me.indicators

  /*
  ** Aggregated properties used by components
  */

  let props = {
    number_of_bins: ~~(indicators.number_of_contacts.length / 7),
    groupby: "week"
  }

  for(var i in indicators) {
    let is_distribution = meta_indicators[i].type == 'distribution'
    let agg = meta_indicators[i].agg == 'mean' ? d3.mean : d3.sum

    if(indicators[i] == null || indicators[i].length == 0)
      props[i] = null
    else if(is_distribution)
      props[i] = agg(flatten(indicators[i]))
    else
      props[i] = agg(indicators[i])
  }

  for (var k in props)
    props[k] = d3.round(props[k], 1) || props[k]

  // Network view
  let network = d3.nest()
    .key((d) => d[1])
    .entries(data.me.network)

  /*
  ** Generate and render charts+panels in a Dashboard object
  */

  let dasboard_div = document.createElement("div");
  dasboard_div.className = "dashboard-wrapper";
  document.body.appendChild(dasboard_div);
  let d = <Dashboard indicators={indicators} timescale={timescale}
                     network={network} stats={props}/>
  let dashboard = ReactDOM.render(d, dasboard_div);
})