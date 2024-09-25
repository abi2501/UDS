import os
import time
import typing
from threading import Thread

import qdarktheme
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QThreadPool
from PyQt6.QtGui import QColor, QIcon, QKeySequence, QShortcut, QPixmap
from PyQt6.QtWidgets import QMainWindow, QGraphicsDropShadowEffect, QVBoxLayout, QGraphicsOpacityEffect, QMessageBox, \
    QStatusBar

from lib.controller import DEFAULT_REQ_CAN_ID, DID_WRITE_RESPONSE, INIT_BATCH_1, LIVE_DATA_CAN_ID, INIT_BATCH_1_ACK, \
    INIT_BATCH_5, DEFAULT_RES_CAN_ID, L3_SEED_REQUEST, L3_KEY_REQUEST, L3_KEY_POSITIVE_RESPONSE, \
    L3_SEED_FROM_ECU
from lib.controller.pcan.PCANBasic import PCANBasic, PCAN_ERROR_OK, PCAN_USBBUS1, PCAN_BAUD_500K
from lib.controller.util.boot_worker import BootWorker, LiveDidWorker

from lib.controller.util.helper import resource_path, make_pcan_pckt, setlogger, generate_key, get_hex_str, applog
from lib.controller.util.runnable import Worker
from lib.controller.views.main import Ui_MainWindow
from lib.controller.widgets.boot_widget import BootUI
from lib.controller.widgets.custom_widgets import CustomDialog
from lib.controller.widgets.did_widget import DidUI
from lib.controller.widgets.dtc_widget import DtcUI
from lib.controller.widgets.live_did_widget import LiveDidUI
from lib.controller.widgets.odata_widget import OdataUI


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.light = True

        self.boot_wid = BootUI()
        self.odata_wid = OdataUI()
        self.did_wid = DidUI()
        self.dtc_wid = DtcUI()
        self.live_did_wid = LiveDidUI()

        self.l3_auth = False

        self.pcan = None
        self.pflag = None
        self.worker = None
        self.boot_worker = None
        self.did_worker = None

        self.pcan_channel = PCAN_USBBUS1
        self.pcan_baudrate = PCAN_BAUD_500K

        self.init_settings()
        self.set_slots()
        self.pool = QThreadPool.globalInstance()

        setlogger()

        self.did_mode = False
        self.dtc_mode = False

    def set_tab_content(self, idx):

        boot = True if idx == self.boot_wid.stack_index else False
        did = True if idx == self.did_wid.stack_index else False
        dtc = True if idx == self.dtc_wid.stack_index else False
        odata = True if idx == self.odata_wid.stack_index else False
        live_did = True if idx == self.live_did_wid.stack_index else False

        if not self.l3_auth:
            if idx == self.dtc_wid.stack_index or idx == self.did_wid.stack_index:
                print("Authenticate L3")
                self.start_l3_authentication()

        self.ui.boot_btn.setChecked(boot)
        self.ui.did_btn.setChecked(did)
        self.ui.dtc_btn.setChecked(dtc)
        self.ui.odata_btn.setChecked(odata)
        self.ui.live_did_btn.setChecked(live_did)

        if not live_did:
            # self.live_did_wid.flag = False
            if self.did_worker:
                self.did_worker.flag = False
                self.did_worker.req_list = []
                self.live_did_wid.clear_txt()

        self.ui.tabWidget.setCurrentIndex(idx)

    def set_slots(self):

        self.ui.connect_btn.clicked.connect(self.connect_pcan)

        self.ui.boot_btn.clicked.connect(lambda : self.set_tab_content(self.boot_wid.stack_index))
        self.ui.odata_btn.clicked.connect(lambda : self.set_tab_content(self.odata_wid.stack_index))
        self.ui.live_did_btn.clicked.connect(lambda : self.set_tab_content(self.live_did_wid.stack_index))
        self.ui.did_btn.clicked.connect(lambda : self.set_tab_content(self.did_wid.stack_index))
        self.ui.dtc_btn.clicked.connect(lambda : self.set_tab_content(self.dtc_wid.stack_index))
        self.ui.exit_btn.clicked.connect(self.close)

        self.boot_wid.switch_signal.connect(lambda : self.set_tab_content(self.odata_wid.stack_index))
        self.boot_wid.boot_signal.connect(self.initiate_boot)

        self.did_wid.did_read_signal.connect(lambda data: self.pcan_write(data))
        self.did_wid.did_write_signal.connect(self.did_process_write)

        self.dtc_wid.dtc_signal.connect(lambda data: self.pcan_write(data))

        self.live_did_wid.live_did_signal.connect(self.init_live_did)

        # Set Shortcut for close window on ctrl + c
        self.short_cut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.short_cut.activated.connect(self.close)

    def init_live_did(self, flag):
        # flag = self.live_did_wid.flag

        if self.pflag and self.ui.tabWidget.currentIndex() == self.live_did_wid.stack_index:
            if flag:
                self.did_worker.flag = True
                self.did_worker.req_list = self.live_did_wid.set_request_list()
            else:
                self.did_worker.flag = False
                self.did_worker.req_list = []
                self.live_did_wid.clear_txt()
        else:
            self.did_worker.flag = False

    def initiate_boot(self, flag, dlist):
        self.pcan_write(dlist)

        if not flag:
            self.start_boot_thread()

    def start_boot_thread(self):
        self.boot_worker = BootWorker(True)
        # self.boot_worker.signals.process.connect(lambda : self.pcan_write(INIT_BATCH_7))
        self.pool.start(self.boot_worker)

    def start_l3_authentication(self):
        self.pcan_write(INIT_BATCH_1)

    def did_process_write(self):
        item = self.did_wid.did_pcan_dlist[0]
        self.pcan_write(item)

    def pcan_write(self, data):
        if self.pflag:
            tpcan = make_pcan_pckt(DEFAULT_REQ_CAN_ID, data)
            print("Flashing ", get_hex_str(data))
            self.pcan.Write(self.pcan_channel, tpcan)


    def closeEvent(self, event) -> None:
        print("Close triggered")
        self.stop_process()
        return None

    def connect_pcan(self):

        state = self.ui.connect_btn.isChecked()

        if state:
            if self.initialize_pcan():
                self.set_status_msg("PCAN Bus Connected !...", True)
                self.pflag = True

                self.enable_tabs(True)
                print("pflag ", self.pflag)

                self.worker = Worker(self.pcan, self.pcan_channel, self.pflag)
                self.worker.signals.process.connect(self.get_pcan_data)
                self.worker.signals.error.connect(self.stop_process)
                self.pool.start(self.worker)

                self.did_worker = LiveDidWorker(False, self.pcan, self.pcan_channel, [])
                self.pool.start(self.did_worker)

            else:
                self.set_status_msg("PCAN Bus Not Connected !...", False)
                self.showDialog("PCAN Bus", "Please Connect PCAN channel")
                self.ui.connect_btn.setChecked(False) if self.ui.connect_btn.isChecked() else None
                self.enable_tabs(False)
                self.stop_process()
        else:
            self.enable_tabs(False)
            self.stop_process()

        self.set_connect_btn()

    def stop_process(self):
        print("Stoping thread")
        if self.pflag:
            self.pflag = False
            self.worker.working = False
            self.l3_auth = False

        if self.did_worker is not None:
            # self.live_did_wid.flag = False
            self.did_worker.working = False

        if self.boot_worker:
            self.boot_worker.working = False

        self.uninitialize_pcan()
        self.reset_connect_btn()

    def get_pcan_data(self, canId, data):
        tab = self.ui.tabWidget.currentIndex()

        if tab == self.boot_wid.stack_index and canId == DEFAULT_RES_CAN_ID:
            # applog("ECU : " + str(get_hex_str(data)))
            if self.boot_worker is not None:
                self.boot_worker.flag = False
                self.boot_worker.working = False
                self.boot_worker = None
            self.boot_wid.process_boot_msg(data)
        elif tab == self.odata_wid.stack_index:
            if canId == LIVE_DATA_CAN_ID:
                self.odata_wid.process_odata(data)
        elif tab == self.live_did_wid.stack_index:
            if canId == DEFAULT_RES_CAN_ID:
                self.live_did_wid.process_live_did(data)
        else:
            if canId == DEFAULT_RES_CAN_ID:
                applog("ECU : " + str(get_hex_str(data)))
                if not self.l3_auth:
                    if self.authenticate_l3(data):
                        self.l3_auth = True
                        self.dtc_wid.ui.dtc_box.setEnabled(True)
                        self.did_wid.ui.did_box.setEnabled(True)
                    else:
                        self.dtc_wid.ui.dtc_box.setEnabled(False)
                        self.did_wid.ui.did_box.setEnabled(False)
                else:
                    if tab == self.did_wid.stack_index:
                        self.process_did_read_write(data)
                    elif tab == self.dtc_wid.stack_index:
                        self.process_dtc(data)

    def process_dtc(self, data):
        self.dtc_wid.process_dtc_data(data)

    def process_did_read_write(self, data):
        if self.did_wid.read_mode:
            print("READ MODE")
            self.did_wid.process_read_data(data)
        elif self.did_wid.write_mode:
            print("WRITE MODE")
            if data == DID_WRITE_RESPONSE:
                for idx, ele in enumerate(self.did_wid.did_pcan_dlist):
                    if idx > 0:
                        self.pcan_write(ele)
                        time.sleep(0.1)
                print("comes here")
            elif data == self.did_wid.selected_did["did_res"]:
                print("Response received for  write success ", self.did_wid.selected_did["text"])
                self.did_wid.did_write_completed()

    def authenticate_l3(self, data):
        print(data)
        state = False
        if data == INIT_BATCH_1_ACK:
            self.pcan_write(L3_SEED_REQUEST)
        elif data[2] == L3_SEED_FROM_ECU[2]:
            ltype = data[2]
            seed = data[3:7]
            key = generate_key(ltype, seed)
            print("key", key)
            L3_KEY_REQUEST[3:7] = key
            print("Processed req", get_hex_str(L3_KEY_REQUEST))
            self.pcan_write(L3_KEY_REQUEST)
        elif data == L3_KEY_POSITIVE_RESPONSE:
            print("L3 Authenticated")
            # self.l3_auth = True
            state = True
        return state

    def initialize_pcan(self):
        try:
            if self.pcan is None:
                self.pcan = PCANBasic()
                status = self.pcan.Initialize(self.pcan_channel, self.pcan_baudrate)
                print(self.pcan.GetStatus(self.pcan_channel))
                if status == PCAN_ERROR_OK:
                    return True
            else:
                return False
        except Exception as ex:
            print("Exception while connecting PCAN")
            print(ex)
            return False

    def uninitialize_pcan(self):
        if self.pcan is not None:
            self.pcan.Uninitialize(self.pcan_channel)
            self.pcan = None

    def reset_connect_btn(self):
        self.ui.connect_btn.setChecked(False)
        self.ui.connect_btn.setText("Connect")

    def set_connect_btn(self):

        state = self.ui.connect_btn.isChecked()

        if state:
            self.ui.connect_btn.setText("Disconnect")
            qIcon = QIcon()
            img = ":images/" + "discon.png" if self.light else "disconnect_white.png"
            qIcon.addPixmap(QPixmap(img))
            # qIcon.addPixmap(QPixmap(":images/disconnect_white.png"))
            self.ui.connect_btn.setIcon(qIcon)
        else:
            self.ui.connect_btn.setText("Connect")
            qIcon = QIcon()
            img = ":images/" + "connect.png" if self.light else "connect_white.png"
            qIcon.addPixmap(QPixmap(img))
            # qIcon.addPixmap(QPixmap(":images/connect_white.png"))
            self.ui.connect_btn.setIcon(qIcon)

    def enable_tabs(self, state):
        self.boot_wid.setEnabled(state)
        self.odata_wid.setEnabled(state)
        self.did_wid.setEnabled(state)
        self.dtc_wid.setEnabled(state)
        self.live_did_wid.setEnabled(state)

        if self.boot_wid.isEnabled():
            self.boot_wid.ui.upload_btn.setEnabled(True)
        else:
            self.boot_wid.ui.progressBar.hide()
        # else:
        #     self.boot_wid.stop_progess_bar()

        if self.live_did_wid.isEnabled():
            self.live_did_wid.ui.live_did_box.setEnabled(True)

        idx = self.ui.tabWidget.currentIndex()
        self.boot_wid.clear_scroll_items()
        self.set_tab_content(idx)

    def init_settings(self):

        styleFile = os.path.join(os.path.split(__file__)[0], resource_path("lib/assets/styles/light.css"))

        with open(styleFile, 'r') as f:
            style = f.read()

        self.setStyleSheet(style)

        # self.light = False
        qdarktheme.setup_theme("light")
        self.set_connect_btn()

        self.setWindowTitle("UDS Flashing Unit")
        self.did_wid.ui.did_box.setEnabled(False)
        self.dtc_wid.ui.dtc_box.setEnabled(False)
        self.live_did_wid.ui.live_did_box.setEnabled(False)

        self.ui.tabWidget.insertTab(self.boot_wid.stack_index, self.boot_wid, "Bootloader")
        self.ui.tabWidget.insertTab(self.odata_wid.stack_index, self.odata_wid, "Live Data")
        self.ui.tabWidget.insertTab(self.live_did_wid.stack_index, self.live_did_wid, "Live DID")
        self.ui.tabWidget.insertTab(self.did_wid.stack_index, self.did_wid, "DID")
        self.ui.tabWidget.insertTab(self.dtc_wid.stack_index, self.dtc_wid, "DTC")
        self.ui.tabWidget.tabBar().hide()

        self.enable_tabs(False)
        self.ui.boot_btn.setChecked(True)

    def set_status_msg(self, msg, state):
        self.ui.con_status_msg.setText(msg)
        self.ui.con_status_msg.setStyleSheet("Color:#FFFFFF") if state else self.ui.con_status_msg.setStyleSheet(
            "Color:Red; font-weight:bold;")
        self.unfade(self.ui.con_status_msg, 1000)
        self.fade(self.ui.con_status_msg, 1000)

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