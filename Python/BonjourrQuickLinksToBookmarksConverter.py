import json
import time

def convert_bonjourr_to_html(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {input_file}")
        return

    # 1. Identify all items and separate Folders from Bookmarks
    items = {}
    roots = []
    
    # Identify top-level 'groups' defined in your linkgroups
    group_names = data.get('linkgroups', {}).get('groups', [])
    
    for key, value in data.items():
        if key.startswith('links') and isinstance(value, dict):
            item_id = value.get('_id', key)
            items[item_id] = {
                'id': item_id,
                'title': value.get('title', 'Untitled'),
                'url': value.get('url'),
                'parent': value.get('parent'),
                'is_folder': value.get('folder', False),
                'icon_url': value.get('icon', {}).get('value') if isinstance(value.get('icon'), dict) else None,
                'children': []
            }

    # 2. Build the tree structure
    final_tree = []
    for item_id, item in items.items():
        parent_id = item['parent']
        
        # If parent exists in our items, add as child
        if parent_id in items:
            items[parent_id]['children'].append(item)
        # If parent is a string name (like "Apps", "Coding") or None, it's a root
        else:
            final_tree.append(item)

    # 3. Generate HTML Content
    timestamp = int(time.time())
    html = [
        '<!DOCTYPE NETSCAPE-Bookmark-file-1>',
        '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
        '<TITLE>Bookmarks</TITLE>',
        '<H1>Bookmarks</H1>',
        '<DL><p>'
    ]

    def render_node(node, indent_level):
        indent = "    " * indent_level
        lines = []
        if node['is_folder']:
            lines.append(f'{indent}<DT><H3 ADD_DATE="{timestamp}" LAST_MODIFIED="{timestamp}">{node["title"]}</H3>')
            lines.append(f'{indent}<DL><p>')
            # Sort children by their original 'order' if available, otherwise alpha
            for child in sorted(node['children'], key=lambda x: x.get('title', '')):
                lines.extend(render_node(child, indent_level + 1))
            lines.append(f'{indent}</DL><p>')
        else:
            icon_str = f' ICON_URI="{node["icon_url"]}"' if node['icon_url'] else ""
            lines.append(f'{indent}<DT><A HREF="{node["url"]}" ADD_DATE="{timestamp}"{icon_str}>{node["title"]}</A>')
        return lines

    for root_node in sorted(final_tree, key=lambda x: x['title']):
        html.extend(render_node(root_node, 1))

    html.append('</DL><p>')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html))
    
    print(f"Successfully exported hierarchy to {output_file}")

# Paths
input_path = r"C:\Users\laxmi\Documents\bonjourr-export.json"
output_path = r"C:\Users\laxmi\Documents\bookmarks.html"

convert_bonjourr_to_html(input_path, output_path)