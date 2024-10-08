# Form implementation generated from reading ui file '.\ui\live_did_ui.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(519, 443)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.live_did_box = QtWidgets.QWidget(parent=Form)
        self.live_did_box.setObjectName("live_did_box")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.live_did_box)
        self.verticalLayout.setObjectName("verticalLayout")
        self.did_title_lbl = QtWidgets.QLabel(parent=self.live_did_box)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.did_title_lbl.setFont(font)
        self.did_title_lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.did_title_lbl.setObjectName("did_title_lbl")
        self.verticalLayout.addWidget(self.did_title_lbl)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.start_btn = QtWidgets.QPushButton(parent=self.live_did_box)
        self.start_btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.start_btn.setObjectName("start_btn")
        self.horizontalLayout_3.addWidget(self.start_btn)
        self.stop_btn = QtWidgets.QPushButton(parent=self.live_did_box)
        self.stop_btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.stop_btn.setObjectName("stop_btn")
        self.horizontalLayout_3.addWidget(self.stop_btn)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.widget = QtWidgets.QWidget(parent=self.live_did_box)
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(parent=self.widget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.bat_vol_txt = QtWidgets.QLineEdit(parent=self.widget)
        self.bat_vol_txt.setObjectName("bat_vol_txt")
        self.gridLayout.addWidget(self.bat_vol_txt, 1, 1, 1, 1)
        self.es_status_txt = QtWidgets.QLineEdit(parent=self.widget)
        self.es_status_txt.setObjectName("es_status_txt")
        self.gridLayout.addWidget(self.es_status_txt, 2, 1, 1, 1)
        self.ign_status_txt = QtWidgets.QLineEdit(parent=self.widget)
        self.ign_status_txt.setObjectName("ign_status_txt")
        self.gridLayout.addWidget(self.ign_status_txt, 3, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(parent=self.widget)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(parent=self.widget)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 5, 0, 1, 1)
        self.mal_txt = QtWidgets.QLineEdit(parent=self.widget)
        self.mal_txt.setObjectName("mal_txt")
        self.gridLayout.addWidget(self.mal_txt, 5, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(parent=self.widget)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 6, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(parent=self.widget)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.derating_txt = QtWidgets.QLineEdit(parent=self.widget)
        self.derating_txt.setObjectName("derating_txt")
        self.gridLayout.addWidget(self.derating_txt, 6, 1, 1, 1)
        self.emf_rpm_txt = QtWidgets.QLineEdit(parent=self.widget)
        self.emf_rpm_txt.setObjectName("emf_rpm_txt")
        self.gridLayout.addWidget(self.emf_rpm_txt, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(parent=self.widget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.cranking_txt = QtWidgets.QLineEdit(parent=self.widget)
        self.cranking_txt.setObjectName("cranking_txt")
        self.gridLayout.addWidget(self.cranking_txt, 7, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(parent=self.widget)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 7, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(parent=self.widget)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 4, 0, 1, 1)
        self.ign_key_txt = QtWidgets.QLineEdit(parent=self.widget)
        self.ign_key_txt.setObjectName("ign_key_txt")
        self.gridLayout.addWidget(self.ign_key_txt, 4, 1, 1, 1)
        self.horizontalLayout.addWidget(self.widget)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem4 = QtWidgets.QSpacerItem(20, 147, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem4)
        self.verticalLayout_2.addWidget(self.live_did_box)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.did_title_lbl.setText(_translate("Form", "Live Data Identifiers (DID)"))
        self.start_btn.setText(_translate("Form", "Start"))
        self.stop_btn.setText(_translate("Form", "Stop"))
        self.label_2.setText(_translate("Form", "Battery Voltage"))
        self.label_5.setText(_translate("Form", "Ignition Disable Status"))
        self.label_6.setText(_translate("Form", "Malfunction"))
        self.label_7.setText(_translate("Form", "Derating Mode"))
        self.label_4.setText(_translate("Form", "ES Switch Status"))
        self.label.setText(_translate("Form", "Back EMF RPM"))
        self.label_9.setText(_translate("Form", "Cranking Cutoff"))
        self.label_10.setText(_translate("Form", "Ignition Key Status"))
