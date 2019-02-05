from WorldState import *
from copy import deepcopy

init_state = {
	'bucket_0': Bucket(black=10, red=0, green=0),
	'bucket_1': Bucket(black=0, red=3, green=7),
	'bucket_2': Bucket(black=0, red=0, green=0),
	'bucket_3': Bucket(black=0, red=0, green=0),
	'hand_right': Hand(),
	'hand_left': Hand(),
}

end_state = {
	'bucket_2': Bucket(black=3, red=3, green=0),
	'bucket_3': Bucket(black=7, red=0, green=7),
}

WS_1 = WorldState(end_state)


WS_init = WorldState(init_state)

WS_0 = deepcopy(WS_init)


def foo(WS):
	WS.grabBall('bucket_1', 'hand_right', 'red')
	WS.dropBall('hand_right','bucket_2','red')

	WS.grabBall('bucket_0', 'hand_right', 'black')
	WS.dropBall('hand_right','bucket_2','black')

	WS.grabBall('bucket_1', 'hand_right', 'green')
	WS.dropBall('hand_right','bucket_3','green')

	WS.grabBall('bucket_0', 'hand_right', 'black')
	WS.dropBall('hand_right','bucket_3','black')

	return WS

WS_out = foo(WS_0)


print WS_out.getContainer('bucket_0')



# print WS_out.getHistory()
# print map(lambda x: x - WS_1.getSnippetWS(), WS_out.getHistory())


# # WS_2 = WorldState(init_state)


# def testWorldStateEqual():
# 	WS_0 = WorldState(init_state)
# 	WS_1 = WorldState(init_state)

# 	print '0: ' + str(WS_0==WS_1)
# 	print str(WS_0) + '\n-----------------------\n' + str(WS_1)
# 	print '========================================='

# 	WS_0.moveBall('bucket_0', 'bucket_3', 'black')
# 	print '1: ' + str(WS_0==WS_1)
# 	print str(WS_0) + '\n-----------------------\n' + str(WS_1)
# 	print '========================================='

# def testMoveBalls():
# 	WS_0 = WorldState(init_state)
# 	WS_0.moveBall('bucket_0', 'bucket_3', 'black')
# 	print '2: '# + str(WS_0==WS_1)
# 	print str(WS_0) + '\n-----------------------\n'# + str(WS_1)
# 	print '========================================='

# 	WS_0.moveBall('bucket_3', 'bucket_0', 'black')
# 	print '3: '# + str(WS_0==WS_1)
# 	print str(WS_0) + '\n-----------------------\n'# + str(WS_1)
# 	print '========================================='

# 	WS_0.moveBall('bucket_1', 'hand_right', 'green')
# 	print '4: '# + str(WS_0==WS_1)
# 	print str(WS_0) + '\n-----------------------\n'# + str(WS_1)
# 	print '========================================='

# 	WS_0.moveBall('bucket_1', 'hand_right', 'green')
# 	print '5: '# + str(WS_0==WS_1)
# 	print str(WS_0) + '\n-----------------------\n'# + str(WS_1)
# 	print '========================================='

# 	WS_0.moveBall('bucket_1', 'hand_right', 'green')
# 	print '6: '# + str(WS_0==WS_1)
# 	print str(WS_0) + '\n-----------------------\n'# + str(WS_1)
# 	print '========================================='

# 	WS_0.moveBall('bucket_0', 'hand_right', 'black')
# 	print '7: '# + str(WS_0==WS_1)
# 	print str(WS_0) + '\n-----------------------\n'# + str(WS_1)
# 	print '========================================='

# 	WS_0.moveBall('hand_right', 'hand_left', 'green')
# 	print '8: '# + str(WS_0==WS_1)
# 	print str(WS_0) + '\n-----------------------\n'# + str(WS_1)
# 	print '========================================='

# 	WS_0.moveBall('hand_left', 'bucket_0', 'green')
# 	print '9: '# + str(WS_0==WS_1)
# 	print str(WS_0) + '\n-----------------------\n'# + str(WS_1)
# 	print '========================================='

# def testSetWorldState():
# 	state = {
# 		'bucket_0': Bucket(black=1, red=2, green=3),
# 		'bucket_1': Bucket(black=4, red=5, green=6),
# 		'bucket_2': Bucket(black=7, red=8, green=9),
# 		'bucket_3': Bucket(black=10, red=11, green=12),
# 		'hand_left': Hand(),
# 		'hand_right': Hand(black=1, green=1)
# 	}

# 	WS_0 = WorldState(init_state)
# 	WS_0.setWorldState(state)
# 	print str(WS_0)

# testWorldStateEqual()
# testMoveBalls()
# testSetWorldState()
