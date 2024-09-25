from threading import Thread

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget
from lib.controller.views.pages.live_did_ui import Ui_Form

class LiveDidUI(QWidget):

    stack_index = 2
    live_did_signal = pyqtSignal(bool)


    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.worker = None

        self.isg_emf_rpm = {
            "req": [0x03, 0x22, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00],
            "res": [0x05, 0x62, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00],
        }
        self.isg_bat_vol = {
            "req": [0x03, 0x22, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00],
            "res": [0x05, 0x62, 0x01, 0x02, 0x00, 0x00, 0x00, 0x00],
        }
        self.isg_es_status = {
            "req": [0x03, 0x22, 0x01, 0x04, 0x00, 0x00, 0x00, 0x00],
            "res": [0x05, 0x62, 0x01, 0x04, 0x00, 0x00, 0x00, 0x00],
        }
        self.isg_ign_key_status = {
            "req": [0x03, 0x22, 0x01, 0x05, 0x00, 0x00, 0x00, 0x00],
            "res": [0x05, 0x62, 0x01, 0x05, 0x00, 0x00, 0x00, 0x00],
        }
        self.isg_ign_status = {
            "req": [0x03, 0x22, 0x01, 0x06, 0x00, 0x00, 0x00, 0x00],
            "res": [0x05, 0x62, 0x01, 0x06, 0x00, 0x00, 0x00, 0x00],
        }
        self.isg_malfunction = {
            "req": [0x03, 0x22, 0x01, 0x07, 0x00, 0x00, 0x00, 0x00],
            "res": [0x05, 0x62, 0x01, 0x07, 0x00, 0x00, 0x00, 0x00],
        }
        self.isg_derating_mode = {
            "req": [0x03, 0x22, 0x01, 0x08, 0x00, 0x00, 0x00, 0x00],
            "res": [0x05, 0x62, 0x01, 0x08, 0x00, 0x00, 0x00, 0x00],
        }
        self.isg_cranking_cutoff = {
            "req": [0x03, 0x22, 0x01, 0x09, 0x00, 0x00, 0x00, 0x00],
            "res": [0x05, 0x62, 0x01, 0x09, 0x00, 0x00, 0x00, 0x00],
        }

        self.current_req = []
        self.flag = False

        self.set_slots()

    def set_slots(self):
        self.ui.start_btn.clicked.connect(lambda : self.live_did_signal.emit(True))
        self.ui.stop_btn.clicked.connect(lambda : self.live_did_signal.emit(False))
        # self.ui.start_btn.clicked.connect(self.send_request)
        # self.ui.stop_btn.clicked.connect(self.stop_request)

    def send_request(self):
        self.flag = True
        self.live_did_signal.emit()
    def clear_txt(self):
        # self.flag = False
        self.current_req.clear()
        self.ui.emf_rpm_txt.clear()
        self.ui.bat_vol_txt.clear()
        self.ui.ign_status_txt.clear()
        self.ui.ign_key_txt.clear()
        self.ui.es_status_txt.clear()
        self.ui.mal_txt.clear()
        self.ui.derating_txt.clear()
        self.ui.cranking_txt.clear()
        # self.live_did_signal.emit()

    def set_request_list(self):
        return [self.isg_emf_rpm["req"], self.isg_bat_vol["req"], self.isg_es_status["req"],self.isg_ign_status["req"],
                self.isg_ign_key_status["req"], self.isg_malfunction["req"], self.isg_derating_mode["req"],
                            self.isg_cranking_cutoff["req"]]

    def process_live_did(self, data):
        print("process live did data", data)
        res = data[:4]
        if self.isg_emf_rpm["res"][:4] == res:
            print("rpm ", data[4], data[5])
            rpm = ((data[4] * 256) + data[5]) / 1000
            self.ui.emf_rpm_txt.setText(str(rpm))
        elif self.isg_bat_vol["res"][:4] == res:
            print("bat ", data[4], data[5])
            bat_volt = round(((data[4] * 256) + data[5]) / 1000, 2)
            self.ui.bat_vol_txt.setText(str(bat_volt))
        elif self.isg_es_status["res"][:4] == res:
            print("es status", data[4])
            self.ui.es_status_txt.setText(str(data[4]))
        elif self.isg_ign_status["res"][:4] == res:
            print("Ign status", data[4])
            self.ui.ign_status_txt.setText(str(data[4]))
        elif self.isg_ign_key_status["res"][:4] == res:
            print("ign key status")
            self.ui.ign_key_txt.setText(str(data[4]))
        elif self.isg_malfunction["res"][:4] == res:
            print("Malfunction", data[4])
            self.ui.mal_txt.setText(str(data[4]))
        elif self.isg_derating_mode["res"][:4] == res:
            print("derating mode", data[4])
            self.ui.derating_txt.setText(str(data[4]))
        elif self.isg_cranking_cutoff["res"][:4] == res:
            print("cranking", data[4])
            self.ui.cranking_txt.setText(str(data[4]))

