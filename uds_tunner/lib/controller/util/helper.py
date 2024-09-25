import logging
import os
import sys

from lib.controller import DATA_LENGTH, L5, L3
from lib.controller.pcan.PCANBasic import TPCANStatus, TPCANMsg, PCAN_MESSAGE_STANDARD
from lib.controller.util.seed_key import SeedKey


def get_hex_str(dlist):
    return " ".join([hex(ele) for ele in dlist])

def generate_key(type, seed):

    # applog("Seed " + get_hex_str(seed))
    lconst = L5 if type == 5 else L3 if type == 3 else None
    seedKey = SeedKey(seed, int(lconst["constant"], 16), lconst["divisor_slice"],
                      lconst["empty_fill_slice"], lconst["seed_pivot_slice"], lconst["lconst_pivot_slice"])

    key = seedKey.final_key
    # applog("Generated Key")
    # applog(get_hex_str(key))
    print("KEy gnerated ", get_hex_str(key))
    if len(key) < 4:
        print("Key length check")
        cnt = 4 - len(key)
        key.insert(0, 0)
        # key.extend([0] * cnt)
        print("New key ", key)

    return key


def make_pcan_pckt(can_id, ele):

    tpcan = TPCANMsg()
    tpcan.ID = can_id

    if(len(ele) == DATA_LENGTH):
        tpcan.LEN = len(ele)
        tpcan.MSGTYPE = PCAN_MESSAGE_STANDARD
        tpcan.DATA[0] = ele[0]
        tpcan.DATA[1] = ele[1]
        tpcan.DATA[2] = ele[2]
        tpcan.DATA[3] = ele[3]
        tpcan.DATA[4] = ele[4]
        tpcan.DATA[5] = ele[5]
        tpcan.DATA[6] = ele[6]
        tpcan.DATA[7] = ele[7]
    else:
        cnt = DATA_LENGTH - len(ele)

    return tpcan

def process_pcan_pckt(pcan_pckt):

    msg = pcan_pckt[1]

    canId = msg.ID
    data = list(msg.DATA)


    return canId, data


def divide_chunks(dlist, n):
    # looping till length l
    for i in range(0, len(dlist), n):
        d = dlist[i:i + n]
        yield d

def setlogger():
    # file_path = resource_path("logfiles/app.log")

    # file_path  = os.path.join(os.path.split(__file__)[0], resource_path("../../logfiles/app.log"))
    file_path = "logs/app.log"
    # logging.basicConfig(filename=file_path, filemode='w', format='%(name)s - %(levelname)s - %(asctime)s - %(message)s',
    #                         level=logging.INFO)
    logging.basicConfig(filename=file_path, filemode='w', format='%(asctime)s - %(message)s',
                            level=logging.INFO)

def applog(message):
    msg = str(message)
    logging.info(msg)

def resource_path(relative_path):

    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
