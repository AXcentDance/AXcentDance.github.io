
import os
import sys
from html.parser import HTMLParser

class SyntaxChecker(HTMLParser):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.stack = []
        self.errors = []
        self.void_elements = {
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 
            'link', 'meta', 'param', 'source', 'track', 'wbr'
        }

    def handle_starttag(self, tag, attrs):
        if tag not in self.void_elements:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in self.void_elements:
            return # Void elements don't have end tags usually, but if present, ignore or handle? 
                   # HTML5 says no end tag for void elements. If present, it's technically invalid but browsers handle it.
                   # For strict syntax, maybe we shouldn't expect them.
                   # But let's focus on structural tags.
            pass

        if not self.stack:
            self.errors.append(f"Line {self.getpos()[0]}: Stray closing tag </{tag}> found (no matching opening tag).")
            return

        top_tag, top_pos = self.stack[-1]
        
        if top_tag == tag:
            self.stack.pop()
        else:
            # Mismatch. 
            # Could be that 'tag' is missing an opener, OR 'top_tag' is unclosed.
            # Example: <div> <p> </div> -> Stack: [div, p]. End tag: div.
            # strict check: error.
            # Heuristic: Is 'tag' anywhere in the stack?
            if any(t == tag for t, _ in self.stack):
                # We missed closing some tags in between.
                # Pop until we find match?
                # For this script, let's just report the mismatch and stop popping to avoid cascading errors?
                # Or better: Report unclosed tags up to the match.
                
                # Check how deep it is
                found_index = -1
                for i in range(len(self.stack) - 1, -1, -1):
                    if self.stack[i][0] == tag:
                        found_index = i
                        break
                
                # Report all tags above it as unclosed
                for i in range(len(self.stack) - 1, found_index, -1):
                    unclosed_tag, unclosed_pos = self.stack[i]
                    self.errors.append(f"Line {unclosed_pos[0]}: Unclosed tag <{unclosed_tag}> (closed by </{tag}> on line {self.getpos()[0]}).")
                
                # Reset stack to found index
                self.stack = self.stack[:found_index]
            else:
                # Stray closing tag (not in stack)
                self.errors.append(f"Line {self.getpos()[0]}: Stray closing tag </{tag}> (expected </{top_tag}>).")

    def check(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                content = f.read()
            self.feed(content)
            
            # Check for unclosed tags at the end
            if self.stack:
                for tag, pos in self.stack:
                    # Ignore commonly unclosed tags if we want to be lenient, but for strict check report them.
                    # Structural tags should always be closed.
                    self.errors.append(f"Line {pos[0]}: Unclosed tag <{tag}> at end of file.")
                    
        except Exception as e:
            self.errors.append(f"Error parsing file: {str(e)}")
            
        return self.errors

def check_structure(root_dir="."):
    print(f"Starting Strict HTML Syntax Check in {os.path.abspath(root_dir)}...\n")
    found_errors = False
    
    for root, _, files in os.walk(root_dir):
        if "node_modules" in root or ".git" in root or ".venv" in root:
            continue
            
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                checker = SyntaxChecker(path)
                errors = checker.check()
                
                if errors:
                    found_errors = True
                    print(f"❌ {path}:")
                    for error in errors:
                        print(f"  - {error}")
                    print("")
    
    if not found_errors:
        print("✅ No syntax errors found in HTML files.")

if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    check_structure(root)
