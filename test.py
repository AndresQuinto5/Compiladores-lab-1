import json
import graphviz

'''
    Parseo la expresion regular y la convierto en un arbol de expresiones
    Donde indico el tipo de nodo y sus hijos
'''
def parse_regex(text):
    def parse_sub(text, begin, end, first):
        last = 0
        node = {'begin': begin, 'end': end}
        stack = 0
        parts = []
        
        if len(text) == 0:
            return f"Error: empty input at {begin}."
        
        if first:
            for i in range(len(text) + 1):
                if i == len(text) or (text[i] == '|' and stack == 0):
                    if last == 0 and i == len(text):
                        return parse_sub(text, begin + last, begin + i, False)
                    
                    sub = parse_sub(text[last:i], begin + last, begin + i, True)
                    if isinstance(sub, str):
                        return sub
                    
                    parts.append(sub)
                    last = i + 1
                elif text[i] == '(':
                    stack += 1
                elif text[i] == ')':
                    stack -= 1
            
            if len(parts) == 1:
                return parts[0]
            
            node['type'] = 'or'
            node['parts'] = parts
        else:
            i = 0
            while i < len(text):
                if text[i] == '(':
                    last = i + 1
                    i += 1
                    stack = 1
                    while i < len(text) and stack != 0:
                        if text[i] == '(':
                            stack += 1
                        elif text[i] == ')':
                            stack -= 1
                        i += 1
                    
                    if stack != 0:
                        return f"Error: missing right bracket for {begin + last}."
                    
                    i -= 1
                    sub = parse_sub(text[last:i], begin + last, begin + i, True)
                    if isinstance(sub, str):
                        return sub
                    
                    sub['begin'] -= 1
                    sub['end'] += 1
                    parts.append(sub)
                elif text[i] == '*':
                    if len(parts) == 0:
                        return f"Error: unexpected * at {begin + i}."
                    
                    temp_node = {'begin': parts[-1]['begin'], 'end': parts[-1]['end'] + 1}
                    temp_node['type'] = 'star'
                    temp_node['sub'] = parts[-1]
                    parts[-1] = temp_node
                elif text[i] == '+':
                    if len(parts) == 0:
                        return f"Error: unexpected + at {begin + i}."
                    
                    vir_node = {'begin': parts[-1]['begin'], 'end': parts[-1]['end'] + 1}
                    vir_node['type'] = 'star'
                    vir_node['sub'] = parts[-1]
                    temp_node = {'begin': parts[-1]['begin'], 'end': parts[-1]['end'] + 1}
                    temp_node['type'] = 'cat'
                    temp_node['parts'] = [parts[-1], vir_node]
                    parts[-1] = temp_node
                elif text[i] == '?':
                    if len(parts) == 0:
                        return f"Error: unexpected ? at {begin + i}."
                    
                    vir_node = {'begin': parts[-1]['begin'], 'end': parts[-1]['end'] + 1}
                    vir_node['type'] = 'empty'
                    vir_node['sub'] = parts[-1]
                    temp_node = {'begin': parts[-1]['begin'], 'end': parts[-1]['end'] + 1}
                    temp_node['type'] = 'or'
                    temp_node['parts'] = [parts[-1], vir_node]
                    parts[-1] = temp_node
                elif text[i] == 'ϵ':
                    temp_node = {'begin': begin + i, 'end': begin + i + 1}
                    temp_node['type'] = 'empty'
                    parts.append(temp_node)
                else:
                    temp_node = {'begin': begin + i, 'end': begin + i + 1}
                    temp_node['type'] = 'text'
                    temp_node['text'] = text[i]
                    parts.append(temp_node)
                i += 1

            if len(parts) == 1:
                return parts[0]

            node['type'] = 'cat'
            node['parts'] = parts

        return node

    return parse_sub(text, 0, len(text), True)

'''
This is the function regex to NFA
Use the tree of expressions to generate the NFA
'''

