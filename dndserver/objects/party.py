from dndserver.objects.user import User


class Party:
    def __init__(self, _id: int, player_1: User) -> None:
        self.id = _id
        self.players = [player_1]
        self.leader = player_1

    def add_member(self, user: User):
        """Add member to the party."""
        if len(self.players) == 3:
            raise Exception("No room in that party for any more players.")
        self.players.append(user)

    def remove_member(self, user: User):
        """Remove member from the party."""
        if user not in self.players:
            raise Exception("User is not in that party.")
        self.players.remove(user)
