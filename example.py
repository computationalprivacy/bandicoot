
import bandicoot as bc


u = bc.read_csv('X', 'bandicoot/tests/samples/special', attributes_path='bandicoot/tests/')
indicators = bc.utils.all(u)
#print indicators
#print indicators['number_of_weeks']