def regex_to_nfa(text):
    def generate_graph(node, start, end, count):
        nonlocal ast
        if 'id' not in start:
            start['id'] = count
            count += 1

        if node['type'] == 'empty':
            start['edges'].append(['ϵ', end])
        elif node['type'] == 'text':
            start['edges'].append([node['text'], end])
        elif node['type'] == 'cat':
            last = start
            for i in range(len(node['parts']) - 1):
                temp = {'type': '', 'edges': []}
                count = generate_graph(node['parts'][i], last, temp, count)
                last = temp
            count = generate_graph(node['parts'][-1], last, end, count)
        elif node['type'] == 'or':
            for i in range(len(node['parts'])):
                temp_start = {'type': '', 'edges': []}
                temp_end = {'type': '', 'edges': [['ϵ', end]]}
                start['edges'].append(['ϵ', temp_start])
                count = generate_graph(node['parts'][i], temp_start, temp_end, count)
        elif node['type'] == 'star':
            temp_start = {'type': '', 'edges': []}
            temp_end = {'type': '', 'edges': [['ϵ', temp_start], ['ϵ', end]]}
            start['edges'].append(['ϵ', temp_start])
            start['edges'].append(['ϵ', end])
            count = generate_graph(node['sub'], temp_start, temp_end, count)

        if 'id' not in end:
            end['id'] = count
            count += 1

        return count

    ast = parse_regex(text)
    start = {'type': 'start', 'edges': []}
    accept = {'type': 'accept', 'edges': []}

    if isinstance(ast, str):
        return ast

    generate_graph(ast, start, accept, 0)
    return start

'''
    Esta funcion la utilizo para dibujar el NFA
    recibe como parametro el NFA en un formato con sus nodos, conexiones y demas
    procede a dibujar el NFA.
'''

def draw_nfa(nfa):
    def traverse_graph(node, visited_nodes, transitions):
        nonlocal dot

        if node['id'] in visited_nodes:
            return
        visited_nodes.add(node['id'])

        for edge in node['edges']:
            label, target_node = edge
            dot.edge(str(node['id']), str(target_node['id']), label=label)
            transitions.append((node['id'], label, target_node['id']))
            traverse_graph(target_node, visited_nodes, transitions)

    dot = graphviz.Digraph()
    visited = set()
    transitions = []

    traverse_graph(nfa, visited, transitions)

    return dot, transitions

'''
    Esta funcion la utilizo para generar la tabla de transiciones
    leyendo el NFA y generando la tabla de transiciones en un formato txt
'''

def generate_transition_table(transitions):
    # Sort transitions by start node id
    transitions.sort(key=lambda x: x[0])

    with open('transition_table.txt', 'w', encoding='utf-8') as f:
        f.write("Transition Table:\n")
        f.write("Start State: {}\n".format(transitions[0][0]))
        f.write("Accept State: {}\n\n".format([transition[2] for transition in transitions if transition[2] in [edge[1]['id'] for edge in nfa['edges'] if edge[1]['type'] == 'accept']][0] if [transition[2] for transition in transitions if transition[2] in [edge[1]['id'] for edge in nfa['edges'] if edge[1]['type'] == 'accept']] else 'None'))
        f.write("From\tInput\tTo\n")
        for start, label, end in transitions:
            f.write("{}\t{}\t{}\n".format(start, label, end))


def traverse_nfa_nodes(nfa):
    nodes = []

    def traverse(node):
        if 'visited' in node:
            return
        node['visited'] = True
        nodes.append(node)
        for edge in node['edges']:
            label, target_node = edge
            traverse(target_node)

    traverse(nfa)
    for node in nodes:
        del node['visited']
    return nodes

'''

    AQUI EVALUO SI SE ACEPTA LA CADENA O NO PARA EL NFA
'''

def evaluate_nfa(nfa, input_string):
    def epsilon_closure(state_id, closure):
        if state_id in closure:
            return
        closure.add(state_id)
        state = state_map[state_id]
        for edge in state['edges']:
            label, target_node = edge
            if label == 'ϵ':
                epsilon_closure(target_node['id'], closure)

    def move(state_id, input_char):
        next_states = set()
        state = state_map[state_id]
        for edge in state['edges']:
            label, target_node = edge
            if label == input_char:
                next_states.add(target_node['id'])
        return next_states

    state_map = {node['id']: node for node in traverse_nfa_nodes(nfa)}

    current_states = set()
    epsilon_closure(nfa['id'], current_states)

    for char in input_string:
        next_states = set()
        for state_id in current_states:
            move_states = move(state_id, char)
            for move_state_id in move_states:
                epsilon_closure(move_state_id, next_states)
        current_states = next_states

    for state_id in current_states:
        state = state_map[state_id]
        if state['type'] == 'accept':
            return 'ACEPTADA'

    return 'NO ACEPTADA'

