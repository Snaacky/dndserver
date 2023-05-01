from dndserver.objects.user import User
from dndserver.persistent import parties


class Party:
    def __init__(self, player_1: User) -> None:
        self.id = len(parties) + 1
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
