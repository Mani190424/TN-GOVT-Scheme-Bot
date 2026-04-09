import os
import re

frontend_dir = r"d:\schemeBot\frontend"

for root, _, files in os.walk(frontend_dir):
    for filename in files:
        if filename.endswith(".html"):
            path = os.path.join(root, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Fix href="/" -> href="index.html"
            content = re.sub(r'href="/"', 'href="index.html"', content)
            
            # Fix href="/something" -> href="something.html"
            def href_replacer(match):
                # Don't modify absolute URLs or anchor links
                link = match.group(1)
                if not link.endswith(".html") and not link.startswith("http") and link != "" and not link.startswith("#"):
                    return f'href="{link}.html"'
                return match.group(0)

            content = re.sub(r'href="/([^"]+)"', href_replacer, content)

            # Ensure api.js is included before </body>
            if "static/api.js" not in content and "</body>" in content:
                content = content.replace("</body>", "    <script src=\"static/api.js\"></script>\n</body>")

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fixed {filename}")
