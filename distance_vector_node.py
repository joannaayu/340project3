from simulator.node import Node
import json
import copy


class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        #keeps own router information with keys to cost and path for all nodes
        self.router_dv = {self.id: {"cost": 0, "path": [self.id]}}

        #cost from current router to adjacent neighbots
        self.neighbor_cost_dv = {}

        #neighbors path & cost to following destination
        self.neighbors_dv = {}

        self.seq_nums = {}

        self.del = False

    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        print("THIS IS SELF ID", self.id)
        print("THIS IS SELF ROUTER", self.router_dv)
        print("THIS IS NEIGHBOR", neighbor)
        print("THIS IS LATENCY", latency)

        is_updated = False

        if latency == -1:
            del self.neighbors_dv[neighbor]
            del self.neighbor_cost_dv[neighbor]
            self.neighbors.remove(neighbor)
            is_updated = True
            self.del = True

            for node in self.router_dv:
                if neighbor in self.router_dv[node]["path"]:
                    self.router_dv[node]["cost"] = float('inf')
                    is_updated = True
                    # self.router_dv[node]["path"] = []
                    if node in self.neighbors:
                        self.router_dv[node]["path"] = [self.id, node]
                        self.router_dv[node]["cost"] = self.neighbor_cost_dv[node]

        elif neighbor not in self.neighbors:
            self.neighbor_cost_dv[neighbor] = latency
            self.neighbors_dv[neighbor] = {}
            self.neighbors.append(neighbor)
            self.router_dv[neighbor] = {"cost": latency, "path": [self.id, neighbor]}
            is_updated = True

        else:
            old_cost = self.neighbor_cost_dv[neighbor]
            self.neighbor_cost_dv[neighbor] = latency
            is_updated = True

            for node in self.router_dv:
                if neighbor in self.router_dv[node]["path"]:
                    self.router_dv[node]["cost"] = (self.router_dv[node]["cost"] - old_cost) + latency


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

        if src_node not in self.seq_nums or src_seq_num > self.seq_nums[src_node]:

            print("THIS IS SRC NODE", src_node)
            print("THIS IS SRC DV", src_dv)
            print("THIS IS SELF ID", self.id)
            print("THIS IS SELF.ROUTER NEIGHBORS", self.neighbors)
            print("THIS IS N_COST", self.neighbor_cost_dv)
            print("THIS IS NEIGHBORS DV", self.neighbors_dv)
            print("THIS IS SELF ROUTER", self.router_dv)
            print()

            self.seq_nums[src_node] = src_seq_num
            self.neighbors_dv[src_node] = src_dv

            #accounting for inf nodes , deleting if a node is not in incoming lsp or if a src has a node = to inf
            for node in list(self.router_dv):
                if src_node in self.router_dv[node]["path"]:
                    if node not in src_dv or src_dv[node]["cost"] == float('inf'):
                        del self.router_dv[node]
                        is_updated = True
                        self.del = True


            if self.del == True:
                for node in src_dv:
                    if node not in self.router_dv:


            else:
                for node in src_dv:
                    #accounting for a new node added
                    if node not in self.router_dv:
                        new_cost = src_dv[node]["cost"] + self.neighbor_cost_dv[src_node]
                        if node == src_node:
                            new_path = [self.id, src_node]
                        else:
                            new_path = [self.id, src_node, node]
                        self.router_dv[node] = {"cost": new_cost, "path": new_path}
                        is_updated = True

                    #incoming message has old info -- need to update neighbors with self.router info

                    if self.router_dv[node]["cost"] == float('inf') and self.router_dv[node]["path"] != []:
                        print("IN FIRST IF STATEMENT")
                        print("INCOMING PATH", src_dv[node]["path"])
                        print("ROUTER PATH", self.router_dv[node]["path"])
                        b_path = self.router_dv[node]["path"]


                        if (set(src_dv[node]["path"]).issubset(set(b_path))) or (set(b_path).issubset(set(src_dv[node]["path"]))):
                                print("IN SECOND IF STATEMENT")
                                for neigh in self.neighbors_dv:
                                    for n in self.neighbors_dv[neigh]:

                                        if (set(b_path).issubset(set(self.neighbors_dv[neigh][n]["path"]))) == True:
                                            print("THIS IS NEIGH", neigh)
                                            print("THIS IS n", n)
                                            print("THIS IS BROKEN PATH", broken_path)
                                            print("THIS IS PATH",self.neighbors_dv[neigh][n]["path"])

                                            self.neighbors_dv[neigh][n]["cost"] = float('inf')
                                            self.neighbors_dv[neigh][n]["path"] = []

                                # # for neigh in neighbors_dv:
                                #     self.neighbors_dv[neigh][n]["path"] = []
                                #     self.neighbors_dv[neigh][n]["cost"] = float('inf')


                    #accounting for updates to nodes already in the dv
                    else:
                        if src_node in self.router_dv[node]["path"]:

                            if src_dv[node]["cost"] == float('inf'):
                                print("CHANGED TO INF")

                                print("THIS IS INF SRC", src_dv)
                                print("THIS IS INF SELF.ROUTER", self.router_dv)

                                self.router_dv[node]["cost"] = float('inf')
                                self.router_dv[node]["path"] = []

                                broken_path = src_dv[node]["path"]

                                print("INF NODE", node)

                                print("IN INF CASE", src_dv[node])
                                print("IN INF CASE NEIGHBORS", self.neighbors_dv)



                                for neigh in self.neighbors_dv:
                                    for n in self.neighbors_dv[neigh]:
                                        if (set(broken_path).issubset(set(self.neighbors_dv[neigh][n]["path"]))) == True:

                                            # if broken_path == []:
                                            #     continue
                                            print("THIS IS NEIGH", neigh)
                                            print("THIS IS n", n)
                                            print("THIS IS BROKEN PATH", broken_path)
                                            print("THIS IS PATH",self.neighbors_dv[neigh][n]["path"])

                                            self.neighbors_dv[neigh][n]["cost"] = float('inf')
                                            self.neighbors_dv[neigh][n]["path"] = []

                                # if len(broken_path) == 0:
                                #     continue



                                # is_updated = True

                            elif self.neighbor_cost_dv[src_node] + src_dv[node]["cost"] != self.router_dv[node]["cost"]:
                                self.router_dv[node]["cost"] = self.neighbor_cost_dv[src_node] + src_dv[node]["cost"]
                                # is_updated = True


            # if len(broken_path) == 0:
            #
            #     for neigh in self.neighbors_dv:
            #         for n in self.neighbors_dv[neigh]:
            #
            #             if (set(broken_path).issubset(set(self.neighbors_dv[neigh][n]["path"]))) == True:
            #                 print("THIS IS NEIGH", neigh)
            #                 print("THIS IS n", n)
            #                 print("THIS IS BROKEN PATH", broken_path)
            #                 print("THIS IS PATH",self.neighbors_dv[neigh][n]["path"])
            #
            #                 self.neighbors_dv[neigh][n]["cost"] = float('inf')
            #                 self.neighbors_dv[neigh][n]["path"] = []

            print("THIS IS SRC NODE", src_node)
            print("THIS IS SRC DV", src_dv)


            print("THIS IS SELF ID", self.id)

            print("THIS IS SELF.ROUTER NEIGHBORS", self.neighbors)
            print("THIS IS N_COST", self.neighbor_cost_dv)
            print("THIS IS NEIGHBORS DV", self.neighbors_dv)

            print("THIS IS SELF ROUTER", self.router_dv)
            print()

        if is_updated == False:

            dv = copy.deepcopy(self.router_dv)

            self.router_dv = self.bellman_ford(dv)[0]

            is_recalc = False

            is_recalc = self.bellman_ford(dv)[1]

        updated_dv_msg = {"src": self.id, "dv": self.router_dv, "seq_num": self.get_time()}

        # print("THIS IS BELLMAN FORD RESULT", self.router_dv)

        if is_updated or is_recalc == True:
            json_msg = json.dumps(updated_dv_msg)

            self.send_to_neighbors(json_msg)



    #calcuates shortest path, bellman_ford come save us
    def bellman_ford(self, dv):

        print("BELLMAN FORD DV", dv)
        print("BELLMAN FORD NEIGHBORS", self.neighbors)
        print("BELLMAN FORD NEIGHBORS_DV", self.neighbors_dv)
        print("BELLMAN FORD NEIGHBORS_COST", self.neighbor_cost_dv)
        print()

        is_recalc = False

        for neighbor in self.neighbors:
            for node in self.neighbors_dv[neighbor]:

                if self.neighbors_dv[neighbor][node]["cost"] + self.neighbor_cost_dv[neighbor] < dv[node]["cost"]:

                    print("BEFORE PATH IS UPDATED", dv[node]["path"])
                    dv[node]["cost"] = self.neighbors_dv[neighbor][node]["cost"] + self.neighbor_cost_dv[neighbor]
                    dv[node]["path"] = [self.id]
                    dv[node]["path"] = dv[node]["path"] + self.neighbors_dv[neighbor][node]["path"]
                    print("AFTER PATH IS UPDATED", dv[node]["path"])
                    is_updated = True

        print("UPDATE", is_recalc)

        print("BELLMAN FORD RECALCULATED_DV", dv)
        print()


        return [dv, is_recalc]


        # if seq_num > self.gettime():



    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # print("THIS IS OUR GET NEXT HOP", self.router_dv)
        # print("THIS IS OUR DEST", destination
        # )

        print("THIS IS GNH ROUTER", self.router_dv)
        if destination in self.router_dv:
            if self.router_dv[destination]["cost"] == float('inf'):
                return -1

            else:
                return self.router_dv[destination]["path"][1]
