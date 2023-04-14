from mesa import Model
from mesa.time import RandomActivation

import pandas as pd
import csv

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.mailbox.Mailbox import Mailbox
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative

from communication.preferences.Item import Item
from communication.preferences.Preferences import Preferences
from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Value import Value

class ArgumentAgent( CommunicatingAgent ) :
    """ ArgumentAgent which inherit from CommunicatingAgent .
    """
    def __init__(self, unique_id, model, name, preferences, item_list) : #Est ce qu'on donne directement l'item list à l'agent? Sinon comment on fixe le preferred object?
        super().__init__ (unique_id, model, name)
        self.preference = preferences
        self.interlocuteur_id = (self.unique_id + 1) % 2
        self.item_list = item_list
        self.argumentation = True

    def get_preference( self ):
        return self.preference

    def generate_preferences(self, List_items, csv_path):
        # Reading preference CSV
        with open(csv_path, 'r') as file:
            csvreader = csv.reader(file)
            rows = []
            for row in csvreader:
                rows.append(row)
            criterion_list = [eval(i) for i in rows[0]]
            iced_values = [eval(i) for i in rows[1]]
            e_values = [eval(i) for i in rows[2]]

        agent_pref = self.preference
        agent_pref.set_criterion_name_list([CriterionName(i) for i in criterion_list])

        for i in range(len(criterion_list)):
                agent_pref.add_criterion_value(CriterionValue(List_items[0], CriterionName(criterion_list[i]), Value(iced_values[i])))
                agent_pref.add_criterion_value(CriterionValue(List_items[1], CriterionName(criterion_list[i]), Value(e_values[i])))

    def send(self, interlocutor_id, message_performative, item):
        interlocutor = self.model.schedule._agents[interlocutor_id]
        m = Message(self.get_name(), interlocutor.get_name(), MessagePerformative(message_performative), item)
        self.send_message(m)

    def step(self) :
        super().step()

        self.interlocuteur = self.model.schedule._agents[self.interlocuteur_id]

        preferred_item = self.preference.most_preferred(self.item_list)

        reponses_propose = self.get_messages_from_performative(MessagePerformative.PROPOSE)
        reponses_accept = self.get_messages_from_performative(MessagePerformative.ACCEPT)
        reponses_ask_why = self.get_messages_from_performative(MessagePerformative.ASK_WHY)
        reponses_commit = self.get_messages_from_performative(MessagePerformative.COMMIT)
        reponses_argue = self.get_messages_from_performative(MessagePerformative.ARGUE)

        if self.argumentation : 
            if len(reponses_commit) > 0:
                for message in reponses_commit:
                    item = message.get_content() 
                print(self.interlocuteur.get_name(), ": COMMIT(", item,")")
                self.send(self.interlocuteur_id, 103, preferred_item)
                self.argumentation = False
            
            elif len(reponses_accept) > 0:
                # COMMIT
                print(self.interlocuteur.get_name(), ": ACCEPT(", reponses_accept[0].get_content(),")")
                self.send(self.interlocuteur_id, 103, preferred_item)

            elif len(reponses_argue) > 0:
                for message in reponses_argue:
                    item = message.get_content() 
                print(self.interlocuteur.get_name(), ": ARGUE(", item,")")

            elif len(reponses_ask_why) > 0:
                #ARGUE
                for message in reponses_ask_why:
                    item = message.get_content() 
                print(self.interlocuteur.get_name(), ": ASK WHY(", item,")")
                self.send(self.interlocuteur_id, 105, "")

            elif len(reponses_propose) > 0:
                for message in reponses_propose:
                    item = message.get_content() #on prend la dernière valeur?
                print(self.interlocuteur.get_name(), ": PROPOSE(", item,")")

                if self.preference.is_item_among_top_10_percent(item, self.item_list):
                    #ACCEPT
                    self.send(self.interlocuteur_id, 102, item)
                    preferred_item = item #On remplace l'objet préféré après l'avoir accepté
                else:
                    #ASK WHY
                    self.send(self.interlocuteur_id, 104, item)

            else:
                # PROPOSE
                self.send(self.interlocuteur_id, 101, preferred_item)


class ArgumentModel( Model ) :
    """ ArgumentModel which inherit from Model .
    """
    def __init__(self) :
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)

        # To be completed
        #
        # a = ArgumentAgent (id , " agent_name ")
        # a. generate_preferences ( preferences )
        # self . schedule .add(a)
        # ...

        self.running = True

    def step( self ) :
        self.__messages_service.dispatch_messages ()
        self.schedule.step ()


if __name__ == "__main__":
    argument_model = ArgumentModel()

    # Creating items
    E = Item("E", "Electric Engine")
    ICED = Item("ICED", "Diesel Engine")

    item_list = [ICED, E]

    # Creating agents
    A1 = ArgumentAgent(0, argument_model, "A1", Preferences(), item_list)
    A2 = ArgumentAgent(1, argument_model, "A2",  Preferences(), item_list)

    argument_model.schedule.add(A1)
    argument_model.schedule.add(A2)

    # Launch the Communication part 
    mailbox_agent1 = Mailbox()
    mailbox_agent2 = Mailbox()


    #Generating preferences
    A1.generate_preferences(item_list, "Pref_agent1.csv")
    A2.generate_preferences(item_list, "Pref_agent2.csv")

    step = 0
    while step < 10: ## CHANGER CONDITION DE TERMINAISON
        argument_model.step()
        step += 1
