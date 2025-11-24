#!/usr/bin/env python3
"""Debug docstring extraction with tree-sitter AST."""

from pathlib import Path
from tree_sitter import Parser
import tree_sitter_language_pack as tlp

test_code = '''
def simple_function():
    """This is a simple docstring."""
    return 42
'''

# Parse
parser = Parser()
parser.language = tlp.get_language('python')
tree = parser.parse(test_code.encode('utf-8'))
root = tree.root_node

def print_tree(node, indent=0):
    """Recursively print the AST."""
    print("  " * indent + f"{node.type} [{node.start_point}-{node.end_point}]")
    for child in node.children:
        print_tree(child, indent + 1)

print("AST Structure:")
print("=" * 60)
print_tree(root)
