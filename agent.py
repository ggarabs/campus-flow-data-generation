from collections import deque
from mesa import Agent
import math
import networkx as nx

class Student(Agent):

    def __init__(self, model, class_buildings, origin):
        super().__init__(model)
        self.class_buildings = class_buildings

        self.routine = deque([
            ("class", self.random.choice(self.class_buildings), 7200), 
            ("interval", self.random.choice(self.model.restaurants), 900), 
            ("class", self.random.choice(self.class_buildings), 7200),
            ("exit", origin, 1000)])

#        self.routine = deque([('class', 'n31', 7200), ('interval', 'n300', 900), ('class', 'n20', 7200), ('exit', 'n71', 1000)])
        print(self.routine)
        
        self.destiny = None
        self.completed = False

        self.activity_time_left = 0
        self.current_activity = None

        self.path = None
        self.path_index = 0

        self.remaining_time = 0
        self.target = None

        self.previous_node = None
        self.moved = False
        self.in_transit = True
        self.changed_route = False

        self.waiting = False
        self.wait_time = 0
        self.walk_speed = self.random.uniform(0.8, 1.4)
        #self.walk_speed = 1

        self.error_prob = self.random.normalvariate(0.01, 0.005)
        self.error_prob = max(0, min(self.error_prob, 0.2))
        #self.error_prob = 0

        self.max_waiting_time = self.random.randint(5, 10)

        self.start_next_activity()

    # PATHFINDING
    def edge_cost(self, u, v, data):
        if self._is_forbidden_places(v):
            return float("inf")

        if self._is_immediate_backtrack(u, v):
            return float("inf")
        
        distance = data["distance"]
        width = data["width"]

        occupancy = len(data["queue"]) + len(data["in_transit"])

        # TRAVERSAL TIME
        walk_speed = self.walk_speed
        travel_time = distance / walk_speed

        # WAITING TIME
        density = occupancy / width if width > 0 else float("inf")

        # DISCOMFORT
        alpha = 20
        discomfort = alpha / width

        beta = 3
        congestion_penalty = beta * (density ** 2)
        
        return travel_time + discomfort + density + (travel_time * congestion_penalty)

    def compute_path(self):
        self.path = nx.shortest_path(
            self.model.graph,
            source=self.pos,
            target=self.destiny,
            weight=self.edge_cost
        )
        self.path_index = 0

    # STEP LOGIC
    def step(self):
        self.moved = False

        if not self.in_transit and not self.completed:
            self.activity_time_left -= 1

            if self.activity_time_left <= 0:
                self.start_next_activity()

            return

        if self._is_moving():
            self._continue_movement()
            return
        
        if self._arrived():
            self.in_transit = False
            return
        
        if self.path is None:
           self.compute_path()

        self._decide_and_start_next_move()
        return        
    
    # MOVEMENT
    def start_next_activity(self):
        if not self.routine:
            self.completed = True
            return
        
        kind, destiny, duration = self.routine.popleft()

        self.current_activity = kind
        self.destiny = destiny
        self.activity_time_left = duration

        self.in_transit = True
        self.path = None
        self.previous_node = None

    def _continue_movement(self):
        self.remaining_time -= 1
        if self.remaining_time == 0:
            self._arrive_at_target()

    def _arrive_at_target(self):
        prev = self.previous_node
        curr = self.target

        self.model.grid.move_agent(self, curr)
        self.model.release_edge(self, prev, curr)

        self.target = None
        self.moved = True

        if not self.completed and self.pos != self.destiny:
            if self.changed_route:
                #print("agente ", self, " mudou de rota")
                self.compute_path()
                self.changed_route = False


    def _remaining_path_cost(self):
        if self.path is None:
            return float("inf")
        
        if self.path_index >= len(self.path) - 1:
            return 0
        
        total_cost = 0

        for i in range(self.path_index, len(self.path) - 1):
            u = self.path[i]
            v = self.path[i+1]
            data = self.model.graph.edges[u, v]
            total_cost += self.edge_cost(u, v, data)

        return total_cost

    def _decide_and_start_next_move(self):
        planned_next = self._planned_next_node()
        if planned_next is None:
            return

        next_node = planned_next

        if self._should_deviate():
            candidate = self._random_neighbor()
            if self._is_valid_deviation(candidate, planned_next):
                next_node = candidate
                self.changed_route = True

        if self.model.request_edge_entry(self, self.pos, next_node):
            self._start_movement_to(next_node, planned_next)
            self.wait_time = 0
        else:
            self.wait_time += 1
            self.moved = False

            if self.wait_time > self.max_waiting_time:
                self.path = None
                self.changed_route = True
                self.wait_time = 0

    def _start_movement_to(self, next_node, planned_next):
        #print("estudante entrou no nó", next_node)
        edge = self.model.graph.edges[self.pos, next_node]

        self.previous_node = self.pos
        self.target = next_node
        self.remaining_time = math.ceil(edge["distance"] / self.walk_speed)

        if self.model.graph.nodes[self.pos]["type"] == 'bathroom':
            self.remaining_time += 150

        if next_node == planned_next:
            self.path_index += 1

    # DECISION HELPERS
    def _planned_next_node(self):
        if self.path is None:
            return None
        if self.path_index + 1 >= len(self.path):
            return None
        return self.path[self.path_index + 1]
    
    def _should_deviate(self):
        return self.random.random() < self.error_prob
    
    def _random_neighbor(self):
        neighbors = self.model.graph.neighbors(self.pos)
        valid_neighbors = [
            n for n in neighbors
            if self.model.graph.nodes[n]["type"] in ("temporary-point", "bathroom")
        ]

        if not valid_neighbors:
            return None
        
        return self.random.choice(
                    list(valid_neighbors)
                ) or None
    
    def _is_valid_deviation(self, candidate, planned_next):
        return candidate is not None and candidate != planned_next and candidate != self.previous_node

    # CONDITIONS
    def _is_moving(self):
        return self.remaining_time > 0
    
    def _arrived(self):
        return self.pos == self.destiny and not self._is_moving()
    
    def _is_forbidden_places(self, node):
        return (
            self.in_transit
            and node != self.destiny
            and self.model.graph.nodes[node]["type"] not in ("temporary-point", "bathroom")
        )
    
    def _is_immediate_backtrack(self, u, v):
        return (self.model.graph.nodes[u]["type"] not in ('building') 
                and self.previous_node is not None 
                and u == self.pos and v == self.previous_node)