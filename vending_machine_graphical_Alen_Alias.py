#TPRG2131 project 1 Vending Machine
#Alen Alias (100931271)

import PySimpleGUI as sg

try:
    from gpiozero import Button, Servo
    from time import sleep
    hardware_present = True
    return_button = Button(5)
    servo = Servo(17)
except ModuleNotFoundError:
    print("Not on a Raspberry Pi or gpiozero not installed.")
    hardware_present = False

TESTING = True

def log(s):
    """Print debug logs if TESTING is True."""
    if TESTING:
        print(s)

class VendingMachine:
    PRODUCTS = {
        "chips": ("Potato Chips", 150),
        "chocolate": ("Chocolate Bar", 200),
        "cookies": ("Cookies", 175),
        "soda": ("Soda Can", 125),
        "juice": ("Juice Box", 100),
    }

    COINS = {
        "5": ("Nickel", 5),
        "10": ("Dime", 10),
        "25": ("Quarter", 25),
        "100": ("Loonie", 100),
        "200": ("Toonie", 200),
    }

    def __init__(self):
        self.state = None
        self.states = {}
        self.event = ""
        self.amount = 0
        self.change_due = 0
        self.coin_values = sorted([self.COINS[k][1] for k in self.COINS], reverse=True)
        log(f"Coin values: {self.coin_values}")

    def add_state(self, state):
        self.states[state.name] = state

    def go_to_state(self, state_name):
        if self.state:
            log(f"Exiting {self.state.name}")
            self.state.on_exit(self)
        self.state = self.states[state_name]
        log(f"Entering {self.state.name}")
        self.state.on_entry(self)

    def update(self):
        if self.state:
            self.state.update(self)

    def add_coin(self, coin):
        """Add coin value."""
        self.amount += self.COINS[coin][1]

    def dispense_product(self):
        """Activate the servo to dispense the product."""
        if hardware_present:
            servo.min()
            sleep(0.5)
            servo.max()
            sleep(0.5)
        print("Product dispensed!")

    def return_coins(self):
        """Reset amount and change_due to simulate returning coins."""
        self.change_due = self.amount
        self.amount = 0

class State:
    """Superclass for states with placeholder methods."""
    _NAME = ""

    @property
    def name(self):
        return self._NAME

    def on_entry(self, machine):
        pass

    def on_exit(self, machine):
        pass

    def update(self, machine):
        pass

class WaitingState(State):
    _NAME = "waiting"

    def update(self, machine):
        if machine.event in machine.COINS:
            machine.add_coin(machine.event)
            machine.go_to_state('add_coins')

class AddCoinsState(State):
    _NAME = "add_coins"

    def update(self, machine):
        if machine.event == "RETURN":
            machine.return_coins()
            machine.go_to_state('count_change')
        elif machine.event in machine.COINS:
            machine.add_coin(machine.event)
        elif machine.event in machine.PRODUCTS:
            product_price = machine.PRODUCTS[machine.event][1]
            if machine.amount >= product_price:
                machine.go_to_state('deliver_product')
            else:
                print("Insufficient funds. Insert more coins.")

class DeliverProductState(State):
    _NAME = "deliver_product"

    def on_entry(self, machine):
        product_name, product_price = machine.PRODUCTS[machine.event]
        machine.change_due = machine.amount - product_price
        machine.amount = 0
        print(f"Dispensing {product_name}")
        machine.dispense_product()

    def update(self, machine):
        if machine.change_due > 0:
            machine.go_to_state('count_change')
        else:
            machine.go_to_state('waiting')

class CountChangeState(State):
    _NAME = "count_change"

    def on_entry(self, machine):
        print(f"Change due: ${machine.change_due / 100:.2f}")
        log(f"Returning change: {machine.change_due}")

    def update(self, machine):
        for coin_value in machine.coin_values:
            while machine.change_due >= coin_value:
                print(f"Returning {coin_value} cents")
                machine.change_due -= coin_value

        if machine.change_due == 0:
            print("All change returned.")
            machine.go_to_state('waiting')

if __name__ == "__main__":
    sg.theme('BluePurple')

    coin_col = [[sg.Text("INSERT COINS", font=("Helvetica", 24))]]
    for coin in VendingMachine.COINS:
        coin_col.append([sg.Button(coin, font=("Helvetica", 18))])

    product_col = [[sg.Text("SELECT PRODUCT", font=("Helvetica", 24))]]
    for product in VendingMachine.PRODUCTS:
        product_col.append([sg.Button(product, font=("Helvetica", 18))])

    layout = [
        [sg.Column(coin_col, vertical_alignment="TOP"),
         sg.VSeparator(),
         sg.Column(product_col, vertical_alignment="TOP")],
        [sg.Button("RETURN", font=("Helvetica", 12))]
    ]
    window = sg.Window('Vending Machine - AJM', layout)

    vending = VendingMachine()
    vending.add_state(WaitingState())
    vending.add_state(AddCoinsState())
    vending.add_state(DeliverProductState())
    vending.add_state(CountChangeState())
    vending.go_to_state('waiting')

    if hardware_present:
        return_button.when_pressed = lambda: vending.go_to_state('count_change')

    while True:
        event, values = window.read(timeout=10)
        if event != '__TIMEOUT__':
            log(f"Event: {event}, Values: {values}")
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        vending.event = event
        vending.update()

    window.close()
    print("Shutting down...")