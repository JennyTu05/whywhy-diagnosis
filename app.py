from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

why_tree = {}

def safe_id(text):
    # Mermaid ID 避免特殊字元
    return ''.join(c if c.isalnum() else '_' for c in text)

def escape_mermaid_text(text):
    max_len = 6
    parts = [text[i:i+max_len] for i in range(0, len(text), max_len)]
    return '<br>'.join(parts).replace('"', '\\"')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_reason', methods=['POST'])
def update_reason():
    global why_tree
    node = request.form.get('node', '').strip()
    reason1 = request.form.get('reason1', '').strip()
    reason2 = request.form.get('reason2', '').strip()

    if not node:
        return jsonify({'status': 'error', 'message': '節點不可為空'})

    if node not in why_tree:
        why_tree[node] = []

    for reason in (reason1, reason2):
        if reason and reason not in why_tree[node]:
            why_tree[node].append(reason)
            if reason not in why_tree:
                why_tree[reason] = []

    return jsonify({'status': 'success'})

@app.route('/get_mermaid')
def get_mermaid():
    def draw(node):
        if node not in why_tree or not why_tree[node]:
            return []
        lines = []
        for reason in why_tree[node]:
            lines.append(
                f'{safe_id(node)}["{escape_mermaid_text(node)}"] --> {safe_id(reason)}["{escape_mermaid_text(reason)}"]'
            )
            lines.extend(draw(reason))
        return lines

    if not why_tree:
        return jsonify({'code': 'graph TD\nA["請輸入第一個問題"]'})

    root = list(why_tree.keys())[0]
    lines = ['graph TD']
    lines.append(f'{safe_id(root)}["{escape_mermaid_text(root)}"]')
    lines.extend(draw(root))
    return jsonify({'code': '\n'.join(lines)})

@app.route('/clear', methods=['POST'])
def clear():
    global why_tree
    why_tree = {}
    return jsonify({'status': 'cleared'})

if __name__ == '__main__':
    app.run(debug=True)
