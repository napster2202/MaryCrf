import numpy as np
from numpy import array

class HMM:
    def __init__(self, pi, A, B1, B2, B3):
        """
        Datastructure that holds the probability tables for
        a discrete observation HMM.

        :param pi: Initial probabilities
        :param A: Transition probabilities
        :param B: Observation probabilities
        """
        self.pi = pi
        self.A = A
        self.B1 = B1
        self.B2 = B2
        self.B3 = B3
        self.num_states = len(pi)

        
def sample(dist):
    """
    This function samples from a discrete one-dimensional probability distribution
    
    :param dist: probability distribution given as numpy array
    :returns: index of sampled value
    """
    return dist.cumsum().searchsorted(np.random.sample())

def sampleG(dist):
    """
    This function samples from a discrete one-dimensional probability distribution
    
    :param dist: probability distribution given as numpy array
    :returns: index of sampled value
    """
    return np.random.normal(dist[0],dist[1])

def gaussian(x, mu, sig):
    return 1.0 / (sig * np.sqrt(2 * np.pi)) * np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

def calcB(hmm, obs):
    b1 = gaussian(obs[0] * np.ones(hmm.B1.shape[1]),hmm.B1[0],hmm.B1[1])
    b2 = gaussian(obs[1] * np.ones(hmm.B2.shape[1]),hmm.B2[0],hmm.B2[1])
    b3 = gaussian(obs[2] * np.ones(hmm.B3.shape[1]),hmm.B3[0],hmm.B3[1])
    return b1 * b2 * b3;

def forwardHMM(hmm, obs):
    """
    Computes the filtering distribution (forward messages) for a given 
    Hidden Markov Model and observations.
    
    :param hmm: HMM datastructure
    :param observations: Numpy array containing the observations

    :return f: filtering distribution (each row represents a time step)
    """ 
    f = np.zeros((len(obs[0])+1,len(hmm.pi)))
    f[0] = hmm.pi
    
    for t in range(0,len(obs[0])):
        v = (hmm.B1[obs[0,t]] * hmm.B2[obs[1,t]]*hmm.B3[obs[2,t]]) * np.dot((hmm.A.T),f[t])
        f[t+1] = v / v.sum()
    return f

def forwardHMMG(hmm, obs):
    """
    Computes the filtering distribution (forward messages) for a given 
    Hidden Markov Model and observations.
    
    :param hmm: HMM datastructure
    :param observations: Numpy array containing the observations

    :return f: filtering distribution (each row represents a time step)
    """ 
    f = np.zeros((len(obs[0])+1,len(hmm.pi)))
    f[0] = hmm.pi
    
    for t in range(0,len(obs[0])):
        bs = calcB(hmm,obs[:,t])
        v = bs * np.dot((hmm.A.T),f[t])
        f[t+1] = v / v.sum()
    return f
def backwardHMM(hmm, obs):
    """
    Computes the backward messages for a given 
    Hidden Markov Model and observations.
    
    :param hmm: HMM datastructure
    :param observations: Numpy array containing the observations

    :return b: backward messages (each row represents a time step)
    """
    b = np.zeros((len(obs[0])+1,len(hmm.pi)))
    b[len(obs[0])] = np.ones(len(hmm.pi)) * 10000000

    for t in reversed(range(1,len(obs[0])+1)):
        b[t-1] = np.dot(hmm.A, (hmm.B1[obs[0,t-1]] * hmm.B2[obs[1,t-1]] * hmm.B3[obs[2,t-1]]).T * b[t])
        
    return b

def backwardHMMG(hmm, obs):
    """
    Computes the backward messages for a given 
    Hidden Markov Model and observations.
    
    :param hmm: HMM datastructure
    :param observations: Numpy array containing the observations

    :return b: backward messages (each row represents a time step)
    """
    b = np.zeros((len(obs[0])+1,len(hmm.pi)))
    b[len(obs[0])] = np.ones(len(hmm.pi)) * 1000#0000

    for t in reversed(range(1,len(obs[0])+1)):
#         bs = (hmm.B1[obs[0,t-1]] * hmm.B2[obs[1,t-1]] * hmm.B3[obs[2,t-1]])
        bs = calcB(hmm,obs[:,t-1])
        v = np.dot(hmm.A, bs.T * b[t])
        b[t-1] = v / v.sum()
        
    return b

def forward_backwardHMM(hmm, obs):
    """
    Computes the posterior (smoothing distribution) for a given 
    Hidden Markov Model and observations.
    
    :param hmm: HMM datastructure
    :param observations: Numpy array containing the observations

    :return post: posterior distribution (each row represents a time step)

    """
    f = forwardHMM(hmm, obs)
    b = backwardHMM(hmm,obs)

    post = f * b;

    post = post / post.sum(1)[:,np.newaxis]
    return post

