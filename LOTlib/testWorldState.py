from LOTlib.WorldState import *

WS_0 = WorldState(n_black_ball=1, n_red_ball=4, n_green_ball=4)
WS_1 = WorldState(n_black_ball=1, n_red_ball=4, n_green_ball=4)

print '0: ' + str(WS_0==WS_1)
print str(WS_0) + '\n-----------------------\n' + str(WS_1)
print '========================================='

WS_0.moveBall('bucket_0', 'bucket_3', 'black')
print '1: ' + str(WS_0==WS_1)
print str(WS_0) + '\n-----------------------\n' + str(WS_1)
print '========================================='

WS_0.moveBall('bucket_0', 'bucket_3', 'black')
print '2: ' + str(WS_0==WS_1)
print str(WS_0) + '\n-----------------------\n' + str(WS_1)
print '========================================='

WS_0.moveBall('bucket_3', 'bucket_0', 'black')
print '3: ' + str(WS_0==WS_1)
print str(WS_0) + '\n-----------------------\n' + str(WS_1)

state = {
	'bucket_0': Bucket(black=1, red=2, green=3),
	'bucket_1': Bucket(black=4, red=5, green=6),
	'bucket_2': Bucket(black=7, red=8, green=9),
	'bucket_3': Bucket(black=10, red=11, green=12)
}

WS_0.setWorldState(state)
print str(WS_0)