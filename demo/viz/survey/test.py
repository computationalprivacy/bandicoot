import parse_survey

def get_survey():
    with open("temp.dat", "r") as f:
        return parse_survey.parse_survey(f)
