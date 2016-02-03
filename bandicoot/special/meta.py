import bandicoot as bc

scalar = "SCALAR"
distribution = "DISTRIBUTION"

def get_resource(tup):
    pointer = bc
    for submodule in tup:
        pointer = getattr(pointer, submodule)
    return pointer

def get_indicator_meta(tup):
    module = get_resource(tup[0:-1])
    _match = lambda ind: (ind.name == tup[-1])
    out = filter(_match, module.indicators)
    assert len(out) == 1
    return out[0]

def indicator_tuples():
    out = []
    #modules whose indicator names are in 'indicators'
    ind_mod_names = [('individual',)]
    ind_mods = map(get_resource, ind_mod_names)
    for mod_name, mod in zip(ind_mod_names, ind_mods):
        # The names of the module's indicators.
        mod_f_names = (f.name for f in mod.indicators)
        out.extend(mod_name + (f_name,) for f_name in mod_f_names)
    return out

def get_name(tup):
    return "_._".join(tup)

def get_tuple(name, indicator=True):
    out = tuple(name.split("_._"))
    if indicator:
        assert out in indicator_tuples()
    return out
