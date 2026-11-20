import heapq
from collections import deque
from typing import Any, Dict, List, Optional, Set, Tuple


class Graph:
    """
    Weighted Adjacency List Graph representing the store floor layout.
    """

    def __init__(self):
        # adj_list: { vertex_id: [ (neighbor_id, weight) ] }
        self.adj_list: Dict[str, List[Tuple[str, float]]] = {}
        # metadata: { vertex_id: { "label": str, "category_id": Optional[int] } }
        self.metadata: Dict[str, Dict[str, Any]] = {}

    def add_vertex(
        self,
        vertex_id: str,
        label: str,
        category_id: Optional[int] = None,
        description: str = ""
    ):
        """Adds a location vertex to the store graph."""
        if vertex_id not in self.adj_list:
            self.adj_list[vertex_id] = []
        self.metadata[vertex_id] = {
            "id": vertex_id,
            "label": label,
            "category_id": category_id,
            "description": description,
        }

    def add_edge(
        self,
        u: str,
        v: str,
        weight: float,
        bidirectional: bool = True
    ):
        """Adds a weighted walkway edge between two locations."""
        if u not in self.adj_list:
            self.add_vertex(u, u)
        if v not in self.adj_list:
            self.add_vertex(v, v)

        self.adj_list[u].append((v, float(weight)))
        if bidirectional:
            self.adj_list[v].append((u, float(weight)))

    def get_neighbors(self, vertex_id: str) -> List[Tuple[str, float]]:
        """Returns adjacent neighbors and walking distances."""
        return self.adj_list.get(vertex_id, [])

    def get_vertices(self) -> List[Dict[str, Any]]:
        """Returns all registered store locations."""
        return list(self.metadata.values())

    def bfs(self, start_vertex: str) -> List[str]:
        """
        Breadth-First Search (BFS) level-order traversal of the store layout.
        Time Complexity: O(V + E)
        """
        if start_vertex not in self.adj_list:
            return []

        visited: Set[str] = set()
        queue: deque = deque([start_vertex])
        visited.add(start_vertex)
        traversal_order: List[str] = []

        while queue:
            current = queue.popleft()
            traversal_order.append(current)

            for neighbor, _ in self.adj_list.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return traversal_order

    def dfs(self, start_vertex: str) -> List[str]:
        """
        Depth-First Search (DFS) store traversal.
        Time Complexity: O(V + E)
        """
        if start_vertex not in self.adj_list:
            return []

        visited: Set[str] = set()
        traversal_order: List[str] = []

        def _dfs_helper(vertex: str):
            visited.add(vertex)
            traversal_order.append(vertex)
            for neighbor, _ in self.adj_list.get(vertex, []):
                if neighbor not in visited:
                    _dfs_helper(neighbor)

        _dfs_helper(start_vertex)
        return traversal_order

    def dijkstra(
        self,
        start_vertex: str,
        end_vertex: str
    ) -> Dict[str, Any]:
        """
        Computes the shortest walking path and distance between two store locations
        using Dijkstra's algorithm with a min-priority heap.

        Time Complexity: O((V + E) log V)
        """
        if start_vertex not in self.adj_list or end_vertex not in self.adj_list:
            raise ValueError(f"Invalid start ({start_vertex}) or destination ({end_vertex}).")

        # Distances map initialized to infinity
        distances: Dict[str, float] = {v: float("inf") for v in self.adj_list}
        previous: Dict[str, Optional[str]] = {v: None for v in self.adj_list}
        distances[start_vertex] = 0.0

        # Min-heap priority queue: (current_distance, vertex_id)
        pq: List[Tuple[float, str]] = [(0.0, start_vertex)]
        visited_nodes: List[str] = []

        while pq:
            current_dist, u = heapq.heappop(pq)

            if u in visited_nodes:
                continue
            visited_nodes.append(u)

            if u == end_vertex:
                break

            for v, weight in self.adj_list.get(u, []):
                new_dist = current_dist + weight
                if new_dist < distances[v]:
                    distances[v] = new_dist
                    previous[v] = u
                    heapq.heappush(pq, (new_dist, v))

        # Reconstruct path
        path = []
        curr = end_vertex
        if distances[end_vertex] != float("inf"):
            while curr is not None:
                path.append(curr)
                curr = previous[curr]
            path.reverse()

        path_details = [self.metadata.get(node_id, {"id": node_id, "label": node_id}) for node_id in path]

        return {
            "start": start_vertex,
            "destination": end_vertex,
            "path": path,
            "path_details": path_details,
            "total_distance_meters": round(distances[end_vertex], 2) if distances[end_vertex] != float("inf") else None,
            "visited_nodes": visited_nodes,
            "reachable": distances[end_vertex] != float("inf"),
        }


def get_default_store_graph() -> Graph:
    """
    Factory function initializing the standard AUTO GEAR retail store layout.
    """
    g = Graph()

    # 1. Vertices (Aisles and service areas)
    g.add_vertex("ENTRANCE", "Store Entrance", description="Customer main entry point")
    g.add_vertex("AISLE_AUDIO", "Audio Aisle", category_id=1, description="Speakers and amplifiers")
    g.add_vertex("AISLE_LIGHTING", "Lighting Aisle", category_id=2, description="LED lights and replacement bulbs")
    g.add_vertex("AISLE_ACCESSORIES", "Accessories Section", category_id=3, description="Car horns and general accessories")
    g.add_vertex("AISLE_SECURITY", "Security Aisle", category_id=4, description="Car alarms and anti-theft kits")
    g.add_vertex("AISLE_EXTERIOR", "Exterior Shelf", category_id=5, description="Rain visors and exterior protection")
    g.add_vertex("AISLE_AIR_FRESHENER", "Air Freshener Display", category_id=6, description="Organic can air fresheners")
    g.add_vertex("CUSTOMER_SERVICE", "Customer Service Desk", description="Product assistance and advice")
    g.add_vertex("CASHIER", "Checkout Counter", description="Point of sale and payments")

    # 2. Weighted Edges (Walkway distances in meters)
    g.add_edge("ENTRANCE", "CUSTOMER_SERVICE", 5.0)
    g.add_edge("ENTRANCE", "AISLE_AUDIO", 10.0)
    g.add_edge("ENTRANCE", "AISLE_AIR_FRESHENER", 6.0)

    g.add_edge("CUSTOMER_SERVICE", "AISLE_AUDIO", 8.0)
    g.add_edge("CUSTOMER_SERVICE", "AISLE_ACCESSORIES", 9.0)

    g.add_edge("AISLE_AUDIO", "AISLE_LIGHTING", 7.0)
    g.add_edge("AISLE_LIGHTING", "AISLE_SECURITY", 6.5)
    g.add_edge("AISLE_SECURITY", "AISLE_EXTERIOR", 8.0)

    g.add_edge("AISLE_AIR_FRESHENER", "AISLE_ACCESSORIES", 7.5)
    g.add_edge("AISLE_ACCESSORIES", "AISLE_EXTERIOR", 9.0)

    g.add_edge("AISLE_EXTERIOR", "CASHIER", 11.0)
    g.add_edge("AISLE_SECURITY", "CASHIER", 10.5)
    g.add_edge("CUSTOMER_SERVICE", "CASHIER", 14.0)

    return g
