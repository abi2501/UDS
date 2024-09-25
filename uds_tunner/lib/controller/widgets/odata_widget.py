import time

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QWidget, QTableView, QHeaderView
from lib.controller.views.pages.odata_ui import Ui_Form

class OdataUI(QWidget):
    stack_index = 1

    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.model = QStandardItemModel()
        self.ui.rolling_trace_radio.setChecked(True)

        self.ui.rolling_trace_radio.clicked.connect(lambda state: self.show_trace(True))
        self.ui.fixed_trace_radio.clicked.connect(lambda state: self.show_trace(False))

        self.ui.fixed_trace_wid.setVisible(False)
        self.ui.tableView_2.setVisible(False)

        self.ui.rolling_trace_radio.setChecked(True)
        self.ui.tableView_2.setVisible(True)
        self.ui.tableView_2.setModel(self.model)
        self.ui.tableView_2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ui.tableView_2.setAlternatingRowColors(True)
        self.ui.tableView_2.setStyleSheet("QTableWidget::item {border: 0px; padding: 5px; font-weight:bold}")
        self.show_trace(True)

    def process_odata(self, data):

        status_data = '{:08b}'.format(data[0])
        status_data = status_data[::-1]

        derating_start = status_data[2]
        thermal_shutdown = status_data[3]
        idss_status = status_data[4]
        es_status = status_data[5]
        isg_disable = status_data[6]
        isg_malfn = status_data[7]

        rpm = (data[1] * 256) + data[2]

        bat = ((data[3] * 256) + data[4]) / 1000
        bat = round(bat, 2)
        counter = data[6] >> 4
        crc = data[7]

        if self.ui.rolling_trace_radio.isChecked():
            item = [QStandardItem(str(derating_start)), QStandardItem(str(thermal_shutdown)), QStandardItem(str(idss_status)),
                    QStandardItem(str(es_status)), QStandardItem(str(isg_disable)),QStandardItem(str(isg_malfn)),
                    QStandardItem(str(rpm)),QStandardItem(str(bat)),QStandardItem(str(counter)), QStandardItem(str(crc))]
            [item.setTextAlignment(Qt.AlignmentFlag.AlignCenter) for item in item]
            self.model.appendRow(item)
            self.set_table_current_row()

        elif self.ui.fixed_trace_radio.isChecked():
            self.model.clear()
            self.set_rounded_label(self.ui.derating_start_lbl, derating_start)
            self.set_rounded_label(self.ui.thermal_sht_lbl, thermal_shutdown)
            self.set_rounded_label(self.ui.idss_status_lbl, idss_status)
            self.set_rounded_label(self.ui.es_status_lbl, es_status)
            self.set_rounded_label(self.ui.isg_disable_lbl, isg_disable)
            self.set_rounded_label(self.ui.isg_malfunction, isg_malfn)
            self.ui.rpm_txt.setText(str(rpm))
            self.ui.battery_volt_txt.setText(str(bat))
            self.ui.counter_txt.setText(str(counter))
            self.ui.crc_txt.setText(str(crc))

        # time.sleep(0.01)
    def show_trace(self, state):
        if state:
            self.model.clear()
            self.model.setHorizontalHeaderLabels(
                ["Derating\nStart", "Thermal\nShutdown", "IDSS\nStatus", "ES\nStatus", "IGN\nDisable",
                 "ISG\nMalfunction", "RPM", "Battery\nVoltage", "Counter", "CRC-8"])
            self.ui.tableView_2.setVisible(True)
            self.ui.fixed_trace_wid.setVisible(False)
        else:
            self.ui.tableView_2.setVisible(False)
            self.ui.fixed_trace_wid.setVisible(True)

    def set_table_current_row(self):
        row_count = self.model.rowCount() - 1
        idx = self.model.index(row_count, 0)

        self.ui.tableView_2.setCurrentIndex(idx)
        self.ui.tableView_2.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.ui.tableView_2.scrollTo(idx)

    def set_rounded_label(self, lbl, value):
        value = value if value else 0
        state = True if int(value) == 1 else False

        if state:
            lbl.setStyleSheet('background-color: green; border-radius:10px; border:1px solid #FFF; font-size: 10px;')
            # lbl.setStyleSheet('background-color: green; border-radius:10px; border:1px solid #CCC; font-size: 18px;')
        else:
            lbl.setStyleSheet('background-color: #DCDCDC; border-radius:10px; border:1px solid #CCC; font-size: 10px;')
            # lbl.setStyleSheet('background-color: red; border-radius:10px; border:1px solid #CCC; font-size: 18px;')

        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setFixedSize(20, 20)