def forward_backwardHMMG(hmm, obs):
    """
    Computes the posterior (smoothing distribution) for a given 
    Hidden Markov Model and observations.
    
    :param hmm: HMM datastructure
    :param observations: Numpy array containing the observations

    :return post: posterior distribution (each row represents a time step)

    """
    f = forwardHMMG(hmm, obs)
    b = backwardHMMG(hmm,obs)

    post = f * b;

    post = post / post.sum(1)[:,np.newaxis]
    return post

def viterbiHMM(hmm, observations):
    """
    Computes the most probable state sequence for a given
    Hidden Markov Model and observations.
    
    :param hmm: HMM datastructure
    :param observations: Numpy array containing the observations

    :return path: Numpy array of state ids representing the most probable state sequence
    :return v: Viterbi messages/variables
    """
    num_frames = observations.shape[1]
    # viterbi variable
    vs = np.empty((num_frames + 1, hmm.num_states))
    # best precursor state
    bps = np.empty_like(vs, dtype=int)
    vs[0] = hmm.pi
    for v_prev, v, bp, obs in zip(vs[:-1], vs[1:], bps[1:], observations.T):
        tmp = v_prev[:,np.newaxis] * hmm.A * hmm.B1[obs[0]] * hmm.B2[obs[1]] * hmm.B3[obs[2]]
        bp[:] = tmp.argmax(0)
        v[:] = tmp.max(0)
        v /= v.sum()

    path = np.empty(num_frames + 1, dtype=int)
    path[-1] = vs[-1].argmax()
    for i in range(len(path)-2, -1, -1):
        path[i] = bps[i+1, path[i+1]]
        
    return path, vs

def viterbiHMMG(hmm, observations):
    """
    Computes the most probable state sequence for a given
    Hidden Markov Model and observations.
    
    :param hmm: HMM datastructure
    :param observations: Numpy array containing the observations

    :return path: Numpy array of state ids representing the most probable state sequence
    :return v: Viterbi messages/variables
    """
    num_frames = observations.shape[1]
    # viterbi variable
    vs = np.empty((num_frames + 1, hmm.num_states))
    # best precursor state
    bps = np.empty_like(vs, dtype=int)
    vs[0] = hmm.pi
    for v_prev, v, bp, obs in zip(vs[:-1], vs[1:], bps[1:], observations.T):
#         bs = hmm.B1[obs[0]] * hmm.B2[obs[1]] * hmm.B3[obs[2]]
        bs = calcB(hmm,obs)
        tmp = v_prev[:,np.newaxis] * hmm.A * bs
        bp[:] = tmp.argmax(0)
        v[:] = tmp.max(0)
        v /= v.sum()

    path = np.empty(num_frames + 1, dtype=int)
    path[-1] = vs[-1].argmax()
    for i in range(len(path)-2, -1, -1):
        path[i] = bps[i+1, path[i+1]]
        
    return path, vs

def generate_sequence(hmm, len_sequence):
    """
    Generates hidden and observed states using the given hmm model. 
    Note that the first hidden state comes only from the initial distribution. This means
    that the hidden_state_sequence has one more value than there are observations
    
    :param hmm: HMM datastructure
    :param len_sequence: Length of sequence

    :return hidden_state_sequence: Numpy array of state ids [len_sequence+1, 1]
    :return observations: Numpy array of state ids [len_sequence, 1]
    """
    hidden_state_sequence = np.empty(len_sequence + 1, dtype=int)
    observations = np.empty((3, len_sequence), dtype=int)
    hidden_state_sequence[0] = sample(hmm.pi)
    for i in range(len_sequence):
        hidden_state_sequence[i+1] = sample(hmm.A[hidden_state_sequence[i], :])
        observations[0, i] = sample(hmm.B1[:, hidden_state_sequence[i+1]])
        observations[1, i] = sample(hmm.B2[:, hidden_state_sequence[i+1]])
        observations[2, i] = sample(hmm.B3[:, hidden_state_sequence[i+1]])
    return hidden_state_sequence, observations
    

def generate_sequenceG(hmm, len_sequence):
    """
    Generates hidden and observed states using the given hmm model. 
    Note that the first hidden state comes only from the initial distribution. This means
    that the hidden_state_sequence has one more value than there are observations
    
    :param hmm: HMM datastructure
    :param len_sequence: Length of sequence

    :return hidden_state_sequence: Numpy array of state ids [len_sequence+1, 1]
    :return observations: Numpy array of state ids [len_sequence, 1]
    """
    hidden_state_sequence = np.empty(len_sequence + 1, dtype=int)
    observations = np.empty((3, len_sequence), dtype=int)
    hidden_state_sequence[0] = sample(hmm.pi)
    for i in range(len_sequence):
        hidden_state_sequence[i+1] = sample(hmm.A[hidden_state_sequence[i], :])
        observations[0, i] = sampleG(hmm.B1[:, hidden_state_sequence[i+1]])
        observations[1, i] = sampleG(hmm.B2[:, hidden_state_sequence[i+1]])
        observations[2, i] = sampleG(hmm.B3[:, hidden_state_sequence[i+1]])
    return hidden_state_sequence, observations
