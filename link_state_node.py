from simulator.node import Node
import json
import heapq

class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)

        #creating a graph that keys edges to dictionary of cost and seq_num
        self.graph = {}


    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        edge = frozenset([self.id, neighbor])

        if latency == -1:
            self.graph[edge]["cost"] = float('inf')
            self.graph[edge]["seq_num"] = self.get_time()

        else:
            self.graph[edge] = {"cost": latency, "seq_num": self.get_time()}

        for e in self.graph:
            holder = []
            for v in e:
                holder.append(v)
            message = {"src": holder[0], "dst": holder[1], "cost": self.graph[e]["cost"], "seq_num": self.graph[e]["seq_num"]}
            json_msg = json.dumps(message)
            self.send_to_neighbor(neighbor, json_msg)

        final_message = {"src": self.id, "dst": neighbor, "cost": self.graph[edge]["cost"], "seq_num": self.graph[edge]["seq_num"]}
        json_final = json.dumps(final_message)
        self.send_to_neighbors(json_final)


    # Fill in this function
    def process_incoming_routing_message(self, m):
        curr_msg = json.loads(m)
        curr_edge = frozenset([curr_msg["src"], curr_msg["dst"]])

        if curr_edge in self.graph:
            old_seq_num = self.graph[curr_edge]["seq_num"]
            new_seq_num = curr_msg["seq_num"]
            if new_seq_num > old_seq_num:
                self.graph[curr_edge] = curr_msg
                json_msg = json.dumps(curr_msg)
                self.send_to_neighbors(json_msg)
        else:
            self.graph[curr_edge] = curr_msg
            json_msg = json.dumps(curr_msg)

            self.send_to_neighbors(json_msg)




    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        path_map = self.dijkstra(self.graph, self.id)
        if path_map[destination][1] == -1:
            return -1

        curr = destination

        while curr != self.id:

            if path_map[curr][1] == self.id:
                return curr

            curr = path_map[curr][1]


    def dijkstra(self, graph, start):

        nodes = []
        dist_prev = []
        visited = []
        neighbors = {}

        edges = [*graph.keys()]

        queue = []
        heapq.heapify(queue)


        for e in edges:
            edge = []

            for v in e:
                edge.append(v)

            if edge[0] not in neighbors:
                neighbors[edge[0]] = [edge[1]]
            else:
                neighbors[edge[0]].append(edge[1])

            if edge[1] not in neighbors:
                neighbors[edge[1]] = [edge[0]]
            else:
                neighbors[edge[1]].append(edge[0])

            if edge[0] not in nodes:
                nodes.append(edge)
                dist_prev.append([float('inf'), -1])
                visited.append(False)

            elif edge[1] not in nodes:
                nodes.append(edge)
                dist_prev.append([float('inf'), -1])
                visited.append(False)

        dist_prev[start] = [0, -1]
        heapq.heappush(queue, [0, start])

        while len(queue) != 0:
            curr_node = heapq.heappop(queue)
            visited[curr_node[1]] = True

            for n in neighbors[curr_node[1]]:
                if visited[n] == False:
                    if dist_prev[curr_node[1]][0] + graph[frozenset([curr_node[1], n])]["cost"] < dist_prev[n][0]:

                        dist_prev[n] = [dist_prev[curr_node[1]][0] + graph[frozenset([curr_node[1], n])]["cost"], curr_node[1]]

                        heapq.heappush(queue, [dist_prev[n][0], n])


        return dist_prev
