def ghvis(file):
    from pyvis.network import Network
    import pandas as pd
    import random
    import time

    li = ['1', '2', '3', '4', '5', '6', '7', '8', '9',
     '0', 'a', 'b', 'c', 'd', 'e', 'f',
     'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
     'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    random.shuffle(li)
    name = li[:7]
    name = str(''.join(name)) + '.html'


    net = Network(height='750px', width='100%', bgcolor='#222222', font_color='white')

    net.barnes_hut()
    data = pd.read_csv(file, delimiter = ',')

    sources = data['Source']
    targets = data['Target']
    weights = data['Weight']

    edge_data = zip(sources, targets, weights)

    for edge in edge_data:
        src = edge[0]
        dst = edge[1]
        w = edge[2]

        net.add_node(src, src, title=src)
        net.add_node(dst, dst, title=dst)
        net.add_edge(src, dst, value=w)

    neighbor_map = net.get_adj_list()

    for node in net.nodes:
        node['title'] += ' Neighbors:<br>' + '<br>'.join(neighbor_map[node['id']])
        node['value'] = len(neighbor_map[node['id']])

    net.save_graph(name)




    from github import Github

    g = Github("a token was here")
    repo = g.get_repo("icba-manager/icba-manager.github.io")

    with open(name, 'r') as f:
        content=f.read()
    repo.create_file(name, 'upload html', content)
    global link2gh
    link2gh = 'https://icba-manager.github.io/' + name
    time.sleep(130)
    return link2gh
