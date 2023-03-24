#!/usr/bin/env python3

from ArguingAgent import ArguingAgent
from ArguingModel import ArguingModel
from communication.mailbox.Mailbox import Mailbox

if __name__ == "__main__":
    # Init the model and the agents
    arguing_model = ArguingModel()

    A1 = ArguingAgent(0, arguing_model, "Agent1")
    A2 = ArguingAgent(1, arguing_model, "Agent2")


    arguing_model.schedule.add(A1)
    arguing_model.schedule.add(A2)

    # Launch the Communication part 

    mailbox_agent1 = Mailbox()
    mailbox_agent2 = Mailbox()
    
    step = 0
    while step < 10: ## CHANGER CONDITION DE TERMINAISON
        arguing_model.step()
        step += 1