#!/usr/bin/env python3
"""Debug Java AST structure."""

from tree_sitter import Parser
import tree_sitter_language_pack as tlp

def print_tree(node, source, indent=0):
    """Recursively print the AST."""
    text = source[node.start_byte:node.end_byte].decode('utf-8', 'replace')[:50]
    print("  " * indent + f"{node.type} (id={node.id}) [{node.start_point}-{node.end_point}] {repr(text)}")
    if hasattr(node, 'parent') and node.parent:
        print("  " * indent + f"  (parent: {node.parent.type}, parent_id={node.parent.id})")
    for child in node.children:
        print_tree(child, source, indent + 1)

# Java with Javadoc
print("=" * 80)
print("Java with Javadoc:")
print("=" * 80)
java_code = b'''/**
 * This is a Javadoc comment.
 */
public class Foo {
    public void bar() {}
}'''
parser = Parser()
parser.language = tlp.get_language('java')
tree = parser.parse(java_code)
print_tree(tree.root_node, java_code)
