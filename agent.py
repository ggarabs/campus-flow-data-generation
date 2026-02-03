from collections import deque
from mesa import Agent
import networkx as nx

class Student(Agent):
    ERROR_PROB = 0.1

    def __init__(self, model, class_buildings, origin):
        super().__init__(model)
        self.class_buildings = class_buildings

        self.routine = deque([
            ("class", self.random.choice(self.class_buildings), 7200), 
            ("interval", self.random.choice(self.model.restaurants), 900), 
            ("class", self.random.choice(self.class_buildings), 7200),
            ("exit", origin, 1000)])
        
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

        self.start_next_activity()

    # PATHFINDING
    def edge_cost(self, u, v, data):
        if self._is_forbidden_places(v):
            return float("inf")

        if self._is_immediate_backtrack(u, v):
            return float("inf")
        
        distance = data["distance"]
        width = data["width"]
        alpha = 0.5
        
        return distance * (1 + alpha / width)

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

    def _continue_movement(self):
        self.remaining_time -= 1
        if self.remaining_time == 0:
            self._arrive_at_target()

    def _arrive_at_target(self):
        self.previous_node = self.pos
        self.model.grid.move_agent(self, self.target)
        self.target = None
        self.moved = True

        if self.changed_route:
            self.path = None
            self.changed_route = False

    def _decide_and_start_next_move(self):
        planned_next = self._planned_next_node()
        next_node = planned_next

        if self._should_deviate():
            candidate = self._random_neighbor()
            if self._is_valid_deviation(candidate, planned_next):
                print('desviei')
                print(next_node, candidate)
                next_node = candidate
                self.changed_route = True

        self._start_movement_to(next_node, planned_next)

    def _start_movement_to(self, next_node, planned_next):
        edge_length = int(self.model.graph.edges[self.pos, next_node]['distance'])

        self.target = next_node
        self.remaining_time = edge_length

        if next_node == planned_next:
            self.path_index += 1

    # DECISION HELPERS
    def _planned_next_node(self):
        return self.path[self.path_index + 1]
    
    def _should_deviate(self):
        return self.random.random() < self.ERROR_PROB
    
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
        return self.pos == self.destiny
    
    def _is_forbidden_places(self, node):
        return (
            self.in_transit
            and node != self.destiny
            and self.model.graph.nodes[node]["type"] not in ("temporary-point", "bathroom")
        )
    
    def _is_immediate_backtrack(self, u, v):
        return (self.previous_node is not None and u == self.pos and v == self.previous_node)