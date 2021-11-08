from typing import List


class Node:
    char = None
    freq = None
    bit = None
    left_child = None
    right_child = None

    def __init__(self, freq, char=None, left_child=None, right_child=None):
        self.char = char
        self.freq = freq
        self.left_child = left_child
        self.right_child = right_child


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
        left_child.bit = 0
        left_child.bit = 1
        new_node = Node(freq=left_child.freq + right_child.freq, left_child=left_child, right_child=right_child)
        node_list.append(new_node)
        node_list.sort(key=lambda node: node.freq, reverse=True)


def print_tree(node: Node):
    print(node.char, end='')


if __name__ == '__main__':
    example_text = 'this is an example of a huffman tree'

    nodes = analyze_text(example_text)
    print_node_list(nodes)
    nodes.sort(key=lambda node: node.freq, reverse=True)
    print_node_list(nodes)
    create_huffman_tree(nodes)
