#!/ usr / bin /env python3

from arguments.Comparison import Comparison
from arguments.CoupleValue import CoupleValue

from communication.preferences.Value import Value

class Argument:
    """ Argument class .
    This class implements an argument used during the interaction .

    attr :
    decision :
    item :
    comparison_list :
    couple_values_list :
    """

    def __init__(self, boolean_decision, item):
        """ Creates a new Argument .
        """
        self.decision = boolean_decision
        self.item = item
        self.comparison_list = []
        self.couple_values_list = []

    def add_premiss_comparison(self, criterion_name_1, criterion_name_2):
        """ Adds a premiss comparison in the comparison list .
        """
        self.comparison_list.append(Comparison(criterion_name_1, criterion_name_2))
        

    def add_premiss_couple_values(self, criterion_name, value):
        """ Add a premiss couple values in the couple values list .
        """
        self.couple_values_list.append(CoupleValue(criterion_name, value))
    
    def List_supporting_proposal ( self , item , preferences ) :
        """ Generate a list of premisses which can be used to support an item
            param item : Item - name of the item
            return : list of all premisses PRO an item ( sorted by order of importance based on agent ’s preferences )
        """
        supporting_proposal = []
        
        crit_name_list = preferences.get_criterion_name_list()
        for criterion_name in crit_name_list:
            crit_value = item.get_value(preferences, criterion_name)
            if (crit_value == Value(4)):
                supporting_proposal.insert(0, CoupleValue(criterion_name, crit_value))
            if (crit_value == Value(3)):
                supporting_proposal.append(CoupleValue(criterion_name, crit_value))
            
        return supporting_proposal
    
    def List_attacking_proposal ( self , item , preferences ) :
        """  Generate a list of premisses which can be used to attack an item
            param item : Item - name of the item
            return : list of all premisses CON an item ( sorted by order of importance based on agent ’s preferences )
        """
        attacking_proposal = []

        crit_name_list = preferences.get_criterion_name_list()

        for criterion_name in crit_name_list:
            crit_value = item.get_value(preferences, criterion_name)
            if (crit_value == Value(1)):
                attacking_proposal.insert(0, CoupleValue(criterion_name, crit_value))
            if (crit_value == Value(0)):
                attacking_proposal.append(CoupleValue(criterion_name, crit_value))
            
        return attacking_proposal