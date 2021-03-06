# ShallowBlue - A Boxes and Dots AI (Python 2.7)

###Overview: ShallowBlue (SB) is an AI that utilizes a Neural Network (NN) and the Minimax algorithm to play Boxes and Dots. The NN is trained using stochastic gradient descent (specifically Nesterov accelerated gradient) from games created by the Minimax algorithm playing itself with optimal depth.

##How does ShallowBlue work?
- Early game - Establish usual board/grid: 
	While the grid is less than ~1/2 full, SB will take the first available move progressing from top left to bottom right. SB initializes a minimax of depth 2 is to take advantage of any mistakes made by the opponent (for an early box) and to prevent giving away any free boxes.
- Mid game - Sacrifices and chain creation: 
	Mid game is general where tje victor is decided. Here, a single move can finish a chain or split it in two smaller ones. Move order is very important. The Neural Network is actived to decide whether SB continue on it's trajectory or sacrifice boxes to win.
- End game (kind of) - Look for ending sequence: 
	While the Neural Net plays a sleeper AI runs in the background looking for a winning/ending sequence of moves. If it spots a way to score a majority amount of boxes, 5 in our case (NN is only trained for 3 x 3 games), or a way to end the game it takes control. Otherwise, if no opportunity presents itself, it lies dormant. 

##How good is ShallowBlue currently?
The answer: ehh okay. The deciding factor is how well the Neural Network performs. Unfortunately, I build the entire network from scratch off of numpy and couldn't find a database of games. Thus, the backpropagation is not optimized for any hardware (runs slow) and I also had to create the training data. This is very computationally expensive and takes a lot of time so I'm constantly having to create more data and train. Eventually it should get much better but it will be a while. FYI there are over 16 billion possible game states. However, I learned a lot from this project and will continue to improve the NN. In the meantime, TensorFlow is definitely the move :)

##New Objective: Have ShallowBlue beat my mom in a best of three.
##Status: Mom make ShallowBlue wish he never even learned the minimax algorithm (0/3). 

##How to play:
- Download files
- Run python Game.py 
- Open Move_Diagram.txt for reference
- Follow directions and pick who will play
- Input moves seperated by a space.
Input 2 numbers: Row then Column (ex. first vertical line would be 10): 0 0 (This is horizontal top left)
- You must make a unit box to score.
- Note: ShallowBlue's Neural Net has not been trained well. I'll upload better weights when I have them. 

##Current Progress:
- Boxes & Dots game created                                                 11/24
- Basic AI w/ single hidden layer                                           11/26
- Attempt to train AI through genetic mutation                              11/27
- Backpropagation working                                                   11/28
- Framework for Deep Learning AI                                            12/5
- Training data storage, interalized data transfer                          12/6
- Trainer created, training for data working, started collecting            12/8
- Implemented gradient descent w/ momentum 				    12/9
- Implemented Nesterov accelerated gradient                                 12/10
- Started work on minimax                                                   12/16
- Created beta minimax w/ depth                                             12/17
- Fixed minimax bugs, starting to train                                     12/18
- Minimax picks a random good move from best valued not first               12/19
- Experimenting with depth and when to increase depth w/ minimax            12/19
- Optimized minimax depth for recording games 				    12/20
- Started training on PI                                                    12/21
- Minimax helper for early and end game                                     12/27
- Attempting to expand input data to require less training                  1/3
- Remote training on server, setup text updates 			    1/15

##Goals & Thoughts:
- Optimization of Gradient Descent by decreasing alpha on cost function and/or theta bounces
	- Start with first layer deeper layers weights not stable 
	- Momentum and Nesterov accelerated gradient
		See: http://sebastianruder.com/optimizing-gradient-descent/index.html#gradientdescentoptimizationalgorithms
	
- Reinforcement Learning. 

- UC Berkeley has noted several strategies other than those listed here. I will not be looking into other algorithms since the focus of this project is the NN and minimax is sufficient for 3 x 3 games. 
See: https://math.berkeley.edu/~berlek/cgt/dots.html

- Minimax Algorithm. Currently, to create artificial data, I am running a random AI vs a minimax depth 2 (mm2) and a mm2 vs a mm2 which switches to a mm5 after move 10. (The next few moves after 10 a critical. Having this extra depth allows the algorithm to make smart sacrifices to win the game). Winner is logged for training ShallowBlue.

- Remotely train on Raspberry Pi (will have to run for days)

- Data logging - RandomAI vs mm2 and S0X (3 > X | Start with X = 1 progress to 2). The deepest the minimax will need to go is 6 in the case of a chain for 4 and a chain of 5 to make a decision. However, we can set the max depth to 5 since one minimax has to win and we log him. 

- As this project is drawing to an end, I'm realizing what's really needed is CPU power and tons^(tons) of training data. Playing and training against the minimax works well but games take too long ~ 5 sec w/ current depth. To actually train Shallow Blue, I'll need in the millions of recorded games. I could optimize the Minimax algorithm more (pruning), or even implement the Monte Carlo search tree to speed things up. However, the real issue is CPU power. Even with the necessary data just trainng takes a very long time. So, get more CPU power, optimize minimax, or a lot of time to get Shallow Blue to a competitve level.

- Furthermore, some of the libraries I use run slowly. Specifically the deepcopy() method from copy is used frequently. 

