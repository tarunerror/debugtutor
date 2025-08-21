#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Install tree-sitter language grammars
python -c "
import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_cpp
import tree_sitter_java
import tree_sitter_go
import tree_sitter_rust
print('Tree-sitter languages installed successfully')
"
