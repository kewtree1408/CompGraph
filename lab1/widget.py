# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget.ui'
#
# Created: Tue Sep 20 10:42:56 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Widget(object):
    def setupUi(self, Widget):
        Widget.setObjectName("Widget")
        Widget.resize(600, 400)
        self.horizontalLayout = QtGui.QHBoxLayout(Widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.label_4 = QtGui.QLabel(Widget)
        self.label_4.setText("")
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_4)
        self.checkBox = QtGui.QCheckBox(Widget)
        self.checkBox.setObjectName("checkBox")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.checkBox)
        self.checkBox_2 = QtGui.QCheckBox(Widget)
        self.checkBox_2.setObjectName("checkBox_2")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.checkBox_2)
        self.horizontalLayout.addLayout(self.formLayout)
        spacerItem = QtGui.QSpacerItem(468, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.retranslateUi(Widget)
        QtCore.QMetaObject.connectSlotsByName(Widget)

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QtGui.QApplication.translate("Widget", "Torus", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("Widget", "Perspective", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_2.setText(QtGui.QApplication.translate("Widget", "Camera (5,3,4)", None, QtGui.QApplication.UnicodeUTF8))

