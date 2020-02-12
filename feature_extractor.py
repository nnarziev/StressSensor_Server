from user.models import Participant
print("ss")

participants = participant = Participant.objects.get(id="test")
print(participants.name)