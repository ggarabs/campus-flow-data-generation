from mesa import Model
from mesa.space import NetworkGrid
from agent import Student

class CampusModel(Model):
    def __init__(self, graph, agent_qtd):
        super().__init__()

        self.graph = graph
        self.grid = NetworkGrid(graph)

        nodes = list(graph.nodes)

        entries = [id for id, data in graph.nodes(data=True) if data['type'] == 'entry/exit']

        for _ in range(agent_qtd):
            origin = self.random.choice(entries)
            destiny = self.random.choice(nodes)

            student = Student(self, destiny)
            self.grid.place_agent(student, origin)

    def step(self):
        self.agents.do("step")
        self.anyone_moved = any(agent.moved for agent in self.agents)