from LOTlib.DataAndObjects import FunctionData
import random
from WorldState import *

# # data for "sorting" algorithm
# initial_state_0 = {
#     'bucket_0': Bucket(black=10, red=0, green=0),
#     'bucket_1': Bucket(black=0, red=3, green=3),
# }

# end_state_0 = {
#     'bucket_0': Bucket(black=10, red=0, green=0),
#     'bucket_2': Bucket(black=0, red=3, green=0),
#     'bucket_3': Bucket(black=0, red=0, green=3),
# }

# initial_state_1 = {
#     'bucket_0': Bucket(black=10, red=0, green=0),
#     'bucket_1': Bucket(black=0, red=3, green=5),
# }

# end_state_1 = {
#     'bucket_0': Bucket(black=10, red=0, green=0),
#     'bucket_2': Bucket(black=0, red=3, green=0),
#     'bucket_3': Bucket(black=0, red=0, green=5),
# }

# initial_state_2 = {
#     'bucket_0': Bucket(black=10, red=0, green=0),
#     'bucket_1': Bucket(black=0, red=10, green=8),
# }

# end_state_2 = {
#     'bucket_0': Bucket(black=10, red=0, green=0),
#     'bucket_2': Bucket(black=0, red=10, green=0),
#     'bucket_3': Bucket(black=0, red=0, green=8),
# }


# data for "sorting + hitchhiker"
initial_state_0 = {
    'bucket_0': Bucket(black=10, red=0, green=0),
    'bucket_1': Bucket(black=0, red=3, green=3),
}

end_state_0 = {
    'bucket_0': Bucket(black=4, red=0, green=0),
    'bucket_2': Bucket(black=3, red=3, green=0),
    'bucket_3': Bucket(black=3, red=0, green=3),
}

initial_state_1 = {
    'bucket_0': Bucket(black=10, red=0, green=0),
    'bucket_1': Bucket(black=0, red=3, green=5),
}

end_state_1 = {
    'bucket_0': Bucket(black=2, red=0, green=0),
    'bucket_2': Bucket(black=3, red=3, green=0),
    'bucket_3': Bucket(black=5, red=0, green=5),
}

initial_state_2 = {
    'bucket_0': Bucket(black=20, red=0, green=0),
    'bucket_1': Bucket(black=0, red=10, green=8),
}

end_state_2 = {
    'bucket_0': Bucket(black=2, red=0, green=0),
    'bucket_2': Bucket(black=10, red=10, green=0),
    'bucket_3': Bucket(black=8, red=0, green=8),
}


WS0 = (WorldState(initial_state_0), WorldState(end_state_0))
WS1 = (WorldState(initial_state_1), WorldState(end_state_1))
WS2 = (WorldState(initial_state_2), WorldState(end_state_2))

WSList = [WS0, WS1, WS2]

def make_data(data_size=1, alpha=0.95):
    data = []
    randomWSList = random.sample(WSList, data_size)
    for i in range(len(randomWSList)):
        data.append(FunctionData(input=[randomWSList[i][0]], output=randomWSList[i][1], alpha=alpha))
    return data



# data = [ FunctionData(input=[WS0_initial], output=WS0_end, alpha=0.95)]
# data_1 = [ FunctionData(input=[WS0_initial], output=WS0_end, alpha=0.95), FunctionData(input=[WS1_initial], output=WS1_end, alpha=0.95)]