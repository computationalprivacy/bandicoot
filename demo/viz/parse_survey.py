import string

CONVERSIONS = {"int": int,
               "float": float,
               "string": str,
               "longstring": str,
               "enum": (lambda inp: inp)}
HTML_INPUT_TYPES = {
    "int": "number",
    "float": "number",
    "string": "text",
    "longstring": "text"
    }

class Question():
    class QuestionConversionError(Exception):
        pass
    def __init__(self, comma_separated, text):
        self.text = text.strip()
        _strip = lambda s: s.strip()
        self.datatype, self.name = map(_strip, string.split(comma_separated, ","))
        assert (self.datatype in ("int", "float", "string", "longstring", "enum"))
        self.is_enum = self.datatype == "enum"
        self.choice_list = []
    def input_box(self, html_input_type, name, text):
        template = """
        <label for='%s'>%s</label>
        <input type='%s' name='%s' id='%s'></input>
        """
        return template % (name, text, html_input_type, name, name)
    def to_html(self):
        if not self.is_enum:
            return self.input_box(HTML_INPUT_TYPES[self.datatype], self.name, self.text)
        return self.text + "".join(c.to_html(self.name) for c in self.choice_list)
    def add_choice(self, choice):
        assert self.is_enum, "Choices should only follow questions of datatype 'enum'"
        self.choice_list.append(choice)
    def enum_values(self):
        return [choice.name for choice in self.choice_list]
    def enum_consistency(self, val):
        if self.is_enum != bool(self.choice_list):
            return False
        if not self.is_enum:
            return True
        return val in self.enum_values()
    def convert_answer(self, val):
        if not self.enum_consistency(val):
            raise self.QuestionConversionError
        try:
            out = CONVERSIONS[self.datatype](val)
        except ValueError:
            raise self.QuestionConversionError
        return out
    def __str__(self):
        return self.to_html()

class Choice():
    def __init__(self, comma_separated, text):
        self.text = text.strip()
        assert "," not in comma_separated
        self.name = comma_separated
    def to_html(self, question_name):
        template =  """
        <input type='radio' name='%s' value='%s' id='%s'></input>
        <label for='%s'>%s</label>
        """
        el_id = question_name + "_-_" + self.name
        return template % (question_name, self.name, el_id, el_id, self.text)

def parse_line(st):
    st = st.strip()
    if st == "":
        return None
    assert(str.isspace(st[1]))
    kind = st[0]
    st = st[1:].strip()
    parts = string.split(st, "//", 1)
    parts = [part.strip() for part in parts]
    if kind == "Q":
        return Question(*parts)
    if kind == "C":
        return Choice(*parts)
    assert False, "Lines must begin with 'Q' or 'C'"

def quash_choices(objects):
    out = []
    for obj in objects:
        if isinstance(obj, Question):
            out.append(obj)
            continue
        if isinstance(obj, Choice):
            out[-1].add_choice(obj)
            continue
        assert False, "quash_choices only accepts objects of type Choice and Question"
    for q in filter(lambda q: q.is_enum, out):
        assert(q.choice_list)
    return out

def parse_survey(lines):
    parsed_lines = map(parse_line, lines)
    parsed_lines = filter((lambda l: l is not None), parsed_lines)
    return quash_choices(parsed_lines)
