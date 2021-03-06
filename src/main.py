'''
Reference implementation of node2vec. 

Author: Aditya Grover

For more details, refer to the paper:
node2vec: Scalable Feature Learning for Networks
Aditya Grover and Jure Leskovec 
Knowledge Discovery and Data Mining (KDD), 2016
'''

import argparse
import numpy as np
import networkx as nx
import node2vec
from collections import defaultdict

def parse_args():
    '''
    Parses the node2vec arguments.
    '''
    parser = argparse.ArgumentParser(description="Run node2vec.")

    parser.add_argument('--input', nargs='?', default='graph/karate.edgelist',
                        help='Input graph path')

    parser.add_argument('--output', nargs='?', default='emb/karate.emb',
                        help='Embeddings path')

    parser.add_argument('--dimensions', type=int, default=128,
                        help='Number of dimensions. Default is 128.')

    parser.add_argument('--walk-length', type=int, default=80,
                        help='Length of walk per source. Default is 80.')

    parser.add_argument('--num-walks', type=int, default=10,
                        help='Number of walks per source. Default is 10.')

    parser.add_argument('--window-size', type=int, default=10,
                        help='Context size for optimization. Default is 10.')

    parser.add_argument('--iter', default=1, type=int,
                      help='Number of epochs in SGD')

    parser.add_argument('--workers', type=int, default=8,
                        help='Number of parallel workers. Default is 8.')

    parser.add_argument('--p', type=float, default=1,
                        help='Return hyperparameter. Default is 1.')

    parser.add_argument('--q', type=float, default=1,
                        help='Inout hyperparameter. Default is 1.')

    parser.add_argument('--weighted', dest='weighted', action='store_true',
                        help='Boolean specifying (un)weighted. Default is unweighted.')
    parser.add_argument('--unweighted', dest='unweighted', action='store_false')
    parser.set_defaults(weighted=False)

    parser.add_argument('--directed', dest='directed', action='store_true',
                        help='Graph is (un)directed. Default is undirected.')
    parser.add_argument('--undirected', dest='undirected', action='store_false')
    parser.set_defaults(directed=False)

    return parser.parse_args()

def read_graph():
    '''
    Reads the input network in networkx.
    '''
    G = nx.Graph()
    with open(args.input) as f:
        for index,line in enumerate(f):
            if index % 100000 == 0:
                print("loading:",index)
            line = [int(x) for x in line.split()]
            G.add_edge(line[0],line[1])
    print("to undirected")
    G = G.to_undirected()
    print("loaded")
    return G

def learn_embeddings(G):
    '''
    Learn embeddings by optimizing the Skipgram objective using SGD.
    '''
    #walks = [map(str, walk) for walk in walks]
    from gensim.models import Word2Vec
    model = Word2Vec(size=args.dimensions, window=args.window_size, min_count=0, sg=1, workers=args.workers, iter=args.iter)
    degree = G.G.degree()
    model.raw_vocab = defaultdict(int,(zip([str(x) for x in degree.keys()],degree.values())))
    model.finalize_vocab()
    model.corpus_count = args.num_walks*args.walk_length*len(G.G.nodes())
    model.total_words = long(len(G.G.nodes()))
    model.train(G.simulate_walks(args.num_walks, args.walk_length))

    model.save_word2vec_format(args.output)
    return

def save_walks(G):
    with open(args.output,'w') as f:
        index = 0
        for walk in G.simulate_walks(args.num_walks, args.walk_length):
            if index % 100000 == 0:
                print("writing:",index)
            f.write(" ".join(walk)+"\n")
            index += 1

def main(args):
    '''
    Pipeline for representational learning for all nodes in a graph.
    '''
    nx_G = read_graph()
    G = node2vec.Graph(nx_G, args.directed, args.p, args.q)
    G.preprocess_transition_probs()
    #learn_embeddings(G)
    save_walks(G)

if __name__ == "__main__":
    args = parse_args()
    main(args)
