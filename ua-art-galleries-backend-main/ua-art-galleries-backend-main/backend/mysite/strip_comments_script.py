import tokenize
import os

def strip_comments(file_path):
    try:
        with open(file_path, 'rb') as f:
            tokens = list(tokenize.tokenize(f.readline))
            
                             
        out_tokens = []
        for t in tokens:
            if t.exact_type == tokenize.COMMENT:
                continue
            out_tokens.append(t)
            
                    
        cleaned_source = tokenize.untokenize(out_tokens)
        with open(file_path, 'wb') as f:
            f.write(cleaned_source)
        return True
    except Exception as e:
        print(f"Failed {file_path}: {e}")
        return False

def clean_all(root_dir):
    cleaned = 0
    for dirpath, dirs, filenames in os.walk(root_dir):
                                  
        if 'venv' in dirpath or '.git' in dirpath or '__pycache__' in dirpath or 'migrations' in dirpath:
            continue
        for f in filenames:
            if f.endswith('.py'):
                file_path = os.path.join(dirpath, f)
                if strip_comments(file_path):
                    cleaned += 1
    print(f"Successfully removed comments from {cleaned} Python files.")

if __name__ == '__main__':
    root_dir = r"d:\ua-art-galleries-backend-mainORIGIN\ua-art-galleries-backend-main\ua-art-galleries-backend-main\backend\mysite"
    clean_all(root_dir)
