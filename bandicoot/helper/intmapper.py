class IntMapper():
    def __init__(self):
        self._map_to_int = {}
        self._objects = []

    def to_int(self, obj):
        if obj in self._map_to_int:
            return self._map_to_int[obj]
        new_index = len(self._objects)
        self._map_to_int[obj] = new_index
        self._objects.append(obj)
        return new_index

    def to_object(self, i):
        return self._objects[i]
