# Neural Network
#
# Author: Luke Munro

import numpy as np
import random

from sigNeuron import *
from Player import *
from Minimax import Minimax
from utils import orderMoves
from utils import makeCommands
from utils import formatMoves
from utils import onlyLegal
from utils import cleanData
from utils import assemble_state
from utils import clean_game_state

class NNet(Player):
	"""Neural net class for systems with any # of hidden layers."""
	def __init__(self, sizeIn, gridSize, layerList=map(int, np.loadtxt('weight_params.txt').tolist())):
		Player.__init__(self, "ShallowBlue")
		self.helperAI = Minimax(gridSize, 0, False)
		self.sizeIn = sizeIn
		self.gridSize = gridSize
		self.numLayers = len(layerList)
		self.layerList = layerList
		self.layers = [[] for x in range(self.numLayers)]
		for i in range(layerList[0]):
			self.layers[0].append(Neuron(self.sizeIn+1, int(random.random()*100)))
		for i, nodes in enumerate(layerList[1:]):
			for x in range(nodes):
				self.layers[i+1].append(Neuron(len(self.layers[i])+1, int(random.random()*100)))
		self.oldUpdateVector = self.getWeights()*0

	def getWeights(self):
		layerWeights = []
		layerWeights.append(np.zeros(shape=(self.layerList[0], self.sizeIn+1)))
		for i in range(self.numLayers-1):
			layerWeights.append(np.zeros(shape=(self.layerList[i+1], self.layerList[i]+1)))
		for i, layer in enumerate(self.layers):
			for x, node in enumerate(layer):
				layerWeights[i][x] = node.getW()
		return np.asarray(layerWeights)


	def writeWeights(self):
		layerWeights = self.getWeights()
		for i, layer in enumerate(layerWeights):
			np.savetxt('{0}weight{1}.txt'.format(self.gridSize, i), layer)


	def loadWeights(self): # BREAKS IF YOU ONLY HAVE 1 NODE IN A LAYER
		loadedWeights = []
		for i in range(self.numLayers):
			loadedWeights.append(np.loadtxt('{0}weight{1}.txt'.format(self.gridSize, i)))
		for i, layer in enumerate(self.layers):
			for x, node in enumerate(layer):
				node.assignW(loadedWeights[i][x])

# -------------------- Keep both of these  ----------------------------

	def updateWeights(self, newLayerWeights):
		for i, layer in enumerate(newLayerWeights):
			np.savetxt('{0}weight{1}.txt'.format(self.gridSize, i), layer)
		self.loadWeights()


	def internalUpdateWeights(self, newLayerWeights): # IMPROVED UPDATEWEIGHTS
		for i, layer in enumerate(self.layers):
			for x, node in enumerate(layer):
				node.assignW(newLayerWeights[i][x])

# ---------------------------------------------------------------------

	def reg(self, Lambda): # CURRENTLY UNUSED 
		reg = []
		for w in self.getWeights():
			np.insert(w, 0, 0, axis=0) # DON'T REGULARIZE BIAS SET TO 0
			reg.append(Lambda * w)
		return np.asarray(reg)

	def forwardPropagate(self, game_state):
		a = []
		z = []
		a1 = cleanData(game_state)
		clean_state = a1
		a.append(addBias(a1))
		for i in range(self.numLayers):
			z.append(computeZ(self.layers[i], a[i]))
			temp = sigmoid(z[i])
			a.append(addBias(temp))
		out = np.delete(a[self.numLayers], 0, axis=0) # REMOVE BIAS IN OUTPUT
		moves = orderMoves(out)
		legalMoves = onlyLegal(moves, clean_state)
		next_moves = formatMoves(legalMoves, makeCommands(self.gridSize))
		return next_moves[0]


	def getMove(self, game_state):
		# EARLY GAME - CREATE USUAL MIDGAME
		total_moves = 2*(self.gridSize**2+self.gridSize) 
		made_moves = sum(clean_game_state(game_state))
		available_moves = total_moves - made_moves
		# MID GAME - CHAIN & SACRIFICE DECISIONS
		NN_move = self.forwardPropagate(game_state)
		# END GAME - CHECK FOR ENDING SEQUENCE
		if not self.helperAI.ENDING_SEQUENCE:
			self.helperAI.check_ending_chain(game_state, self.getScore())
		# CHOOSING GAME STATE
		if made_moves < 12:
			next_move = self.helperAI.getMove(game_state, 2)
		elif self.helperAI.ENDING_SEQUENCE:
			next_move = self.helperAI.getMove(game_state, 3) # 3 FOR 3 + 1 CHAIN SCENARIO
		else:
			next_move = NN_move
		return next_move

# ----------------------- Gradient Descent Algorithms ----------------------------------------------------------

# KEEP SEPERATE FOR NOW

	def train(self, alpha, old_state, y): # REGULARIZATION POSSIBLY 
