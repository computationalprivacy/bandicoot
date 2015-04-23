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

        self.user = bc.io.read_csv("ego", "samples/network", describe=False)

    def test_unweighted_clustering_coefficient(self):
        G = nx.Graph()
        G.add_edges_from([('ego','A'),('ego','F'),('ego','H'),('ego','B'),('F','H')])
        bc_clustering_coeff = bc.network.unweighted_clustering_coefficient(self.user)
        nx_clustering_coeff = nx.clustering(G, 'ego')

        self.assertEqual(bc_clustering_coeff, nx_clustering_coeff)


    def test_weighted_clustering_coefficient(self, interaction=None):
        G = nx.Graph()
        G.add_weighted_edges_from([('ego','A', 4),('ego','F', 3),('ego','H', 3),('ego','B', 4),('F','H', 2)])
        bc_clustering_coeff = bc.network.weighted_clustering_coefficient(self.user, interaction=interaction)
        nx_clustering_coeff = nx.clustering(G, 'ego', weight='weight')

        self.assertEqual(bc_clustering_coeff, nx_clustering_coeff)




   