#DFA SECTION:
def nfa_to_dfa(nfa):
    def get_closure(nodes):
        closure = []
        stack = []
        symbols = []
        node_type = ''
        for node in nodes:
            stack.append(node)
            closure.append(node)
            if node['type'] == 'accept':
                node_type = 'accept'
        while len(stack) > 0:
            top = stack.pop()
            for edge in top['edges']:
                if edge[0] == 'ϵ':
                    if edge[1] not in closure:
                        stack.append(edge[1])
                        closure.append(edge[1])
                        if edge[1]['type'] == 'accept':
                            node_type = 'accept'
                else:
                    if edge[0] not in symbols:
                        symbols.append(edge[0])
        closure.sort(key=lambda x: x['id'])
        symbols.sort()
        return {
            'key': ','.join([str(x['id']) for x in closure]),
            'items': closure,
            'symbols': symbols,
            'type': node_type,
            'edges': [],
            'trans': {}
        }

    def get_closed_move(closure, symbol):
        nexts = []
        for node in closure['items']:
            for edge in node['edges']:
                if symbol == edge[0]:
                    if edge[1] not in nexts:
                        nexts.append(edge[1])
        return get_closure(nexts)

    def to_alpha_count(n):
        a = ord('A')
        z = ord('Z')
        length = z - a + 1
        s = ''
        while n >= 0:
            s = chr(n % length + a) + s
            n = n // length - 1
        return s

    first = get_closure([nfa])
    states = {}
    front = 0
    queue = [first]
    count = 0
    first['id'] = to_alpha_count(count)
    states[first['key']] = first
    while front < len(queue):
        top = queue[front]
        front += 1
        for symbol in top['symbols']:
            closure = get_closed_move(top, symbol)
            if closure['key'] not in states:
                count += 1
                closure['id'] = to_alpha_count(count)
                states[closure['key']] = closure
                queue.append(closure)
            top['trans'][symbol] = states[closure['key']]
            top['edges'].append([symbol, states[closure['key']]])
    return first

def draw_dfa(dfa):
    def traverse_graph(node, visited_nodes, transitions):
        nonlocal dot

        if node['id'] in visited_nodes:
            return
        visited_nodes.add(node['id'])

        for edge in node['edges']:
            label, target_node = edge
            dot.edge(str(node['id']), str(target_node['id']), label=label)
            transitions.append((node['id'], label, target_node['id']))
            traverse_graph(target_node, visited_nodes, transitions)

    dot = graphviz.Digraph()
    visited = set()
    transitions = []

    traverse_graph(dfa, visited, transitions)

    return dot, transitions

def generate_dfa_transition_table(transitions):
    transitions.sort(key=lambda x: x[0])

    with open('dfa_transition_table.txt', 'w', encoding='utf-8') as f:
        f.write("Transition Table (DFA):\n")
        f.write("Start State: {}\n".format(transitions[0][0]))
        f.write("Accept State(s): {}\n\n".format(sorted([transition[2] for transition in transitions if transition[2] in [edge[1]['id'] for edge in dfa['edges'] if edge[1]['type'] == 'accept']])))
        f.write("From\tInput\tTo\n")
        for start, label, end in transitions:
            f.write("{}\t{}\t{}\n".format(start, label, end))

def evaluate_dfa(dfa, input_string):
    def move(state, input_char):
        next_state = None
        for edge in state['edges']:
            label, target_node = edge
            if label == input_char:
                next_state = target_node
                break
        return next_state

    current_state = dfa

    for char in input_string:
        current_state = move(current_state, char)
        if current_state is None:
            break

    if current_state is not None and current_state['type'] == 'accept':
        return 'ACEPTADA'

    return 'NO ACEPTADA'
'''
    algoritmo de minimizacion de DFA
'''


