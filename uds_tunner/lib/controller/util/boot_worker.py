import time

from PyQt6.QtCore import QObject, pyqtSignal, QRunnable
from qdarktheme.qtpy.QtCore import Slot

from lib.controller import DEFAULT_REQ_CAN_ID
from lib.controller.pcan.PCANBasic import PCAN_ERROR_INITIALIZE, PCAN_ERROR_ILLHW
from lib.controller.util.helper import make_pcan_pckt


class Signals(QObject):
    process = pyqtSignal()


class BootWorker(QRunnable):

    def __init__(self, flag):
        super().__init__()
        self.working = True
        self.flag = flag
        self.counter = 0
        self.signals = Signals()

    @Slot()
    def run(self):
        while self.working:
            if self.flag:
                if self.counter < 1000:
                    print("counter ", self.counter)
                    time.sleep(0.01)
                    self.counter += 1
                else:
                    self.signals.process.emit()
                    self.working = False
                    self.counter = 0



class LiveDidWorker(QRunnable):

    def __init__(self, flag, pcan, pcan_channel, dlist):
        super().__init__()
        self.working = True
        self.flag = flag
        self.pcan = pcan
        self.pcan_channel = pcan_channel
        self.dlist = dlist
        self.req_list = dlist
        self.signals = Signals()
        self.error = Signals()


    def run(self):
        while self.working:
            try:
                if (self.pcan.GetStatus(self.pcan_channel) != PCAN_ERROR_INITIALIZE
                        and self.pcan.GetStatus(self.pcan_channel) != PCAN_ERROR_ILLHW):

                    if self.req_list:
                        for ele in self.req_list:
                            if self.flag:
                                print("Flashing live did req ", ele)
                                tpcan = make_pcan_pckt(DEFAULT_REQ_CAN_ID, ele)
                                self.pcan.Write(self.pcan_channel, tpcan)
                                # time.sleep(1)
                                time.sleep(0.5)

            except Exception as ex:
                self.error.process.emit()
                print("Exception from worker : ")
                print(ex)
                self.working = False
