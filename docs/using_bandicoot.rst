Using bandicoot
===============

bandicoot indicators are divided in four modules (:doc:`reference/bandicoot.individual`,
:doc:`reference/bandicoot.spatial`, :doc:`reference/bandicoot.network`, and :doc:`reference/bandicoot.recharge`).

They can also be computed at once using :meth:`bandicoot.utils.all`. :doc:`reference/bandicoot.network`
indicators will only be returned if the user was loaded in :meth:`~bandicoot.io.read_csv` using  the option ``network=True``.


Summary
-------

As described in :doc:`quickstart`, bandicoot returns by default the mean and std or the value of indicators.


When the indicator is a timeseries, for example in the case of
:meth:`~bandicoot.individual.call_duration`, bandicoot can also return the
median, min, max, kurtosis, and skewness using ``summary=extended`` or the full
timeserie using ``summary=None``. Note that, by default, bandicoot returns a list of lists with one list for every week.

  >>> bc.individual.call_duration(B, summary='extended')
  {
      "allweek": {
          "allday": {
              "call": {
                  "mean": {
                      "mean": 487.37072353402834,
                      "std": 45.45198877486552
                  },
                  "std": {
                      "mean": 290.83801983951815,
                      "std": 16.80049312510362
                  },
                  "median": {
                      "mean": 496.65,
                      "std": 89.55251252756675
                  },
                  "skewness": {
                      "mean": -0.020629629074944145,
                      "std": 0.316056976875559
                  },
                  "kurtosis": {
                      "mean": 1.831122766069137,
                      "std": 0.2258792542370957
                  },
                  "min": {
                      "mean": 17.3,
                      "std": 23.48212085821892
                  },
                  "max": {
                      "mean": 974.6,
                      "std": 18.369540005128055
                  }
              }
          }
      }
  }


  >>> bc.individual.call_duration(B, summary=None)
  {
      "allweek": {
          "allday": {
              "call": [
                  [ 84, 209, 279, 279, 416, 441, 800, 860, 940], ... [ 8, 57, 127, 317, 536, 601, 619, 702, 769, 791, 792, 858, 867, 886, 932, 947]
              ]
          }
      }
  }

  >>> bc.individual.call_duration(B, summary=None, groupby=None)
  {
      "allweek": {
          "allday": {
              "call": [ 84, 209, 279, 279, 416, 441, 800, 860, 940, ..., 8, 57, 127, 317, 536, 601, 619, 702, 769, 791, 792, 858, 867, 886, 932, 947]
          }
      }
  }


=============== ============ ===============================================
summary         single value timeserie
=============== ============ ===============================================
default          value       mean, std
extended         value       mean, std, median, min, max, kurtosis, skewness
None             value       the full distribution
=============== ============ ===============================================

Interaction type
----------------


Calls and texts
~~~~~~~~~~~~~~~

The :doc:`reference/bandicoot.individual` and :doc:`reference/bandicoot.network` indicators can be computed on records of type ``call``, ``text``, or ``callandtext`` (which includes both calls and texts).

For example, :meth:`~bandicoot.individual.active_days` returns, by default, the
number of days a user has been active overall::

   >>> bc.individual.active_days(B)
   {
        "allweek": {
            "allday": {
                "callandtext": {
                    "mean": 5.4,
                    "std": 2.33238075793812
                }
            }
        }
    }


This behavior can be changed using the ``interaction`` keyword which takes a list::

   >>> bc.individual.active_days(B, interaction=['callandtext','call','text'])
   {
        "allweek": {
            "allday": {
                "callandtext": {
                    "mean": 5.4,
                    "std": 2.33238075793812
                },
                "call": {
                    "mean": 5.4,
                    "std": 2.33238075793812
                },
                "text": {
                    "mean": 5.4,
                    "std": 2.33238075793812
                }
            }
        }
    }

If an interaction type is specified and there are no records of that type, bandicoot will return ``None`` for that indicator::

    >>> B.has_text
    False
    >>> bc.individual.number_of_contacts(B, interaction=['call','text'])   
    {
        "allweek": {
            "allday": {
                "call": {
                    "mean": 31.9,
                    "std": 10.681292056675542
                },
                "text": {
                    "mean": None,
                    "std": None
                }
            }
        }
    }


GPS locations
~~~~~~~~~~~~~

bandicoot also supports fine-grained mobility traces, with records of interaction type ``gps``.
GPS records are used only for spatial indicators. We provide tools to:

1. automatically cluster GPS records around stops locations,
2. map the antenna of call and text records to the new stop locations.

See :meth:`~bandicoot.helper.stops.cluster_and_update` and :meth:`~bandicoot.helper.stops.fix_location` for more information.


Splits (days and hours)
-----------------------

* ``split_week=True`` causes records from weekdays and weekends to be considered separately and reported along with the allweek values.
* ``split_day=True`` causes records from daytime and nightime to be considered separately and reported along with the allday values.

(By default, "night" is defined as 7 p.m. to 7 a.m.)

    >>> bc.individual.active_days(B, split_week=True)
    {
        "allweek": {
            "allday": {
                "callandtext": {
                    "mean": 5.4,
                    "std": 2.33238075793812
                }
            }
        },
        "weekday": {
            "allday": {
                "callandtext": {
                    "mean": 4.333333333333333,
                    "std": 1.3333333333333333
                }
            }
        },
        "weekend": {
            "allday": {
                "callandtext": {
                    "mean": 1.875,
                    "std": 0.33071891388307384
                }
            }
        }
    }

This output implies that the user ``B`` is active approximately 1.875 days (out of 2) each weekend while 5.4 days (out of 7) for the all week.