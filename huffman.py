import argparse
import pickle
import threading
import time
from bitstring import BitArray, BitStream, Bits, ConstBitStream

debug: bool = True


class Node:
    freq: int
    data: bytes
    code = None  # can change type from BitArray to Bits
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
    encode_dict = None  # encode_dict: dict[bytes:Bits] = None
    decode_dict = None  # decode_dict: dict[Bits:bytes] = None

    data_byte_count = None
    encoded_bit_count = None

    def __init__(self, data: bytes = None):
        if data is None:
            return
        self.data_byte_count = len(data)

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

        print(f'finished parsing data, {len(node_list)} different bytes found')

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

        self.encoded_bit_count = len(encoded_data)

        # add pad to get a full byte
        pad_len = len(encoded_data) % 8
        if pad_len == 0:
            print('no pad needed')
        else:
            bits = None
            print(f'{pad_len} bits left to full byte')
            for i in range(2 ** pad_len):
                bits = Bits(int=i, length=pad_len)
                valid_pad = True
                for j in range(pad_len):
                    piece = Bits(bits[:j + 1])
                    if piece in self.decode_dict:
                        valid_pad = False
                if valid_pad:
                    break

            encoded_data += bits
            pad_len = len(encoded_data) % 8
            print(f'added {bits.bin}, {pad_len} bits left to full byte')

        print(f'data size in bits: {self.data_byte_count*8}, encoded data size in bits: {len(encoded_data)}')
        print(f'mean code length: {(len(encoded_data)/self.data_byte_count):.2f}')

        return encoded_data.tobytes()

    def decode(self, data: bytes):
        decoded_data = bytes()
        bit_stream = ConstBitStream(data)
        print(f'total bits in stream: {len(bit_stream)}')

        chunk_size = 2 ** 9
        piece = BitArray()
        global thread_orig_size
        thread_orig_size = len(bit_stream)
        global thread_size

        while bit_stream.pos != len(bit_stream):
            thread_size = bit_stream.pos

            read_size = chunk_size if len(bit_stream) - bit_stream.pos > chunk_size else len(
                bit_stream) - bit_stream.pos
            chunk: BitStream = bit_stream.read(read_size)
            # print(read_size, chunk)

            piece = BitArray() if len(piece) == 0 else piece
            while chunk.pos < len(chunk):
                piece.append(chunk.read(1))
                piece_as_bits = Bits(piece)
                if piece_as_bits in self.decode_dict:
                    decoded_data += self.decode_dict[piece_as_bits]
                    piece = BitArray()

        return decoded_data


thread_orig_size = 0
thread_size = 0
seconds = 0


def thread_log():
    while True:
        time.sleep(.5)
        global seconds
        seconds += .5
        percent = (thread_size / thread_orig_size) * 100
        print(
            f'progress: {thread_size:10} / {thread_orig_size} :: {percent:2.2f}%')


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Program to encode or decode a message using a Huffman Tree.')
    arg_parser.add_argument('-m', '--mode', metavar='Mode', type=str, help='encrypt mode (e)\ndecrypt mode (d)',
                            choices=('e', 'd'), required=True)
    arg_parser.add_argument('-i', '--file-in', metavar='Input File', type=str,
                            help='The file from which input will be read.', required=True)
    arg_parser.add_argument('-o', '--file-out', metavar='Output File', type=str,
                            help='The file where output will be written.', required=True)
    arg_parser.add_argument('-d', '--dict', metavar='Dict File', type=str,
                            help='Translation dictionary file path. In encode mode this file will be created/overwritten. In decode mode an existing dictionary file is required for translation.', required=True)

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
        print(f'progress: {thread_size:10} / {thread_orig_size} :: {(thread_size / thread_orig_size) * 100:2.2f}%')
        print(f'seconds: {seconds}')

        # write output
        open(file_out, 'wb').write(bytes_decoded)
