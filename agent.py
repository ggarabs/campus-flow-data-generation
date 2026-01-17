from mesa import Agent

class Student(Agent):
    def __init__(self, model, destiny=None):
        super().__init__(model)
        self.destiny = destiny
        self.remaining_time = 0
        self.previous_node = None
        self.moved = False

    def step(self):
        self.moved = False

        if self.remaining_time > 0:
            self.remaining_time -= 1

            if self.remaining_time == 0 and self.target is not None:
                self.previous_node = self.pos
                self.model.grid.move_agent(self, self.target)
                self.target = None
                self.moved = True
            
            return

        if self.pos == self.destiny:
            return

        neighboors = self.model.grid.get_neighborhood(
            self.pos,
            include_center=False
        )

        if self.previous_node in neighboors:
            neighboors.remove(self.previous_node)

        if not neighboors:
            return

        new_node = self.random.choice(neighboors)
        length = int(self.model.graph.edges[self.pos, new_node]['distance'])

        self.target = new_node
        self.remaining_time = length