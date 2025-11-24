#!/usr/bin/env python3
"""Generate expected output JSON files for test artifacts."""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, 'src')

from treesitter_tools import api

artifacts = [
    'tests/artifacts/sample_react.jsx',
    'tests/artifacts/sample_complex.rs',
    'tests/artifacts/sample_complex.go',
    'tests/artifacts/sample_complex.c',
]

for artifact_path in artifacts:
    f = Path(artifact_path)
    if not f.exists():
        continue
    
    symbols = api.list_symbols(f)
    result = [s.to_dict() for s in symbols]
    
    # Strip content to keep expected files small
    for r in result:
        r['content'] = None
    
    output_path = Path(str(f) + '.expected.json')
    output_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(f"Generated {output_path}")
