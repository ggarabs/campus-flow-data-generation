from mesa import Agent

class Student(Agent):
    def __init__(self, model, destiny):
        super().__init__(model)
        self.destiny = destiny

    def step(self):
        if self.pos == self.destiny:
            return

        neighboors = self.model.grid.get_neighborhood(
            self.pos,
            include_center=False
        )

        if neighboors:
            new_node = self.random.choice(neighboors)
            self.model.grid.move_agent(self, new_node)
