import bandicoot as bc
from collections import Counter


def write_antenna_csv(user, pointer):
    f = pointer
    f.write('id,latitude,longitude,interactions\n')
    for id, (lat, lon) in user.antennas.items():
        interactions = sum([1 for r in user.records if r.position.antenna == id])
        f.write("{},{},{},{}\n".format(id, lat, lon, interactions))

def write_transitions_csv(user, pointer):
    antennas_id = [r.position.antenna for r in user.records]
    transitions = Counter([(min(i, j), max(i, j)) for (i, j) in zip(antennas_id, antennas_id[1:])])
    f = pointer
    f.write('source,target,amount\n')
    for (source, target), count in transitions.items():
        if source != target:
            f.write("{},{},{}\n".format(source, target, count))


def write_timeline_csv(user, pointer):
    f = pointer
    f.write('time,type,call_duration\n')
    records = filter(lambda r: r.interaction, user.records)
    for r in records:
        time = r.datetime.strftime('%d-%m-%y %H:%M')
        interaction = ('inc_' if r.direction == 'in' else 'out_') + r.interaction
        call_duration = r.call_duration or ''
        f.write("{},{},{}\n".format(time, interaction, call_duration))


def write_network_csv(user, nodes_pointer, links_pointer, decode_name):
    m_texts = bc.network.matrix_directed_weighted(user, 'text')
    m_calls = bc.network.matrix_directed_weighted(user, 'call')
    nb_users = len(m_texts)

    links = []

    for i in range(nb_users):
        for j in range(nb_users):
            source_calls = m_calls[j][i] or 0
            target_calls = m_calls[i][j] or 0
            source_texts = m_texts[j][i] or 0
            target_texts = m_texts[i][j] or 0

            if i < j and source_calls + target_calls + source_texts + target_texts > 0:
                links.append([i, j, (source_calls, target_calls, source_texts, target_texts)])

    names = [user.name] + [i for i in user.network.keys() if i != user.name]
    nodes = set(l[0] for l in links) | set(l[1] for l in links)

    f = nodes_pointer
    f.write('name,no_network_info\n')
    for n in nodes:
        f.write("{},{}\n".format(decode_name(names[n]), int(None in m_texts[n] or None in m_calls[n])))

    compress_ids = dict(zip(nodes, range(len(nodes))))
    f = links_pointer
    f.write('source,target,source_calls,target_calls,source_texts,target_texts\n')
    for i, j, data in links:
        f.write("{},{},{},{},{},{}\n".format(*(compress_ids[i], compress_ids[j]) + data))
