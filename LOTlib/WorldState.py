from sets import Set
import sys
import random
from copy import deepcopy

"""

---------------------------------------
Bucket and Hand as subclass of Container object
---------------------------------------

- The superclass Container has _contents attribute, which is a dictionary of things (ball of 
different colors) that a Container object stores. It also has _capacity attribute, which
dictates the maximum number of balls the container can store.

- Two container objects are defined to be equal if the numbers of black, red, green balls they hold
are the same. 

- Hand and Bucket inherit from Container, and has different capacity. (Bucket: 1000, Hand: 3)

To declare a Hand/Bucket object, you can do this:
----
bucket_0 = Bucket(black=2, red=3, green=4),
hand_left = Hand(red=1)
----

"""
Accordance_Penalty = {
	'low' : 10,
	'medium': 40,
	'high': 100
}

possible_colors = Set([
	'black',
	'red',
	'green'
	])

class Container(object):
	def __init__(self, **kwargs):
		self._contents = {} # Balls stored as a '_contents' dict by their color and number
		for color in possible_colors: # set all color in dict and their number to zero
			self._contents[color] = 0
		for color, number in kwargs.items(): # set container's _contents according to arguments
			if not color in possible_colors: # only allow certian color and integer number
				sys.exit('[Error]: Color \'' + color + '\' is not allowed.' )
			elif not isinstance(number, int):
				sys.exit('[Error]: \'' + number + '\' is not an integer.' )
			else:
				self._contents[color] = number
		self._capacity = 1000 # default capacity of container is 1000

	def __eq__(self, other): # equality define as having the same color set and same quantities
		for color, number in self._contents.items():
			if color not in other._contents.keys():
				return False
			elif other._contents[color] != number:
				return False
		for color, number in other._contents.items():
			if color not in self._contents.keys():
				return False
			elif self._contents[color] != number:
				return False
		return True

	def __sub__(self, other): # difference define as color and ball number difference
		selfCount = 0
		otherCount = 0
		colorDiff = 0
		countDiff = 0
		for color, number in self._contents.items():
			assert color in other._contents.keys(), "lists of color in two container don't match"
			colorDiff += abs(self._contents[color] - other._contents[color])
			selfCount += self._contents[color]
			otherCount +=other._contents[color]
		countDiff = abs(selfCount - otherCount)
		return colorDiff + countDiff

	def __gt__(self, other):
		return self.get_content_amount() > other.get_content_amount()

	def __ge__(self, other):
		return self.get_content_amount() >= other.get_content_amount()

	def __lt__(self, other):
		return self.get_content_amount() < other.get_content_amount()

	def __le__(self, other):
		return self.get_content_amount() <= other.get_content_amount()

	def __str__(self):
		outstr = '<'
		for color, number in self._contents.items():
			outstr = outstr + color + ': ' + str(number) + ' '
		outstr = outstr + '>'
		return outstr

	def __repr__(self): # used for being printed in lists
		return str(self)

	def remove_all_contents(self): # reset items in _contents dict to zero 
		for color, number in self._contents.items():
			number = 0

	def get_content_amount(self):
		content_amount = 0
		for color, number in self._contents.items():
			content_amount += number
		return content_amount

	def get_vacancy(self): # check Bucket vacancy
		vacancy = self._capacity
		vacancy -= self.get_content_amount()
		return vacancy

class Bucket(Container): # Bucket as a subclass of Container
	def __init__(self, *args, **kwargs):
		super(Bucket, self).__init__(**kwargs)
		self._capacity = 1000 

	def isEmpty(self):
		return self.get_vacancy() == self._capacity


class Hand(Container): # Bucket as a subclass of Container
	def __init__(self, *args, **kwargs):
		self._capacity = 3 # Hand has much smaller capacity
		handTotal = 0
		for color, number in kwargs.items(): # check if exceed capacity
			handTotal += number
			if handTotal > 3:
				sys.exit('[Error]: Hand cannot hold more than 3 items.')
		super(Hand, self).__init__(**kwargs)

	def isEmpty(self):
		return self.get_vacancy() == self._capacity

