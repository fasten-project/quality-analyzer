"""
Module provides graph query and json query of a call graph in FASTEN json format.
"""


class GraphQuery:

    def __init__(self, cg):
        self._cg = cg

    def get_trans_callees(self, method):
        return []

    def get_trans_callers(self, method):
        return []