import os
import numpy as np

from glue.config import menubar_plugin
from glue.core.subset import combine_multiple, MultiOrState
from qtpy import QtWidgets
from glue.core.state_objects import State
from echo import CallbackProperty, SelectionCallbackProperty
from glue.utils.qt import load_ui
from glue.core.data_combo_helper import DataCollectionComboHelper, ComponentIDComboHelper, ComboHelper
from echo.qt import autoconnect_callbacks_to_qt

__all__ = ['DiffGeneExpDialog']


class DiffGeneExpState(State):

    data = SelectionCallbackProperty()
    s1_att = SelectionCallbackProperty()
    s2_att = SelectionCallbackProperty()
    att = SelectionCallbackProperty()

    def __init__(self, data_collection):

        super(DiffGeneExpState, self).__init__()

        self.data_collection = data_collection
        self.data_helper = DataCollectionComboHelper(self, 'data', data_collection)
        self.att_helper = ComponentIDComboHelper(self, 'att')

        self.subset1_helper = ComboHelper(self, 's1_att')
        self.subset2_helper = ComboHelper(self,'s2_att')

        def display_func_label(subset_group):
            return subset_group.label

        self.add_callback('data', self._on_data_change)
        self._on_data_change()

        self.subset1_helper.choices = data_collection.subset_groups
        self.subset2_helper.choices = data_collection.subset_groups
        
        self.subset1_helper.display = display_func_label
        self.subset2_helper.display = display_func_label

    def _on_data_change(self, *args, **kwargs):
        self.att_helper.set_multiple_data([] if self.data is None else [self.data])


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
        Actually make the subset from the differential gene expression calculation
        """
        for subset1 in self.state.s1_att.subsets:
            if subset1.data == self.state.data:
                continue
        for subset2 in self.state.s2_att.subsets:
            if subset2.data == self.state.data:
                continue
        gene_list = np.unique(self.state.data['gene'])
        
        mask1 = subset1.to_mask()
        mask2 = subset2.to_mask()
        len1 = np.sum(subset1.to_mask())
        len2 = np.sum(subset2.to_mask())
        geneset1 = self.state.data['gene'][mask1]
        geneset2 = self.state.data['gene'][mask2]

        gene_expression_set1 = self.state.data[self.state.att][mask1]
        gene_expression_set2 = self.state.data[self.state.att][mask2]
        
        differential_genes = []
        state_list = []
        for gene in gene_list:
            # Sum over gene expression values, divide by length of subset to get
            # the average value for this SPARSE array
            g1 = np.sum(gene_expression_set1[geneset1 == gene])/len1
            g2 = np.sum(gene_expression_set2[geneset2 == gene])/len2
            
            if (g1/g2 < 0.5) or (g1/g2 > 2):
                differential_genes.append(gene)
                state_list.append(self.state.data.id['gene'] == gene)
        print(differential_genes)
        final_state = MultiOrState(state_list)
        self.state.data_collection.new_subset_group('Diff Gene', final_state)

    @classmethod
    def create_subset(cls, collect, default=None, parent=None):
        self = cls(collect, parent=parent, default=default)
        value = self.exec_()

        if value == QtWidgets.QDialog.Accepted:
            self._apply()



@menubar_plugin("Differential Gene Expression")
def diff_gene_exp_plugin(session, data_collection):
    DiffGeneExpDialog.create_subset(data_collection,
        default=None, parent=None)
    return
