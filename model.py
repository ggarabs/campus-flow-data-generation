from mesa import Model
from mesa.space import NetworkGrid
from agent import Student
from courses import weighted_random, load_courses
from entries import weighted_random_entry, load_entries

class CampusModel(Model):
    def __init__(self, graph, agent_qtd):
        super().__init__()

        self.graph = graph
        self.grid = NetworkGrid(graph)

        nodes = list(graph.nodes)

        entries = load_entries('entries.json')
        courses = load_courses('courses.json')

        for _ in range(agent_qtd):
            course = weighted_random(courses, 'morning')
            origin = weighted_random_entry(entries)
            destiny = self.random.choice(nodes)

            student = Student(self, destiny)
            self.grid.place_agent(student, origin)

    def step(self):
        self.agents.do("step")
        self.anyone_moved = any(agent.moved for agent in self.agents)