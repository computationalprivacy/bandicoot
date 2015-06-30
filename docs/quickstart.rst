Quick start
===========

Installation
------------
The easiest way to install it is using PyPI::

        pip install bandicoot


Alternatively, you can download it from `here <https://github.com/yvesalexandre/bandicoot/archive/master.zip>`_. Once unzipped you can either import it ``import bandicoot as bc`` or install it::

        python setup.py install


Loading data
------------
bandicoot takes one file per user and assume that all user records are in the provided directory `records/`:

>>> B = bc.read_csv('my_user', 'records/', 'antennas.csv')

This :meth:`~bandicoot.io.read_csv` will load records for the user `my_user` from `records/my_user.csv` and will load antennas from the file `antennas.csv`.


.. image:: _static/mini-mockups-01.png


bandicoot uses one record file per user.  Record files are structured as follows:

=========== ========= ================ =================== ============= ===========
interaction direction correspondent_id datetime            call_duration antenna_id
=========== ========= ================ =================== ============= ===========
call        in        8f8ad28de134     2012-05-20 20:30:37 137           13084
call        out       fe01d67aeccd     2012-05-20 20:31:42 542           13084
text        in        c8f538f1ccb2     2012-05-20 21:10:31               13087
=========== ========= ================ =================== ============= ===========


records.csv::

  interaction,direction,correspondent_id,datetime,call_duration,antenna_id
  call,in,8f8ad28de134,2012-05-20 20:30:37,137,13084
  call,out,fe01d67aeccd,2012-05-20 20:31:42,542,13084
  text,in,c8f538f1ccb2,2012-05-20 21:10:31,,13087

while the antennas file contains the latitude and longitude coordinates of the antennas::

  antenna_id,latitude,longitude
  13084,42.360888,-71.0877297
  13087,42.367709,-71.107692

Computing indicators
--------------------

