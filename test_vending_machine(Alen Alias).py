"""
Unit tests for the 'vending_machine_graphical.py' script.
"""
from vending_machine_graphical_Alen_Alias import VendingMachine, WaitingState, AddCoinsState, DeliverProductState, CountChangeState

def test_VendingMachine():
    """Test the VendingMachine class and its states."""

    vending = VendingMachine()

    vending.add_state(WaitingState())
    vending.add_state(AddCoinsState())
    vending.add_state(DeliverProductState())
    vending.add_state(CountChangeState())

    vending.go_to_state('waiting')
    assert vending.state.name == 'waiting', "Initial state should be 'waiting'"

    vending.event = '200'
    vending.update()
    assert vending.state.name == 'add_coins', "State should transition to 'add_coins' after inserting a coin"
    assert vending.amount == 200, "Amount should be updated to 200 cents after inserting a toonie"

    vending.event = '25'
    vending.update()
    assert vending.amount == 225, "Amount should be 225 cents after adding a quarter"

    vending.event = 'chips'
    vending.update()
    assert vending.state.name == 'deliver_product', "State should transition to 'deliver_product' after selecting a product"
    assert vending.change_due == 75, "Change due should be 75 cents after selecting a product costing 150 cents"

    vending.go_to_state('count_change')
    vending.change_due = 75
    vending.update()
    assert vending.change_due == 0, "Change due should be 0 after dispensing all change"
    assert vending.state.name == 'waiting', "State should return to 'waiting' after dispensing change"

    vending.go_to_state('add_coins')
    vending.amount = 100
    vending.event = 'RETURN'
    vending.update()
    assert vending.state.name == 'count_change', "State should transition to 'count_change' when RETURN button is pressed"
    assert vending.change_due == 100, "Change due should match the inserted amount after RETURN is pressed"

    print("All tests passed!")


if __name__ == "__main__":
    test_VendingMachine()