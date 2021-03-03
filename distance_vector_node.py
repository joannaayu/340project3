from simulator.node import Node
import json
import copy


class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        #keeps own router information with keys to cost and path for all nodes
        self.router_dv = {self.id: {"cost": 0, "path": [self.id]}}
        #cost from current router to adjacent neighbors
        self.neighbor_cost_dv = {}
        #neighbors path & cost to following destination
        self.neighbors_dv = {}

        self.seq_nums = {}

        self.is_recalc = False

    # Return a string
    def __str__(self):
        return "nodes nodes nodes nodes nodes nodes nodes"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        print("BEFORE")
        print("THIS IS SELF ID", self.id)
        print("THIS IS SELF ROUTER", self.router_dv)
        print("THIS IS NEIGHBOR", neighbor)
        print("THIS IS LATENCY", latency)
        print()

        is_updated = False

        #updating the router's dv, neighbors, & neighbors_dv/cost if link is dropped
        if latency == -1:
            self.neighbors.remove(neighbor)
            del self.neighbors_dv[neighbor]
            del self.neighbor_cost_dv[neighbor]

            # print("neighborsdv", self.neighbors_dv)
            print("LINK IS DROPPED---------------------------------------------------")
            print("unique")
            is_updated = True
            # self.delete = True

            #checks each node in the graph & updates if link dropped is in the path
            for node in self.router_dv:
                if neighbor in self.router_dv[node]["path"]:
                    self.router_dv[node]["cost"] = float('inf')
                    # self.router_dv[node]["path"] = []
                    is_updated = True
                    #updates the node if it is a neighbor because there is a sure pathway
                    if neighbor in self.neighbors:
                        self.router_dv[node]["path"] = [self.id, node]
                        self.router_dv[node]["cost"] = self.neighbor_cost_dv[node]

            for neigh in self.neighbors_dv:
                for n in self.neighbors_dv[neigh]:
                    if (frozenset([self.id, neighbor]).issubset(frozenset(self.neighbors_dv[neigh][n]["path"]))) == True:
                        self.neighbors_dv[neigh][n]["cost"] = float('inf')

        #updating the router's dv, neighbors, & neighbors_dv/cost if a new node is present
        elif neighbor not in self.neighbors:
            print("I have a new neighbor")
            self.neighbor_cost_dv[neighbor] = latency
            self.neighbors_dv[neighbor] = {}
            self.neighbors.append(neighbor)
            self.router_dv[neighbor] = {"cost": latency, "path": [self.id, neighbor]}
            is_updated = True

        #updating the router's dv, neighbors, & neighbors_dv/cost if a cost is changed
        else:
            print("LATENCE CHANGE")
            if latency < self.neighbor_cost_dv[neighbor]:

                self.neighbor_cost_dv[neighbor] = latency
                old_cost = self.router_dv[neighbor]["cost"]
                old_path = self.router_dv[neighbor]["path"]
                is_updated = True

                if self.neighbor_cost_dv[neighbor] != self.router_dv[neighbor]["cost"]:

                    self.router_dv[neighbor] = {"cost": self.neighbor_cost_dv[neighbor], "path": [self.id, neighbor]}
                    is_updated = True

                    for node in self.router_dv:
                        if node != neighbor:
                            if (frozenset(old_path).issubset(frozenset(self.router_dv[node]["path"]))) == True:
                                print("FROZEN SET WORKS")
                                print("THIS IS NODE NUM", node)
                                self.router_dv[node]["cost"] = (self.router_dv[node]["cost"] - old_cost) + latency
                                is_updated = True

                    for neigh in self.neighbors_dv:
                        for n in self.neighbors_dv[neigh]:
                            if (frozenset(old_path).issubset(frozenset(self.neighbors_dv[neigh][n]["path"]))) == True:
                                self.neighbors_dv[neigh][n]["cost"] = float('inf')

            elif latency > self.neighbor_cost_dv[neighbor]:

                self.neighbor_cost_dv[neighbor] = latency
                old_cost = self.router_dv[neighbor]["cost"]
                old_path = self.router_dv[neighbor]["path"]
                is_updated = True

                if self.neighbor_cost_dv[neighbor] != self.router_dv[neighbor]["cost"]:
                    old_path = self.router_dv[neighbor]["path"]
                    self.router_dv[neighbor] = {"cost": self.neighbor_cost_dv[neighbor], "path": [self.id, neighbor]}
                    is_updated = True

                    for node in self.router_dv:
                        if node != neighbor:
                            if (frozenset(old_path).issubset(frozenset(self.router_dv[node]["path"]))) == True:
                                self.router_dv[node]["cost"] = (self.router_dv[node]["cost"] - old_cost) + latency
                                is_updated = True

                    for neigh in self.neighbors_dv:
                        for n in self.neighbors_dv[neigh]:
                            if (frozenset(old_path).issubset(frozenset(self.neighbors_dv[neigh][n]["path"]))) == True:
                                self.neighbors_dv[neigh][n]["cost"] = float('inf')
                                self.neighbors_dv[neigh][n]["path"] = []
                            if (frozenset(self.router_dv[neighbor]["path"]).issubset(frozenset(self.neighbors_dv[neigh][n]["path"]))) == True:
                                self.neighbors_dv[neigh][n]["cost"] = float('inf')
                                self.neighbors_dv[neigh][n]["path"] = []

        if is_updated == True:
            dv = copy.deepcopy(self.router_dv)
            self.router_dv = self.bellman_ford(dv)[0]


        # print("THIS IS SELF ID", self.id)
        # print("THIS IS SELF ROUTER", self.router_dv)
        # print("THIS IS NEIGHBOR", neighbor)
        # print("THIS IS LATENCY", latency)
        # print()

        if is_updated == True:
            message = {"src": self.id, "dv": self.router_dv, "seq_num": self.get_time()}
            json_msg = json.dumps(message)
            self.send_to_neighbors(json_msg)

    # Fill in this function
    def process_incoming_routing_message(self, m):
        is_updated = False
        msg = json.loads(m)
        src_node = msg["src"]
        str_dv = msg["dv"]
        src_dv = {}
        for i in str_dv:
            new_val = str_dv[i]
            num_key = int(i)
            src_dv[num_key] = new_val
        src_seq_num = msg["seq_num"]
        broken_path = []

        print("NEW PROCESSING")

        #accounts for timing errors and only gets ones sent latest
        if src_node not in self.seq_nums or src_seq_num > self.seq_nums[src_node]:
            print("THIS IS SRC DV", src_dv)
            print("THIS IS SELF ROUTER BEFORE", self.router_dv)
            print()

            self.seq_nums[src_node] = src_seq_num
            self.neighbors_dv[src_node] = src_dv
            is_updated = False

            #checking for if the neighbor cost is less so we want to update
            if self.neighbor_cost_dv[src_node] < self.router_dv[src_node]["cost"]:

                old_path = self.router_dv[src_node]["path"]
                old_cost = self.router_dv[src_node]["cost"]
                self.router_dv[src_node]["cost"] = self.neighbor_cost_dv[src_node]
                self.router_dv[src_node]["path"] = [self.id, src_node]
                is_updated = True

                for node in self.router_dv:
                    if node != src_node:
                        if (frozenset(old_path).issubset(frozenset(self.router_dv[node]["path"]))) == True:
                            self.router_dv[node]["cost"] = (self.router_dv[node]["cost"] - old_cost) + self.router_dv[src_node]["cost"]

                        if (frozenset([self.id, src_node]).issubset(frozenset(self.router_dv[node]["path"]))) == True:
                            self.router_dv[node]["cost"] = (self.router_dv[node]["cost"] - old_cost) + self.router_dv[src_node]["cost"]
                            is_updated = True

                for neigh in self.neighbors_dv:
                    for n in self.neighbors_dv[neigh]:
                        if (frozenset(old_path).issubset(frozenset(self.neighbors_dv[neigh][n]["path"]))) == True:
                            self.neighbors_dv[neigh][n]["cost"] = float('inf')
                            self.neighbors_dv[neigh][n]["path"] = []
                            # self.neighbors_dv[neigh][n]["cost"] = (self.neighbors_dv[neigh][n]["cost"] - old_cost) + self.router_dv[node]["cost"]


            elif self.neighbor_cost_dv[src_node] > self.router_dv[src_node]["cost"]:
                if (frozenset([self.id, src_node]) == (frozenset(self.router_dv[src_node]["path"]))):
                    old_cost = self.router_dv[src_node]["cost"]
                    self.router_dv[src_node]["cost"] = self.neighbor_cost_dv[src_node]
                    is_updated = True

                    for node in self.router_dv:
                        if node != src_node:
                            if (frozenset([self.id, src_node]).issubset(frozenset(self.router_dv[node]["path"]))) == True:
                                self.router_dv[node]["cost"] = (self.router_dv[node]["cost"] - old_cost) + self.router_dv[src_node]["cost"]

                    for neigh in self.neighbors_dv:
                        for n in self.neighbors_dv[neigh]:
                            if (frozenset([self.id, src_node]).issubset(frozenset(self.neighbors_dv[neigh][n]["path"]))) == True:
                                self.neighbors_dv[neigh][n]["cost"] = float('inf')
                                self.neighbors_dv[neigh][n]["path"] = []

            for node in src_dv:
                    #accounting for a new node added and not inf
                    if node not in self.router_dv and src_dv[node]["cost"] != float('inf'):
                        new_cost = src_dv[node]["cost"] + self.neighbor_cost_dv[src_node]
                        new_path = [self.id]
                        for i in src_dv[node]["path"]:
                            new_path.append(i)
                        self.router_dv[node] = {"cost": new_cost, "path": new_path}
                        is_updated = True

                    #accounting for updates to nodes already in the dv
                    else:
                        # if node != self.id:
                            #checking for inf if it is coming from the src_dv -- updating src_dv with new dropped link
                            if src_dv[node]["cost"] == float('inf') and self.router_dv[node]["cost"] != float('inf'):
                                if (frozenset(src_dv[node]["path"]).issubset(frozenset(self.router_dv[node]["path"]))) == True:
                                    if node != self.id:
                                        self.router_dv[node]["cost"] = float('inf')
                                        self.router_dv[node]["path"] = []
                                        broken_path = src_dv[node]["path"]
                                        is_updated = True
                                        if broken_path != []:
                                            for neigh in self.neighbors_dv:
                                                for n in self.neighbors_dv[neigh]:
                                                    if (frozenset(broken_path).issubset(frozenset(self.neighbors_dv[neigh][n]["path"]))) == True:
                                                        self.neighbors_dv[neigh][n]["cost"] = float('inf')
                                                        self.neighbors_dv[neigh][n]["path"] = []

                            #if link dropped in updated packets so u need to update neighbors
                            elif self.router_dv[node]["cost"] == float('inf') and src_dv[node]["cost"] != float('inf'):
                                if node != self.id:
                                    broken_path = self.router_dv[node]["path"]
                                    if len(broken_path) != 0:
                                        for neigh in self.neighbors_dv:
                                            for n in self.neighbors_dv[neigh]:
                                                if (frozenset(broken_path).issubset(frozenset(self.neighbors_dv[neigh][n]["path"]))) == True:
                                                    self.neighbors_dv[neigh][n]["cost"] = float('inf')
                                                    self.neighbors_dv[neigh][n]["path"] = []
                                                    is_updated = True

                            #checking latency increase for rest of edges where you have to add an additional cost
                            elif src_dv[node]["cost"] + self.router_dv[src_node]["cost"] > self.router_dv[node]["cost"]:
                                if (frozenset(src_dv[node]["path"]).issubset(frozenset(self.router_dv[node]["path"]))) == True:
                                    if node != src_node and node != self.id:
                                        print("into increasing latency")
                                        old_path = self.router_dv[node]["path"]
                                        old_cost = self.router_dv[node]["cost"]

                                        self.router_dv[node]["cost"] = src_dv[node]["cost"] + self.router_dv[src_node]["cost"]
                                        is_updated = True
                                        # bad_path = self.router_dv[node]["path"]

                                        for n in self.router_dv:
                                            if n != node:
                                                if (frozenset(old_path).issubset(frozenset(self.router_dv[n]["path"]))) == True:
                                                    self.router_dv[n]["cost"] = (self.router_dv[n]["cost"] - old_cost) + self.router_dv[node]["cost"]
                                                    is_updated = True

                                        for neigh in self.neighbors_dv:
                                            for n in self.neighbors_dv[neigh]:
                                                if (frozenset(old_path).issubset(frozenset(self.neighbors_dv[neigh][n]["path"]))) == True:
                                                    self.neighbors_dv[neigh][n]["cost"] = float('inf')
                                                    self.neighbors_dv[neigh][n]["path"] = []


                            elif src_dv[node]["cost"] + self.router_dv[src_node]["cost"] < self.router_dv[node]["cost"]:
                                if (frozenset(src_dv[node]["path"]).issubset(frozenset(self.router_dv[node]["path"]))) == True:
                                    if node != src_node and node != self.id:

                                        print("into decreasing latency")

                                        old_path = self.router_dv[node]["path"]
                                        old_cost = self.router_dv[node]["cost"]
                                        self.router_dv[node]["cost"] = src_dv[node]["cost"] + self.router_dv[src_node]["cost"]
                                        is_updated = True
                                        # bad_path = self.router_dv[node]["path"]

                                        for n in self.router_dv:
                                            if n != node:
                                                if (frozenset(old_path).issubset(frozenset(self.router_dv[n]["path"]))) == True:
                                                    self.router_dv[n]["cost"] = (self.router_dv[n]["cost"] - old_cost) + self.router_dv[node]["cost"]
                                                    is_updated = True

                                        for neigh in self.neighbors_dv:
                                            for n in self.neighbors_dv[neigh]:
                                                if (frozenset(old_path).issubset(frozenset(self.neighbors_dv[neigh][n]["path"]))) == True:

                                                    # self.neighbors_dv[neigh][n]["cost"] = float('inf')
                                                    # self.neighbors_dv[neigh][n]["path"] = []
                                                    self.neighbors_dv[neigh][n]["cost"] = (self.neighbors_dv[neigh][n]["cost"] - old_cost) + self.router_dv[node]["cost"]


        # print("THIS IS SRC NODE", src_node)
        # print("THIS IS SRC DV", src_dv)
        # print("THIS IS SELF ID", self.id)
        # print("THIS IS SELF.ROUTER NEIGHBORS", self.neighbors)
        # print("THIS IS N_COST", self.neighbor_cost_dv)
        print("THIS IS SELF ROUTER AFTER", self.router_dv)
        # print("THIS IS NEIGHBORS DV AFTER", self.neighbors_dv)
        # print("THIS IS UPDATE STATUS", is_updated)
        print()

        self.is_recalc = False
        dv = copy.deepcopy(self.router_dv)
        self.router_dv = self.bellman_ford(dv)[0]
        updated_dv_msg = {"src": self.id, "dv": self.router_dv, "seq_num": self.get_time()}

        if is_updated or self.is_recalc == True:
            json_msg = json.dumps(updated_dv_msg)
            self.send_to_neighbors(json_msg)

    #calcuates shortest path, bellman_ford come save us
    def bellman_ford(self, dv):
        print("BELLMAN FORD DV", dv)

        neighbors_holder = copy.deepcopy(self.neighbors)
        neighbors_dv_holder = copy.deepcopy(self.neighbors_dv)
        neighbors_dv_holder_2 = copy.deepcopy(self.neighbors_dv)

        for node in dv:
            if dv[node]["cost"] == float('inf') and node in self.neighbor_cost_dv:
                dv[node]["cost"] = self.neighbor_cost_dv[node]
                dv[node]["path"] = [self.id, node]
                self.is_recalc = True

            elif node in self.neighbor_cost_dv and self.neighbor_cost_dv[node] < self.router_dv[node]["cost"]:
                self.router_dv[node]["cost"] = self.neighbor_cost_dv[node]
                self.router_dv["path"] = [self.id, node]

        for neighbor in neighbors_holder:
            for node in neighbors_dv_holder[neighbor]:
                # print(self.neighbors_dv[neighbor][node]["cost"])
                # print(dv[node]["cost"])
                # print("THIS IS DV NODE COST", dv[node]["cost"])
                # print(dv)
                if node != self.id:
                    if node in dv and neighbors_dv_holder_2[neighbor][node]["cost"] + dv[neighbor]["cost"] < dv[node]["cost"]:

                        broken_path = dv[node]["path"]

                        dv[node]["cost"] = neighbors_dv_holder_2[neighbor][node]["cost"] + dv[neighbor]["cost"]

                        self.is_recalc = True
                        new_path = []

                        for i in dv[neighbor]["path"]:
                            if i not in new_path:
                                new_path.append(i)

                        for i in neighbors_dv_holder_2[neighbor][node]["path"]:
                            if i not in new_path:
                                new_path.append(i)

                        dv[node]["path"] = new_path

                        broken_path = dv[node]["path"]

                        if len(broken_path) != 0:
                            for neigh in neighbors_dv_holder_2:
                                for n in neighbors_dv_holder_2[neigh]:
                                    if (frozenset(broken_path).issubset(frozenset(neighbors_dv_holder_2[neigh][n]["path"]))) == True:
                                        neighbors_dv_holder_2[neigh][n]["cost"] = float('inf')
                                        neighbors_dv_holder_2[neigh][n]["path"] = []


        print("BELLMAN FORD RECALCULATED_DV", dv)
        print()

        return [dv, self.is_recalc]

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        print("THIS IS GNH ROUTER", self.router_dv)
        if destination in self.router_dv:
            if self.router_dv[destination]["cost"] == float('inf'):
                return -1

            else:
                return self.router_dv[destination]["path"][1]