def min_dfa(dfa):
    def get_reverse_edges(start):
        front = 0
        queue = [start]
        visited = {}
        symbols = {}
        id_map = {}
        rev_edges = {}
        visited[start['id']] = True
        while front < len(queue):
            top = queue[front]
            front += 1
            id_map[top['id']] = top
            for symbol in top['symbols']:
                if symbol not in symbols:
                    symbols[symbol] = True
                next_node = top['trans'][symbol]
                if next_node['id'] not in rev_edges:
                    rev_edges[next_node['id']] = {}
                if symbol not in rev_edges[next_node['id']]:
                    rev_edges[next_node['id']][symbol] = []
                rev_edges[next_node['id']][symbol].append(top['id'])
                if next_node['id'] not in visited:
                    visited[next_node['id']] = True
                    queue.append(next_node)
        return list(symbols.keys()), id_map, rev_edges

    def hopcroft(symbols, id_map, rev_edges):
        ids = sorted(id_map.keys())
        partitions = {}
        front = 0
        queue = []
        visited = {}
        group1 = []
        group2 = []
        for id in ids:
            if id_map[id]['type'] == 'accept':
                group1.append(id)
            else:
                group2.append(id)
        key = ','.join(group1)
        partitions[key] = group1
        queue.append(key)
        visited[key] = 0
        if group2:
            key = ','.join(group2)
            partitions[key] = group2
            queue.append(key)
        while front < len(queue):
            top = queue[front]
            front += 1
            if top:
                top = top.split(',')
                for symbol in symbols:
                    rev_group = {}
                    for id in top:
                        if id in rev_edges and symbol in rev_edges[id]:
                            for from_id in rev_edges[id][symbol]:
                                rev_group[from_id] = True
                    keys = list(partitions.keys())
                    for key in keys:
                        group1 = []
                        group2 = []
                        for id in partitions[key]:
                            if id in rev_group:
                                group1.append(id)
                            else:
                                group2.append(id)
                        if group1 and group2:
                            del partitions[key]
                            key1 = ','.join(group1)
                            key2 = ','.join(group2)
                            partitions[key1] = group1
                            partitions[key2] = group2
                            if key1 in visited:
                                queue[visited[key1]] = None
                                visited[key1] = len(queue)
                                queue.append(key1)
                                visited[key2] = len(queue)
                                queue.append(key2)
                            elif len(group1) <= len(group2):
                                visited[key1] = len(queue)
                                queue.append(key1)
                            else:
                                visited[key2] = len(queue)
                                queue.append(key2)
        return list(partitions.values())

    def build_min_nfa(start, partitions, id_map, rev_edges):
        nodes = []
        group = {}
        edges = {}
        partitions.sort(key=lambda x: ','.join(x))
        for i, partition in enumerate(partitions):
            if start['id'] in partition:
                if i > 0:
                    temp = partitions[i]
                    partitions[i] = partitions[0]
                    partitions[0] = temp
                break
        for i, partition in enumerate(partitions):
            node = {
                'id': str(i + 1),
                'key': ','.join(partition),
                'items': [],
                'symbols': [],
                'type': id_map[partition[0]]['type'],
                'edges': [],
                'trans': {},
            }
            for id in partition:
                node['items'].append(id_map[id])
                group[id] = i
            edges[i] = {}
            nodes.append(node)

        for to in rev_edges:
            for symbol in rev_edges[to]:
                for from_id in rev_edges[to][symbol]:
                    if group[from_id] not in edges:  # Verificar si la clave existe en el diccionario
                        edges[group[from_id]] = {}
                    if group[to] not in edges[group[from_id]]:
                        edges[group[from_id]][group[to]] = {}
                    if symbol not in edges[group[from_id]][group[to]]:
                        edges[group[from_id]][group[to]][symbol] = True

        for from_id in edges:
            for to in edges[from_id]:
                symbols = ','.join(sorted(edges[from_id][to].keys()))
                nodes[from_id]['symbols'].append(symbols)
                nodes[from_id]['edges'].append([symbols, nodes[to]])
                for symbol in symbols.split(','):
                    if symbol not in nodes[from_id]['trans']:
                        nodes[from_id]['trans'][symbol] = nodes[to]

        return nodes[0]



    edges_tuple = get_reverse_edges(dfa)
    symbols = edges_tuple[0]
    id_map = edges_tuple[1]
    rev_edges = edges_tuple[2]
    partitions = hopcroft(symbols, id_map, rev_edges)

    return build_min_nfa(dfa, partitions, id_map, rev_edges)


