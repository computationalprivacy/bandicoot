import os
import bandicoot as bc
import unittest
import datetime

class TestRecharges(unittest.TestCase):
    HERE = os.path.dirname(__file__)
    userA = bc.io.read_csv("A", os.path.join(HERE, "samples", "manual"), recharges_path=os.path.join(HERE, "samples", "manual", "recharges"))
    
    def to_datetime(self, datestring):
        return datetime.datetime.strptime(datestring, "%Y-%m-%d")

    def test_combine_same_day_recharges_A(self):
        user = self.userA
        Recharge = bc.core.Recharge
        to_datetime = self.to_datetime

        user_recharges_as_string = str(user.recharges)
        result = bc.helper.tools.combine_same_day_recharges(user.recharges)
        expect = [
            Recharge(to_datetime("2015-1-1"), 23, 1),
            Recharge(to_datetime("2015-1-20"), 3, 2),
            Recharge(to_datetime("2015-1-21"), 2, 1),
            Recharge(to_datetime("2016-12-1"), 3, 4),
            Recharge(to_datetime("2016-12-2"), 1, 1),
            Recharge(to_datetime("2016-12-3"), 3, 4),
            Recharge(to_datetime("2016-12-28"), 2, 2)
            ]
        assert expect == result, "\nexpected: " + str(expect) + "\nfound: " + str(result)
