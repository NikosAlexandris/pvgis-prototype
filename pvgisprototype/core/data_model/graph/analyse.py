#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#

import networkx as nx

def basic_metrics(G):
    print(f"Number of nodes (models): {G.number_of_nodes()}")
    print(f"Number of edges (dependencies): {G.number_of_edges()}")
    print(f"Graph density: {nx.density(G):.4f}")
    print(f"Is the graph a DAG (Directed Acyclic Graph)? {nx.is_directed_acyclic_graph(G)}")
