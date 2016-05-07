from datetime import datetime

from google.appengine.ext import ndb


class Location(ndb.Model):
    """ Location in the galaxy to depart or arrive to: Planet, Star, City """
    name = ndb.StringProperty(required=True)
    parent_location = ndb.KeyProperty()

    @classmethod
    def save_from_request(cls, request):
        location = cls(id=request.get('name'), name=request.get('name'))
        parent = request.get('parent')
        if parent:  # in case we ever pass a parent location
            location.parent_location = ndb.Key(cls, parent)
        location.put()


class StarTrip(ndb.Model):
    """ Trip across the galaxy from one origin to a destination """
    description = ndb.TextProperty(required=True)
    origin = ndb.KeyProperty(required=True)
    destiny = ndb.KeyProperty(required=True)
    date = ndb.DateProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    available_seats = ndb.IntegerProperty(default=1)
    booked_seats = ndb.IntegerProperty(default=0)
    pilot_name = ndb.StringProperty()
    price = ndb.IntegerProperty(default=0)  # in Galactic Credits

    @classmethod
    def save_from_request(cls, request):
        """ Save trip from http request parameters """
        star_trip = cls()
        star_trip.date = datetime.strptime(request.get('date'), '%Y-%m-%d')
        star_trip.description = request.get('description')
        star_trip.available_seats = int(request.get('seats'))
        star_trip.pilot_name = request.get('pilot')
        star_trip.origin = ndb.Key(Location, request.get('origin'))
        star_trip.destiny = ndb.Key(Location, request.get('destiny'))
        star_trip.price = int(request.get('price'))
        star_trip.put()

    @classmethod
    def query_from_request(cls, request, limit=10):
        """ TODO: pagination (cursors) """
        try:
            origin = ndb.Key(Location, request.get('origin'))
            destiny = ndb.Key(Location, request.get('destiny'))
            date = datetime.strptime(request.get('date'), '%Y-%m-%d').date()
        except:
            origin = destiny = date = None
        if origin and destiny and date:
            result = cls.query(cls.origin == origin, cls.destiny == destiny, cls.date == date
                               ).order(-cls.date).fetch(limit)
        else:
            result = cls.query().order(-cls.date).fetch(limit)
        params = {'searched_origin': origin, 'searched_destiny': destiny, 'searched_date': date}
        return result, params