import os
import re

frontend_dir = r"d:\schemeBot\frontend"

for root, _, files in os.walk(frontend_dir):
    for filename in files:
        if filename.endswith(".html"):
            path = os.path.join(root, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Fix window.location.href = '/foo' -> window.location.href = 'foo.html'
            def js_replacer(match):
                link = match.group(1)
                # Avoid modifying already absolute or correct links
                if not link.endswith(".html") and link != "":
                    return f"window.location.href= '{link}.html'"
                return match.group(0)

            content = re.sub(r"window\.location\.href\s*=\s*'\/([^']*)'", js_replacer, content)
            content = re.sub(r'window\.location\.href\s*=\s*"\/([^"]*)"', lambda m: js_replacer(m).replace("'", '"'), content)

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fixed JS in {filename}")
