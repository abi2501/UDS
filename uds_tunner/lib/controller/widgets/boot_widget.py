import time
from array import array

from PyQt6.QtCore import pyqtSignal, Qt, QThread
from PyQt6.QtWidgets import QWidget, QFileDialog, QLabel, QWidgetItem
from intelhex import IntelHex

from lib.controller import START_ADDRESS, END_ADDRESS, BIN_FILE_PADDING_SIZE, INIT_BATCH_1, INIT_BATCH_1_ACK, \
    INIT_BATCH_2, INIT_BATCH_2_ACK, INIT_BATCH_3, INIT_BATCH_3_ACK, INIT_BATCH_4, INIT_BATCH_4_ACK, INIT_BATCH_5, \
    INIT_BATCH_5_ACK, INIT_BATCH_6, INIT_BATCH_6_ACK, INIT_BATCH_8, INIT_BATCH_8_ACK, \
    INIT_BATCH_10, INIT_BATCH_10_ACK, BIN_FLASH_START_ACK,  \
    DATA_LENGTH, POST_PGM_MSG, \
    ECU_HARD_RESET_REQUEST, ECU_HARD_RESET_RESPONSE, LSB, MSB, EOF_CHUNK_DATA, \
    EOF_CHUNK_DATA_ACK, INIT_BATCH_ACK_LIST, HEX_CHUNK_SIZE, POST_PGM_MSG_ACK, CONTROL_FLOW_TAG, HEX_CHUNK_END_ACK, \
    INIT_ERASE_REQ, DEFAULT_FLASH_RESPONSE, INIT_ERASE_REQ_ACK, INIT_REQUEST_DOWNLOAD, \
    CHECK_SUM_REQUEST, CHECK_SUM_RESPONSE, CHECK_VALIDATION_RESPONSE, CHECK_VALIDATION_REQUEST
from lib.controller.util.helper import applog, generate_key, get_hex_str, resource_path
from lib.controller.util.seed_key import SeedKey
from lib.controller.views.pages.boot_ui import Ui_Form
from lib.controller.widgets.custom_widgets import CustomDialog
import datetime

import pandas as pd
import numpy as np


