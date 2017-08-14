### CPuFF: Causal Potential using Framenet Frames

### David R. Winer

Input:
--- 

Triples of the form (e1=<verb, frame>, e2=<verb, frame>, CP-score) where the CP-score is the Causal Potential score of e1 causing e2. Causal Potential is calculated as CP(e1,e2) = PMI(e1,e2) + log(P(e1 < e2)/ P(e2 < e1)) and PMI(e1,e2) = log(P(e1,e2)/P(e1)P(e2)).

The Semafor Parser, a frame-semantic parser which takes a sentence as input and outputs FrameNet frames for that sentence. SpaCy is used to feed Semafor a dependency parse.

The COPA (Choice Of Plausible Alternatives), the SemEval 2012 task, where as input we receive a request for a Cause or an Effect, a sentence, and 2 plausibly causally-related sentences, and the goal is to pick the best plausible sentence among the 2 alternatives.


Process:
---

Currently testing how well this performs on development set. Will not make a choice (between alternatives) when Semafor does not tag a framenet frame in a sentence. If the e1, e2 pair is not in the CP-score database, then the causality is deemed as 0. 