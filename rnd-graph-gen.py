#!/usr/bin/python3
#######################################################################
# Copyright 2020 Josep Argelich

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#######################################################################

# Libraries

import sys
import random
from math import ceil
import os
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
 


# Classes 

class CNF():
    """A CNF formula randomly generated"""

    def __init__(self, num_nodes, edge_prob, num_colors):
        """
        Initialization
        num_nodes: Number of nodes
        edge_prob: Edge probability between two nodes
        num_colors: Number of colors to color the graph
        clauses: List of clauses
        """
        self.num_nodes = num_nodes
        self.edge_prob = edge_prob
        self.num_colors = num_colors
        self.clauses = []
        self.gen_node_clauses()
        self.gen_edge_clauses()

    def gen_node_clauses(self):
        '''Generate the ALO + AMO clauses for all the nodes'''
        for n in range(self.num_nodes):
            # ALO
            var1 = n * self.num_colors + 1
            self.clauses.append([i for i in range(var1, var1 + self.num_colors)])
            # AMO
            for v1 in range(var1, var1 + self.num_colors - 1):
                for v2 in range(v1 + 1, var1 + self.num_colors):
                    self.clauses.append([-v1, -v2])

    def gen_edge_clauses(self):
        '''Generates the clauses for each pair of nodes that have an edge with certain prob'''
        for n1 in range(self.num_nodes - 1):
            for n2 in range(n1 + 1, self.num_nodes):
                if random.random() < self.edge_prob:
                    var1 = n1 * self.num_colors + 1
                    var2 = n2 * self.num_colors + 1
                    for c in range(self.num_colors):
                        self.clauses.append([-(var1 + c), -(var2 + c)])

    def writte_output(self):
        clauses = ''
        coment = "c Random CNF formula\n"
        param  = "p cnf %d %d\n" % (self.num_nodes * self.num_colors, len(self.clauses))
        with open('benchmarks/graph.cnf', 'w') as file:
            file.write(coment)
            file.write(param)
            for c in self.clauses:
                clauses = ("%s 0\n" % " ".join(map(str, c)))
                file.write(clauses)


def getOutput():
    with open('output.cnf') as line:
        for i,l in enumerate(line):
            if i ==1: return l
    
def getcolors(solution):
    colorslist = []
    i = 0
    for v in solution.split()[1:]:
        i += 1
        if int(v) > 0: colorslist.append(str(i))
        if i % num_colors == 0: i = 0
    return colorslist

def getConnections():
    #We skip the nodes information that goes in the graph.cnf file from line 1 to sum(num_colors-1)*num_nodes+1
    fromm, to = [], []
    nodes_info = ((sum([int(_) for _ in range(1,num_colors)])+1)*num_nodes)+1
    j = 0 
    with open('benchmarks/graph.cnf') as filee:
        for i,l in enumerate(filee):
            if i>nodes_info:
                if j%num_colors==0:
                    fromm.append(str(ceil(abs(int(l.split()[0]))/num_colors)))
                    to.append(str(ceil(abs(int(l.split()[1]))/num_colors)))
                j+=1
    return fromm, to

def paint_graph():
    solution = getOutput()
    colors = getcolors(solution)
    nodes = [str(_) for _ in range(1,num_nodes+1)]
    fromm , to = getConnections()

    df = pd.DataFrame({ 'from': fromm, 'to':to})
    carac = pd.DataFrame({ 'ID':nodes, 'myvalue':colors})
    
    G=nx.from_pandas_edgelist(df, 'from', 'to', create_using=nx.Graph() )
    G.nodes()
    carac= carac.set_index('ID')
    carac=carac.reindex(G.nodes())
    carac['myvalue']=pd.Categorical(carac['myvalue'])
    carac['myvalue'].cat.codes

    nx.draw(G, with_labels=True, node_color=carac['myvalue'].cat.codes, cmap=plt.cm.Set1, node_size=1500)
    plt.show()
    
# Main

if __name__ == '__main__' :
    """A random CNF generator"""

    # Check parameters
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        sys.exit("Use: %s <num-nodes> <edge-prob> <num-colors> [<random-seed>]" % sys.argv[0])
    
    try:
        num_nodes = int(sys.argv[1])
    except:
        sys.exit("ERROR: Number of nodes not an integer (%s)." % sys.argv[1])
    if (num_nodes < 1):
        sys.exit("ERROR: Number of nodes must be >= 1 (%d)." % num_nodes)

    try:
        edge_prob = float(sys.argv[2])
    except:
        sys.exit("ERROR: Edge probability not a float (%s)." % sys.argv[2])
    if (edge_prob < 0 or edge_prob > 1):
        sys.exit("ERROR: Edge probability must be in [0, 1] range (%d)." % edge_prob)

    try:
        num_colors = int(sys.argv[3])
    except:
        sys.exit("ERROR: Number of colors not an integer (%s)." % sys.argv[3])
    if (num_colors < 1):
        sys.exit("ERROR: Number of colors must be >= 1 (%d)." % num_colors)

    if len(sys.argv) > 4:
        try:
            seed = int(sys.argv[4])
        except:
            sys.exit("ERROR: Seed number not an integer (%s)." % sys.argv[4])
    else:
        seed = None

    # Initialize random seed (current time)
    random.seed(seed)
    # Create a CNF instance
    cnf_formula = CNF(num_nodes, edge_prob, num_colors)
    # Writte in output file the formula
    cnf_formula.writte_output()
    #Run the solver
    os.system('python sgdb-solver.py graph.cnf')
    #Paint the out.png
    paint_graph()
