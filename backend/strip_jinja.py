import os
import re

frontend_dir = 'd:\\schemeBot\\frontend'

jinja_block_pattern = re.compile(r'\{%.*?%\}', re.DOTALL)
jinja_var_pattern = re.compile(r'\{\{.*?\}\}', re.DOTALL)

for root, dirs, files in os.walk(frontend_dir):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove {% commands %}
            new_content = re.sub(jinja_block_pattern, '', content)
            
            # Optionally replace {{ vars }} with a span so it doesn't break layout too much
            new_content = re.sub(jinja_var_pattern, '<span class="dynamic-data"></span>', new_content)
            
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Stripped Jinja from {file}")
