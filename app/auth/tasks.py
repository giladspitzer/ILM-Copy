from flask import flash
from app.models import Country
from app.tasks import check_location, add_locations


def check_entered_location(country, city, zip):
    """This function ensures that the returned data from the google maps api is sufficient for what was
    requested and then calls the function add_locations to create/assign the locations. It returns the user_codes
    which is the dictionary of id's of the locations"""
    if country == Country.query.filter_by(code='US').first().id:  # if they enter an address in the US
        # print(zip)
        data = check_location(zip)  # check their entered data
        # print(data)
        if data == {}:
            flash('There was an error with your postal code input. Please ensure you entered it correctly.')
            return None
        if 'postal' not in list(data.keys()):  # if no postal code then return redirect
            return None
        if 'city' not in list(data.keys()):  # if no postal code then return redirect
            flash('Unable to determine city')
            return None
        if int(data['postal']) != int(zip):
            flash('There was an error with your postal code input. Please ensure you entered it correctly.')
            return None
        if data['country'][1] != Country.query.filter_by(id=country).first().code:
            flash('The Postal Code you entered does not match the country you entered')
            return None
        user_codes = add_locations(4, data)
    else:
        data = check_location(city)  # check their entered data
        if data == {}:
            flash('There was an error with your location input. Please ensure you entered it correctly.')
            return None
        if 'city' not in list(data.keys()):  # if no postal code then return redirect
            flash('Unable to determine city')
            return None
        if data['country'][1] != Country.query.filter_by(id=country).first().code:
            flash('The City you entered does not match the country you entered')
            return None
        user_codes = add_locations(3, data)
    return user_codes



