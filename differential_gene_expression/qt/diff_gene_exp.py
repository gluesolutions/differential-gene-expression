import os
import numpy as np
from qtpy import QtWidgets
from echo.qt import autoconnect_callbacks_to_qt

from glue.core.subset import MultiOrState
from glue.utils.qt import load_ui

from ..state import DiffGeneExpState

__all__ = ['DiffGeneExpDialog']


class DiffGeneExpDialog(QtWidgets.QDialog):

    def __init__(self, collect, default=None, parent=None):

        super(DiffGeneExpDialog, self).__init__(parent=parent)

        self.state = DiffGeneExpState(collect)

        self.ui = load_ui('diff_gene_exp.ui', self,
                          directory=os.path.dirname(__file__))
        self._connections = autoconnect_callbacks_to_qt(self.state, self.ui)

        self._collect = collect

        if default is not None:
            self.state.data = default

        self.ui.button_ok.clicked.connect(self.accept)
        self.ui.button_cancel.clicked.connect(self.reject)

    def _apply(self):
        """
        Calculate differential gene expression between the two selected
        subsets and create a new subset_group with the genes that are
        differentially expressed. Currently this calculation is just
        genes that show 2x expression in one or other subset.
        """
        for subset1 in self.state.subset1.subsets:
            if subset1.data == self.state.data:
                continue
        for subset2 in self.state.subset2.subsets:
            if subset2.data == self.state.data:
                continue
        gene_list = np.unique(self.state.data[self.state.gene_att])

        mask1 = subset1.to_mask()
        mask2 = subset2.to_mask()
        len1 = np.sum(subset1.to_mask())
        len2 = np.sum(subset2.to_mask())
        geneset1 = self.state.data[self.state.gene_att][mask1]
        geneset2 = self.state.data[self.state.gene_att][mask2]

        gene_expression_set1 = self.state.data[self.state.exp_att][mask1]
        gene_expression_set2 = self.state.data[self.state.exp_att][mask2]

        differential_genes = []
        state_list = []
        for gene in gene_list:
            # Sum over gene expression values, divide by length of subset to
            # get the average value for this SPARSE array (missing = 0)
            g1 = np.sum(gene_expression_set1[geneset1 == gene])/len1
            g2 = np.sum(gene_expression_set2[geneset2 == gene])/len2

            if (g1/g2 < 0.5) or (g1/g2 > 2):
                differential_genes.append(gene)
                state_list.append(self.state.data.id[self.state.gene_att] == gene)
        print(differential_genes)
        final_state = MultiOrState(state_list)
        self.state.data_collection.new_subset_group('Differentially expressed genes', final_state)

    @classmethod
    def create_subset(cls, collect, default=None, parent=None):
        self = cls(collect, parent=parent, default=default)
        value = self.exec_()

        if value == QtWidgets.QDialog.Accepted:
            self._apply()
