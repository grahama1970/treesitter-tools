#!/usr/bin/env python3
"""Analyze AST structures for doc comments in different languages."""

from tree_sitter import Parser
import tree_sitter_language_pack as tlp

def print_tree(node, source, indent=0):
    """Recursively print the AST."""
    text = source[node.start_byte:node.end_byte].decode('utf-8', 'replace')[:50]
    print("  " * indent + f"{node.type} [{node.start_point}-{node.end_point}] {repr(text)}")
    for child in node.children:
        print_tree(child, source, indent + 1)

# JavaScript with JSDoc
print("=" * 80)
print("JavaScript with JSDoc:")
print("=" * 80)
js_code = b'''/**
 * This is a JSDoc comment.
 */
function foo() {
    return 42;
}'''
parser = Parser()
parser.language = tlp.get_language('javascript')
tree = parser.parse(js_code)
print_tree(tree.root_node, js_code)

# Rust with doc comment
print("\n" + "=" * 80)
print("Rust with doc comment:")
print("=" * 80)
rust_code = b'''/// This is a doc comment.
fn foo() -> i32 {
    42
}'''
parser.language = tlp.get_language('rust')
tree = parser.parse(rust_code)
print_tree(tree.root_node, rust_code)

# Go with doc comment
print("\n" + "=" * 80)
print("Go with doc comment:")
print("=" * 80)
go_code = b'''package main

// Foo does something.
func Foo() int {
    return 42
}'''
parser.language = tlp.get_language('go')
tree = parser.parse(go_code)
print_tree(tree.root_node, go_code)
