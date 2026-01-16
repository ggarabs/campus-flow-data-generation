from mesa import Model
from mesa.space import NetworkGrid
from agent import Student

class CampusModel(Model):
    def __init__(self, graph, agent_qtd):
        super().__init__()

        self.graph = graph
        self.grid = NetworkGrid(graph)

        nodes = list(graph.nodes)

        for _ in range(agent_qtd):
            origin = self.random.choice(nodes)
            destiny = self.random.choice(nodes)

            student = Student(self, destiny)
            self.grid.place_agent(student, origin)

    def step(self):
        self.agents.do("step")
