"""
Test the unweighted and weighted clustering methods from bandicoot.network.
"""

import bandicoot as bc
import unittest
import os
import networkx as nx


class TestClustering(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._dir_changed = False

    def setUp(self):
        if not TestClustering._dir_changed:
            abspath = os.path.abspath(__file__)
            name = abspath.index(os.path.basename(__file__))
            abspath = abspath[:name]
            os.chdir(abspath)
            TestClustering._dir_changed = True

        self.user = bc.io.read_csv("ego", "samples/network", network=True,
                                   describe=False, warnings=False)

    def test_unweighted_clustering_coefficient(self):
        G = nx.Graph()
        G.add_edges_from([
            ('ego', 'A'),
            ('ego', 'B'),
            ('ego', 'F'),
            ('A', 'B'),
            ('B', 'D'),
            ('F', 'H')
        ])
        bc_clustering_coeff = bc.network.clustering_coefficient_unweighted(self.user)
        nx_clustering_coeff = nx.clustering(G, 'ego')

        self.assertAlmostEqual(bc_clustering_coeff, nx_clustering_coeff)

    def test_weighted_clustering_coefficient(self, interaction=None):
        G = nx.Graph()
        G.add_weighted_edges_from([
            ('ego', 'A', 4),
            ('ego', 'B', 4),
            ('ego', 'F', 3),
            ('A', 'B', 2),
            ('F', 'H', 2)
        ])
        bc_clustering_coeff = bc.network.clustering_coefficient_weighted(
            self.user, interaction=interaction)
        nx_clustering_coeff = nx.clustering(G, 'ego', weight='weight')

        self.assertAlmostEqual(bc_clustering_coeff, nx_clustering_coeff)


class TestAssortativity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._dir_changed = False

    def setUp(self):
        if not TestAssortativity._dir_changed:
            abspath = os.path.abspath(__file__)
            name = abspath.index(os.path.basename(__file__))
            abspath = abspath[:name]
            os.chdir(abspath)
            TestAssortativity._dir_changed = True

        self.user = bc.io.read_csv("ego", "samples/network", attributes_path="samples/attributes", network=True, describe=False, warnings=False)

    def test_attributes_assortativity(self):
        self.assertEqual(bc.network.assortativity_attributes(self.user), {
                         'gender': 0.0, 'age': 1.0, 'is_subscriber': 1.0, 'individual_id': 0.0})
