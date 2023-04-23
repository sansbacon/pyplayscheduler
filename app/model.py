import json
import uuid
from google.cloud import ndb


class OptimalSchedule(ndb.Model):
    """Represents an optimal schedule"""
    optimal_schedule_id = ndb.ComputedProperty(lambda self: f'schedule_{self.n_courts}_{self.n_rounds}_{self.n_players}', indexed=True)
    n_courts = ndb.IntegerProperty(indexed=True)
    n_rounds = ndb.IntegerProperty(indexed=True)
    n_players = ndb.IntegerProperty(indexed=True)
    schedule = ndb.JsonProperty()

    @classmethod
    def find_by_id(cls, id):
        return cls.query().filter(cls.optimal_schedule_id == id)

    @classmethod
    def from_json(cls, j):
        """Creates object from stringified json. Reverse of to_json"""
        data = json.loads(j)
        return OptimalSchedule(**data)

    def to_json(self):
        """Creates object from stringified json. Reverse of to_json"""
        return json.dumps(self.to_dict())


class CustomSchedule(ndb.Model):
    custom_schedule_id = ndb.StringProperty(default=uuid.uuid4(), indexed=True)
    n_courts = ndb.IntegerProperty(required=True, indexed=True)
    n_rounds = ndb.IntegerProperty(required=True, indexed=True)
    players = ndb.JsonProperty(required=True, indexed=False)
    n_players = ndb.ComputedProperty(lambda self: len(self.players), indexed=True)
    optimal_schedule = ndb.StructuredProperty(OptimalSchedule, required=False, indexed=False, default=None)
    readable_schedule = ndb.JsonProperty(required=False, indexed=False, default=None)

    @classmethod
    def find_by_id(cls, id):
        return cls.query().filter(cls.custom_schedule_id == id)

    @classmethod
    def from_json(cls, j):
        """Creates object from stringified json. Reverse of to_json"""
        data = json.loads(j)
        return CustomSchedule(**data)

    def to_json(self):
        """Creates object from stringified json. Reverse of to_json"""
        return json.dumps(self.to_dict())

    def readable_schedule(self, sep=' - '):
        """Creates readable schedule from CustomSchedule object"""
        if not self.optimal_schedule:
            return [[1, 1, 'No available schedule', 'No available schedule']]
        sched = json.loads(self.optimal_schedule) if isinstance(self.optimal_schedule, str) else self.optimal_schedule

        items = []
        for idx, rnd in enumerate(sched):
            for court, matchup in enumerate(rnd):
                team1 = sep.join([self.players[int(i)].strip() for i in matchup[0:2]])
                team2 = sep.join([self.players[int(i)].strip() for i in matchup[2:]])            
                items.append([idx + 1, court + 1, team1, team2])
        self.readable_schedule = items
        return items
