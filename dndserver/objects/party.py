from dndserver.objects.user import User

# starting id of the parties
party_id = 0


class Party:
    def __init__(self, player_1: User) -> None:
        global party_id
        party_id += 1
        self.id = party_id

        self.players = [player_1]
        self.leader = player_1

    def add_member(self, user: User) -> None:
        """Add member to the party."""
        if len(self.players) == 3:
            raise Exception("No room in that party for any more players.")
        self.players.append(user)

    def remove_member(self, user: User) -> None:
        """Remove member from the party."""
        if user not in self.players:
            raise Exception("User is not in that party.")
        self.players.remove(user)
