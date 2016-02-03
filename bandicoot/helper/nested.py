import itertools

def _nested_helper(leaf_list, node_content, leaf_content, index=0):
    # We return the string as a list of strings for efficiency.
    out = []

    # We will be working with the 0 through index of the leaf specifiers.
    # If this fully specifies the leaf, we print the leaf.
    # If this does not, we print the "node" and then recurse
    # on the set of everything under it.
    leaf_list.sort(key=lambda x: x[0:index + 1]);
    group_iterator = itertools.groupby(leaf_list, lambda x: x[0:index + 1])
    group_dict = {}
    for key, value in group_iterator:
        group_dict[key] = list(value)
    keys = group_dict.keys()
    keys.sort()

    for key in keys:
        # The key *is* a leaf, since its length is the same as
        # one of the leaf specifiers 'under' it.
        if (len(key) == min(len(l) for l in group_dict[key])):
            # The leaf should not have children.
            assert(len(group_dict[key]) == 1)
            leaf = "<li>"+leaf_content(key)+"</li>"
            out.append(leaf)
        else:
            # Recurse.
            internal = _nested_helper(group_dict[key],
                                      node_content, leaf_content,
                                      index=len(key))
            # Introduce the category.
            openpart = """
               <li class="parent">
                 <span class="parent_text">
                   """ + node_content(key) + """
                 </span>
                 <ul>"""
            # Close the category.
            closepart = """
                 </ul>
               </li>"""
            out.append(openpart)
            out.extend(internal)
            out.append(closepart)
    return out

def _squash(ls):
    '''
    flattens a nested list
    '''
    out = []
    for elem in ls:
        if type(elem) == type([]):
            out.extend(_squash(elem))
        else:
            out.append(elem)
    return out

def nested(leaf_list, node_content, leaf_content):
    '''
    Takes a set of leaves and lays them out in a nested HTML
    tree list that will work with the nested js/css to hide
    children in the usual way.  Tree in alphabetical order. child

    Input a list of elements of the form
    ( ..., leaf's grandparent, leaf's parent, leaf)
    and a node_content and leaf_content function.

    Leaves will be grouped by common ancestor; the html at
    the junction will be node_content(common ancestors tuple).

    The html at the leaf is determined will be
    leaf_content(specifying tuple).
    '''
    leaf_list = list(set(leaf_list))
    out = _nested_helper(leaf_list, node_content, leaf_content, 0)
    out = ["<ul>"] + _squash(out) + ["</ul>"]
    out = "".join(out)
    out = out.split()
    out = " ".join(out)
    return out
