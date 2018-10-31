import numpy as np
import pylab
import matplotlib.pyplot as plt

def compare_signal(signal, samples_per_symbol):

    signal = signal[1:-1]



    signal_ceil = max(signal)
    signal_floor = min(signal)
    ratio = 0.45

    threshold = ((signal_ceil - signal_floor)*ratio)   + signal_floor



    #pylab.plot(signal)


    signal_zero_centered = [(x - threshold) for x in signal]

    zero_crossings = np.where(np.diff(np.signbit(signal_zero_centered)))[0]
    #np.append(zero_crossings, len(signal_zero_centered))
    zero_crossings = zero_crossings.tolist()

    #print(zero_crossings)
    #print(type(zero_crossings))
    zero_crossings.append(len(signal_zero_centered))


    allindexes = []
    chosen_samples = []
    for a in range(len(zero_crossings)-1):
        index = zero_crossings[a] + round(samples_per_symbol/2)
        while(index < (zero_crossings[a+1]-(samples_per_symbol/8))):
            #print(index)

            allindexes.append(index)
            chosen_samples.append(signal_zero_centered[index])
            index += round(samples_per_symbol)

    signal_samples = []
    for x in range(len(allindexes)):
        signal_samples.append(signal[allindexes[x]])
    pylab.plot(signal)
    #plt.axhline(y=threshold, color='k', linestyle='-')
    #plt.scatter(allindexes, signal_samples, color='orange')
    #pylab.show()
    #print(chosen_samples)
    result = np.where(np.asarray(chosen_samples) > 0, 1, 0)

    return result
