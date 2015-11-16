import os
import bandicoot as bc
import unittest

class TestRecharges(unittest.TestCase):
    HERE = os.path.dirname(__file__)
    user = bc.io.read_csv("A", os.path.join(HERE, "samples", "manual"), recharges_path=os.path.join(HERE, "samples", "manual", "recharges"))

    def test_recharge_amount(self):
        result = bc.individual.recharge_amount(self.user, groupby="year")
        assert result['mean']['mean'] == 4.625, "mean mean"
        assert result['mean']['std'] == 2.375, "mean std"
        assert abs(result['std']['mean'] - 2.67842437) < 0.00001, "std mean"
        assert abs(result['std']['std'] - 1.84926818) < 0.00001, "std std"

    def test_recharge_interevent(self):
        result = bc.individual.recharge_interevent(self.user, groupby="year")
        seconds_per_day = 60 * 60 * 24
        s = seconds_per_day
        assert abs(result['mean']['mean'] - s * 7.8333333333333) < 1
        assert abs(result['mean']['std'] - s * 1.1666666666666) < 1
        assert abs(result['std']['mean'] - s * 10.0221212) < 1
        assert abs(result['std']['std'] - s * 1.2915873) < 1

    def test_recharges_percent_below_all(self):
        result = bc.individual.recharges_percent_below(self.user, groupby="year", amount=13)
        assert result['mean'] ==  1.0
        assert result['std'] == 0

    def test_recharges_percent_below_annual(self):
        result = bc.individual.recharges_percent_below(self.user, groupby="year", amount=2)
        assert abs(result['mean'] - .125) < .000001
        assert abs(result['std'] - .125) < .000001
    
    def test_recharges_percent_below_day(self):
        result = bc.individual.recharges_percent_below(self.user, groupby="day", amount=12)
        assert abs(result['mean'] - .92857142) < .000001
        assert abs(result['std'] - .17496355) < .000001

    def test_recharges_count_day(self):
        result = bc.individual.recharges_count(self.user, groupby="day")
        assert abs(result['mean'] - 1.14285714) < .000001
        assert abs(result['std'] - .3499271) < .000001

    def test_recharges_count_year(self):
        result = bc.individual.recharges_count(self.user, groupby="year")
        assert abs(result['mean'] - 4) < .000001
        assert abs(result['std'] - 0.0) < .000001

    def test_recharges_total_grouping_none(self):
        result = bc.individual.recharges_total(self.user, groupby=None)
        assert result['mean'] == 37

    def test_recharges_total_grouping_year(self):
        result = bc.individual.recharges_total(self.user, groupby="year")
        assert result['mean'] == 18.5
        assert abs(result['std'] - 9.5) < .000001
 
    def test_recharges_percent_spent_within(self):
        result = bc.individual.recharge_percent_spent_within(self.user, days=1, groupby="year")
        assert abs(.37525737 - result['mean']) < .000001
        assert abs(.21331405 - result['std']) < .000001
