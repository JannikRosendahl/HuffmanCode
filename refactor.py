import argparse
import pickle
import threading
import time
from typing import Type
from bitstring import BitArray, BitStream, Bits, ConstBitStream

debug: bool = True


def printd(string, end=None):
    if debug:
        if end is not None:
            return print(string, end=end)
        return print(string)


class Node:
    freq: int
    data: bytes
    code = None     # can change type from BitArray to Bits
    l_child = None
    r_child = None

    def __init__(self, freq: int, data: bytes = None, l_child=None, r_child=None):
        self.freq = freq
        self.data = data
        self.l_child = l_child
        self.r_child = r_child

        self.code = BitArray()

    def get_child_count(self):
        child_count = 1
        if self.l_child is not None:
            child_count += self.l_child.get_child_count()
        if self.r_child is not None:
            child_count += self.r_child.get_child_count()
        return child_count


class HuffmanTree:
    tree: Node = None
    encode_dict = None #encode_dict: dict[bytes:Bits] = None
    decode_dict = None #decode_dict: dict[Bits:bytes] = None

    def __init__(self, data: bytes = None):
        if data is None:
            return

        # 1. iterate over data, create Nodes for different bytes
        node_list: list[Node] = []
        for byte in data:
            byte = byte.to_bytes(length=1, byteorder='big')
            node = [node for node in node_list if node.data == byte]
            node = None if len(node) == 0 else node[0]
            if node is not None:
                node.freq += 1
            else:
                node_list.append(Node(1, byte))

        printd(f'finished parsing data, {len(node_list)} different bytes found')

        # 2. create tree by combining nodes until only one is left
        while len(node_list) > 1:
            node_list.sort(key=lambda curr_node: (curr_node.freq, curr_node.get_child_count()), reverse=True)
            l_node, r_node = node_list.pop(), node_list.pop()
            node_list.append(Node(l_node.freq + r_node.freq, l_child=l_node, r_child=r_node))
        self.tree = node_list.pop()

        # 3. traverse tree to set code. left traversal adds '0' to code, right traversal adds '1'
        self.set_code(self.tree)
        if debug:
            self.print_tree(self.tree)

        self.encode_dict = {}
        self.decode_dict = {}
        self.set_dicts(self.tree)
        if debug:
            print(self.encode_dict)
            print(self.decode_dict)

    def set_code(self, node: Node):
        code: BitArray = node.code
        if node.l_child is not None:
            # append '0b0' to left child of node
            node.l_child.code.append(code)
            node.l_child.code.append('0b0')
            self.set_code(node.l_child)
        if node.r_child is not None:
            # append '0b1' to left child of node
            node.r_child.code.append(code)
            node.r_child.code.append('0b1')
            self.set_code(node.r_child)

    def set_dicts(self, node: Node):
        if node.data is not None:
            if type(node.code) is BitArray:
                node.code = Bits(node.code)
            self.encode_dict[node.data] = node.code
            self.decode_dict[node.code] = node.data
        if node.l_child is not None:
            self.set_dicts(node.l_child)
        if node.r_child is not None:
            self.set_dicts(node.r_child)

    def print_tree(self, node: Node):
        if node.data is not None:
            print(f'freq: {node.freq} hex: {node.data.hex()} ascii: {node.data} code: {node.code.bin}')
        if node.l_child is not None:
            self.print_tree(node.l_child)
        if node.r_child is not None:
            self.print_tree(node.r_child)

    def encode(self, data: bytes):
        encoded_data = BitArray()

        for byte in data:
            byte = byte.to_bytes(length=1, byteorder='big')

            if byte not in self.encode_dict:
                print(f'encode error at \'{byte}\'')
                return bytes()
            encoded_data += self.encode_dict[byte]

        print(len(encoded_data))
        return encoded_data.tobytes()

    def decode(self, data: bytes):
        decoded_data = bytes()

        bit_data = ConstBitStream(data)
        bit_data_len = len(bit_data)
        print(bit_data)

        sub = BitArray
        bitsread = 0
        chunk_size = 256

        chunk = bit_data.read(chunk_size)
        for key in self.decode_dict:
            if chunk.

        '''
        while bit_data_len - bitsread > chunk_size:
            chunk = bit_data.read(chunk_size)
            bitsread += chunk_size
        '''


        '''
        while bit_data_len - bitsread > chunk_size:
            chunk = bit_data.read(chunk_size)
            for bit in chunk:
                pass
            bitsread += chunk_size
        if bit_data_len - bitsread > 0:
            print(f'{bit_data_len - bitsread} bits left')
            chunk = bit_data.read(bit_data_len - bitsread)
        '''
        '''
        try:
            while(True):
                bit = bit_data.read(256)
                bitsread += 1*256
                print(len(bit))
        except:
            print(f'reached end {bitsread}')
        
        for byte in data:
            bitsread += 8
        '''

        print(f'bits read {bitsread}')
        return decoded_data

thread_orig_size = 0
thread_size = 0
seconds = 0
def thread_log():
    while True:
        time.sleep(1)
        global seconds
        seconds += 1
        print(f'progress: {thread_size} / {thread_orig_size}')


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Program to encode or decode a message using a Huffman Tree.')
    arg_parser.add_argument('-m', '--mode', metavar='Mode', type=str, help='encrypt mode (e)\ndecrypt mode (d)',
                            choices=('e', 'd'))
    arg_parser.add_argument('-i', '--file-in', metavar='Input File', type=str,
                            help='The file from which input will be read.')
    arg_parser.add_argument('-o', '--file-out', metavar='Output File', type=str,
                            help='The file where output will be written.')
    arg_parser.add_argument('-d', '--dict', metavar='Dict File', type=str, help='Translation dictionary file path. In '
                                                                                'encode mode this file will be '
                                                                                'created/overwritten. In decode mode '
                                                                                'an existing dictionary file is '
                                                                                'required for translation.')

    args = arg_parser.parse_args()

    mode = args.mode
    file_in = args.file_in
    file_out = args.file_out
    file_dict = args.dict

    print(f'found mode {mode}, file_in {file_in}, file_out {file_out}, file_dict {file_dict}')

    if mode == 'e':
        # read file_in
        bytes_in = open(file_in, 'rb').read()

        # construct tree
        tree = HuffmanTree(bytes_in)

        # generate output
        bytes_encoded = tree.encode(bytes_in)

        # write output
        file_o = open(file_out, 'wb')
        file_o.write(bytes_encoded)
        file_o.close()

        # write dictionary
        file_d = open(file_dict, 'wb')
        file_d.write(pickle.dumps(tree.decode_dict))
        file_d.close()

    elif mode == 'd':
        # read file_in
        file = open(file_in, 'rb')
        bytes_in = file.read()

        # construct empty tree
        tree = HuffmanTree()

        # read dict
        tree.decode_dict = pickle.loads(open(file_dict, 'rb').read())

        # generate output
        print(f'start decoding')
        thread = threading.Thread(target=thread_log, daemon=True)
        thread.start()
        bytes_decoded = tree.decode(bytes_in)
        print(f'seconds: {seconds}')


        # write output
        open(file_out, 'wb').write(bytes_decoded)
