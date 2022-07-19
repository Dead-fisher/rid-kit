import numpy as np

def inverse(list):
    outarray = np.zeros(shape=list.shape)
    for i in range(len(list)):
        if list[i][1] > list[i][0]:
            # outarray[i][0] = 0.1/(list[i][1]%(2*np.pi)-list[i][0]%(2*np.pi))**2
            # outarray[i][1] = -0.1/(list[i][1]%(2*np.pi)-list[i][0]%(2*np.pi))**2
            outarray[i][0] = np.abs(list[i][0]-list[i][1])%(2*np.pi)
            outarray[i][1] = -np.abs(list[i][0]-list[i][1])%(2*np.pi)
        else:
            outarray[i][0] = np.abs(list[i][0]-list[i][1])%(2*np.pi)
            outarray[i][1] = -np.abs(list[i][0]-list[i][1])%(2*np.pi)
            # outarray[i][0] = -0.1/(list[i][1]%(2*np.pi)-list[i][0]%(2*np.pi))**2
            # outarray[i][1] = 0.1/(list[i][1]%(2*np.pi)-list[i][0]%(2*np.pi))**2
    return outarray

input1 = np.random.uniform(0,20,size=(100000,1))
input2 = np.random.uniform(21,41,size=(100000,1))
input = np.concatenate((input1,input2), axis=1)
output = inverse(input) + np.random.normal(0, 0.1)
data = np.concatenate((input,output), axis=1)
np.savetxt("./data/data.raw", data)