class BootUI(QWidget):

    stack_index = 0
    switch_signal = pyqtSignal()
    boot_signal = pyqtSignal(bool, list)

    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.custom_dialog = CustomDialog("Flashing Completed !!")

        self.pre_pgm = False
        self.post_pgm = False
        self.ctl_flow_item = []
        self.flash_index = 0
        self.chunk_index = 0
        self.pbar_count = 0

        self.dlist = []
        self.flash_chunks = []
        self.check_sum = 0

        self.st = 0
        self.end = 0

        self.init_settings()
        self.ui.progressBar.hide()
        self.ui.progressBar.setValue(0)

        # self.ui.boot_flash_btn.setVisible(False)

    def init_settings(self):

        self.ui.upload_btn.setEnabled(False)
        self.ui.flash_btn.setVisible(False)
        self.ui.progressBar.setVisible(False)

        self.ui.upload_btn.clicked.connect(self.browse_file)
        self.ui.flash_btn.clicked.connect(lambda: self.init_flashing(True))
        self.ui.boot_flash_btn.clicked.connect(lambda: self.init_flashing(False))

        self.custom_dialog.accepted.connect(lambda : self.switch_signal.emit())

        self.ui.boot_msg_box.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.ui.scroll_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.ui.scroll_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.ui.scroll_view.setWidgetResizable(True)

        self.ui.scroll_view.verticalScrollBar().rangeChanged.connect(self.scrollToBottom)
        self.ui.progressBar.setMinimum(0)

    def init_flashing(self, flag):
        self.clear_scroll_items()
        self.show_pcan_messages("Bootloader Initiated")
        applog("------------------------------------------------------------------------")
        applog("*************************Bootloader Initiated*************************")
        applog("------------------------------------------------------------------------")
        msg = ''
        if flag:
            print("Applicaiton flash")
            msg = "GUI : " + get_hex_str(INIT_BATCH_1)
            self.boot_signal.emit(True, INIT_BATCH_1)

        else:
            # msg = "GUI : " + get_hex_str(INIT_ERASE_REQ[0])
            # self.boot_signal.emit(False, INIT_ERASE_REQ[0])
            # self.ctl_flow_item = INIT_ERASE_REQ[1:]
            print("Bootflash")
            msg = "GUI : " + get_hex_str(INIT_BATCH_5)
            self.boot_signal.emit(False, INIT_BATCH_5)

        self.show_pcan_messages(msg)
        applog(msg)

    def process_boot_msg(self, data):

        if not self.pre_pgm and not self.post_pgm:
            # self.progress_pre_pgm(data)
            self.process_pre_pgm(data)
            self.set_progress_bar(50)
        else:
            if self.post_pgm:
                self.process_post_pgm(data)
                self.set_progress_bar(400)
            else:
                self.process_hex_content_flashing(data)
                self.set_progress_bar(5)

    def process_post_pgm(self, data):
        flag = False
        flash_item = []

        if data == INIT_BATCH_1_ACK:
            self.show_pcan_messages("ECU : " + get_hex_str(data))
            applog("ECU : " + get_hex_str(data))
            for ele in [POST_PGM_MSG[0], POST_PGM_MSG[1], POST_PGM_MSG[2]]:
                self.boot_signal.emit(True, ele)
                time.sleep(0.01)
                self.show_pcan_messages("GUI : " + get_hex_str(ele))
                applog("GUI : " + get_hex_str(ele))

            self.custom_dialog.show()
            self.reset()

    def reset(self):
        self.pre_pgm = self.post_pgm = False
        self.st = self.end = self.flash_index = self.chunk_index = self.pbar_count = 0
        self.stop_progess_bar()
        self.ui.progressBar.hide()
        applog("-------------------------------- Flashing Completed --------------------------------")

    def process_hex_content_flashing(self, data):
        flash_item = []
        flag = False
        if data == DEFAULT_FLASH_RESPONSE:
            if self.flash_chunks:
                self.flash_next_flash_chunks()
            else:
                self.flash_control_flow_item()
        elif data[1] == HEX_CHUNK_END_ACK[1]:
            self.set_hex_flash_chunk()
            if self.flash_chunks:
                flash_item = self.flash_chunks[self.flash_index]
                self.boot_signal.emit(True, flash_item)
                flag = False
            else:
                flash_item = EOF_CHUNK_DATA
                self.boot_signal.emit(True, flash_item)
                flag = True
        elif data == EOF_CHUNK_DATA_ACK:
            flash_item = CHECK_SUM_REQUEST[0]
            self.check_sum = self.calculate_checksum(self.dlist)
            CHECK_SUM_REQUEST[1][7] = LSB(self.check_sum)
            CHECK_SUM_REQUEST[2][1] = MSB(self.check_sum)
            self.ctl_flow_item = CHECK_SUM_REQUEST[1:]
            self.boot_signal.emit(True, flash_item)
            flag = True
        elif data == CHECK_SUM_RESPONSE:
            flash_item = CHECK_VALIDATION_REQUEST
            self.boot_signal.emit(True, flash_item)
            flag = True
        elif data == CHECK_VALIDATION_RESPONSE:
            now = datetime.datetime.now()
            date_txt = ''.join(str(now.date()).split('-')[::-1])
            datetxt = list(bytes(date_txt, 'ascii'))
            flash_item = [0x10, 0x0b, 0x2E, 0xF1, 0x99, datetxt[0], datetxt[1], datetxt[2]]

            self.ctl_flow_item = [
                [CONTROL_FLOW_TAG[0], datetxt[3], datetxt[4], datetxt[5], datetxt[6], datetxt[7], 0x00, 0x00]
            ]
            self.boot_signal.emit(True, flash_item)
            flag = True
        elif data == [0x03, 0x62, 0xF1, 0x99, 0, 0, 0, 0]:
            # applog("Hard resset")
            flash_item = ECU_HARD_RESET_REQUEST
            self.boot_signal.emit(True, flash_item)
            flag = True
        elif data == ECU_HARD_RESET_RESPONSE:
            time.sleep(2)
            self.show_pcan_messages("ECU : " + get_hex_str(data))
            applog("ECU : " + get_hex_str(data))
            self.show_pcan_messages("----------------POST PROGRAMMING----------------")
            applog("----------------POST PROGRAMMING----------------")

            self.post_pgm = True
            flash_item = INIT_BATCH_1
            self.boot_signal.emit(True, flash_item)

            self.show_pcan_messages("GUI : " + get_hex_str(flash_item))
            applog("GUI : " + get_hex_str(flash_item))
            flag = False

        if flag:
            self.show_pcan_messages("ECU : " + get_hex_str(data))
            self.show_pcan_messages("GUI : " + get_hex_str(flash_item))

            applog("ECU : " + get_hex_str(data))
            applog("GUI : " + get_hex_str(flash_item))

    def flash_next_flash_chunks(self):
        for idx, ele in enumerate(self.flash_chunks):
            if idx != 0:
                self.boot_signal.emit(True, ele)
                time.sleep(0.001)
                self.set_progress_bar(1)

        # self.set_progress_bar(5)
        self.flash_chunks = []

    def process_pre_pgm(self, data):
        flash_item = []
        flag = False

        if data == INIT_BATCH_1_ACK:
            self.show_pcan_messages("ECU : " + get_hex_str(data))
            applog("ECU : " + get_hex_str(data))
            for ele in [INIT_BATCH_2, INIT_BATCH_3, INIT_BATCH_4]:
                self.boot_signal.emit(True, ele)
                time.sleep(0.5)
                self.show_pcan_messages("GUI : " + get_hex_str(ele))
                applog("GUI : " + get_hex_str(ele))
        elif data in [INIT_BATCH_4_ACK, INIT_BATCH_6_ACK, INIT_ERASE_REQ_ACK, INIT_BATCH_8_ACK ]:
            if data == INIT_BATCH_4_ACK:
                time.sleep(0.5)
                flash_item = INIT_BATCH_5
                flag = True
            elif data == INIT_BATCH_6_ACK:
                time.sleep(1)
                flash_item = INIT_ERASE_REQ[0]
                self.ctl_flow_item = INIT_ERASE_REQ[1:]
                self.ui.progressBar.show()
                flag = True
            elif data == INIT_ERASE_REQ_ACK:
                time.sleep(1)
                flash_item = INIT_BATCH_8
                flag = True
            elif data == INIT_BATCH_8_ACK:
                flash_item = INIT_REQUEST_DOWNLOAD[0]
                self.ctl_flow_item = INIT_REQUEST_DOWNLOAD[1:]
                flag = True
        elif data[1:3] == INIT_BATCH_5_ACK[1:3]:
            ltype = data[2]
            seed = data[3:7]
            key = generate_key(ltype, seed)
            flash_item = INIT_BATCH_6.copy()
            flash_item[3:7] = key
            flag = True
        elif data == INIT_BATCH_10_ACK:
            self.show_pcan_messages("ECU : " + get_hex_str(data))
            applog("ECU : " + get_hex_str(data))
            applog("----------------Hex File Flashing Started----------------")
            self.show_pcan_messages("----------------Flashing Hex File----------------")

            self.set_hex_flash_chunk()
            flash_item = self.flash_chunks[self.flash_index]
            self.boot_signal.emit(True, flash_item)
            self.pre_pgm = True
            flag = False
        elif data == DEFAULT_FLASH_RESPONSE:
            self.show_pcan_messages("ECU : " + get_hex_str(data))
            applog("ECU : " + get_hex_str(data))
            self.flash_control_flow_item()

        if flag and flash_item:

            self.boot_signal.emit(True, flash_item)

            self.show_pcan_messages("ECU : " + get_hex_str(data))
            self.show_pcan_messages("GUI : " + get_hex_str(flash_item))

            applog("ECU : " + get_hex_str(data))
            applog("GUI : " + get_hex_str(flash_item))


    def progress_pre_pgm(self, data):
        flash_item = []
        flag = False

        if data == INIT_BATCH_1_ACK:
            self.boot_signal.emit(True, INIT_BATCH_2)
            time.sleep(0.5)

            self.boot_signal.emit(True, INIT_BATCH_3)
            time.sleep(0.5)

            self.boot_signal.emit(True, INIT_BATCH_4)
            flag = True
        elif data == INIT_BATCH_4_ACK:
            time.sleep(0.5)
            self.boot_signal.emit(True, INIT_BATCH_5)
            flag = True
        elif data[1:3] == INIT_BATCH_5_ACK[1:3]:
            ltype = data[2]
            seed = data[3:7]
            key = generate_key(ltype, seed)
            flash_item = INIT_BATCH_6.copy()
            flash_item[3:7] = key
            self.boot_signal.emit(True, flash_item)
            flag = True
        elif data == INIT_BATCH_6_ACK:
            time.sleep(1)
            self.boot_signal.emit(True, INIT_ERASE_REQ[0])
            applog("Check erase ctl flow")
            self.ctl_flow_item = INIT_ERASE_REQ[1:]
            self.ui.progressBar.show()
            flag = True
        elif data == INIT_ERASE_REQ_ACK:
            time.sleep(1)
            flash_item = INIT_BATCH_8
            self.boot_signal.emit(True, flash_item)
            self.ui.progressBar.show()
            flag = True
        elif data == INIT_BATCH_8_ACK:
            time.sleep(0.02)
            flash_item = INIT_REQUEST_DOWNLOAD[0]
            self.boot_signal.emit(True, flash_item)
            self.ctl_flow_item = INIT_REQUEST_DOWNLOAD[1:]
            flag = True
        elif data == INIT_BATCH_10_ACK:
            applog("----------------Hex File Flashing Started----------------")
            self.show_pcan_messages("----------------Flashing Hex File----------------")
            self.pre_pgm = True
            self.set_hex_flash_chunk()
            flash_item = self.flash_chunks[self.flash_index]
            self.boot_signal.emit(True, flash_item)
            flag = False
        elif data == DEFAULT_FLASH_RESPONSE:
            applog("Default res " + get_hex_str(data))
            flag = False
            self.show_pcan_messages("ECU : " + get_hex_str(data))
            applog("ECU : " + get_hex_str(data))
            self.flash_control_flow_item()

        if flag:
            self.show_pcan_messages("ECU : " + get_hex_str(data))
            self.show_pcan_messages("GUI : " + get_hex_str(flash_item))

            applog("ECU : " + get_hex_str(data))
            applog("GUI : " + get_hex_str(flash_item))

    def flash_control_flow_item(self):
        for ele in self.ctl_flow_item:
            self.boot_signal.emit(True, ele)
            self.show_pcan_messages("GUI : " + get_hex_str(ele))
            applog("GUI : " + get_hex_str(ele))

    def set_hex_flash_chunk(self):
        self.st = self.end
        self.end += HEX_CHUNK_SIZE
        chunks = self.dlist[self.st:self.end]

        self.flash_chunks = self.pre_process_flash_chunks(chunks)
        # applog(len(self.flash_chunks))
        # applog(self.flash_chunks)
        if chunks:
            pass
        else:
            applog("----------------Hex File Flashing Completed----------------")
            self.show_pcan_messages("----------------Flashing Hex File Finished----------------")
            self.flash_chunks = []

        self.flash_index = 0

    def pre_process_flash_chunks(self, chunks):
        flash_batch = []
        data_list = []
        tags = list(range(0x21, 0x2f)) + [0x2f, 0x20]
        tag_id = 0
        data_cnt = 0xFE

        if len(chunks) < HEX_CHUNK_SIZE and len(chunks) != 0:
            data_cnt = len(chunks) + 2
            # applog("data count")
            # applog(data_cnt)
            # applog(hex(data_cnt))

        for idx, ele in enumerate(chunks):
            if idx == 0:
                self.chunk_index += 1
                data_list = [0x10, data_cnt, 0x36, self.chunk_index] + data_list
            if len(data_list) < 7:
                data_list.append(ele)
                if idx == len(chunks) - 1:
                    cnt = 8 - len(data_list)
                    data_list.extend([255] * cnt)
                    flash_batch.append(data_list)
            elif len(data_list) == 7:
                data_list.append(ele)
                flash_batch.append(data_list)
                data_list = [tags[tag_id]]
                tag_id += 1
                tag_id = 0 if tag_id == len(tags) else tag_id

        return flash_batch

    def calculate_checksum(self, chunk):
        # BYTE_SIZE_IN_BITS = 16
        BYTE_SIZE_IN_BITS = 8
        # wsum1 = wsum2 = ERASED_STATE = 0xFFFF
        wsum1 = wsum2 = ERASED_STATE = 0xFF

        for ele in chunk:
            wsum1 += ele

            if wsum1 > 65535:
                wsum1 = wsum1 - 65536

            wsum2 += wsum1

            if wsum2 > 65535:
                wsum2 = wsum2 - 65536

        wsum1 = (wsum1 & ERASED_STATE) + (wsum1 >> BYTE_SIZE_IN_BITS)
        wsum2 = (wsum2 & ERASED_STATE) + (wsum2 >> BYTE_SIZE_IN_BITS)

        res = ((wsum2 << BYTE_SIZE_IN_BITS) & 0xFFFF) | wsum1
        # res = ((wsum2 << BYTE_SIZE_IN_BITS)) | wsum1
        return res

    def show_pcan_messages(self, msg):
        self.ui.boot_msg_box.addWidget(QLabel(msg))

    def set_progress_bar(self, val):
        value = self.ui.progressBar.value()
        value += val * 5
        self.ui.progressBar.setValue(value)

    def stop_progess_bar(self):
        value = self.ui.progressBar.maximum() - self.ui.progressBar.value()
        self.ui.progressBar.setValue(value)
        self.ui.progressBar.hide()
        self.ui.progressBar.setValue(0)

    def browse_file(self):
        file_dialog = QFileDialog()
        filename, _ = file_dialog.getOpenFileName(None, 'Open Bin File', '', "Hex files (*.hex)")

        if filename:
            ih = IntelHex()
            ih.fromfile(filename, format='hex')

            """
                From the selected hex file extract data from starting address 0x2000
            """

            # Save the data in a bin file
            # ih.tobinfile("led_extracted1.txt", start=0x2000, end=0xFFFFFF)

            # -- Extract data from hex file from starting address 0x2000
            bin_data_chunks = ih.tobinarray(start=START_ADDRESS, end=END_ADDRESS)

            # bin_data = list(self.divide_chunks(bin_data_chunks, 252, True))
            bin_data = list(self.divide_chunks(bin_data_chunks, 252, False))

            bin_chunks = list(filter(lambda ele: ele != [255] * HEX_CHUNK_SIZE, bin_data))
            self.dlist = sum(bin_chunks, [])

            # for ele in self.dlist:
            #     self.set_test_chunks()

            if len(self.dlist):
                self.ui.flash_btn.setVisible(True)
                self.pbar_count = 40
                self.pbar_count += len(self.dlist)
                self.ui.progressBar.setMaximum(self.pbar_count)


    # def set_test_chunks(self):
    #     self.st = self.end
    #     self.end += HEX_CHUNK_SIZE
    #     chunks = self.dlist[self.st:self.end]
    #
    #     self.flash_chunks = self.pre_process_flash_chunks(chunks)
    #     # applog("len" + str(len(self.flash_chunks)))
    #
    #     applog(self.flash_chunks)
    #     #
    #     # if self.flash_chunks:
    #     #     if len(self.flash_chunks) < 37:
    #     #         applog("check")
    #     #         applog(len(self.flash_chunks))
    #     #         applog(sum(self.flash_chunks, []))
    #     #         applog(len(sum(self.flash_chunks, [])))
    #     #         applog(len(self.flash_chunks) + 2)
    #     #     else:
    #     #         applog("not chek")
    #     #         applog(len(self.flash_chunks))
    #
    #     # if chunks:
    #     #     pass
    #     # else:
    #     #     applog("----------------Hex File Flashing Completed----------------")
    #     #     self.show_pcan_messages("----------------Flashing Hex File Finished----------------")
    #     #     self.flash_chunks = []
    #
    #     # self.flash_index = 0

    def divide_chunks(self, dlist, n, padding):
        # looping till length l
        for i in range(0, len(dlist), n):
            d = dlist[i:i + n]
            d = list(d)
            if len(d) < n and padding:
                cnt = n - len(d)
                d.extend([255]*cnt)
            yield d

    def clear_scroll_items(self):
        layout = self.ui.boot_msg_box
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)

            if isinstance(item, QWidgetItem):
                item.widget().close()
            else:
                self.clear_scroll_items(item.layout())
            # remove the item from layout
            layout.removeItem(item)

    def scrollToBottom(self, minVal=None, maxVal=None):
        # Additional params 'minVal' and 'maxVal' are declared because
        # rangeChanged signal sends them, but we set it to optional
        # because we may need to call it separately (if you need).

        self.ui.scroll_view.verticalScrollBar().setValue(
            self.ui.scroll_view.verticalScrollBar().maximum()
        )