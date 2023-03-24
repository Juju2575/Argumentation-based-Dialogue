import random

from mesa import Model
from mesa.time import RandomActivation

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.mailbox.Mailbox import Mailbox
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative
from communication.message.MessageService import MessageService


class ArguingAgent(CommunicatingAgent):
    def __init__(self, unique_id, model, name):
        super().__init__(unique_id, model, name)

        #Define preferences
    
    def step(self):
        super().step()
        