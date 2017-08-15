import xml.etree.ElementTree

import pickle
from collections import namedtuple, defaultdict

from verb_sense.VSD_withSpacy import sense_profile
from CausalPotential.causal_potential_with_frames import Event

QA = namedtuple('QA', 'id asks_for p a1 a2 answer')


# extract from COPA folder
def get_QAs(file):
	QAs = []
	e = xml.etree.ElementTree.parse(file).getroot()
	for item in e:
		id = item.attrib['id']
		asks_for = item.attrib['asks-for']
		problem = item.find('p').text
		answer = item.attrib['most-plausible-alternative']
		alt1 = item.find('a1').text
		alt2 = item.find('a2').text
		QAs.append(QA(id, asks_for, problem, alt1, alt2, answer))
	return QAs


def get_CPUFF(cpuff_pickle):
	# get CP
	return pickle.load(open('CausalPotential//' + cpuff_pickle, 'rb'))
	# cp = list(cp.items())
	# cp.sort(key=lambda tup: -tup[1])
	# return cp


def get_ranked_CPUFF(cpuff):
	cp = list(cpuff.items())
	cp.sort(key=lambda tup: -tup[1])
	return cp


def frame_2_event(frame):
	return Event(frame[0], frame[1][0])


def compare_events(e1, e2):
	if (e1,e2) not in cpuff.keys():
		return 0

	return cpuff[(e1, e2)]


def test_causality(E1, E2):
	tally = [compare_events(e1, e2) for e1 in E1 for e2 in E1]
	if len(tally) == 0:
		return (0, 0, 0)
	_min = min(tally)
	_max = sum(tally)
	_avg = sum(tally) / len(tally)
	return (_min, _max, _avg)


def eval_diff(score1, score2):
	x = score1 < 5
	y = score2 < 5
	if x and y:
		return -1
	if not x and y:
		return False
	if not y and x:
		return True
	return score1 < score2


def choose_effect(P, A1, A2):
	(_min1, _max1, _avg1) = test_causality(P, A1)
	(_min2, _max2, _avg2) = test_causality(P, A2)
	return eval_diff(_min1, _min2), eval_diff(_max1, _max2), eval_diff(_avg1, _avg2)


def choose_cause(P, A1, A2):
	(_min1, _max1, _avg1) = test_causality(A1, P)
	(_min2, _max2, _avg2) = test_causality(A2, P)
	return eval_diff(_min1, _min2), eval_diff(_max1, _max2), eval_diff(_avg1, _avg2)


def parse_QAs(QAs):

	total = 0
	book_keep = {0: 0, 1: 0, 2: 0}
	r1, r2, r3 = 0, 0, 0

	for qa in QAs:
		id, asks_for, problem, alt1, alt2, answer = qa

		# get the frames from semafor
		prob_frames = sense_profile(problem)
		alt1_frames = sense_profile(alt1)
		alt2_frames = sense_profile(alt2)

		# transform frames into events
		prob_events = [frame_2_event(frame) for frame in prob_frames]
		alt1_events = [frame_2_event(frame) for frame in alt1_frames]
		alt2_events = [frame_2_event(frame) for frame in alt2_frames]

		# asks for cause
		if asks_for == 'cause':
			v1, v2, v3 = choose_cause(prob_events, alt1_events, alt2_events)
		else:
			v1, v2, v3 = choose_effect(prob_events, alt1_events, alt2_events)
		# True is choice 2, False is choice 1

		answer = int(answer)
		if v1 < 0:
			pass
		else:
			if v1 and answer == 2:
				book_keep[0] += 1
			elif not v1 and answer == 1:
				book_keep[0] += 1
			r1 += 1

		if v2 < 0:
			pass
		else:
			if v2 and answer == 2:
				book_keep[1] += 1
			elif not v2 and answer == 1:
				book_keep[1] += 1
			r2 += 1

		if v3 < 0:
			pass
		else:
			if v3 and answer == 2:
				book_keep[2] += 1
			elif not v3 and answer == 1:
				book_keep[2] += 1
		r3 += 1

		total += 1
		# evaluate answer
	print('v1: {}'.format(str(book_keep[0])))
	print('v2: {}'.format(str(book_keep[1])))
	print('v3: {}'.format(str(book_keep[2])))
	print('total: {}'.format(str(total)))

	print('r1: {}'.format(str(r1)))
	print('r2: {}'.format(str(r2)))
	print('r3: {}'.format(str(r3)))

if __name__ == '__main__':

	# get CP
	cpuff = get_CPUFF('CP_scores.pkl')
	# cpuff_seg = get_CPUFF('CP_Seg_scores.pkl')
	# triple = get_CPUFF('basic_triple.pkl')

	# get QAs
	qas = get_QAs('COPA//copa-dev.xml')

	# process QAs
	parse_QAs(qas)

	# Run

	print('here')