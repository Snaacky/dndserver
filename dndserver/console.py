def give_item(user, item_name):
    print(f"Giving {user} an item named {item_name}")

def give_money(user, value):
    print(f"Giving {user} {value} money")

commands = {
    "/give_item": {
        "function": give_item,
        "help": "/give_item <user> <item_name>"
    },
    "/give_money": {
        "function": give_money,
        "help": "/give_money <user> <value>"
    },
    # add more commands here
}

def console():
    while True:
        command = input()
        parts = command.split()

        if parts[0] not in commands:
            print("Invalid command")
            continue

        try:
            commands[parts[0]]["function"](*parts[1:])
        except TypeError:
            print(f"Invalid command. Usage: {commands[parts[0]]['help']}")
