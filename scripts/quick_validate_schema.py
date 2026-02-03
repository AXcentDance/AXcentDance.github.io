
import json
import re
import sys
from html.parser import HTMLParser

class JsonLdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.json_blocks = []
        self.in_script = False

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            attrs_dict = dict(attrs)
            if attrs_dict.get('type') == 'application/ld+json':
                self.in_script = True

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_script = False

    def handle_data(self, data):
        if self.in_script:
            self.json_blocks.append(data)

def validate_file(file_path):
    print(f"Validating {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        parser = JsonLdParser()
        parser.feed(content)
        
        if not parser.json_blocks:
            print(f"WARNING: No JSON-LD blocks found in {file_path}")
            return
            
        for i, block in enumerate(parser.json_blocks):
            try:
                json.loads(block)
                print(f"  Block {i+1}: VALID JSON")
            except json.JSONDecodeError as e:
                print(f"  Block {i+1}: INVALID JSON - {e}")
                print(f"  Error at line {e.lineno}, column {e.colno}")
                # Print context
                lines = block.split('\n')
                start = max(0, e.lineno - 2)
                end = min(len(lines), e.lineno + 2)
                for j in range(start, end):
                    print(f"    {lines[j]}")

    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    files = sys.argv[1:]
    for file in files:
        validate_file(file)
        print("-" * 30)
