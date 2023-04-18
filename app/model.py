from google.cloud import ndb


class OptimalSchedule(ndb.Model):
    schedule_id = ndb.StringProperty()
    n_courts = ndb.IntegerProperty()
    n_rounds = ndb.IntegerProperty()
    n_players = ndb.IntegerProperty()
    schedule = ndb.JsonProperty()
