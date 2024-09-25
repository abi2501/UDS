
kmap = {
    "0000": 0, "0001": 1, "0010": 2, "0011" : 3, "0100" : 4, "0101" : 5,
    "0110": 6, "0111": 7, "1000": 8, "1001" : 9, "1010" : 10, "1011" : 11,
    "1100": 12, "1101": 13, "1110": 14, "1111" : 15
}

class SeedKey:

    def __init__(self, seed, lconstant, divisor_slice, empty_fill_slice, seed_pivot_slice, lconst_pivot_slice):
        self.seed = seed
        self.lconstant = lconstant
        self.divisor_slice = divisor_slice
        self.empty_fill_slice = empty_fill_slice
        self.seed_pivot_slice = seed_pivot_slice
        self.lconst_pivot_slice = lconst_pivot_slice

        self.final_key = [0, 0, 0, 0]

        print("SEED ", self.seed)
        print("constant ", self.lconstant)

        self.seed_byte_list = ['{:08b}'.format(ele) for ele in self.seed]
        # print(self.seed_byte_list)

        sliced_byte = self.byte_slicer(self.seed_byte_list, self.divisor_slice[0], self.divisor_slice[1])
        # print("Byte to be sliced", sliced_byte)

        seed_div_list = [ele for idx, ele in enumerate(self.seed.__reversed__()) if idx != sliced_byte]
        seed_div_list = list(seed_div_list.__reversed__())
        # print(seed_div_list)

        divisor = bytearray(seed_div_list).hex()
        # print(divisor)
        my_hex = ''.join(f'{i:02x}' for i in seed_div_list)
        # print(my_hex)

        # print(int(divisor, 16))

        dividend = int(hex(self.lconstant), 16)
        remainder = hex(dividend % int(divisor, 16))
        remainder = remainder[2:]
        # print(remainder)

        rlist = [ele for ele in remainder]
        rlist.insert(0, '0') if len(rlist) % 2 !=0 else rlist
        # print(rlist)
        hex_rlist = ''.join(rlist)
        remainder_list = self.get_splitted_bytes_list(hex_rlist)
        # print(remainder_list)


        self.fill_zero_pos = self.byte_slicer(self.seed_byte_list, self.empty_fill_slice[0], self.empty_fill_slice[1])
        # print("fill zero pos ", self.fill_zero_pos)

        zero_fill_list = list(remainder_list.__reversed__())
        # print("remainder list ", zero_fill_list)

        index1 = self.byte_slicer(self.seed_byte_list, self.seed_pivot_slice[0], self.seed_pivot_slice[1])
        index2 = self.byte_slicer(self.seed_byte_list, self.lconst_pivot_slice[0], self.lconst_pivot_slice[1])

        # print("index1, index2" , index1, index2)
        #
        ex_seed = list(self.seed.__reversed__())[index1]

        # print("ex_seed ", ex_seed, hex(ex_seed))

        ex_const = list(self.get_splitted_bytes_list(hex(self.lconstant)).__reversed__())[index2]
        # print("ex_const" , ex_const)

        exor = hex(ex_seed ^ int(ex_const, 16))
        exor = exor[2:]
        # print("exored value ", exor)
        zero_fill_list.insert(self.fill_zero_pos, exor)
        # print(zero_fill_list)
        #
        self.final_key = [int(ele, 16) for ele in zero_fill_list[::-1]]
        print("divisor", divisor, "remainder ", rlist, "fill zero pos", self.fill_zero_pos, "ex_seed ", hex(ex_seed), "ex_const" , ex_const,"exored value ", exor)
        print(self.final_key)

        # print(" ".join([hex(ele) for ele in self.final_key]))
        #
        print(" ".join([hex(ele) for ele in self.final_key]))



    def byte_slicer(self, dlist, slice_from, slice_to):
        """
            To find divisor, seed is sliced to get the byte to be removed
            hence, the given value is sliced and resultant is the byte order to be removed
        :param value: Seed or lconstant hex string
        :param slice_from: Starting byte
        :param slice_to: End byte
        :return: Sliced hex string
        """

        sliced_byte = 0

        res = ''.join(dlist)

        res = res[::-1]

        sliced_byte = res[slice_from] + res[slice_to]
        formatted_slice = sliced_byte.zfill(4)
        return kmap[formatted_slice]

    def get_splitted_bytes_list(self, hex_str):
        hex_str = hex_str[2:] if hex_str[:2] == '0x' else hex_str
        n = 2
        dlist = [(hex_str[i:i + n]) for i in range(0, len(hex_str), n)]
        return dlist


