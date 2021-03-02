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

        self.delete = False

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
                    is_updated = True
                    # self.router_dv[node]["path"] = []

                    #updates the node if it is a neighbor because there is a sure pathway
                    if neighbor in self.neighbors:
                        self.router_dv[node]["path"] = [self.id, node]
                        self.router_dv[node]["cost"] = self.neighbor_cost_dv[node]

            print(self.router_dv)

        #updating the router's dv, neighbors, & neighbors_dv/cost if a new node is present
        elif neighbor not in self.neighbors:
            self.neighbor_cost_dv[neighbor] = latency
            self.neighbors_dv[neighbor] = {}
            self.neighbors.append(neighbor)
            self.router_dv[neighbor] = {"cost": latency, "path": [self.id, neighbor]}
            is_updated = True

        #updating the router's dv, neighbors, & neighbors_dv/cost if a cost is changed
        elif self.neighbor_cost_dv[neighbor] != latency:

            old_cost = self.neighbor_cost_dv[neighbor]
            self.neighbor_cost_dv[neighbor] = latency

            for node in self.router_dv:
                if neighbor in self.router_dv[node]["path"]:
                    self.router_dv[node]["cost"] = (self.router_dv[node]["cost"] - old_cost) + latency
                    is_updated = True

            # dv = copy.deepcopy(self.router_dv)
            # print("before BELLMAN ford", self.router_dv)
            # self.router_dv = self.bellman_ford(dv)[0]
            # print("after BELLMAN ford", self.router_dv)


        if is_updated == True:

            # dv = copy.deepcopy(self.router_dv)
            # print("before BELLMAN ford", self.router_dv)
            # self.router_dv = self.bellman_ford(dv)[0]
            # print("after BELLMAN ford", self.router_dv)

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

        #accounts for timing errors and only gets ones sent latest

        print("INCOMING PACKET TIME", self.seq_nums)

        print("OWN PACKET UPDATED", src_seq_num)


        if src_node not in self.seq_nums or src_seq_num > self.seq_nums[src_node]:

            # print("THIS IS SRC NODE", src_node)
            print("THIS IS SRC DV", src_dv)
            # print("THIS IS SELF ID", self.id)
            # print("THIS IS SELF.ROUTER NEIGHBORS", self.neighbors)
            # print("THIS IS N_COST", self.neighbor_cost_dv)

            print("THIS IS SELF ROUTER BEFORE", self.router_dv)
            print("THIS IS NEIGHBORS DV BEFORE", self.neighbors_dv)
            print()

            self.seq_nums[src_node] = src_seq_num
            self.neighbors_dv[src_node] = src_dv


            #deleting the node for poisoned reverse/count to inf
            # for node in list(self.router_dv):
            #     if src_node in self.router_dv[node]["path"]:
            #         #node was deleted earlier and or node is inf
            #         if node not in src_dv or src_dv[node]["cost"] == float('inf'):
            #             del self.router_dv[node]
            #             is_updated = True
            #             self.delete = True


            # if self.del == True:
            #     for node in src_dv:
            #         if self.id not in src_dv[node]["path"]:
            #             "FIGURE THIS OUTTTTT AGH"
            #
            #             if node not in self.router_dv:
            #
            #
            #
            # else:

            for node in src_dv:

                #accounting for a new node added and not inf
                if node not in self.router_dv and src_dv[node]["cost"] != float('inf'):
                    new_cost = src_dv[node]["cost"] + self.neighbor_cost_dv[src_node]

                    new_path = [self.id]

                    for i in src_dv[node]["path"]:
                        new_path.append(i)

                    self.router_dv[node] = {"cost": new_cost, "path": new_path}
                    is_updated = True
                #
                # else:
                #     if src_node in self.router_dv[node]["path"]:
                #
                #         if self.router_dv[node]["cost"] == float('inf') or self.router_dv[node]["cost"] != src_dv[node]["cost"]:
                #
                #
                #             self.router_dv[]

                # if self.router_dv[node]["cost"] == float('inf') and self.router_dv[node]["path"] != []:
                #     # print("IN FIRST IF STATEMENT")
                #     # print("INCOMING PATH", src_dv[node]["path"])
                #     # print("ROUTER PATH", self.router_dv[node]["path"])
                #     b_path = self.router_dv[node]["path"]
                #
                #
                #     if (set(src_dv[node]["path"]).issubset(set(b_path))) or (set(b_path).issubset(set(src_dv[node]["path"]))):
                #             print("IN SECOND IF STATEMENT")
                #             for neigh in self.neighbors_dv:
                #                 for n in self.neighbors_dv[neigh]:
                #
                #                     if (set(b_path).issubset(set(self.neighbors_dv[neigh][n]["path"]))) == True:
                #                         print("THIS IS NEIGH", neigh)
                #                         print("THIS IS n", n)
                #                         print("THIS IS BROKEN PATH", broken_path)
                #                         print("THIS IS PATH",self.neighbors_dv[neigh][n]["path"])
                #
                #                         self.neighbors_dv[neigh][n]["cost"] = float('inf')
                #                         self.neighbors_dv[neigh][n]["path"] = []

                            # # for neigh in neighbors_dv:
                            #     self.neighbors_dv[neigh][n]["path"] = []
                            #     self.neighbors_dv[neigh][n]["cost"] = float('inf')


                #accounting for updates to nodes already in the dv
                else:

                    # if node != self.id:


                        #checking for inf if it is coming from the src_dv -- updating src_dv with new dropped link
                        if src_dv[node]["cost"] == float('inf') and self.router_dv[node]["cost"] != float('inf'):



                            if (frozenset(src_dv[node]["path"]).issubset(frozenset(self.router_dv[node]["path"]))) == True:


                            # print("CHANGED TO INF")
                            #
                            # print("THIS IS INF SRC", src_dv)
                            # print("THIS IS INF SELF.ROUTER", self.router_dv)

                                self.router_dv[node]["cost"] = float('inf')
                                self.router_dv[node]["path"] = []

                                broken_path = src_dv[node]["path"]

                                is_updated = True

                                # print("INF NODE", node)
                                #
                                # print("IN INF CASE", src_dv[node])
                                # print("IN INF CASE NEIGHBORS", self.neighbors_dv)

                                if broken_path != []:

                                    for neigh in self.neighbors_dv:
                                        for n in self.neighbors_dv[neigh]:
                                            if (frozenset(broken_path).issubset(frozenset(self.neighbors_dv[neigh][n]["path"]))) == True:

                                                # if broken_path == []:
                                                #     continue
                                                # print("THIS IS NEIGH", neigh)
                                                # print("THIS IS n", n)
                                                # print("THIS IS BROKEN PATH", broken_path)
                                                # print("THIS IS PATH",self.neighbors_dv[neigh][n]["path"])

                                                self.neighbors_dv[neigh][n]["cost"] = float('inf')
                                                self.neighbors_dv[neigh][n]["path"] = []

                                # if len(broken_path) == 0:
                                #     continue


                        #if link dropped in updated packets so u need to update neighbors
                        elif self.router_dv[node]["cost"] == float('inf') and src_dv[node]["cost"] != float('inf'):

                            broken_path = self.router_dv[node]["path"]

                            if len(broken_path) != 0:

                                for neigh in self.neighbors_dv:
                                    for n in self.neighbors_dv[neigh]:
                                        if (frozenset(broken_path).issubset(frozenset(self.neighbors_dv[neigh][n]["path"]))) == True:

                                            # if broken_path == []:
                                            #     continue
                                            # print("THIS IS NEIGH", neigh)
                                            # print("THIS IS n", n)
                                            print("THIS IS BROKEN PATH", broken_path)
                                            print("THIS IS PATH",self.neighbors_dv[neigh][n]["path"])

                                            self.neighbors_dv[neigh][n]["cost"] = float('inf')
                                            self.neighbors_dv[neigh][n]["path"] = []

                                            is_updated = True

                        #checking latency increase for a single edge - ie no adding additional cost
                        elif src_node in self.router_dv[node]["path"]:
                            print("srcdev", src_dv)
                            print(self.id)
                            print(node)
                            print("router", self.router_dv)
                            print("neighbor_cost", self.neighbor_cost_dv)


                            if len(self.router_dv[src_node]["path"]) == 2 and len(src_dv[node]["path"]) == 2:


                                if self.router_dv[src_node]["path"][0] == src_dv[node]["path"][1] and self.router_dv[src_node]["path"][1] == src_dv[node]["path"][0]:
                                        print("srcdev", src_dv)
                                        print(self.id)
                                        if src_dv[node]["cost"] > self.router_dv[src_node]["cost"]:

                                            self.router_dv[src_node]["cost"] = src_dv[node]["cost"]

                                            bad_path = [node, src_node]

                                            is_updated = True

                                            for neigh in self.neighbors_dv:
                                                for n in self.neighbors_dv[neigh]:
                                                    if (frozenset(bad_path).issubset(frozenset(self.neighbors_dv[neigh][n]["path"]))) == True:
                                                        self.neighbors_dv[neigh][n]["cost"] = float('inf')
                                                        self.neighbors_dv[neigh][n]["path"] = []



                        #checking latency increase for rest of edges where you have to add an additional cost
                        elif src_dv[node]["cost"] + self.router_dv[src_node]["cost"] > self.router_dv[node]["cost"] and (frozenset(src_dv[node]["path"]).issubset(frozenset(self.router_dv[node]["path"]))) == True:

                                # print("unique", self.id)
                                # print("hello",self.router_dv[node]["path"])
                                # print(src_dv[node]["path"])
                                # print(node)
                            if node != self.id:
                                print("changed latency")

                                self.router_dv[node]["cost"] = src_dv[node]["cost"] + self.router_dv[src_node]["cost"]


                                is_update = True

                                bad_path = self.router_dv[node]["path"]

                                for neigh in self.neighbors_dv:
                                    for n in self.neighbors_dv[neigh]:
                                        if (frozenset(bad_path).issubset(frozenset(self.neighbors_dv[neigh][n]["path"]))) == True:
                                            self.neighbors_dv[neigh][n]["cost"] = float('inf')
                                            self.neighbors_dv[neigh][n]["path"] = []




                            else:

                                #updating latency for a single edge

                                if len(self.router_dv[src_node]["path"]) == 2 and len(src_dv[node]["path"]) == 2:

                                    if self.router_dv[src_node]["path"][0] == src_dv[node]["path"][1] and self.router_dv[src_node]["path"][1] == src_dv[node]["path"][0]:

                                        if src_dv[node]["cost"] != self.router_dv[src_node]["cost"]:

                                            self.router_dv[src_node]["cost"] = src_dv[node]["cost"]

                                            is_updated = True

                                    #updating latency if latency chagned for not a direct neighbors edge
                                    elif (frozenset(src_dv[node]["path"]).issubset(frozenset(self.router_dv[node]["path"]))) == True:

                                        self.router_dv[node]["cost"] = src_dv[node]["cost"] + self.router_dv[src_node]["cost"]

                                        # self.router_dv[node]["cost"] = self.neighbor_cost_dv[src_node] + src_dv[node]["cost"]
                                        is_updated = True


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

            # print("THIS IS SRC NODE", src_node)
            # print("THIS IS SRC DV", src_dv)
            #
            #
            # print("THIS IS SELF ID", self.id)
            #
            # print("THIS IS SELF.ROUTER NEIGHBORS", self.neighbors)
            # print("THIS IS N_COST", self.neighbor_cost_dv)
            print("THIS IS SELF ROUTER AFTER", self.router_dv)
            print("THIS IS NEIGHBORS DV AFTER", self.neighbors_dv)
            print("THIS IS UPDATE STATUS", is_updated)
            print()
            #

            # print()

        is_recalc = False

        # if is_updated == False:

        dv = copy.deepcopy(self.router_dv)

        self.router_dv = self.bellman_ford(dv)[0]

        is_recalc = self.bellman_ford(dv)[1]

        updated_dv_msg = {"src": self.id, "dv": self.router_dv, "seq_num": self.get_time(), "neighbors": self.neighbors_dv}

        # print("THIS IS BELLMAN FORD RESULT", self.router_dv)

        if is_updated or is_recalc == True:

            json_msg = json.dumps(updated_dv_msg)

            self.send_to_neighbors(json_msg)



    #calcuates shortest path, bellman_ford come save us
    def bellman_ford(self, dv):

        print("BELLMAN FORD DV", dv)
        # print("BELLMAN FORD NEIGHBORS", self.neighbors)
        print("BELLMAN FORD NEIGHBORS_DV", self.neighbors_dv)
        # print("BELLMAN FORD NEIGHBORS_COST", self.neighbor_cost_dv)
        # print()
        # print(self.neighbors_dv)
        is_recalc = False
        visited = []

        neighbors_holder = copy.deepcopy(self.neighbors)
        neighbors_dv_holder = copy.deepcopy(self.neighbors_dv)

        neighbors_dv_holder_2 = copy.deepcopy(self.neighbors_dv)

        for node in dv:
            if dv[node]["cost"] == float('inf') and node in self.neighbor_cost_dv:
                dv[node]["cost"] = self.neighbor_cost_dv[node]
                dv[node]["path"] = [self.id, node]


        for neighbor in neighbors_holder:
            for node in neighbors_dv_holder[neighbor]:
                # print(self.neighbors_dv[neighbor][node]["cost"])
                # print(dv[node]["cost"])
                # print("THIS IS DV NODE COST", dv[node]["cost"])
                # print(dv)


                #NEED TO ACCOUNT FOR ONLY 1 EDGE

                # if node != self.id:


                    # if dv[neighbor]["cost"] == self.neighbor_cost_dv[neighbor]:


                    #
                    #     dv[neighbor]["path"] = [self.id, neighbor]

                    if neighbors_dv_holder_2[neighbor][node]["cost"] + dv[neighbor]["cost"] < dv[node]["cost"]:
                        if (frozenset(neighbors_dv_holder_2[neighbor][node]["path"]).issubset(frozenset(dv[node]["path"]))) == False:


                            # print("BEFORE PATH IS UPDATED", dv[node]["path"])

                            dv[node]["cost"] = neighbors_dv_holder_2[neighbor][node]["cost"] + dv[neighbor]["cost"]

                            new_path = []


                            print("THIS IS PATH PART 1:", dv[neighbor]["path"])

                            print("THIS IS PATH PART 2:", neighbors_dv_holder_2[neighbor][node]["path"])

                            for i in dv[neighbor]["path"]:
                                if i not in new_path:
                                    new_path.append(i)

                            for i in neighbors_dv_holder_2[neighbor][node]["path"]:
                                if i not in new_path:
                                    new_path.append(i)

                            dv[node]["path"] = new_path

                            print("HOPEFULLY THIS IS THE RIGHT PATH OTHERWISE I WILL DIE", new_path)


                            broken_path = dv[node]["path"]

                            if len(broken_path) != 0:
                                for neigh in neighbors_dv_holder_2:
                                    for n in neighbors_dv_holder_2[neigh]:
                                        if (frozenset(broken_path).issubset(frozenset(neighbors_dv_holder_2[neigh][n]["path"]))) == True:

                                            # if broken_path == []:
                                            #     continue
                                            # print("THIS IS NEIGH", neigh)
                                            # print("THIS IS n", n)
                                            print("THIS IS BROKEN PATH", broken_path)
                                            print("THIS IS PATH",neighbors_dv_holder_2[neigh][n]["path"])

                                            neighbors_dv_holder_2[neigh][n]["cost"] = float('inf')

                                            # self.neighbors_dv[neigh][n]["path"] =



                            is_recalc = True

                            # print("AFTER PATH IS UPDATED", dv[node]["path"])





        print("BELLMAN FORD RECALCULATED_DV", dv)
        # print()


        return [dv, is_recalc]



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
