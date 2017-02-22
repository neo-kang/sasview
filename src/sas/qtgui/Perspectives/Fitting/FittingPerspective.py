import sys
import json
import  os
from collections import defaultdict

from PyQt4 import QtGui
from PyQt4 import QtCore

from UI.FittingUI import Ui_FittingUI

from sasmodels import generate
from sasmodels import modelinfo
from sas.sasgui.guiframe.CategoryInstaller import CategoryInstaller

class FittingWindow(QtGui.QDialog, Ui_FittingUI):
    """
    Main window for selecting form and structure factor models
    """
    def __init__(self, manager=None, parent=None):
        """

        :param manager:
        :param parent:
        :return:
        """
        super(FittingWindow, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("Fitting")
        self._model_model = QtGui.QStandardItemModel()
        self._poly_model = QtGui.QStandardItemModel()
        self.tableView.setModel(self._model_model)

        self._readCategoryInfo()

        structure_factor_list = self.master_category_dict.pop('Structure Factor')
        for (structure_factor, enabled) in structure_factor_list:
            self.cbStructureFactor.addItem(structure_factor)
        self.cbStructureFactor.currentIndexChanged.connect(self.selectStructureFactor)

        category_list = sorted(self.master_category_dict.keys())
        self.cbCategory.addItems(category_list)
        self.cbCategory.currentIndexChanged.connect(self.selectCategory)

        category = self.cbCategory.currentText()
        model_list = self.master_category_dict[str(category)]
        for (model, enabled) in model_list:
            self.cbModel.addItem(model)
        self.cbModel.currentIndexChanged.connect(self.selectModel)

        self.pushButton.setEnabled(False)
        self.chkPolydispersity.setEnabled(False)
        self.chkSmearing.setEnabled(False)

        self.lblMinRangeDef.setText("---")
        self.lblMaxRangeDef.setText("---")
        self.lblChi2Value.setText("---")

        #self.setTableProperties(self.tableView)

        self.tableView_2.setModel(self._poly_model)
        self.setPolyModel()
        self.setTableProperties(self.tableView_2)

        for row in range(2):
            c = QtGui.QComboBox()
            c.addItems(['rectangle','array','lognormal','gaussian','schulz',])
            i = self.tableView_2.model().index(row,6)
            self.tableView_2.setIndexWidget(i,c)

    def selectCategory(self):
        """
        Select Category from list
        :return:
        """
        self.cbModel.clear()
        category = self.cbCategory.currentText()
        model_list = self.master_category_dict[str(category)]
        for (model, enabled) in model_list:
            self.cbModel.addItem(model)

    def selectModel(self):
        """
        Select Model from list
        :return:
        """
        model = self.cbModel.currentText()
        self.setModelModel(model)

    def selectStructureFactor(self):
        """
        Select Structure Factor from list
        :param:
        :return:
        """


    def _readCategoryInfo(self):
        """
        Reads the categories in from file
        """
        self.master_category_dict = defaultdict(list)
        self.by_model_dict = defaultdict(list)
        self.model_enabled_dict = defaultdict(bool)

        try:
            categorization_file = CategoryInstaller.get_user_file()
            if not os.path.isfile(categorization_file):
                categorization_file = CategoryInstaller.get_default_file()
            cat_file = open(categorization_file, 'rb')
            self.master_category_dict = json.load(cat_file)
            self._regenerate_model_dict()
            cat_file.close()
        except IOError:
            raise
            print 'Problem reading in category file.'
            print 'We even looked for it, made sure it was there.'
            print 'An existential crisis if there ever was one.'

    def _regenerate_model_dict(self):
        """
        regenerates self.by_model_dict which has each model name as the
        key and the list of categories belonging to that model
        along with the enabled mapping
        """
        self.by_model_dict = defaultdict(list)
        for category in self.master_category_dict:
            for (model, enabled) in self.master_category_dict[category]:
                self.by_model_dict[model].append(category)
                self.model_enabled_dict[model] = enabled

        
    def setModelModel(self, model_name):
        """
        Setting model parameters into table based on selected
        :param model_name:
        :return:
        """
        # Crete/overwrite model items
        self._model_model.clear()
        model_name = str(model_name)
        kernel_module = generate.load_kernel_module(model_name)
        parameters = modelinfo.make_parameter_table(getattr(kernel_module, 'parameters', []))

        #TODO: scaale and background are implicit in sasmodels and needs to be added
        item1 = QtGui.QStandardItem('scale')
        item1.setCheckable(True)
        item2 = QtGui.QStandardItem('1.0')
        item3 = QtGui.QStandardItem('0.0')
        item4 = QtGui.QStandardItem('inf')
        item5 = QtGui.QStandardItem('')
        self._model_model.appendRow([item1, item2, item3, item4, item5])

        item1 = QtGui.QStandardItem('background')
        item1.setCheckable(True)
        item2 = QtGui.QStandardItem('0.001')
        item3 = QtGui.QStandardItem('-inf')
        item4 = QtGui.QStandardItem('inf')
        item5 = QtGui.QStandardItem('1/cm')
        self._model_model.appendRow([item1, item2, item3, item4, item5])

        #TODO: iq_parameters are used here. If orientation paramateres or magnetic are needed kernel_paramters should be used instead
        #For orientation and magentic parameters param.type needs to be checked
        for param in parameters.iq_parameters:
            item1 = QtGui.QStandardItem(param.name)
            item1.setCheckable(True)
            item2 = QtGui.QStandardItem(str(param.default))
            item3 = QtGui.QStandardItem(str(param.limits[0]))
            item4 = QtGui.QStandardItem(str(param.limits[1]))
            item5 = QtGui.QStandardItem(param.units)
            self._model_model.appendRow([item1, item2, item3, item4, item5])

        self._model_model.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant("Parameter"))
        self._model_model.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant("Value"))
        self._model_model.setHeaderData(2, QtCore.Qt.Horizontal, QtCore.QVariant("Min"))
        self._model_model.setHeaderData(3, QtCore.Qt.Horizontal, QtCore.QVariant("Max"))
        self._model_model.setHeaderData(4, QtCore.Qt.Horizontal, QtCore.QVariant("[Units]"))

    def setTableProperties(self, table):
        """
        Setting table properties
        :param table:
        :return:
        """
        table.setStyleSheet("background-image: url(model.png);")

        # Table properties
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding)
        table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        # Header
        header = table.horizontalHeader()
        header.setResizeMode(QtGui.QHeaderView.Stretch)
        header.setStretchLastSection(True)

    def setPolyModel(self):
        """
        Set polydispersity values
        :return:
        """
        item1 = QtGui.QStandardItem("Distribution of radius")
        item1.setCheckable(True)
        item2 = QtGui.QStandardItem("0")
        item3 = QtGui.QStandardItem("")
        item4 = QtGui.QStandardItem("")
        item5 = QtGui.QStandardItem("35")
        item6 = QtGui.QStandardItem("3")
        item7 = QtGui.QStandardItem("")
        self._poly_model.appendRow([item1, item2, item3, item4, item5, item6, item7])
        item1 = QtGui.QStandardItem("Distribution of thickness")
        item1.setCheckable(True)
        item2 = QtGui.QStandardItem("0")
        item3 = QtGui.QStandardItem("")
        item4 = QtGui.QStandardItem("")
        item5 = QtGui.QStandardItem("35")
        item6 = QtGui.QStandardItem("3")
        item7 = QtGui.QStandardItem("")
        self._poly_model.appendRow([item1, item2, item3, item4, item5, item6, item7])

        self._poly_model.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant("Parameter"))
        self._poly_model.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant("PD[ratio]"))
        self._poly_model.setHeaderData(2, QtCore.Qt.Horizontal, QtCore.QVariant("Min"))
        self._poly_model.setHeaderData(3, QtCore.Qt.Horizontal, QtCore.QVariant("Max"))
        self._poly_model.setHeaderData(4, QtCore.Qt.Horizontal, QtCore.QVariant("Npts"))
        self._poly_model.setHeaderData(5, QtCore.Qt.Horizontal, QtCore.QVariant("Nsigs"))
        self._poly_model.setHeaderData(6, QtCore.Qt.Horizontal, QtCore.QVariant("Function"))

        self.tableView_2.resizeColumnsToContents()
        header = self.tableView_2.horizontalHeader()
        header.ResizeMode(QtGui.QHeaderView.Stretch)
        header.setStretchLastSection(True)


if __name__ == "__main__":
    app = QtGui.QApplication([])
    dlg = FittingWindow()
    dlg.show()
    sys.exit(app.exec_())