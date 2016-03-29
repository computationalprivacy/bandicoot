export const meta_indicators = {
  "nb_all": {
    "description": "number of interactions",
    "agg": "sum"
  },
  "nb_inc_all": {
    "description": "number of incoming interactions",
    "agg": "sum"
  },
  "nb_out_all": {
    "description": "number of outgoing interactions",
    "agg": "sum"
  },
  "nb_out_call": {
    "description": "number of outgoing calls",
    "agg": "sum"
  },
  "nb_out_text": {
    "description": "number of outgoing texts",
    "agg": "sum"
  },
  "nb_inc_call": {
    "description": "number of incoming calls",
    "agg": "sum"
  },
  "nb_inc_text": {
    "description": "number of incoming texts",
    "agg": "sum"
  },
  "active_day": {
    "description": "average number of active days",
    "agg": "mean"
  },
  "call_duration": {
    "description": "average call duration (in seconds)",
    "unit": "second",
    "agg": "mean",
    "type": "distribution"
  },
  "percent_initiated_interactions": {
    "description": "percentage of initiated calls",
    "unit": "percent",
    "agg": "mean"
  },
  "percent_initiated_conversations": {
    "description": "percentage of initiated conversation",
    "unit": "percent",
    "agg": "mean"
  },
  "number_of_contacts": {
    "description": "number of contacts",
    "agg": "mean"
  },
  "percent_nocturnal": {
    "description": "percentage of interactions at night",
    "unit": "percent",
    "agg": "mean"
  },
  "response_rate": {
    "description": "response rate",
    "unit": "percent",
    "agg": "mean"
  },
  "response_delay": {
    "description": "response delay",
    "unit": "second",
    "agg": "mean",
    "type": "distribution"
  },
  "balance_of_contacts": {
    "description": "balance of contacts",
    "agg": "mean",
    "type": "distribution"
  }
}

export function flatten(arr) {
  if (arr.length == 0)
    return null;
  return arr.reduce((a, b) => a.concat(b))
}