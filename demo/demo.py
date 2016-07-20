"""
To try bandicoot without installing it, add the bandicoot toolbox
to your Python path with:

>>> import sys
>>> sys.path.append("../")
"""

from bandicoot.helper.group import grouping
import bandicoot as bc


# Loading a User
U = bc.read_csv('ego', 'data/', 'data/antennas.csv')


#######################
# Export visulization #
#######################

bc.visualization.export(U, 'my-viz-path')


#########################################
# Run individual and spatial indicators #
#########################################

bc.individual.percent_initiated_conversations(U)
bc.spatial.number_of_antennas(U)
bc.spatial.radius_of_gyration(U)


######################################
# Group indicators by weeks or month #
######################################

# The groupby keyword controls the aggregation:
# - groupby='week' to divide by week (by default),
# - groupby='month' to divide by month,
# - groupby=None to aggregate all values.

bc.individual.active_days(U, groupby='week')
bc.individual.active_days(U, groupby='month')
bc.individual.active_days(U, groupby=None)  # No grouping


################################
# Returning extended summaries #
################################

# The summary keyword can take three values:
# - summary='default' to return mean and standard deviation,
# - summary='extended' for the second type of indicators, to return mean, std,
#   median, skewness and std of the distribution,
# - summary=None to return the full distribution.

bc.individual.call_duration(U)
bc.individual.call_duration(U, summary='extended')
bc.individual.call_duration(U, summary=None)

############################
# Splitting days and weeks #
############################

# split_week divide records by 'all week', 'weekday', and 'weekend'.
# split_day divide records by 'all day', 'day', and 'night'.

bc.individual.active_days(U, split_week=True, split_day=True)

########################
# Exporting indicators #
########################

# The function bc.utils.all computes automatically all indicators for a single
# user. You can use the same keywords to group by week/month/all time range, or
# return extended statistics.

features = bc.utils.all(U, groupby=None)

bc.to_csv(features, 'demo_export_user.csv')
bc.to_json(features, 'demo_export_user.json')

#######################
# Extending bandicoot #
#######################

# You can easily develop your indicator using the @grouping decorator. You only
# need to write a function taking as input a list of records and returning an
# integer or a list of integers (for a distribution). The @grouping decorator
# wraps the function and call it for each group of weeks.


@grouping(interaction='call')
def shortest_call(records):
    in_durations = (r.call_duration for r in records)
    return min(in_durations)

shortest_call(U)
shortest_call(U, split_day=True)
