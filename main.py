from typing import List


class Node:
    char = None
    freq = None
    bit = ''
    left_child = None
    right_child = None

    def __init__(self, freq, char=None, left_child=None, right_child=None):
        self.char = char
        self.freq = freq
        self.left_child = left_child
        self.right_child = right_child

    def __repr__(self, level=0):
        ret = "\t" * level + repr(str(self.char) + ' ' + str(self.freq) + ' ' + self.bit) + "\n"
        for child in [self.left_child, self.right_child]:
            if child is not None:
                ret += child.__repr__(level + 1)
        return ret


def analyze_text(text: str):
    node_list = []

    for char in text:
        already_in_list = False
        for node in node_list:
            if node.char == char:
                already_in_list = True
                node.freq += 1

        if not already_in_list:
            node_list.append(Node(char=char, freq=1))

    return node_list


def print_node_list(node_list: List[Node]):
    for node in node_list:
        print(node.char, node.freq, end=', ')
    print()


def create_huffman_tree(node_list: List[Node]):
    while len(node_list) > 1:
        left_child = node_list.pop()
        right_child = node_list.pop()
        new_node = Node(freq=left_child.freq + right_child.freq, left_child=left_child, right_child=right_child)
        node_list.append(new_node)
        node_list.sort(key=lambda node: node.freq, reverse=True)
    set_bits(node_list[0])
    return node_list[0]


def print_tree(node: Node):
    print(node.char, end='')


def set_bits(node: Node):
    if node.left_child is not None:
        node.left_child.bit += node.bit + '0'
        set_bits(node.left_child)
    if node.right_child is not None:
        node.right_child.bit += node.bit + '1'
        set_bits(node.right_child)


def get_dict_from_tree(node: Node, dictionary=None):
    if dictionary is None:
        dictionary = {}
    if node.char is not None:
        dictionary[node.char] = node.bit
        dictionary[node.bit] = node.char
    if node.left_child is not None:
        dictionary = get_dict_from_tree(node.left_child, dictionary)
    if node.right_child is not None:
        dictionary = get_dict_from_tree(node.right_child, dictionary)
    return dictionary


def encode(text: str, dictionary: dict):
    result = ''
    for char in text:
        result += dictionary[char]
    return result


def decode(text: str, dictionary: dict):
    result = ''
    current_bits = ''
    for bit in text:
        current_bits += bit
        if current_bits in dictionary:
            result += dictionary[current_bits]
            current_bits = ''
    return result


if __name__ == '__main__':
    example_text = 'this is an example of a huffman tree'

    nodes = analyze_text(example_text)
    print_node_list(nodes)
    nodes = sorted(nodes, key=lambda node: node.freq, reverse=True)
    print_node_list(nodes)
    tree = create_huffman_tree(nodes)

    print(nodes)
    print(get_dict_from_tree(tree))

    encoded = encode(example_text, get_dict_from_tree(tree))
    decoded = decode(encoded, get_dict_from_tree(tree))

    print(encoded)
    print(decoded)
