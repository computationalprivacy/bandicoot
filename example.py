
import bandicoot as bc


u = bc.read_csv('X', 'bandicoot/tests/samples/special')
indicators = bc.utils.all(u)
print indicators
#print indicators['number_of_weeks']