"""

---------------------------------------
contruct the object class of WorldState
---------------------------------------

- A WorldState (WS) object captures the experiment setting in a certain state. A WorldState (i.e.
an experimental setting) contains four buckets and two hands, stored in a dictionary called
_contents, in which four bucket objects and two hand objects are created and keyworded 
as: 'bucket_0' to 'bucket_3' and 'hand_left' and 'hand_right'.

- To declare a WS object, create a dict with bucket objects and hand objects you want to specify,
like this:

------
init_state = {
	'bucket_3': Bucket(black=2, red=3, green=4),
	'hand_right': Hand(red=1)
}
------

then feed the dict as a argument to WorldState constructor (any unspecified buckets and hand
will initiate as 0): 

------
WS_0 = WorldState(init_state)
print WS_0

*** return ***
<WorldState: 
bucket_0: <black: 0 green: 0 red: 0 >
bucket_1: <black: 0 green: 0 red: 0 >
bucket_2: <black: 0 green: 0 red: 0 >
bucket_3: <black: 2 green: 4 red: 3 >
hand_left: <black: 0 green: 0 red: 0 >
hand_right: <black: 0 green: 0 red: 1 >
>
*** end of return ****
------



- Two WS objects are defined to be equal if all bucket and hand objects that they hold are equal
to their corresponding others.

- Three methods that I've built:

1. existColor() check if there is a certain color ball in a container
e.g.: WS_0.existColor('bucket_0', 'black') -- check if bucket_0 has at least one black ball,
return True or False

2. moveBall() take a certain color ball from one container and add to the other.
e.g.: WS_0.moveBall('bucket_0', 'hand_left', 'black') -- count of black ball in bucket_0 
decrease by one while in hand_left increase by one. 

3. setWorldState() take in a dictionary that specifies the state of the world and set the WS
object accordingly. Used in WS object initiation.
e.g.: 
state = {
	'bucket_0': Bucket(black=1, red=0, green=0),
	'bucket_1': Bucket(black=0, red=4, green=4),
	'bucket_2': Bucket(black=0, red=0, green=0),
	'bucket_3': Bucket(black=0, red=0, green=0),
	'hand_right': Hand(black=1),
	'hand_left': Hand()
}
WS_0.setWorldState(state)


"""



class WorldState():
	def __init__(self, *args):
		self._ws = SnippetWS(*args)
		self._wsHistory = []
		self.addHistory(self._ws)

	def __eq__(self, other):
		return self._ws == other._ws

	def __sub__(self, other):
		return self._ws.__sub__(self._ws, other._ws)

	def __str__(self):
		return self._ws.__str__(self._ws)

	def __repr__(self):
		return str(self)

	def addHistory(self, wsSnippet):
		assert isinstance(wsSnippet, SnippetWS), "Not storing WorldStateSnippet object"
		self._wsHistory.append(deepcopy(wsSnippet))

	def getSnippetWS(self):
		return self._ws

	def getHistory(self):
		return self._wsHistory

	def getContainer(self, container):
		return self._ws.getContainer(container)

	def getAffordanceViolateCnt(self):
		return self._ws.getAffordanceViolateCnt()

	def incItrCounter(self):
		self._ws.incItrCounter()

	def getItrCounter(self):
		return self._ws.getItrCounter()

	def resetItrCounter(self):
		self._ws.resetItrCounter()

	def existColor(self, container, color, number=1):
		return self._ws.existColor(container, color, number=1)

	def canAddBall(self, container, number=1):
		return self._ws.canAddBall(container, number=1)

	def moveBall(self, from_container, to_container, color, number=1):
		self._ws.moveBall(from_container, to_container, color, number=1)
		self.addHistory(self._ws)
		return self

	def moveRandomBall(self, from_container, to_container):
		self._ws.moveRandomBall(from_container, to_container)
		self.addHistory(self._ws)
		return self

	def grabBall(self, from_bucket, to_hand, color): 
		self._ws.grabBall(from_bucket, to_hand, color)
		self.addHistory(self._ws)
		return self

	def dropBall(self, from_hand, to_bucket, color):
		self._ws.dropBall(from_hand, to_bucket, color)
		self.addHistory(self._ws)
		return self

	def grabRandomBall(self, from_bucket, to_hand): 
		self._ws.grabRandomBall(from_bucket, to_hand)
		self.addHistory(self._ws)
		return self


