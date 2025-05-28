from collections import defaultdict, deque


def topological_sort(graph: dict) -> list:
    """Perform topological sort using Kahn's algorithm"""
    in_degree = defaultdict(int)
    for node in graph:
        for neighbor in graph.get(node, []):
            in_degree[neighbor] += 1
            
    queue = deque([node for node in graph if in_degree[node] == 0])
    result = []
    
    while queue:
        node = queue.popleft()
        result.append(node)
        
        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
                
    # Check for cycles
    if len(result) < len(graph):
        raise ValueError("Graph has a cycle")
        
    return result
