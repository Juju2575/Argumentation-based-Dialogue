from mesa import Model
from mesa.time import RandomActivation, BaseScheduler

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

from arguments.Argument import Argument

#List for argument storage
argument_list = []

class ArgumentAgent( CommunicatingAgent ) :
    """ ArgumentAgent which inherit from CommunicatingAgent .
    """
    def __init__(self, unique_id, model, name, preferences, item_list) : #Est ce qu'on donne directement l'item list à l'agent? Sinon comment on fixe le preferred object?
        super().__init__ (unique_id, model, name)
        self.preference = preferences
        self.interlocuteur_id = (self.unique_id + 1) % 2
        self.item_list = item_list
        self.argumentation = True
        self.has_proposed_preferred = False
        self.preferred_item = None
        self.other_item = None

    def get_preference( self ):
        return self.preference

    def generate_preferences(self, List_items, csv_path):
        """ Generate agent's preferences from csv 
        """ 
        with open(csv_path, 'r') as file:
            csvreader = csv.reader(file)
            rows = []
            #Get all rows from csv
            for row in csvreader:
                rows.append(row)

            criterion_list = [eval(i) for i in rows[0]]
            iced_values = [eval(i) for i in rows[1]]
            e_values = [eval(i) for i in rows[2]]

        # Set criterion names
        agent_pref = self.preference
        agent_pref.set_criterion_name_list([CriterionName(i) for i in criterion_list])

        #Generate preferences
        for i in range(len(criterion_list)):
                agent_pref.add_criterion_value(CriterionValue(List_items[0], CriterionName(criterion_list[i]), Value(iced_values[i])))
                agent_pref.add_criterion_value(CriterionValue(List_items[1], CriterionName(criterion_list[i]), Value(e_values[i])))

    def send(self, interlocutor_id, message_performative, item):
        """ Sends message to interlocutor with message_performative as Message Performative
        """ 
        interlocutor = self.model.schedule._agents[interlocutor_id]
        m = Message(self.get_name(), interlocutor.get_name(), MessagePerformative(message_performative), item)
        self.send_message(m)

    def support_proposal( self , item ):
        """
        Used when the agent receives " ASK_WHY " after having proposed an item
        : param item : str - name of the item which was proposed
        : return : string - the strongest supportive argument
        """

        support_arg = Argument(boolean_decision=True, item=item)

        # Create list of supporting arguments
        support_arg_list = support_arg.List_supporting_proposal(item, self.preference)

        best_arg = None

        # Find best argument not already used 
        for arg in support_arg_list:
            if (item, str(arg.criterion_name), str(arg.value)) not in argument_list:
                best_arg = arg
                break 

        # Return argument as string or None if no argument found
        if best_arg is not None:
            return (str(item.get_name()) + " <= " + str(best_arg.criterion_name)  + " = " + str(best_arg.value))
        else:
            return None


    def attacking_proposal(self , item, crit_name, crit_value ):
        """
        Used to format the CON argument 
        """

        return ("not " + str(item.get_name()) + " <= " + str(crit_name)  + " = " + str(crit_value))


    def argument_parsing(self ,argument ) :
        """
        Takes argument as string and parses it to return item, criterion name and criterion value
        """

        # Separate conclusion from premises
        argument_list = argument.split(" <= ")

        # Separate criterion name from criterion value
        premise_list = argument_list[1].split(" = ")

        # Remove "not" if it is a CON argument
        argument_list[0] = argument_list[0].replace("not ", "")
        argument_list[0] = argument_list[0].split(" ")[0]

        conclusion_item = argument_list[0]
        premise_criterion_name = premise_list[0]
        premise_value = premise_list[1]

        arg_item = Item("Placeholder", "")

        # Loop to move up from item name to item instance
        for item in self.item_list:
            if conclusion_item== item.get_name():
                arg_item = item

        return arg_item, premise_criterion_name, premise_value


    def can_be_attacked(self, argument):
        """
        Takes argument and returns best attacking argument if there is one
        """
        # arg_item, crit_name, value = self.argument_parsing(argument)    #Previous version
        arg_item, crit_name, value = argument

        attacking_arg = Argument(boolean_decision=False, item=arg_item)

        # Create list of attacking arguments
        attacking_arg_list = attacking_arg.List_attacking_proposal(arg_item, self.preference)

        # Find best attacking argument not already used (or None if none found)
        for arg in attacking_arg_list:
            if self.preference.is_preferred_criterion(arg.criterion_name, crit_name):
                return arg_item, str(arg.criterion_name), str(arg.value)
            else:
                None 


    def find_attacking_arg(self, item):
        """
        Find best attacking argument against item
        """
        #Si cette fonction retourne None alors on ne peut plus trouver d'arguments contre un item
        previous_arg_list = argument_list.copy()

        attacking_arg = None

        # Loops through already used arguments PRO item to find if any of them can be attacked
        for previous_arg in previous_arg_list:
            if item == previous_arg[0]:
                if self.can_be_attacked(previous_arg) is not None:
                    if tuple(self.can_be_attacked(previous_arg)) not in argument_list:
                        attacking_arg = tuple(self.can_be_attacked(previous_arg))

        return attacking_arg      


    def step(self) :
        super().step()

        self.interlocuteur = self.model.schedule._agents[self.interlocuteur_id]

        self.preferred_item = self.preference.most_preferred(self.item_list)
        
        # Check Mailbox 
        reponses_propose = self.get_new_messages_from_performative(MessagePerformative.PROPOSE)
        reponses_accept = self.get_new_messages_from_performative(MessagePerformative.ACCEPT)
        reponses_ask_why = self.get_new_messages_from_performative(MessagePerformative.ASK_WHY)
        reponses_commit = self.get_new_messages_from_performative(MessagePerformative.COMMIT)
        reponses_argue = self.get_new_messages_from_performative(MessagePerformative.ARGUE)


        if self.argumentation : 
            if len(reponses_commit) > 0:
                # COMMIT
                for message in reponses_commit:
                    item = message.get_content() 
                print(self.interlocuteur.get_name(), ": COMMIT(", item,")")
                self.send(self.interlocuteur_id, 103, item)
                self.argumentation = False
            

            elif len(reponses_accept) > 0:
                # COMMIT
                print(self.interlocuteur.get_name(), ": ACCEPT(", reponses_accept[0].get_content(),")")
                self.send(self.interlocuteur_id, 103, self.preferred_item)

            
            elif len(reponses_argue) > 0:
                # ARGUMENTATION
                for message in reponses_argue:
                    argument = message.get_content() 
                argument_list.append(self.argument_parsing(argument))
                print(self.interlocuteur.get_name(), ": ARGUE(", argument,")")

                if not self.has_proposed_preferred:
                    # PROPOSE 
                    self.has_proposed_preferred=True
                    self.send(self.interlocuteur_id, 101, self.preferred_item)
                
                else:
                    if "not" in argument:
                        item, _, _ = self.argument_parsing(argument)
                        support_arg = self.support_proposal(item)
                        if support_arg is not None:
                            #ARGUE PRO
                            self.send(self.interlocuteur_id, 105, support_arg)
                        else: 
                            #ARGUE CON sur l'autre object - TO BE IMPLEMENTED
                            self.send(self.interlocuteur_id, 102, "I  don't have any supporting argument")
                    else:
                        # if self.can_be_attacked(argument) is not None:                        #Previous version
                        #     item, crit_name, crit_value = self.can_be_attacked(argument)
                        #     counter_arg = self.attacking_proposal(item, crit_name, crit_value)
                        #     self.send(self.interlocuteur_id, 105, counter_arg)

                        item, _, _ = self.argument_parsing(argument)
                        if self.find_attacking_arg(item) is not None:
                            #ARGUE CON
                            item, crit_name, crit_value = self.find_attacking_arg(item)
                            counter_arg = self.attacking_proposal(item, crit_name, crit_value)
                            self.send(self.interlocuteur_id, 105, counter_arg)
                        else:
                            #ACCEPT
                            self.send(self.interlocuteur_id, 102, item)
                            # self.send(self.interlocuteur_id, 102, "I  don't have any attacking argument")


            elif len(reponses_ask_why) > 0:
                # ARGUE PRO
                for message in reponses_ask_why:
                    item = message.get_content() 
                print(self.interlocuteur.get_name(), ": ASK WHY(", item,")")
                self.send(self.interlocuteur_id, 105, self.support_proposal(item))


            elif len(reponses_propose) > 0:
                for message in reponses_propose:
                    item = message.get_content() 
                print(self.interlocuteur.get_name(), ": PROPOSE(", item,")")

                if self.preference.is_item_among_top_10_percent(item, self.item_list):
                    #ACCEPT
                    self.send(self.interlocuteur_id, 102, item)
                    preferred_item = item #On remplace l'objet préféré après l'avoir accepté
                else:
                    #ASK WHY
                    self.other_item = item
                    self.send(self.interlocuteur_id, 104, item)


            else:
                # PROPOSE
                self.has_proposed_preferred=True
                self.send(self.interlocuteur_id, 101, self.preferred_item)


class ArgumentModel( Model ) :
    """ ArgumentModel which inherit from Model .
    """
    def __init__(self) :
        self.schedule = BaseScheduler(self)
        self.__messages_service = MessageService(self.schedule)

        # Creating items
        E = Item("E", "Electric Engine")
        ICED = Item("ICED", "Diesel Engine")

        item_list = [ICED, E]

        # Creating agents
        A1 = ArgumentAgent(0, self, "A1", Preferences(), item_list)
        A2 = ArgumentAgent(1, self, "A2",  Preferences(), item_list)

        self.schedule.add(A1)
        self.schedule.add(A2)

        # Launch the Communication part 
        mailbox_agent1 = Mailbox()
        mailbox_agent2 = Mailbox()


        #Generating preferences
        A1.generate_preferences(item_list, "Pref_agent1.csv")
        A2.generate_preferences(item_list, "Pref_agent2.csv")

        self.running = True

    def step( self ) :
        self.__messages_service.dispatch_messages ()
        self.schedule.step ()



if __name__ == "__main__":
    argument_model = ArgumentModel()

    step = 0
    while step < 20: # Pas très important, les agents arrêtent de parler après un COMMIT
        argument_model.step()
        step += 1

