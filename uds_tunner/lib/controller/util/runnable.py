import time

from PyQt6.QtCore import QObject, pyqtSignal, QRunnable
from qdarktheme.qtpy.QtCore import Slot

from lib.controller import DEFAULT_RES_CAN_ID, LIVE_DATA_CAN_ID
from lib.controller.pcan.PCANBasic import PCAN_ERROR_OK, PCAN_ERROR_INITIALIZE, PCAN_ERROR_ILLHW
from lib.controller.util.helper import process_pcan_pckt, applog, get_hex_str


class Signals(QObject):
    process = pyqtSignal(int, list)
    error = pyqtSignal()

class Worker(QRunnable):

    def __init__(self, pcan, pcan_channel, flag):
        super().__init__()
        self.working = flag
        self.pcan = pcan
        self.pcan_channel = pcan_channel
        self.signals = Signals()
        self.pcan_empty_data = [0, 0, 0, 0, 0, 0, 0, 0]

    @Slot()
    def run(self):
        while self.working:
            try:
                # print("status ", self.pcan.GetStatus(self.pcan_channel))
                if (self.pcan.GetStatus(self.pcan_channel) != PCAN_ERROR_INITIALIZE
                        and self.pcan.GetStatus(self.pcan_channel) != PCAN_ERROR_ILLHW):
                    pcan_pckt = self.pcan.Read(self.pcan_channel)
                    # print(pcan_pckt[1])
                    # print(pcan_pckt[1].DATA)

                    canId, data = process_pcan_pckt(pcan_pckt)

                    # if data != self.pcan_empty_data:
                    #     print("From runnable ", data)

                    if canId == DEFAULT_RES_CAN_ID:

                        if data != self.pcan_empty_data:
                            print("From runnable ", get_hex_str(data), canId)
                            self.signals.process.emit(canId, data)

                    elif canId == LIVE_DATA_CAN_ID:
                        if data != self.pcan_empty_data:
                            # time.sleep(1)
                            self.signals.process.emit(canId, data)
                            # pass
                else:
                    print("Error emit")
                    self.signals.error.emit()

            except Exception as ex:
                self.signals.error.emit()
                print("Exception from worker : ")
                print(ex)
                self.working = False