class SnippetWS():
	def __init__(self, *args):
		self._container = {
			'bucket_0': Bucket(),
			'bucket_1': Bucket(),
			'bucket_2': Bucket(),
			'bucket_3': Bucket(),
			'hand_left': Hand(),
			'hand_right': Hand()
		}
		self.setWorldState(*args)
		self._affordanceViolateCnt = 0
		self._itrCounter = 0

	def __eq__(self, other):
		bucket_0_is_equal = (self._container['bucket_0'] == other._container['bucket_0'])
		bucket_1_is_equal = (self._container['bucket_1'] == other._container['bucket_1'])
		bucket_2_is_equal = (self._container['bucket_2'] == other._container['bucket_2'])
		bucket_3_is_equal = (self._container['bucket_3'] == other._container['bucket_3'])
		hand_left_is_equal = (self._container['hand_left'] == other._container['hand_left'])
		hand_right_is_equal = (self._container['hand_right'] == other._container['hand_right'])
		return bucket_0_is_equal and bucket_1_is_equal and bucket_0_is_equal and bucket_1_is_equal and hand_left_is_equal and hand_right_is_equal

	def __sub__(self, other):
		bucket_0_diff = self._container['bucket_0'] - other._container['bucket_0']
		bucket_1_diff = self._container['bucket_1'] - other._container['bucket_1']
		bucket_2_diff = self._container['bucket_2'] - other._container['bucket_2']
		bucket_3_diff = self._container['bucket_3'] - other._container['bucket_3']
		hand_left_diff = self._container['hand_left'] - other._container['hand_left']
		hand_right_diff = self._container['hand_right'] - other._container['hand_right']
		return bucket_0_diff + bucket_1_diff + bucket_2_diff + bucket_3_diff + hand_left_diff + hand_right_diff

	def __str__(self):
		outstr = '<WorldState: \n'
		outstr = outstr + 'bucket_0: ' + str(self._container['bucket_0']) + '\n'
		outstr = outstr + 'bucket_1: ' + str(self._container['bucket_1']) + '\n'
		outstr = outstr + 'bucket_2: ' + str(self._container['bucket_2']) + '\n'
		outstr = outstr + 'bucket_3: ' + str(self._container['bucket_3']) + '\n'
		outstr = outstr + 'hand_left: ' + str(self._container['hand_left']) + '\n'
		outstr = outstr + 'hand_right: ' + str(self._container['hand_right']) + '\n'
		outstr = outstr + '>'
		return outstr

	def __repr__(self): # used for being printed in lists
		return str(self)

	def getAffordanceViolateCnt(self):
		return self._affordanceViolateCnt

	def incItrCounter(self):
		self._itrCounter += 1

	def getItrCounter(self):
		return self._itrCounter

	def resetItrCounter(self):
		self._itrCounter = 0

	def getContainer(self, container):
		return self._container[container]

	def setWorldState(self, state):
		for container_name, container in self._container.items():
			container.remove_all_contents()
		for container_name, container in state.items():
			if isinstance(container, Bucket):
				# self._container[container_name] = Bucket(container)
				self._container[container_name] = container
			elif isinstance(container, Hand):
				# self._container[container_name] = Hand(container)
				self._container[container_name] = container
			else:
				sys.exit('[Error]: expect Bucket object or Hand object.') 

	def existColor(self, container, color, number=1):
		if container not in self._container.keys():
			sys.exit('[Error]: number of ' + color + ' balls in ' + container + ' is less than' + number)
		elif color in self._container[container]._contents:
			return self._container[container]._contents[color] >= number
		else:
			return False

	def canAddBall(self, container, number=1):
		return self._container[container].get_vacancy() >= number

	def moveBall(self, from_container, to_container, color, number=1):
		assert from_container in self._container, "Incorrect source container name: "+from_container
		assert to_container in self._container, "Incorrect target container name: "+to_container

		# To penalize the least-likely moveball action in this experiemental environment
		def checkAffordance (self, from_container, to_container, color, number): 
			if self.existColor(from_container, color, number) ^ self.canAddBall(to_container, number):
				self._affordanceViolateCnt += Accordance_Penalty['medium']
			elif not self.existColor(from_container, color, number) and not self.canAddBall(to_container, number):
				self._affordanceViolateCnt += Accordance_Penalty['high']
			if from_container == to_container: 
				self._affordanceViolateCnt += Accordance_Penalty['medium']
		checkAffordance(self, from_container, to_container, color, number=1)

		if self.existColor(from_container, color, number) and self.canAddBall(to_container, number):
			self._container[from_container]._contents[color] = self._container[from_container]._contents[color] - number
			self._container[to_container]._contents[color] = self._container[to_container]._contents[color] + number
		
		# self._WSHistory.append(deepcopy(self))
		return self

	def moveRandomBall(self, from_container, to_container):
		existedBalls = []
		if not self._container[from_container].isEmpty():
			for color, number in self._container[from_container]._contents.items():
				if number != 0:
					existedBalls.append(color)
			self = self.moveBall(from_container, to_container, random.choice(existedBalls))
		return self

	def grabBall(self, from_bucket, to_hand, color): 
		assert isinstance(self._container[from_bucket], Bucket), "Not drawing from a Bucket object"
		assert isinstance(self._container[to_hand], Hand), "Not drawing to a Hand obect"
		assert from_bucket in self._container, "Incorrect source container name: "+ from_container
		assert to_hand in self._container, "Incorrect target container name: "+ to_container

		return self.moveBall(from_bucket, to_hand, color)

	def dropBall(self, from_hand, to_bucket, color):
		assert isinstance(self._container[to_bucket], Bucket), "Not drawing to a Bucket object"
		assert isinstance(self._container[from_hand], Hand), "Not drawing from a Hand obect"
		assert from_hand in self._container, "Incorrect source container name: "+ from_container
		assert to_bucket in self._container, "Incorrect target container name: "+ to_container

		return self.moveBall(from_hand, to_bucket, color)

	def grabRandomBall(self, from_bucket, to_hand): 
		assert isinstance(self._container[from_bucket], Bucket), "Not drawing from a Bucket object"
		assert isinstance(self._container[to_hand], Hand), "Not drawing to a Hand obect"
		assert from_bucket in self._container, "Incorrect source container name: "+ from_container
		assert to_hand in self._container, "Incorrect target container name: "+ to_container

		return self.moveRandomBall(from_bucket, to_hand)