The behavioral indicators can be computed by individual functions such as :meth:`~bandicoot.individual.response_rate_text` and :meth:`~bandicoot.spatial.radius_of_gyration` or by using :meth:`~bandicoot.utils.all` which returns all the indicators defined in :doc:`reference/bandicoot.individual` and :doc:`reference/bandicoot.spatial`.


  >>> B = bc.tests.sample_user()  # Load a sample user
  >>> bc.utils.all(B)
  OrderedDict({'name': 'sample_user',
    'reporting': OrderedDict({'antennas_path': None,
    'groupby': 'week',
    'split_week': false, 
    'split_day': false, 
    'start_time': '2012-01-01 00:55:56',
    'end_time': '2014-11-27 00:31:44',
    ...,
    'call_duration': {
        'allweek': {
            'allday': {
                'call': {
                    'std': {
                        'std': 0.0, 
                        'mean': 202.5
                    }, 
                    'mean: {
                        'std': 0.0, 
                        'mean': 339.5
                    }
                }
            }
        }
    }, ,
    'percent_nocturnal': {
        'allweek': {
            'allday': {
                'text': {
                    'std': 0.0, 
                    'mean': 1.0
                }, 
                'call': {
                    'std': 0.0, 
                    'mean': 1.0
                }
            }
        }
    },
    ...
    'percent_initiated_interactions': {
        'allweek': {
            'allday': {
                'call': {
                    'std': 0.0, 
                    'mean': 0.5
                }
            }
        }
    },
    ...
    'radius_of_gyration': {
        'allweek': {
            'allday': {
                'std': 0.0, 
                'mean': 1.2777217936866738
            }
        }
    },
    'frequent_antennas': {
        'allweek': {
            'allday': {
                'std': 0.0, 
                'mean': 1.0
            }
        }
    }})

:meth:`~bandicoot.utils.all` returns a nested dictionary with all indicators (:doc:`reference/bandicoot.individual`, :doc:`reference/bandicoot.spatial`, and :doc:`reference/bandicoot.network`) and some reporting metrics (the name of the user, ``groupby``, the ``version`` of bandicoot used, the number of ``records_missing_locations``, etc)


By default, bandicoot computes the indicators on a **weekly basis** over all the weeks for which data is available. The indicators from each week are computed, and their averages and standard deviations are returned. bandicoot defines weeks as beginning on a Monday and ending on a Sunday.  The parameter ``groupby=None`` can be used to compute the indicators over the entire timeframe instead. (See below).

.. image:: _static/mini-mockups-02.png


.. code-block:: python

  >>> bc.utils.all(B, groupby=None)
  {
    "name": "sample_user",
    "reporting": {
        "antennas_path": None,
        "attributes_path": None,
        "version": "0.3.0",
        "groupby": None,
        "split_week": false,
        "split_day": false,
        "start_time": "2012-01-01 00:11:23",
        "end_time": "2012-02-27 13:08:45",
        "night_start": "19:00:00",
        "night_end": "07:00:00",
        "weekend": [
            6,
            7
        ],
        "bins": 1,
        "has_call": true,
        "has_text": true,
        "has_home": true,
        "has_network": true,
        "percent_records_missing_location": 0.0,
        "antennas_missing_locations": 0,
        "percent_outofnetwork_calls": 0.21859706362153344,
        "percent_outofnetwork_texts": 0.2474108170310702,
        "percent_outofnetwork_contacts": 0.22448979591836735,
        "percent_outofnetwork_call_durations": 0.22252973202865783,
        "number_of_records": 1482,
        "ignored_records": {
            "all": 0,
            "interaction": 0,
            "correspondent_id": 0,
            "call_duration": 0,
            "direction": 0,
            "datetime": 0
        }
    },
    "active_days": {
        "allweek": {
            "allday": {
                "callandtext": 54
            }
        }
    },
    "number_of_contacts": {
        "allweek": {
            "allday": {
                "text": 47,
                "call": 49
            }
        }
    },
    "call_duration": {
        "allweek": {
            "allday": {
                "call": {
                    "std": 294.98456007533633,
                    "mean": 521.652528548124
                }
            }
        }
    },
    "percent_nocturnal": {
        "allweek": {
            "allday": {
                "text": 0.9332566168009206,
                "call": 0.9135399673735726
            }
        }
    },
    "percent_initiated_conversations": {
        "allweek": {
            "allday": {
                "callandtext": 0.3279901356350185
            }
        }
    },
    "percent_initiated_interactions": {
        "allweek": {
            "allday": {
                "call": 0.34094616639477976
            }
        }
    },
    "response_delay_text": {
        "allweek": {
            "allday": {
                "callandtext": {
                    "std": 1127.6208330177108,
                    "mean": 1771.4166666666667
                }
            }
        }
    },
    "response_rate_text": {
        "allweek": {
            "allday": {
                "callandtext": 0.022018348623853212
            }
        }
    },
    "entropy_of_contacts": {
        "allweek": {
            "allday": {
                "text": 3.6817755703730386,
                "call": 3.6850731160849772
            }
        }
    },
    "balance_of_contacts": {
        "allweek": {
            "allday": {
                "text": {
                    "std": 0.004259371589350954,
                    "mean": 0.006953455916558533
                },
                "call": {
                    "std": 0.0046815612567376215,
                    "mean": 0.006958085028464894
                }
            }
        }
    },
    "interactions_per_contact": {
        "allweek": {
            "allday": {
                "text": {
                    "std": 10.1685211804289,
                    "mean": 18.48936170212766
                },
                "call": {
                    "std": 7.384822960804971,
                    "mean": 12.510204081632653
                }
            }
        }
    },
    "interevent_time": {
        "allweek": {
            "allday": {
                "text": {
                    "std": 19208.587496739972,
                    "mean": 5692.7062211981565
                },
                "call": {
                    "std": 22427.30864417751,
                    "mean": 8123.271241830065
                }
            }
        }
    },
    "percent_pareto_interactions": {
        "allweek": {
            "allday": {
                "text": 0.031070195627157654,
                "call": 0.04404567699836868
            }
        }
    },
    "percent_pareto_durations": {
        "allweek": {
            "allday": {
                "call": 0.04567699836867863
            }
        }
    },
    "number_of_interactions": {
        "allweek": {
            "allday": {
                "text": 869,
                "call": 613
            }
        }
    },
    "number_of_interaction_in": {
        "allweek": {
            "allday": {
                "text": 585,
                "call": 404
            }
        }
    },
    "number_of_interaction_out": {
        "allweek": {
            "allday": {
                "text": 284,
                "call": 209
            }
        }
    },
    "number_of_antennas": {
        "allweek": {
            "allday": 7
        }
    },
    "entropy_of_antennas": {
        "allweek": {
            "allday": 1.9076206619448606
        }
    },
    "percent_at_home": {
        "allweek": {
            "allday": 0.21100917431192662
        }
    },
    "radius_of_gyration": {
        "allweek": {
            "allday": 1.5368985423098422
        }
    },
    "frequent_antennas": {
        "allweek": {
            "allday": 5
        }
    },
    "churn_rate": {
        "std": 0.1077531155950712,
        "mean": 0.11880956290008478
    }
}


Note that, while some indicators return a mean and a std per time period (e.g., each week), others return only one value. For example, :meth:`~bandicoot.individual.percent_initiated_interactions` and :meth:`~bandicoot.individual.active_days` return only one value per time period, the percentage of interactions initiated by the user (48.8%) and the number of days he has been active. Others, such as :meth:`~bandicoot.individual.call_duration` will return the mean and std of the value over the time period (509 seconds on average with a standard deviation of 288 seconds). If passed ``summary=extended``, bandicoot will also return the median, min, max, kurtosis, and skewness (among the values from each time period)::

  >>> bc.individual.call_duration(B, groupby=None)
  {'allweek': {'allday': {'call': {'mean': 521.652528548124,
    'std': 294.98456007533633}}}}
  >>> bc.individual.call_duration(B, summary='extended', groupby=None)
  {'allweek': {'allday': {'call': {'kurtosis': 1.7522977930497714,
    'max': 1000.0,
    'mean': 521.652528548124,
    'median': 532.0,
    'min': 1.0,
    'skewness': -0.07157493958994408,
    'std': 294.98456007533633}}}}

``summary=extended`` can also be passed to :meth:`~bandicoot.utils.all`::

    >>> bc.utils.all(B, summary='extended', flatten=True)
    {
        "name": "sample_user",
        ...
        "call_duration__allweek__allday__call__std__std": 14.111679981502093,
        "call_duration__allweek__allday__call__std__mean": 291.9860252840037,
        "call_duration__allweek__allday__call__skewness__std": 0.2327813923167136,
        "call_duration__allweek__allday__call__skewness__mean": -0.14905391966308995,
        "call_duration__allweek__allday__call__min__std": 36.765336935760565,
        "call_duration__allweek__allday__call__min__mean": 30.9,
        ...
    })
 

