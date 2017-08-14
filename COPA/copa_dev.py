import xml.etree.ElementTree

import pickle
from collections import namedtuple

from verb_sense.semafor_api import semafor, semafor_util
from verb_sense.VSD_withSpacy import spacy_sents_to_conll


QA = namedtuple('QA', 'id asks-for p a1 a2 answer')


def get_frames(sentence):
	conllu = spacy_sents_to_conll(sentence)

	# get frames for verbs and noun chunks
	sem_output = semafor(sock=None, text=conllu, reconnect=1)
	frame_list_dict = semafor_util(sem_output)

	return frame_list_dict


def get_QAs():
	QAs = []
	e = xml.etree.ElementTree.parse('datasets//copa-dev.xml').getroot()
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
	cp = pickle.load(open('D:\\documents\\python\\screenpy\\CausalPotential\\' + cpuff_pickle, 'rb'))
	cp = list(cp.items())
	cp.sort(key=lambda tup: -tup[1])
	return cp


def parse_QAs(QAs):
	for qa in QAs:
		id, asks_for, problem, alt1, alt2, answer = qa
		prob_frames = get_frames(problem)
		alt1_frames = get_frames(alt1)
		alt2_frames = get_frames(alt2)

		# pairwise comparison, max, avg, min?
	


if __name__ == '__main__':

	# get CP
	cpuff = get_CPUFF('CP_scores.pkl')
	# get QAs
	qas = get_QAs()
	# process QAs

	# Run

	print('here')