#!/usr/bin/env python3
"""Quick test for docstring extraction."""

from pathlib import Path
import sys
sys.path.insert(0, 'src')

from treesitter_tools.core import extract_symbols

# Create test file
test_file = Path('/tmp/test_docstring.py')
test_file.write_text('''
def simple_function():
    """This is a simple docstring."""
    return 42

class SimpleClass:
    """This is a class docstring."""
    def method(self):
        """This is a method docstring."""
        pass
''')

# Extract symbols
symbols = extract_symbols(test_file)

print("Docstring Extraction Test:")
print("=" * 60)
for sym in symbols:
    print(f"\nKind: {sym.kind}")
    print(f"Name: {sym.name}")
    print(f"Signature: {sym.signature}")
    print(f"Docstring: {sym.docstring}")
    print(f"Content (first 100 chars): {sym.content[:100] if sym.content else 'None'}...")
