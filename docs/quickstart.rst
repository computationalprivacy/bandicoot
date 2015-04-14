Quick start
===========

Installation
------------
The easiest is just to install it using PyPI::

      pip install bandicoot


Alternatively, you can download it from `here <https://github.com/yvesalexandre/bandicoot/archive/master.zip>`_. Once unzipped you can either import it ``import bandicoot as bc`` or install it::

        python setup.py install


Loading data
------------
bandicoot takes one files per user as standard input and assume that all the user records are in the same directory `records/`.

>>> B = bc.read_csv('my_user', 'records/', 'antennas.csv')

This :meth:`~bandicoot.io.read_csv` will load the records of the user `my_user` from `records/my_user.csv` and the antenna file from `antennas.csv`.


bandicoot's records files are per user and structured as follow.

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

The behavioral indicators can be computed using individual function such as :meth:`~bandicoot.individual.response_rate_text` and :meth:`~bandicoot.spatial.radius_of_gyration` or by using :meth:`~bandicoot.utils.all` which return all the indicators.


  >>> B = bc.tests.sample_user()  # Load a sample user
  >>> bc.utils.all(B)
  OrderedDict({'name': 'sample_user',
    'reporting': OrderedDict({'antennas_path': None,
    'groupby': 'week',
    'start_time': '2012-01-01 00:55:56',
    'end_time': '2014-11-27 00:31:44',
    ...,
    'call_duration': {'call': {'std': {'std': 85.48627089424896, 'mean': 238.69736346741757}, 'mean': {'std': 133.02496554053093, 'mean': 509.85158868177155}}},
    'percent_nocturnal': {'text': {'std': 0.11496930069267557, 'mean': 0.9108055090449453}, 'call': {'std': 0.11006480488825417, 'mean': 0.9244309521895726}},
    ...
    'percent_initiated_interactions': {'call': {'std': 0.22322545460001883, 'mean': 0.4735613383686402}},
    ...
    'radius_of_gyration': {'std': 0.26544350516080456, 'mean': 1.4274315700646447},
    'frequent_locations': {'std': 0.8516613127743775, 'mean': 3.586206896551724}})

:meth:`~bandicoot.utils.all` returns a nested dictionnary with all the indicators (:mod:`bandicoot.individual`, :mod:`bandicoot.spatial`, and :mod:`bandicoot.network`) and some reporting metrics (the name of the user, ``groupby``, the ``version`` of bandicoot used, the number of ``records_missing_locations``, etc)


By default, bandicoot computes the indicators on a **weekly basis** over all the weeks available. It then returns their mean and standard deviation in a nested dictionary. bandicoot consider weeks starting on Monday and ending on Sunday.


The parameter ``groupby=None`` can be used to compute the indicators on the entire timeframe instead.

  >>> bc.utils.all(B, groupby=None)
  OrderedDict({'name': 'sample_user',
    'reporting': OrderedDict({'antennas_path': None,
    'groupby': None,
    'start_time': '2012-01-01 00:55:56',
    'end_time': '2014-11-27 00:31:44',
    ...,
    'call_duration': {'call': {'std': 288.20204388583556, 'mean': 509.09016393442624}},
    'percent_nocturnal': {'text': 0.9065040650406504, 'call': 0.9180327868852459},
    ...
    'percent_initiated_interactions': {'call': 0.4887295081967213},
    ...
    'radius_of_gyration': 1.5368293314872674,
    'frequent_locations': 6})



Note that, while some indicators return a mean and a std per time period (week or the entire period), other return only one value. For example, :meth:`~bandicoot.individual.percent_initiated_interactions` and :meth:`~bandicoot.individual.active_days` return only one value per time period, the percentage of interactions initiated by the user (48.8%) and the number of days he has been active. Other, such as :meth:`~bandicoot.individual.call_duration` will return the mean and std of the value over the time period (509 seconds on average with a standard deviation of 288 seconds). If passed ``summary=extended``, bandicoot will also return the weekly median, min, max, kurtosis, and skewness::

  >>> bc.individual.call_duration(B, groupby=None)
  {'call': {'mean': 509.09016393442624, 'std': 288.20204388583556}}
  >>> bc.individual.call_duration(B, summary='extended', groupby=None)
  {'call': {'kurtosis': 1.7893082779332345,
  'max': 997.0,
  'mean': 509.09016393442624,
  'median': 512.5,
  'min': 7.0,
  'skewness': -0.025855693793360647,
  'std': 288.20204388583556}}

``summary=extended`` can also be passed to :meth:`~bandicoot.utils.all`::

  >>> bc.utils.all(B, summary='extended', flatten=True)
  OrderedDict({'name': 'sample_user',
               ...
               'call_duration__call__std__std': 85.48627089424896,
               'call_duration__call__std__mean': 238.69736346741757,
               'call_duration__call__skewness__std': 0.472380180345131,
               'call_duration__call__skewness__mean': -0.03923002617046248,
               'call_duration__call__min__std': 175.2274765482155,
               'call_duration__call__min__mean': 172.02068965517242,
               'call_duration__call__max__std': 171.05797586147924,
               'call_duration__call__max__mean': 839.1310344827587,
               'call_duration__call__median__std': 169.27744486865464,
               'call_duration__call__median__mean': 511.11034482758623,
               'call_duration__call__kurtosis__std': 0.5453153466587801,
               'call_duration__call__kurtosis__mean': 1.7387436274109511,
               'call_duration__call__mean__std': 133.02496554053093,
               'call_duration__call__mean__mean': 509.85158868177155,
               ...
               })

Exporting indicators
--------------------

Once computed using :meth:`~bandicoot.utils.all`, the indicators of one or seveval users can be easily exported using :meth:`~bandicoot.io.to_csv` and :meth:`~bandicoot.io.to_json`.

   >>> bc.io.to_csv([bc.utils.all(user, groupby=None) for user in [B, other_user]], "bandicoot_indicators.csv")
   Successfully exported 2 objects to bandicoot_indicators.csv

will flatten the dictionaries and write the indicators in a CSV file with a header and one line per user::

    name,reporting__antennas_path,reporting__attributes_path,reporting__version,reporting__grouping_method,reporting__start_time,reporting__end_time,reporting__bins,reporting__has_call,reporting__has_text,reporting__has_home,reporting__percent_records_missing_location,reporting__antennas_missing_locations,reporting__percent_outofnetwork_calls,reporting__percent_outofnetwork_texts,reporting__percent_outofnetwork_contacts,reporting__percent_outofnetwork_call_durations,reporting__nb_records,reporting__ignored_records__all,reporting__ignored_records__interaction,reporting__ignored_records__correspondent_id,reporting__ignored_records__call_duration,reporting__ignored_records__direction,reporting__ignored_records__datetime,active_days__callandtext,number_of_contacts__text,number_of_contacts__call,call_duration__call__std,call_duration__call__mean,percent_nocturnal__text,percent_nocturnal__call,percent_initiated_conversation__callandtext,percent_initiated_interactions__call,response_delay_text__callandtext__std,response_delay_text__callandtext__mean,response_rate_text__callandtext,entropy_of_contacts__text,entropy_of_contacts__call,balance_contacts__text__std,balance_contacts__text__mean,balance_contacts__call__std,balance_contacts__call__mean,interactions_per_contact__text__std,interactions_per_contact__text__mean,interactions_per_contact__call__std,interactions_per_contact__call__mean,interevents_time__text__std,interevents_time__text__mean,interevents_time__call__std,interevents_time__call__mean,number_of_contacts_xpercent_interactions__text,number_of_contacts_xpercent_interactions__call,number_of_contacts_xpercent_durations__call,number_of_interactions__text,number_of_interactions__call,number_of_interaction_in__text,number_of_interaction_in__call,number_of_interaction_out__text,number_of_interaction_out__call,number_of_places,entropy_places,percent_at_home,radius_of_gyration,frequent_locations
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