# class WorldState(): 
# 	def __init__(self, *args):
# 		self._container = {
# 			'bucket_0': Bucket(),
# 			'bucket_1': Bucket(),
# 			'bucket_2': Bucket(),
# 			'bucket_3': Bucket(),
# 			'hand_left': Hand(),
# 			'hand_right': Hand()
# 		}
# 		self.setWorldState(*args)
# 		self._affordanceViolateCnt = 0
# 		self._itrCounter = 0
# 		self._WSHistory = []

# 	def __eq__(self, other):
# 		bucket_0_is_equal = (self._container['bucket_0'] == other._container['bucket_0'])
# 		bucket_1_is_equal = (self._container['bucket_1'] == other._container['bucket_1'])
# 		bucket_2_is_equal = (self._container['bucket_2'] == other._container['bucket_2'])
# 		bucket_3_is_equal = (self._container['bucket_3'] == other._container['bucket_3'])
# 		hand_left_is_equal = (self._container['hand_left'] == other._container['hand_left'])
# 		hand_right_is_equal = (self._container['hand_right'] == other._container['hand_right'])
# 		return bucket_0_is_equal and bucket_1_is_equal and bucket_0_is_equal and bucket_1_is_equal and hand_left_is_equal and hand_right_is_equal

# 	def __sub__(self, other):
# 		bucket_0_diff = self._container['bucket_0'] - other._container['bucket_0']
# 		bucket_1_diff = self._container['bucket_1'] - other._container['bucket_1']
# 		bucket_2_diff = self._container['bucket_2'] - other._container['bucket_2']
# 		bucket_3_diff = self._container['bucket_3'] - other._container['bucket_3']
# 		hand_left_diff = self._container['hand_left'] - other._container['hand_left']
# 		hand_right_diff = self._container['hand_right'] - other._container['hand_right']
# 		return bucket_0_diff + bucket_1_diff + bucket_2_diff + bucket_3_diff + hand_left_diff + hand_right_diff

# 	def __str__(self):
# 		outstr = '<WorldState: \n'
# 		outstr = outstr + 'bucket_0: ' + str(self._container['bucket_0']) + '\n'
# 		outstr = outstr + 'bucket_1: ' + str(self._container['bucket_1']) + '\n'
# 		outstr = outstr + 'bucket_2: ' + str(self._container['bucket_2']) + '\n'
# 		outstr = outstr + 'bucket_3: ' + str(self._container['bucket_3']) + '\n'
# 		outstr = outstr + 'hand_left: ' + str(self._container['hand_left']) + '\n'
# 		outstr = outstr + 'hand_right: ' + str(self._container['hand_right']) + '\n'
# 		outstr = outstr + '>'
# 		return outstr

