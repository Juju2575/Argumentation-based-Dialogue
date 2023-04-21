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
        very_good_proposal = []
        good_proposal = []
        
        crit_name_list = preferences.get_criterion_name_list()
        for criterion_name in crit_name_list:
            crit_value = item.get_value(preferences, criterion_name)

            #Liste des critères notés VERY GOOD
            if (crit_value == Value(4)):
                very_good_proposal.insert(0, CoupleValue(criterion_name, crit_value))
                if len(very_good_proposal) > 1:
                    if preferences.is_preferred_criterion(very_good_proposal[1].criterion_name, very_good_proposal[0].criterion_name):
                        very_good_proposal[0], very_good_proposal[1] = very_good_proposal[1], very_good_proposal[0]

            #Liste des critères notés GOOD
            if (crit_value == Value(3)):
                good_proposal.insert(0, CoupleValue(criterion_name, crit_value))
                if len(good_proposal) > 1:
                    if preferences.is_preferred_criterion(good_proposal[1].criterion_name, good_proposal[0].criterion_name):
                        good_proposal[0], good_proposal[1] = good_proposal[1], good_proposal[0]

        
            
        return very_good_proposal + good_proposal
    
    def List_attacking_proposal ( self , item , preferences ) :
        """  Generate a list of premisses which can be used to attack an item
            param item : Item - name of the item
            return : list of all premisses CON an item ( sorted by order of importance based on agent ’s preferences )
        """
        very_bad_proposal = []
        bad_proposal = []
        
        crit_name_list = preferences.get_criterion_name_list()
        for criterion_name in crit_name_list:
            crit_value = item.get_value(preferences, criterion_name)

            #Liste des critères notés VERY GOOD
            if (crit_value == Value(1)):
                very_bad_proposal.insert(0, CoupleValue(criterion_name, crit_value))
                if len(very_bad_proposal) > 1:
                    if preferences.is_preferred_criterion(very_bad_proposal[1].criterion_name, very_bad_proposal[0].criterion_name):
                        very_bad_proposal[0], very_bad_proposal[1] = very_bad_proposal[1], very_bad_proposal[0]

            #Liste des critères notés GOOD
            if (crit_value == Value(2)):
                bad_proposal.insert(0, CoupleValue(criterion_name, crit_value))
                if len(bad_proposal) > 1:
                    if preferences.is_preferred_criterion(bad_proposal[1].criterion_name, bad_proposal[0].criterion_name):
                        bad_proposal[0], bad_proposal[1] = bad_proposal[1], bad_proposal[0]
            
        return very_bad_proposal + bad_proposal