#
# class SeedKey:
#     divisor = 0x0
#     remainder = 0x0
#     pivot_position = 0
#     pivot = 0x0
#     key = 0x0
#
#     def __init__(self, seed, lconstant, divisor_slice, empty_fill_slice, seed_pivot_slice, lconst_pivot_slice):
#         self.seed = seed
#         self.lconstant = lconstant
#         self.divisor_slice = divisor_slice
#         self.empty_fill_slice = empty_fill_slice
#         self.seed_pivot_slice = seed_pivot_slice
#         self.lconst_pivot_slice = lconst_pivot_slice
#
#         self.final_key = []
#
#         print("SEED ", seed)
#         print("Const ", hex(self.lconstant))
#
#         self.seed_byte_list = ['{:08b}'.format(ele) for ele in self.seed]
#         print(self.seed_byte_list)
#
#         sliced_byte = self.byte_slicer(self.seed_byte_list, self.divisor_slice[0], self.divisor_slice[1])
#
#         print("Byte to be sliced ", sliced_byte)
#         seed_div_list = [ele for idx, ele in enumerate(self.seed.__reversed__()) if idx != sliced_byte]
#         seed_div_list = list(seed_div_list.__reversed__())
#
#         div= ''.join(["{0:x}".format(ele) for ele in seed_div_list])
#
#         print("divisor", "ox"+str(div))
#
#         self.divisor = int(div, 16)
#         dividend = int(hex(self.lconstant), 16)
#         self.remainder = hex(dividend % self.divisor)
#         print("remainder", self.remainder)
#         remainder_list = self.get_splitted_bytes_list(self.remainder)
#
#         self.fill_zero_pos = self.byte_slicer(self.seed_byte_list, self.empty_fill_slice[0], self.empty_fill_slice[1])
#         print("fill zero pos ", self.fill_zero_pos)
#
#         zero_fill_list = list(remainder_list.__reversed__())
#         print("remainder list ", remainder_list)
#         print("zero fill lister ",zero_fill_list)
#         # zero_fill_list.insert(self.fill_zero_pos, "XX")
#
#         # empty_fill_byte =
#         index1 = self.byte_slicer(self.seed_byte_list, self.seed_pivot_slice[0], self.seed_pivot_slice[1])
#         index2 = self.byte_slicer(self.seed_byte_list, self.lconst_pivot_slice[0], self.lconst_pivot_slice[1])
#
#         print("index1, index2" , index1, index2)
#
#         ex_seed = list(self.seed.__reversed__())[index1]
#
#         print("ex_seed ", ex_seed, hex(ex_seed))
#
#         ex_const = list(self.get_splitted_bytes_list(hex(self.lconstant)).__reversed__())[index2]
#         print("ex_const" , ex_const)
#
#         exor = hex(ex_seed ^ int(ex_const, 16))
#         exor = exor[2:]
#         print("exored value ", exor)
#         zero_fill_list.insert(self.fill_zero_pos, exor)
#         print(zero_fill_list)
#
#         self.final_key = [int(ele, 16) for ele in zero_fill_list[::-1]]
#         print(self.final_key)
#
#         print('0x' + ''.join([hex(ele) for ele in self.final_key]))
#
#
#     def byte_slicer(self, dlist, slice_from, slice_to):
#         """
#             To find divisor, seed is sliced to get the byte to be removed
#             hence, the given value is sliced and resultant is the byte order to be removed
#         :param value: Seed or lconstant hex string
#         :param slice_from: Starting byte
#         :param slice_to: End byte
#         :return: Sliced hex string
#         """
#
#         sliced_byte = 0
#
#         res = ''.join(dlist)
#
#         res = res[::-1]
#
#         sliced_byte = res[slice_from] + res[slice_to]
#         formatted_slice = sliced_byte.zfill(4)
#         return kmap[formatted_slice]
#
#
#     def get_splitted_bytes_list(self, hex_str):
#         hex_str = hex_str[2:] if hex_str[:2] == '0x' else hex_str
#         n = 2
#         dlist = [hex_str[i:i + n] for i in range(0, len(hex_str), n)]
#         return dlist
#
#


#
# l5_seed = [156, 22, 7, 164]
# # l5_seed = [91, 167, 110, 58]
# l5_constant = 0x841B8CEC
# # l5_constant = 0x841B8CEC
# divisor_slice = (9, 8)
# empty_fill_slice = (9,8)
# seed_pivot_slice = (27, 26)
# lconst_pivot_slice = (4, 3)
#
# l5 = SeedKey(l5_seed, l5_constant, divisor_slice, empty_fill_slice, seed_pivot_slice, lconst_pivot_slice)



#
# # l5_seed = [211, 178, 127, 152]
# l5_seed = [91, 167, 110, 58]
# # l5_constant = 0x841B8CEC
# l5_constant = 0x841B8CDB
# divisor_slice = (9, 8)
# empty_fill_slice = (9,8)
# seed_pivot_slice = (27, 26)
# lconst_pivot_slice = (4, 3)
#
# l5 = SeedKey(l5_seed, l5_constant, divisor_slice, empty_fill_slice, seed_pivot_slice, lconst_pivot_slice)
