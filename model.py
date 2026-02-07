from mesa import Model
from mesa.space import NetworkGrid
from agent import Student
from courses import weighted_random, load_courses
from entries import weighted_random_entry, load_entries

class CampusModel(Model):
    def __init__(self, graph, agent_qtd, restaurants, restrooms):
        super().__init__()

        self.graph = graph
        self.grid = NetworkGrid(graph)
        self.restaurants = restaurants
        self.restrooms = restrooms

        entries = load_entries('entries.json')
        courses = load_courses('courses.json')

        for _ in range(agent_qtd):
            course = weighted_random(courses, 'morning')
            origin = weighted_random_entry(entries)
            origin = 'n71'
            class_buildings = course["class_buildings"]

            student = Student(self, class_buildings, origin)
            print(course, origin)
            self.grid.place_agent(student, origin)

    def step(self):
        for _, _, data in self.graph.edges(data=True):
            data["entered_this_tick"] = 0

        self.agents.do("step")
        self.anyone_moved = any(agent.moved for agent in self.agents)

    def request_edge_entry(self, agent, u, v):
        edge = self.graph.edges[u, v]

        if edge["entered_this_tick"] < edge["width"]:
            edge["entered_this_tick"] += 1
            return True
        
        return False
        
    def release_edge(self, agent, u, v):
        edge = self.graph.edges[u, v]
        edge["in_transit"].remove(agent)

        if edge["queue"]:
            next_agent = edge["queue"].popleft()
            edge["in_transit"].add(next_agent)
            next_agent.start_edge(u, v)