def min_dfa_to_dict(min_dfa):
    dfa_dict = {
        "id": min_dfa["id"],
        "key": min_dfa["key"],
        "items": [item["id"] for item in min_dfa["items"]],
        "symbols": min_dfa["symbols"],
        "type": min_dfa["type"],
        "edges": [
            {"symbol": edge[0], "to": edge[1]["id"]} for edge in min_dfa["edges"]
        ],
        "trans": {symbol: node["id"] for symbol, node in min_dfa["trans"].items()},
    }

    return dfa_dict


def save_min_dfa_to_json(min_dfa, filename):
    dfa_dict = min_dfa_to_dict(min_dfa)
    with open(filename, "w") as f:
        json.dump(dfa_dict, f, indent=2)


#Funcion que utilizo para dibujar el automata finito determinista minimizado

def draw_min_dfa(dfa):
    def traverse_graph(node, visited_nodes, transitions):
        nonlocal dot

        if node['id'] in visited_nodes:
            return
        visited_nodes.add(node['id'])

        for edge in node['edges']:
            label, target_node = edge
            dot.edge(str(node['id']), str(target_node['id']), label=label)
            transitions.append((node['id'], label, target_node['id']))
            traverse_graph(target_node, visited_nodes, transitions)

    dot = graphviz.Digraph()
    visited = set()
    transitions = []

    traverse_graph(dfa, visited, transitions)

    return dot, transitions


'''
    Flujo donde se ejecuta el programa y sus funciones
'''

# Generate the transition table and save it to a .txt file
regex = input("Ingresa la expresión regular: ")
cadena = input("Ingresa la cadena a evaluar: ")

method_choice = input("Elige el método de construcción (1: Construcción Directa, 2: Construcción de Subconjuntos): ")
use_direct_method = method_choice == '1'

if use_direct_method:
    print('hola')


else:
    # Construcción de NFA y DFA utilizando construcción de subconjuntos
    nfa = regex_to_nfa(regex)

    dot, transitions = draw_nfa(nfa)

    # Set the direction of the layout to left-to-right
    dot.attr(rankdir='LR')

    # Set the output format to jpg
    dot.format = 'jpg'

    # Render the graph to a JPG file
    dot.render('nfa', view=True)
    
    print('Tabla de transiciones para NFA creada')
    generate_transition_table(transitions)
    evaluate_nfa(nfa, cadena)
    print('La cadena fue:', evaluate_nfa(nfa, cadena))
    dfa = nfa_to_dfa(nfa)

    dot, transitions = draw_dfa(dfa)

    # Set the direction of the layout to left-to-right
    dot.attr(rankdir='LR')

    # Set the output format to jpg
    dot.format = 'jpg'

    # Render the graph to a JPG file
    dot.render('dfa', view=True)

    print('Tabla de transiciones para DFA creada')
    generate_dfa_transition_table(transitions)
    evaluate_dfa(dfa, cadena)
    print('La cadena fue:', evaluate_dfa(nfa, cadena))
    # Minimización del DFA y dibujo del DFA minimizado
    min_dfa2 = min_dfa(dfa)

    dot, transitions = draw_min_dfa(min_dfa2)

    # Set the direction of the layout to left-to-right
    dot.attr(rankdir='LR')

    # Set the output format to jpg
    dot.format = 'jpg'

    # Render the graph to a JPG file
    dot.render('min_dfa', view=True)
    minimized_dfa = min_dfa(dfa)
    save_min_dfa_to_json(minimized_dfa, "minimized_dfa.json")

    print('Tabla de transiciones para DFA minimizado creada')

'''
UTILS:
regex_str = "((ε|a)b*)*"
regex_dict = parse_regex(regex_str)
print(regex_dict)

with open("parsed_regex.json", "w") as f:
    json.dump(regex_dict, f, indent=4)
'''

