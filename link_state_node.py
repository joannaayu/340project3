from simulator.node import Node
import json

#creating a graph that keys edges to dictionary of cost and seq_num
self.graph = {}


class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)

    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        edge = [self.id, neighbor]

        if latency == -1:
            self.graph[edge] = float('inf')

        # elif edge in self.graph:
        #     self.graph[edge]["cost"] = latency
        #     self.graph[edge]["seq_num"] = self.get_time()

        else:
            self.graph[edge] = {"cost": latency, "seq_num": self.get_time()}


        for e in self.graph:
            message = {"src": e[0], 'dst': e[1], 'cost': self.graph[e]["cost"], 'seq_num': self.graph[e]["seq_num"]}
            json_msg = json.dumps(message)
            self.send_to_neighbor(neighbor, json_msg)

        final_message = {"src": self.id, 'dst': neighbor, 'cost': self.graph[edge]['cost'], 'seq_num': self.graph[edge]['seq_num']}
        json_final = json.dumps(final_message)
        self.send_to_neighbors(json_final)


    # Fill in this function
    def process_incoming_routing_message(self, m):
        pass

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        return -1
