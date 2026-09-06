"""Risk-aware graph route planner (Dijkstra).

Nodes  = road intersections.
Edges  = road segments, each with a base travel time (minutes) and a current
         risk score (0-100).

edge_cost = base_time + risk_penalty(risk)
  risk > 80 : very high penalty  (effectively avoid)
  risk > 50 : moderate penalty
  else      : no penalty

Two planning modes:
  * "fastest" -> ignores risk (pure travel time)
  * "safe"    -> applies risk penalty so unsafe segments are avoided
"""
import heapq
from collections import defaultdict

from .reliability import RISK_CAUTION, RISK_UNSAFE


def risk_penalty(base_time, risk):
    if risk > RISK_UNSAFE:
        return base_time * 10.0 + 1000.0
    if risk > RISK_CAUTION:
        return base_time * 2.0
    return 0.0


def edge_cost(base_time, risk, mode="safe"):
    if mode == "fastest":
        return base_time
    return base_time + risk_penalty(base_time, risk)


class RoadGraph:
    """Lightweight road graph supporting risk-aware shortest paths."""

    def __init__(self):
        self.nodes = {}   # node_id -> {"lat", "lon", "name"}
        self.edges = {}   # edge_id -> {"u","v","base_time","risk","name", ...}
        self.adj = defaultdict(list)  # node_id -> [(neighbor, edge_id)]

    def add_node(self, node_id, lat, lon, name=None):
        self.nodes[node_id] = {"lat": lat, "lon": lon, "name": name or node_id}

    def add_edge(self, edge_id, u, v, base_time, risk=0, name=None,
                 bidirectional=True, **extra):
        data = {"id": edge_id, "u": u, "v": v, "base_time": float(base_time),
                "risk": float(risk), "name": name or edge_id}
        data.update(extra)
        self.edges[edge_id] = data
        self.adj[u].append((v, edge_id))
        if bidirectional:
            self.adj[v].append((u, edge_id))

    def set_risk(self, edge_id, risk):
        if edge_id in self.edges:
            self.edges[edge_id]["risk"] = float(risk)

    def plan(self, start, goal, mode="safe"):
        """Dijkstra shortest path. Returns a route dict or None if unreachable."""
        if start not in self.nodes or goal not in self.nodes:
            return None
        dist = {start: 0.0}
        prev = {}            # node -> (prev_node, edge_id)
        pq = [(0.0, start)]
        visited = set()
        while pq:
            d, node = heapq.heappop(pq)
            if node in visited:
                continue
            visited.add(node)
            if node == goal:
                break
            for neighbor, edge_id in self.adj[node]:
                if neighbor in visited:
                    continue
                e = self.edges[edge_id]
                cost = edge_cost(e["base_time"], e["risk"], mode)
                nd = d + cost
                if nd < dist.get(neighbor, float("inf")):
                    dist[neighbor] = nd
                    prev[neighbor] = (node, edge_id)
                    heapq.heappush(pq, (nd, neighbor))
        if goal not in dist:
            return None

        # Reconstruct path.
        node_path = [goal]
        edge_path = []
        cur = goal
        while cur != start:
            p, edge_id = prev[cur]
            edge_path.append(edge_id)
            node_path.append(p)
            cur = p
        node_path.reverse()
        edge_path.reverse()

        total_time = sum(self.edges[e]["base_time"] for e in edge_path)
        risks = [self.edges[e]["risk"] for e in edge_path] or [0.0]
        return {
            "mode": mode,
            "nodes": node_path,
            "edges": edge_path,
            "total_cost": round(dist[goal], 2),
            "total_time": round(total_time, 2),
            "max_risk": round(max(risks)),
            "avg_risk": round(sum(risks) / len(risks)),
            "coordinates": [[self.nodes[n]["lat"], self.nodes[n]["lon"]]
                            for n in node_path],
        }

    def plan_comparison(self, start, goal):
        """Plan both the fastest and the risk-aware safe route and compare."""
        fastest = self.plan(start, goal, mode="fastest")
        safe = self.plan(start, goal, mode="safe")
        avoided = []
        if fastest and safe:
            fastest_edges = set(fastest["edges"])
            safe_edges = set(safe["edges"])
            for e in fastest_edges - safe_edges:
                if self.edges[e]["risk"] > RISK_CAUTION:
                    avoided.append({
                        "id": e,
                        "name": self.edges[e]["name"],
                        "risk": round(self.edges[e]["risk"]),
                    })
        return {"fastest": fastest, "safe": safe, "avoided": avoided}
