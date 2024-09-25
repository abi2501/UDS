from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect, QMessageBox

from lib.controller import did_dict, DATA_LENGTH, DID_READ_RES_FIRST_BYTE, DID_RESPONSE, DID_MSG_FIRST_BYTES
from lib.controller.util.helper import applog
from lib.controller.views.pages.did_ui import Ui_Form


class DidUI(QWidget):

    stack_index = 3
    did_read_signal = pyqtSignal(list)
    did_write_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.did_pcan_dlist = []
        self.did_read_data = []

        self.selected_did = None
        self.selected_read_did = None

        self.init_settings()
        self.read_mode = False
        self.write_mode = False

    def init_settings(self):

        self.ui.did_list_combo.addItem("Select", None)

        for ele in did_dict:
            self.ui.did_list_combo.addItem(did_dict[ele]["text"], did_dict[ele])

        self.ui.did_list_combo.setCurrentIndex(0)
        self.ui.did_list_combo.currentIndexChanged.connect(self.selected_did_item)

        self.ui.did_item_txt.textChanged.connect(lambda val: self.ui.did_item_txt.setText(val.upper()))
        self.ui.clear_btn.clicked.connect(lambda: self.ui.did_item_txt.clear())

        self.ui.read_btn.clicked.connect(self.did_pcan_read)
        self.ui.write_btn.clicked.connect(self.did_pcan_write)

        # self.ui.did_box.

    def did_pcan_write(self):

        self.read_mode = False
        self.write_mode = True
        did_txt = self.ui.did_item_txt.text().strip()

        if self.selected_did and self.validate_did(did_txt):
            # applog("DID WRITE " + str(self.selected_did["text"]))

            did_item_txt = list(bytes(did_txt, 'ascii'))
            did_write_data = did_item_txt + [0] * (self.selected_did["data_length"] - len(did_item_txt))

            req_did = self.selected_did["did_req"]
            start = 0
            end = 0

            for ele in req_did:
                cnt = DATA_LENGTH - len(ele)
                end = end + cnt
                pckt = ele + did_write_data[start:end]
                pckt = pckt + [0] * (DATA_LENGTH - len(pckt))
                start = end
                self.did_pcan_dlist.append(pckt)

            self.did_write_signal.emit()
        else:
            # print("invalued")
            pass
    def did_write_completed(self):
        self.did_pcan_dlist.clear()
        msg = self.selected_did["text"] + " Flashed...!!"
        self.ui.did_flash_msg.setText(msg)
        self.ui.did_flash_msg.setStyleSheet("Color:green")
        self.unfade(self.ui.did_flash_msg, 1000)
        self.fade(self.ui.did_flash_msg, 1000)

    def did_read_completed(self):
        self.did_pcan_dlist.clear()
        msg = self.selected_did["text"] + " Read Complete...!!"
        self.ui.did_flash_msg.setText(msg)
        self.ui.did_flash_msg.setStyleSheet("Color:green")
        self.unfade(self.ui.did_flash_msg, 1000)
        self.fade(self.ui.did_flash_msg, 1000)


    def did_pcan_read(self):
        self.read_mode = True
        self.write_mode = False
        self.did_read_data.clear()
        self.ui.did_item_txt.clear()
        if self.selected_did:
            self.did_read_req = self.selected_did["did_read_req"]
            self.did_read_signal.emit(self.did_read_req)

    def process_read_data(self, data):
        print("process read data from can", data)

        if data[2] == DID_READ_RES_FIRST_BYTE or data[1] == DID_READ_RES_FIRST_BYTE:
            l = len(self.selected_did["did_read_res"])
            if self.selected_did["did_read_res"] == data[:l]:
                self.did_read_data = self.did_read_data + data[l:]
                # print("DID RESPONSE")
                # print(self.selected_did["id"] , did_dict["did_dealer_code"]["id"])
                if self.selected_did["id"] != did_dict["did_dealer_code"]["id"] and self.selected_did["id"] != did_dict["did_calib_checksum"]["id"]:
                    print("DID no response")
                    self.did_read_signal.emit(DID_RESPONSE)
        else:
            if data[0] in DID_MSG_FIRST_BYTES:
                self.did_read_data = self.did_read_data + data[1:]

        # print(self.did_read_data, len(self.did_read_data))
        # print("READ CHECKER ", [chr(ele) for ele in self.did_read_data])

        if len(self.did_read_data) > self.selected_did["data_length"]:
            self.did_read_data = self.did_read_data[:self.selected_did["data_length"]]

        if len(self.did_read_data) == self.selected_did["data_length"]:
            read_data = str(''.join(chr(ele) for ele in self.did_read_data))
            read_data = [chr(ele) for ele in self.did_read_data]
            rdata = ''.join(read_data)
            self.ui.did_item_txt.setText(rdata.strip())
            self.did_read_completed()

    def validate_did(self, did_txt):
        state = True
        msg = ''

        if len(did_txt) == 0 or len(did_txt) > self.selected_did["data_length"]:
            state = False
            msg = "Pls Enter Valid Details"

        self.set_error_msg(msg, False)
        return state

    def selected_did_item(self, index):
        item = self.ui.did_list_combo.itemData(index)
        self.selected_did = item

        print("Selected did item ", self.selected_did)
        self.ui.did_item_txt.clear()
        self.ui.did_error_lbl.clear()

    def set_error_msg(self, msg, state):
        self.ui.did_error_lbl.setText(msg)
        self.ui.did_error_lbl.setStyleSheet("color:green") if state else self.ui.did_error_lbl.setStyleSheet("color:red")

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


    def showDialog(self, title, description):
        msgBox = QMessageBox()
        msgBox.setText(description)
        msgBox.setWindowTitle(title)
        msgBox.exec()
        return msgBox