# 	def __repr__(self): # used for being printed in lists
# 		return str(self)

# 	def setWorldState(self, state):
# 		for container_name, container in self._container.items():
# 			container.remove_all_contents()
# 		for container_name, container in state.items():
# 			if isinstance(container, Bucket):
# 				# self._container[container_name] = Bucket(container)
# 				self._container[container_name] = container
# 			elif isinstance(container, Hand):
# 				# self._container[container_name] = Hand(container)
# 				self._container[container_name] = container
# 			else:
# 				sys.exit('[Error]: expect Bucket object or Hand object.') 

# 	def existColor(self, container, color, number=1):
# 		if container not in self._container.keys():
# 			sys.exit('[Error]: number of ' + color + ' balls in ' + container + ' is less than' + number)
# 		elif color in self._container[container]._contents:
# 			return self._container[container]._contents[color] >= number
# 		else:
# 			return False

# 	def canAddBall(self, container, number=1):
# 		return self._container[container].get_vacancy() >= number

# 	def moveBall(self, from_container, to_container, color, number=1):
# 		assert from_container in self._container, "Incorrect source container name: "+from_container
# 		assert to_container in self._container, "Incorrect target container name: "+to_container

# 		# To penalize the least-likely moveball action in this experiemental environment
# 		def checkAffordance (self, from_container, to_container, color, number): 
# 			if self.existColor(from_container, color, number) ^ self.canAddBall(to_container, number):
# 				self._affordanceViolateCnt += Accordance_Penalty['medium']
# 			elif not self.existColor(from_container, color, number) and not self.canAddBall(to_container, number):
# 				self._affordanceViolateCnt += Accordance_Penalty['high']
# 			if from_container == to_container: 
# 				self._affordanceViolateCnt += Accordance_Penalty['medium']
# 		checkAffordance(self, from_container, to_container, color, number=1)

# 		if self.existColor(from_container, color, number) and self.canAddBall(to_container, number):
# 			self._container[from_container]._contents[color] = self._container[from_container]._contents[color] - number
# 			self._container[to_container]._contents[color] = self._container[to_container]._contents[color] + number
		
# 		self._WSHistory.append(deepcopy(self))
# 		return self

# 	def moveRandomBall(self, from_container, to_container):
# 		existedBalls = []
# 		if not self._container[from_container].isEmpty():
# 			for color, number in self._container[from_container]._contents.items():
# 				if number != 0:
# 					existedBalls.append(color)
# 			self = self.moveBall(from_container, to_container, random.choice(existedBalls))
# 		return self

# 	def grabBall(self, from_bucket, to_hand, color): 
# 		assert isinstance(self._container[from_bucket], Bucket), "Not drawing from a Bucket object"
# 		assert isinstance(self._container[to_hand], Hand), "Not drawing to a Hand obect"
# 		assert from_bucket in self._container, "Incorrect source container name: "+ from_container
# 		assert to_hand in self._container, "Incorrect target container name: "+ to_container

# 		return self.moveBall(from_bucket, to_hand, color)

# 	def dropBall(self, from_hand, to_bucket, color):
# 		assert isinstance(self._container[to_bucket], Bucket), "Not drawing to a Bucket object"
# 		assert isinstance(self._container[from_hand], Hand), "Not drawing from a Hand obect"
# 		assert from_hand in self._container, "Incorrect source container name: "+ from_container
# 		assert to_bucket in self._container, "Incorrect target container name: "+ to_container

# 		return self.moveBall(from_hand, to_bucket, color)

# 	def grabRandomBall(self, from_bucket, to_hand): 
# 		assert isinstance(self._container[from_bucket], Bucket), "Not drawing from a Bucket object"
# 		assert isinstance(self._container[to_hand], Hand), "Not drawing to a Hand obect"
# 		assert from_bucket in self._container, "Incorrect source container name: "+ from_container
# 		assert to_hand in self._container, "Incorrect target container name: "+ to_container

# 		return self.moveRandomBall(from_bucket, to_hand)





