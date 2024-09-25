from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QHeaderView, QTableView, QGraphicsOpacityEffect

from lib.controller import DTC_COUNT_RESPONSE, DTC_SINGLE_ERROR_RESPONSE, DTC_ERROR_CODE_DICT, DTC_ACTIVE_STATE_DICT, \
    DTC_STATE_PRIORITY_DICT, DTC_STATE_GROUP_DICT, DTC_MULTI_ERROR_RESPONSE_IDS, DTC_START_BYTE_MULTI_ERROR, \
    DTC_WRITE_RESPONSE, DTC_ERROR_COUNT_REQUEST, DTC_ERROR_REQUEST, DTC_ERASE_REQUEST, DTC_ERASE_RESPONSE
from lib.controller.util.helper import divide_chunks
from lib.controller.views.pages.dtc_ui import Ui_Form


class DtcUI(QWidget):

    stack_index = 4
    dtc_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.dtc_error_list = []
        self.dtc_error_length = None

        self.ui.read_no_dtc_btn.clicked.connect(self.read_no_of_dtc)
        self.ui.read_single_dtc_btn.clicked.connect(self.read_dtc_error_code)
        self.ui.erase_dtc_btn.clicked.connect(self.erase_dtc)

        self.ui.dtc_error_tbl.setColumnCount(4)
        self.ui.dtc_error_tbl.setHorizontalHeaderLabels(["Fault", "Priority", "Group", "Status"])
        self.ui.dtc_error_tbl.resizeRowsToContents()
        self.ui.dtc_error_tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ui.dtc_error_tbl.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.ui.dtc_error_tbl.setAlternatingRowColors(True)

        self.ui.dtc_error_tbl.setMinimumWidth(self.width() + 200)

    def erase_dtc(self):
        print("Erase dtc")
        self.dtc_signal.emit(DTC_ERASE_REQUEST)

    def read_no_of_dtc(self):
        # self.dtc_mode = True
        print("Send msg for no. of dtc")
        # count_dtc_pckt = [0x03, 0x19, 0x01, 0, 0, 0, 0, 0]
        self.dtc_signal.emit(DTC_ERROR_COUNT_REQUEST)

    def read_dtc_error_code(self):
        self.dtc_error_list.clear()
        self.dtc_signal.emit(DTC_ERROR_REQUEST)

    def process_dtc_data(self, data):
        print("process dtc data ", data)

        if data[:5] == DTC_COUNT_RESPONSE:
            print("count ", str(data[6]))
            self.ui.dtc_no_txt.setText(str(data[6]))
        elif data[:4] == DTC_SINGLE_ERROR_RESPONSE:
            dlist = data[4:7]
            dlist.append(data[7])
            self.set_dtc_error_table([dlist])

        elif data[0] == DTC_START_BYTE_MULTI_ERROR:
            print("Multi error")

            self.dtc_error_length = data[1] - 3
            print("data len ", self.dtc_error_length)
            self.dtc_error_list.extend(data[5:])
            print("error code container list first", self.dtc_error_list)
            self.dtc_signal.emit(DTC_WRITE_RESPONSE)
        elif data[0] in DTC_MULTI_ERROR_RESPONSE_IDS:
            print("data for multi error")
            print(data[1:])
            for ele in data[1:]:
                if len(self.dtc_error_list) < self.dtc_error_length:
                    # dlist = [ele for ele in data[1:]]
                    self.dtc_error_list.append(ele)
                else:
                    print(self.dtc_error_length, "-------", len(self.dtc_error_list))

                    multi_error_list = list(divide_chunks(self.dtc_error_list, 4))
                    multi_error_list = [ele for ele in multi_error_list if len(ele) == 4]

                    self.set_dtc_error_table(multi_error_list)
        elif data == DTC_ERASE_RESPONSE:
            print("Erase completed")
            self.ui.erase_dtc_msg_lbl.setText("DTC Erase Completed !!!")
            # self.ui.erase_dtc_msg_lbl.setStyleSheet("""color:green;""")
            self.unfade(self.ui.erase_dtc_msg_lbl, 1000)
            self.fade(self.ui.erase_dtc_msg_lbl, 1000)

    def set_dtc_error_table(self, dlist):

        self.ui.dtc_error_tbl.setRowCount(len(dlist))

        for idx, ele in enumerate(dlist):
            print("dtc ele leng", len(ele))
            if len(ele) == 4:
                print("idx , ele ", idx, ele)
                err_msg = [i for i in DTC_ERROR_CODE_DICT if DTC_ERROR_CODE_DICT[i] == ele[:3]]

                state, priority, group = self.get_status_mask(ele[3])

                print(self.get_status_mask(ele[3]))
                self.ui.dtc_error_tbl.setItem(idx, 0, QTableWidgetItem(err_msg[0]))
                self.ui.dtc_error_tbl.setItem(idx, 1, QTableWidgetItem(priority))
                self.ui.dtc_error_tbl.setItem(idx, 2, QTableWidgetItem(group))
                self.ui.dtc_error_tbl.setItem(idx, 3, QTableWidgetItem(state))

    def get_status_mask(self, data):
        msg = ''
        print(data)
        print('{:08b}'.format(data))

        status_mask = '{:08b}'.format(data)

        print("STATE, Priority, Group")
        print(status_mask[-2:], status_mask[-5:-2], status_mask[:3])

        dtc_state = DTC_ACTIVE_STATE_DICT.get(status_mask[-2:])
        dtc_priority = DTC_STATE_PRIORITY_DICT.get(status_mask[-5:-2])
        dtc_group = DTC_STATE_GROUP_DICT.get(status_mask[:3])

        return dtc_state.upper(), dtc_priority.upper(), dtc_group.upper()


    def get_dtc_error_message(self, dlist):
        items = DTC_ERROR_CODE_DICT.items()
        print(items)
        res = tuple(filter(lambda val: val[1] == dlist, items))

        return res[0][0]


    def fade(self, widget, duration):
        self.effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(self.effect)
        self.animation = QtCore.QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.start()

    def unfade(self, widget, duration):
        self.effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(self.effect)
        self.animation = QtCore.QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
