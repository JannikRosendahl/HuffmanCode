import argparse
import pickle

debug: bool = True


class Node:
    char = None
    freq = None
    code = None
    left_child = None
    right_child = None

    def __init__(self, freq, char=None, left_child=None, right_child=None):
        self.char = char
        self.freq = freq
        self.left_child = left_child
        self.right_child = right_child
        self.code = ''

    def get_child_count(self):
        child_count = 1
        if self.left_child is not None:
            child_count += self.left_child.get_child_count()
        if self.right_child is not None:
            child_count += self.right_child.get_child_count()
        return child_count


def print_node(node: Node, print_empty=False):
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

    def construct_from_string(self, string):
        node_list = []
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

    def tree_from_node_list(self, node_list: list[Node]):
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
        if node.char is not None and node.code != '':
            self.encode_dict[node.char] = node.code
            self.decode_dict[node.code] = node.char

        if node.left_child is not None:
            self.set_dicts(node.left_child)
        if node.right_child is not None:
            self.set_dicts(node.right_child)

    def encode(self, string):
        result = ''
        for char in string:
            if char not in self.encode_dict:
                print(f'error at char \'{char}\', dict not large enough')
                return ''
            result += self.encode_dict[char]
        return result

    def decode(self, string):
        result = ''
        sub = ''
        for char in string:
            sub += char
            if sub in self.decode_dict:
                result += self.decode_dict[sub]
                sub = ''
        if sub != '':
            print('sub error: ' + sub)
        return result


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
    arg_parser.add_argument('-m', '--mode', metavar='Mode', type=str, help='encrypt mode (e)\ndecrypt mode (d)', choices=('e', 'd'))
    arg_parser.add_argument('-i', '--file-in', metavar='Input File', type=str, help='The file from which input will be read.')
    arg_parser.add_argument('-o', '--file-out', metavar='Output File', type=str, help='The file where output will be written.')
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
        text_in = open(file_in, 'r').read()
        print(text_in)

        # construct tree
        tree = HuffmanTree(text_in)

        # write output
        file_o = open(file_out, 'w')
        file_o.write(tree.encode(text_in))
        file_o.close()

        # write dictionary

        file_d = open(file_dict, 'wb')
        file_d.write(pickle.dumps(tree.decode_dict))
        file_d.close()

    elif mode == 'd':
        # read file_in
        text_in = open(file_in, 'r').read()
        # read dict
        tree = HuffmanTree()
        tree.decode_dict = pickle.loads(open(file_dict, 'rb').read())
        # write output
        text_decoded = tree.decode(text_in)

        open(file_out, 'w').write(text_decoded)

