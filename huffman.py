import argparse
import pickle

debug: bool = False


class Node:
    char: chr = None
    freq: int = None
    code: str = None
    left_child = None
    right_child = None

    def __init__(self, freq: int, char: chr = None, left_child=None, right_child=None):
        self.char: chr = char
        self.freq: int = freq
        self.left_child: Node = left_child
        self.right_child: Node = right_child
        self.code = ''

    def get_child_count(self):
        child_count = 1
        if self.left_child is not None:
            child_count += self.left_child.get_child_count()
        if self.right_child is not None:
            child_count += self.right_child.get_child_count()
        return child_count


def print_node(node: Node, print_empty: bool = False):
    print(
        f"'{node.char}' {node.freq} {node.get_child_count()} '{node.code}'") if node.char is not None or print_empty else ''
    if node.left_child is not None:
        print_node(node.left_child)
    if node.right_child is not None:
        print_node(node.right_child)


class HuffmanTree:
    tree: Node = None
    encode_dict: dict = None
    decode_dict: dict = None

    def __init__(self, string=None):
        self.encode_dict = {}
        self.decode_dict = {}
        if string is not None:
            self.construct_from_string(string)

    def construct_from_string(self, string: str):
        node_list = []
        # node_list.append(Node(0, char=''))
        for char in string:
            node = [node for node in node_list if (node.char == char)]
            node = None if len(node) == 0 else node[0]
            if node is not None:
                node.freq += 1
            else:
                node_list.append(Node(1, char))

        self.tree_from_node_list(node_list)

    def reconstruct_from_string(self, string, string_dict):
        pass

    def construct_from_file(self, file):
        pass

    def reconstruct_from_file(self, file, dict_file):
        pass

    def tree_from_node_list(self, node_list):
        while len(node_list) > 1:
            # node_list = sorted(node_list, key=lambda node: node.freq, reverse=True)
            node_list = sorted(node_list, key=lambda node: (node.freq, node.get_child_count()), reverse=True)

            node1 = node_list.pop()
            # print(node1.freq)
            node2 = node_list.pop()
            # print(node2.freq)

            # print(f"combining nodes '{node1.char}' + '{node2.char}'")

            node_list.append(Node(node1.freq + node2.freq, left_child=node1, right_child=node2))

        self.set_code(node_list[0])
        self.tree = node_list.pop()
        self.set_dicts(self.tree)

    def set_code(self, node):
        code = node.code
        if node.left_child is not None:
            node.left_child.code += code + '0'
            self.set_code(node.left_child)
        if node.right_child is not None:
            node.right_child.code += code + '1'
            self.set_code(node.right_child)

    def set_dicts(self, node):
        if node.char is not None:
            self.encode_dict[node.char] = node.code
            self.decode_dict[node.code] = node.char
        if node.left_child is not None:
            self.set_dicts(node.left_child)
        if node.right_child is not None:
            self.set_dicts(node.right_child)

    def encode(self, string):
        result = '1'
        for char in string:
            if char not in self.encode_dict:
                print(f'error at char \'{char}\', dict not large enough')
                return ''
            result += self.encode_dict[char]
        return result

    def decode(self, string):
        print(f'type={type(string)} first 10 chars of string {string[0:10]}')

        result = ''
        sub = ''
        for char in string[1:]:
            sub += char
            if sub in self.decode_dict:
                print(f'replacing {sub} with \'{self.decode_dict[sub]}\'') if debug else ''
                temp = self.decode_dict[sub]
                if temp == '\0':
                    return result
                result += temp
                sub = ''
        if sub != '':
            print('sub error: ' + sub)
        return result


def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s))// 8, byteorder='big')


def test():
    huff_string = 'this is an example of a huffman tree'
    tree = HuffmanTree(huff_string)

    print(tree.encode(huff_string))
    print(tree.decode(tree.encode(huff_string)))

    string = 'abcdefghijklmnopqrstuvwxyz 1234567890'

    tree = HuffmanTree(string)

    print(tree.encode(string))
    print(tree.decode(tree.encode(string)))


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
        text_in = open(file_in, 'rb').read()
        #text_in += '\0'

        # construct tree
        tree = HuffmanTree(text_in)
        print(tree.encode_dict)

        # write output
        file_o = open(file_out, 'wb')
        output = tree.encode(text_in)
        # right pad string with 0s until len(string) is dividable by 8
        while len(output) % 8 != 0:
            output += '0'
            print('right_pad')
        print(output) if debug else ''
        byte_array = bitstring_to_bytes(output)
        #output_utf8 = ''
        # convert binary encoding to characters to write
        '''for i in range(len(output)//8):
            print(output[i * 8:i * 8 + 8]) if debug else ''
            print(int(output[i * 8:i * 8 + 8], 2)) if debug else ''
            print(chr(int(output[i * 8:i * 8 + 8], 2))) if debug else ''
            print('') if debug else ''
            output_utf8 += chr(int(output[i * 8:i * 8 + 8], 2))'''

        file_o.write(byte_array)
        file_o.close()

        # write dictionary
        file_d = open(file_dict, 'wb')
        file_d.write(pickle.dumps(tree.decode_dict))
        file_d.close()

    elif mode == 'd':
        # read file_in
        file = open(file_in, 'rb')
        file.seek(0)
        text_in = file.read()
        #text_in = '{0:b}'.format(int.from_bytes(text_in, byteorder='big'))
        #print(f'first 10 as string {text_in[:10]}')
        # convert read chars back to binary
        '''print(text_in) if debug else ''
        bin_in = ''.join(format(ord(i), '08b') for i in text_in)
        print(bin_in) if debug else ''
        '''

        # read dict
        tree = HuffmanTree()
        tree.decode_dict = pickle.loads(open(file_dict, 'rb').read())
        print(tree.decode_dict)
        # write output
        text_decoded = tree.decode(text_in)

        open(file_out, 'w', encoding='utf-8').write(text_decoded)