Exporting indicators
--------------------

Once computed using :meth:`~bandicoot.utils.all`, the indicators of one or seveval users can be easily exported using :meth:`~bandicoot.io.to_csv` and :meth:`~bandicoot.io.to_json`.

   >>> bc.io.to_csv([bc.utils.all(user, groupby=None) for user in [B, other_user]], "bandicoot_indicators.csv")
   Successfully exported 2 objects to bandicoot_indicators.csv

will flatten the dictionaries and write the indicators in a CSV file with a header and one line per user::

    name,reporting__antennas_path,reporting__attributes_path,reporting__version,reporting__grouping_method,reporting__start_time,reporting__end_time,reporting__bins,reporting__has_call,reporting__has_text,reporting__has_home,reporting__percent_records_missing_location,reporting__antennas_missing_locations,reporting__percent_outofnetwork_calls,reporting__percent_outofnetwork_texts,reporting__percent_outofnetwork_contacts,reporting__percent_outofnetwork_call_durations,reporting__nb_records,reporting__ignored_records__all,reporting__ignored_records__interaction,reporting__ignored_records__correspondent_id,reporting__ignored_records__call_duration,reporting__ignored_records__direction,reporting__ignored_records__datetime,active_days__callandtext,number_of_contacts__text,number_of_contacts__call,call_duration__call__std,call_duration__call__mean,percent_nocturnal__text,percent_nocturnal__call,percent_initiated_conversations__callandtext,percent_initiated_interactions__call,response_delay_text__callandtext__std,response_delay_text__callandtext__mean,response_rate_text__callandtext,entropy_of_contacts__text,entropy_of_contacts__call,balance_of_contacts__text__std,balance_of_contacts__text__mean,balance_of_contacts__call__std,balance_of_contacts__call__mean,interactions_per_contact__text__std,interactions_per_contact__text__mean,interactions_per_contact__call__std,interactions_per_contact__call__mean,interevent_time__text__std,interevent_time__text__mean,interevent_time__call__std,interevent_time__call__mean,percent_pareto_interactions__text,percent_pareto_interactions__call,percent_pareto_durations__call,number_of_interactions__text,number_of_interactions__call,number_of_interaction_in__text,number_of_interaction_in__call,number_of_interaction_out__text,number_of_interaction_out__call,number_of_antennas,entropy_of_antennas,percent_at_home,radius_of_gyration,frequent_antennas
    sample_user,,,0.2.3,,2012-01-01 00:55:56,2014-11-27 00:31:44,1,True,True,True,0.0,0,0,0,0,0,1960,0,0,0,0,0,0,800,150,149,288.20204,509.09016,0.9065,0.91803,0.50813,0.48873,,,0.0,4.92907,4.9139,0.00175,0.00339,0.00196,0.00328,2.5961,6.56,2.73048,6.55034,110028.24,88312.70905,107264.44395,88859.44308,99,96,94,984,976,484,499,500,477,7,1.94257,0.15508,1.53683,6
    other_user,...


Full pipeline
-------------

The following code will load all the users in one directory, compute the indicators, and export them to a csv file::

   >>> import bandicoot as bc
   >>> import glob, os
   
   >>> path_dir = 'users/'
   >>> antenna_file = 'antennas.csv'
   
   >>> indicators = []
   >>> for f in glob.glob(records_path + '*.csv'):
   >>>     user_id = os.path.basename(f)[:-4]

   >>>     try:
   >>>         B = bc.read_csv(user_id, records_path, antenna_file, describe=False)
   >>>         metrics_dict = bc.utils.all(B)
   >>>     except Exception as e:
   >>>         metrics_dic = {'name': user_id, 'error': True}

   >>>     indicators.append(metrics_dict)

   >>> bc.io.to_csv(indicators, 'bandicoot_indicators_full.csv')

The full pipeline file is available `here <https://github.com/yvesalexandre/bandicoot/blob/master/sample_code/full_pipeline.py>`_. A parallel version using `MultiProcessing <https://docs.python.org/2/library/multiprocessing.html>`_ is available `here <https://github.com/yvesalexandre/bandicoot/blob/master/sample_code/full_pipeline_mp.py>`_.


