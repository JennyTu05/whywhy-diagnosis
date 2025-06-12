from flask import Flask, render_template, request, jsonify
from collections import defaultdict

app = Flask(__name__)

# 為每個節點儲存兩個子原因
why_tree = defaultdict(list)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_reason', methods=['POST'])
def update_reason():
    node = request.form['node'].strip()
    reason1 = request.form['reason1'].strip()
    reason2 = request.form['reason2'].strip()
    if node and reason1 and reason2:
        why_tree[node] = [reason1, reason2]
    return ('', 204)

@app.route('/clear', methods=['POST'])
def clear():
    why_tree.clear()
    return ('', 204)

@app.route('/get_mermaid')
def get_mermaid():
    id_map = {}
    id_counter = [0]

    def get_node_id(text):
        if text not in id_map:
            id_map[text] = f"node{id_counter[0]}"
            id_counter[0] += 1
        return id_map[text]

    def draw(node):
        lines = []
        if node not in why_tree or not why_tree[node]:
            return lines
        for reason in why_tree[node]:
            parent_id = get_node_id(node)
            child_id = get_node_id(reason)
            lines.append(f'{parent_id}["{escape_mermaid_text(node)}"] --> {child_id}["{escape_mermaid_text(reason)}"]')
            lines.extend(draw(reason))
        return lines

    if not why_tree:
        return jsonify({'code': 'graph TD\nA["請輸入第一個問題"]'})

    root = list(why_tree.keys())[0]
    lines = ['graph TD']
    lines.extend(draw(root))
    return jsonify({'code': '\n'.join(lines)})

def escape_mermaid_text(text):
    return text.replace('"', '\\"')

if __name__ == '__main__':
    app.run(debug=True)
