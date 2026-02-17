#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Static site generator for wiki-netlify.
Reads markdown from content/ and generates HTML in dist/.
Paths are relative to script location.
"""
import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime

try:
    import markdown
except ImportError:
    print("Error: markdown library not installed. Run: pip install markdown")
    exit(1)
try:
    import rcssmin
    import rjsmin
except ImportError:
    print("Error: rcssmin and rjsmin required for minification. Run: pip install rcssmin rjsmin")
    exit(1)

# Paths relative to script location
BASE_DIR = Path(__file__).resolve().parent
WIKI_PAGES_DIR = BASE_DIR / 'content'
TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'
DIST_DIR = BASE_DIR / 'dist'
SITE_TITLE = "Континент: много веков спустя"

# Category order on index page
CATEGORY_ORDER = ['предыстории', 'сеттинг', 'порча']

# Markdown extensions
MD_EXTENSIONS = [
    'codehilite',
    'tables',
    'fenced_code',
    'nl2br',
]

def read_template(name):
    """Read HTML template file"""
    template_path = TEMPLATES_DIR / name
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_markdown_file(file_path):
    """Read and parse markdown file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract title (first # header)
    title_match = re.match(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else file_path.stem
    
    # Remove title from content for processing
    content_body = re.sub(r'^#\s+.+$', '', content, count=1, flags=re.MULTILINE).strip()
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=MD_EXTENSIONS)
    html_content = md.convert(content_body)
    
    return title, html_content

def get_category_structure(pages_dir):
    """Build category structure from directory tree"""
    categories = {}
    pages = []
    
    for md_file in pages_dir.rglob('*.md'):
        rel_path = md_file.relative_to(pages_dir)
        parts = rel_path.parts
        
        # Read page
        title, content = read_markdown_file(md_file)
        
        # Build URL path
        url_parts = [p for p in parts[:-1]]  # All but filename
        filename = parts[-1].replace('.md', '')
        url_path = '/'.join(url_parts + [filename]) if url_parts else filename
        url = f"/{url_path}.html"
        
        page_data = {
            'title': title,
            'url': url,
            'path': str(rel_path),
            'category': url_parts[0] if url_parts else 'root',
            'content': content,
            'filename': filename,
        }
        pages.append(page_data)
        
        # Build category structure
        if url_parts:
            cat = url_parts[0]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(page_data)
        else:
            if 'root' not in categories:
                categories['root'] = []
            categories['root'].append(page_data)
    
    return categories, pages

def generate_index_page(categories, pages, template):
    """Generate main index page with fixed category order."""
    categories_html = '<div class="categories">'
    
    # Ordered categories first
    for cat_name in CATEGORY_ORDER:
        if cat_name not in categories:
            continue
        cat_pages = categories[cat_name]
        categories_html += '<div class="category">'
        categories_html += f'<h2>{cat_name.capitalize()}</h2>'
        categories_html += '<ul class="page-list">'
        for page in sorted(cat_pages, key=lambda x: x['title']):
            categories_html += f'<li><a href="{page["url"]}">{page["title"]}</a></li>'
        categories_html += '</ul></div>'
    
    # Root pages (if any)
    root_pages_html = ''
    if 'root' in categories:
        root_pages_html = '<div class="category"><h2>Другие статьи</h2><ul class="page-list">'
        for page in sorted(categories['root'], key=lambda x: x['title']):
            root_pages_html += f'<li><a href="{page["url"]}">{page["title"]}</a></li>'
        root_pages_html += '</ul></div>'
    
    html = template.replace('{{TITLE}}', SITE_TITLE)
    html = html.replace('{{CONTENT}}', categories_html + root_pages_html)
    html = html.replace('{{PAGE_TITLE}}', 'Главная')
    html = html.replace('{{BREADCRUMBS}}', '<a href="/">Главная</a>')
    
    return html

def generate_article_page(page, categories, template):
    """Generate article page"""
    # Build breadcrumbs
    breadcrumbs = '<a href="/">Главная</a>'
    if page['category'] != 'root':
        breadcrumbs += f' / <a href="/#{page["category"]}">{page["category"].capitalize()}</a>'
    breadcrumbs += f' / {page["title"]}'
    
    # Build navigation (previous/next)
    all_pages = []
    for cat_name in CATEGORY_ORDER:
        if cat_name in categories:
            all_pages.extend(categories[cat_name])
    if 'root' in categories:
        all_pages.extend(categories['root'])
    all_pages.sort(key=lambda x: x['title'])
    
    current_idx = next((i for i, p in enumerate(all_pages) if p['url'] == page['url']), -1)
    nav_html = ''
    if current_idx > 0:
        prev_page = all_pages[current_idx - 1]
        nav_html += f'<a href="{prev_page["url"]}" class="nav-prev">← {prev_page["title"]}</a>'
    if current_idx < len(all_pages) - 1:
        next_page = all_pages[current_idx + 1]
        nav_html += f'<a href="{next_page["url"]}" class="nav-next">{next_page["title"]} →</a>'
    
    html = template.replace('{{TITLE}}', SITE_TITLE)
    html = html.replace('{{CONTENT}}', page['content'])
    html = html.replace('{{PAGE_TITLE}}', page['title'])
    html = html.replace('{{BREADCRUMBS}}', breadcrumbs)
    html = html.replace('{{NAVIGATION}}', nav_html)
    
    return html

def generate_search_index(pages):
    """Generate JSON index for search"""
    search_index = []
    for page in pages:
        # Extract text content (strip HTML tags for search)
        text_content = re.sub(r'<[^>]+>', ' ', page['content'])
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        search_index.append({
            'title': page['title'],
            'url': page['url'],
            'category': page['category'],
            'content': text_content[:500],  # First 500 chars for preview
        })
    
    return search_index

def copy_static_files():
    """Copy static files to dist; minify CSS and JS."""
    static_dest = DIST_DIR / 'static'
    if static_dest.exists():
        shutil.rmtree(static_dest)
    static_dest.mkdir(parents=True)
    for src in STATIC_DIR.rglob('*'):
        if src.is_file():
            rel = src.relative_to(STATIC_DIR)
            dest = static_dest / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            if src.suffix == '.css':
                with open(src, 'r', encoding='utf-8') as f:
                    content = rcssmin.cssmin(f.read())
                with open(dest, 'w', encoding='utf-8') as f:
                    f.write(content)
            elif src.suffix == '.js':
                with open(src, 'r', encoding='utf-8') as f:
                    content = rjsmin.jsmin(f.read())
                with open(dest, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                shutil.copy2(src, dest)

def main():
    print("Building wiki site...")
    
    # Check directories
    if not WIKI_PAGES_DIR.exists():
        print(f"Error: Wiki pages directory not found: {WIKI_PAGES_DIR}")
        return 1
    
    if not TEMPLATES_DIR.exists():
        print(f"Error: Templates directory not found: {TEMPLATES_DIR}")
        return 1
    
    # Clean dist
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir()
    
    # Read templates
    print("Reading templates...")
    index_template = read_template('index.html')
    article_template = read_template('article.html')
    search_template = read_template('search.html')
    
    # Get pages structure
    print("Scanning markdown files...")
    categories, pages = get_category_structure(WIKI_PAGES_DIR)
    print(f"Found {len(pages)} pages in {len(categories)} categories")
    
    # Generate pages
    print("Generating HTML pages...")
    
    # Index page
    index_html = generate_index_page(categories, pages, index_template)
    with open(DIST_DIR / 'index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
    print("  Generated: index.html")
    
    # Search page
    search_html = search_template.replace('{{TITLE}}', SITE_TITLE)
    search_html = search_html.replace('{{BREADCRUMBS}}', '<a href="/">Главная</a> / Поиск')
    with open(DIST_DIR / 'search.html', 'w', encoding='utf-8') as f:
        f.write(search_html)
    print("  Generated: search.html")
    
    # Article pages
    for page in pages:
        html = generate_article_page(page, categories, article_template)
        
        # Create directory structure
        url_path = Path(page['url'].lstrip('/'))
        output_path = DIST_DIR / url_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  Generated: {url_path}")
    
    # Generate search index
    print("Generating search index...")
    search_index = generate_search_index(pages)
    with open(DIST_DIR / 'search-index.json', 'w', encoding='utf-8') as f:
        json.dump(search_index, f, ensure_ascii=False, indent=2)
    print("  Generated: search-index.json")
    
    # Copy static files
    print("Copying static files...")
    copy_static_files()
    print("  Copied static files")
    
    print(f"\n✓ Build complete! Generated {len(pages) + 1} pages in {DIST_DIR}/")
    return 0

if __name__ == '__main__':
    exit(main())