# ----- Leave steps split for easier comprehension ------
		a = []
		z = []
		a1 = old_state # Already cleaned
		a.append(addBias(a1))
		for i in range(self.numLayers):
			z.append(computeZ(self.layers[i], a[i]))
			temp = sigmoid(z[i])
			a.append(addBias(temp))
		out = np.delete(a[self.numLayers], 0, axis=0)
		# print np.hstack((y, out, out-y))
		# print costMeanSquared(y, out) 
		noBiasWeights = self.getWeights()
		for i, weights in enumerate(noBiasWeights):
			noBiasWeights[i] = rmBias(weights)
		deltas = []
		# EDIT THIS IF CHANGING COST FUNCTION
		# MEAN SQUARED
		# initialDelta = (out - y) * sigGradient(z[len(z)-1])
		# LOG COST
		initialDelta = (out - y)
		deltas.append(initialDelta)
		for x in range(self.numLayers-2, -1, -1):
			deltaIndex = (self.numLayers-2) - x
			delta = np.dot(noBiasWeights[x+1].transpose(), deltas[deltaIndex]) * sigGradient(z[x])
			deltas.append(delta)
		Grads = []
		# REORDER DELTAS FROM FIRST LAYER TO LAST			
		for i, delta in enumerate(deltas[::-1]):
			Grads.append(delta*a[i].transpose())
		updateVector = alpha*(np.asarray(Grads))
		updatedWeights = self.getWeights() - updateVector
		self.internalUpdateWeights(updatedWeights)

# MOMENTUM

	def trainMomentum(self, alpha, old_state, y, gamma=0.9):
		a = []
		z = []
		a1 = old_state # Already cleaned
		a.append(addBias(a1))
		for i in range(self.numLayers):
			z.append(computeZ(self.layers[i], a[i]))
			temp = sigmoid(z[i])
			a.append(addBias(temp))
		out = np.delete(a[self.numLayers], 0, axis=0)
		# print np.hstack((y, out, out-y))
		# print costMeanSquared(y, out) 
		noBiasWeights = self.getWeights()
		for i, weights in enumerate(noBiasWeights):
			noBiasWeights[i] = rmBias(weights)
		deltas = []
		initialDelta = (out - y) * sigGradient(z[len(z)-1])
		deltas.append(initialDelta)
		for x in range(self.numLayers-2, -1, -1):
			deltaIndex = (self.numLayers-2) - x # THIS IS UGLY. UR UGLY. STOP TALKING TO YOURSELF
			delta = np.dot(noBiasWeights[x+1].transpose(), deltas[deltaIndex]) * sigGradient(z[x])
			deltas.append(delta)
		Grads = []
		for i, delta in enumerate(deltas[::-1]):
			Grads.append(delta*a[i].transpose())
		Grads = np.asarray(Grads)
		updateVector = gamma*self.oldUpdateVector + alpha*Grads
		updatedWeights = self.getWeights() - updateVector
		self.oldUpdateVector = updateVector
		self.internalUpdateWeights(updatedWeights)

# NESTEROV ACCELERATED GRADIENT 
	def trainNAG(self, alpha, old_state, y, gamma=0.9):
# UPDATE WEIGHTS RERUN TO GET FUTURE GRADIENT 
		a = []
		z = []
		a1 = old_state
		a.append(addBias(a1))
		futureWeights = self.getWeights() - gamma*self.oldUpdateVector
		for i in range(self.numLayers): # same size
			zi = np.dot(futureWeights[i], a[i]).reshape(np.size(self.layers[i]), 1)
			z.append(zi)
			temp = sigmoid(z[i])
			a.append(addBias(temp))
		out = np.delete(a[self.numLayers], 0, axis=0)
		# print np.hstack((y, out, out-y))
		# print costMeanSquared(y, out) 
		noBiasWeights = self.getWeights()
		for i, weights in enumerate(noBiasWeights):
			noBiasWeights[i] = rmBias(weights)
		deltas = []
		initialDelta = (out - y) * sigGradient(z[len(z)-1])
		deltas.append(initialDelta)		
		for x in range(self.numLayers-2, -1, -1):
			deltaIndex = (self.numLayers-2) - x
			delta = np.dot(noBiasWeights[x+1].transpose(), deltas[deltaIndex]) * sigGradient(z[x])
			deltas.append(delta)
		futureGrads = []
		for i, delta in enumerate(deltas[::-1]):
			futureGrads.append(delta*a[i].transpose())
		futureGrads = np.asarray(futureGrads)
		# GRADIENTS FOR FUTURE THETAS
		updateVector = gamma*self.oldUpdateVector + alpha*(futureGrads)
		updatedWeights = self.getWeights() - updateVector
		self.oldUpdateVector = updateVector
		self.internalUpdateWeights(updatedWeights)




# -------------------------- Computations -------------------------------

def computeZ(Nodes, X):
	w = np.zeros(shape=(np.size(Nodes), np.size(X)))
	for i, node in enumerate(Nodes):
		w[i] = node.getW()
	z = np.dot(w, X).reshape(np.size(Nodes), 1)
	return z

def sigmoid(z):
	return 1/(1+np.exp(-z))

def costLog(y, a):
	cost = -y * np.log10(a) - (1 - y) * np.log10(1 - a)
	return sum(cost)

def costMeanSquared(y, a):
	cost = ((a - y)**2)/2.0
	return sum(cost)

def sigGradient(z):
	return sigmoid(z) * (1 - sigmoid(z))

def estimateGradlog(y, a, weights, epsilon): # DO THIS LATER.
	for i in range(weights):
		for i in range(weights[i]):
			continue
	return None
	# return (costLog(y, a+epsilon) - costLog(y, a-epsilon))


# ---------------------------- Utility ----------------------------------
		
def addBias(aLayer): # Adds 1 to vertical vector matrix
	return np.insert(aLayer, 0, 1, axis=0)


def rmBias(weightMatrix): # removes bias weight from all nodes 
	return np.delete(weightMatrix, 0, axis=1)
