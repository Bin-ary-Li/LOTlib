"""

---------------------------------------
contruct the object class of bucket
---------------------------------------

- each bucket object has a attribute called _contents, which is a dictionary of things (ball of
different colors) that the bucket stores. To create a bucket object, with 1 black ball, 2 reds 
and 3 greens in it, you could do this: 

bucket_01 = Bucket(black=1, red=2, green=3)


- Two bucket objects are defined to be equal if the numbers of black, red, green balls they hold
are the same. 


"""

class Bucket():

	def __init__(self, **kwargs):
		self._contents = {'black': 0,
				 'red': 0,
				 'green': 0}
		if len(kwargs) != 0:
			assert len(kwargs)==3, "Need to specify number of black balls, red balls, and green balls."
			self._contents['black'] = kwargs.get('black')
			self._contents['red'] = kwargs.get('red')
			self._contents['green'] = kwargs.get('green')

	def __eq__(self, other):
		return self._contents['black'] == other._contents['black'] and self._contents['red'] == other._contents['red'] and self._contents['green'] == other._contents['green']

 	def __str__(self):
		outstr = '<Black: ' + str(self._contents['black']) + ', '
		outstr = outstr + 'Red: ' + str(self._contents['red']) + ', '
		outstr = outstr + 'Green: ' + str(self._contents['green']) + '>'
		return outstr

	def __repr__(self): 
		return str(self)

"""

---------------------------------------
contruct the object class of WorldState
---------------------------------------

- A WorldState (WS) object captures the experiment setting in a certain state. A WorldState (i.e.
an experimental setting) should describe the state of four buckets in term of their content. A  
WS object has a dictionary called _buckets, in which four bucket objects would be created and
keyworded from 'bucket_0' to 'bucket_3'.

- Per basic experiment setup, a WS object is designed to be declared in such way that we need
to feed it with 3 arguments to start: n_black_ball (number of black ball), n_red_ball and
n_green_ball. Then a WS object will be created with: n_black_ball in bucket_0; n_red_ball
and n_green_ball in bucket_1; two empty buckets, bucket_2 and bucket_3. 
(In this way, bucket_0 and bucket_1 correspond to the source buckets while bucket_2 and
bucket_3 to the target buckets as in the experiment setup.)

For example: 
WS_0 = WorldState(n_black_ball=1, n_red_ball=4, n_green_ball=4)
print WS_0

## return ##
<WorldState: 
Bucket 0: <Black: 1, Red: 0, Green: 0>
Bucket 1: <Black: 0, Red: 4, Green: 4>
Bucket 2: <Black: 0, Red: 0, Green: 0>
Bucket 3: <Black: 0, Red: 0, Green: 0>
>
######


- Two WS objects are defined to be equal if all four of the bucket objects they hold are equal
to their corresponding others.

- Three methods that I've built:

1. existColor() check if there is a certain color ball in the bucket
e.g.: WS_0.existColor('bucket_0', 'black') -- check if bucket_0 has at least one black ball,
return True or False

2. moveBall() take a certain color ball from one bucket and add it to the other.
e.g.: WS_0.moveBall('bucket_0', 'bucket_3', 'black') -- count of black ball in bucket_0 
decrease by one while in bucket_3 increase by one. 

3. setWorldState() take in a dictionary that specifies the state of the world and set the WS
object accordingly.
e.g.: 
state = {
	'bucket_0': Bucket(black=1, red=2, green=3),
	'bucket_1': Bucket(black=4, red=5, green=6),
	'bucket_2': Bucket(black=7, red=8, green=9),
	'bucket_3': Bucket(black=10, red=11, green=12)
}
WS_0.setWorldState(state)


"""

class WorldState():
	def __init__(self, **kwargs):
		self._buckets = {}

		assert 'n_black_ball' in kwargs and 'n_red_ball' in kwargs and 'n_green_ball' in kwargs, "Need n_black_ball, n_red_ball, and n_red_ball"
		self._buckets['bucket_0'] = Bucket(black=kwargs.get('n_black_ball'), red=0, green=0)
		self._buckets['bucket_1'] = Bucket(black=0, red=kwargs.get('n_red_ball'), green=kwargs.get('n_green_ball'))
		self._buckets['bucket_2'] = Bucket()
		self._buckets['bucket_3'] = Bucket()

	def __eq__(self, other):
		bucket_0_is_equal = (self._buckets['bucket_0'] == other._buckets['bucket_0'])
		bucket_1_is_equal = (self._buckets['bucket_1'] == other._buckets['bucket_1'])
		bucket_2_is_equal = (self._buckets['bucket_2'] == other._buckets['bucket_2'])
		bucket_3_is_equal = (self._buckets['bucket_3'] == other._buckets['bucket_3'])
		return bucket_0_is_equal and bucket_1_is_equal and bucket_2_is_equal and bucket_3_is_equal

	def __str__(self):
		outstr = '<WorldState: \n'
		outstr = outstr + 'Bucket 0: ' + str(self._buckets['bucket_0']) + '\n'
		outstr = outstr + 'Bucket 1: ' + str(self._buckets['bucket_1']) + '\n'
		outstr = outstr + 'Bucket 2: ' + str(self._buckets['bucket_2']) + '\n'
		outstr = outstr + 'Bucket 3: ' + str(self._buckets['bucket_3']) + '\n'
		outstr = outstr + '>'
		return outstr

	def __repr__(self): 
		return str(self)

	def existColor(self, bucket, color):
		if color=='black':
			return self._buckets[bucket]._contents['black']>0
		elif color=='red':
			return self._buckets[bucket]._contents['red']>0
		elif color=='green':
			return self._buckets[bucket]._contents['green']>0
		else:
			return False

	def moveBall(self, from_bucket, to_bucket, color):
		assert from_bucket in self._buckets and to_bucket in self._buckets, "Incorrect bucket name"
		if self.existColor(from_bucket, color):
			self._buckets[from_bucket]._contents[color] = self._buckets[from_bucket]._contents[color] - 1
			self._buckets[to_bucket]._contents[color] = self._buckets[to_bucket]._contents[color] + 1

	def setWorldState(self, bucketDict):
		assert len(bucketDict) == 4, "Need to know the setting of the four buckets"
		for key, value in bucketDict.iteritems():	
			self._buckets[key] = value
