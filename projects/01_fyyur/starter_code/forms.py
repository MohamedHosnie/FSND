from enum import Enum
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, Optional
from wtforms.widgets import TextArea, CheckboxInput

#  Enums
#  ----------------------------------------------------------------
class State(Enum):
    AL = 'AL'
    AK = 'AK'
    AZ = 'AZ'
    AR = 'AR'
    CA = 'CA'
    CO = 'CO'
    CT = 'CT'
    DE = 'DE'
    DC = 'DC'
    FL = 'FL'
    GA = 'GA'
    HI = 'HI'
    ID = 'ID'
    IL = 'IL'
    IN = 'IN'
    IA = 'IA'
    KS = 'KS'
    KY = 'KY'
    LA = 'LA'
    ME = 'ME'
    MT = 'MT'
    NE = 'NE'
    NV = 'NV'
    NH = 'NH'
    NJ = 'NJ'
    NM = 'NM'
    NY = 'NY'
    NC = 'NC'
    ND = 'ND'
    OH = 'OH'
    OK = 'OK'
    OR = 'OR'
    MD = 'MD'
    MA = 'MA'
    MI = 'MI'
    MN = 'MN'
    MS = 'MS'
    MO = 'MO'
    PA = 'PA'
    RI = 'RI'
    SC = 'SC'
    SD = 'SD'
    TN = 'TN'
    TX = 'TX'
    UT = 'UT'
    VT = 'VT'
    VA = 'VA'
    WA = 'WA'
    WV = 'WV'
    WI = 'WI'
    WY = 'WY'

class Genre(Enum):
    Alternative = 'Alternative'
    Blues = 'Blues'
    Classical = 'Classical'
    Country = 'Country'
    Electronic = 'Electronic'
    Folk = 'Folk'
    Funk = 'Funk'
    Hip_Hop = 'Hip-Hop'
    Heavy_Metal = 'Heavy Metal'
    Instrumental = 'Instrumental'
    Jazz = 'Jazz'
    Musical_Theatre = 'Musical Theatre'
    Pop = 'Pop'
    Punk = 'Punk'
    R_B = 'R&B'
    Reggae = 'Reggae'
    Rock_n_Roll = 'Rock n Roll'
    Soul = 'Soul'
    Other = 'Other'

#  Forms
#  ----------------------------------------------------------------
class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), AnyOf(values=[state.value for state in State])],
        choices=[(state.value, state.value) for state in State]
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link', validators=[DataRequired(), URL()]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=[(genre.value, genre.value) for genre in Genre]
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL(), Optional()]
    )
    website = StringField(
        'website', validators=[URL(), Optional()]
    )
    seeking_talent = BooleanField(
        'seeking_talent', widget=CheckboxInput()
    )
    seeking_description = StringField(
        'seeking_description', widget=TextArea()
    )

class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), AnyOf(values=[state.value for state in State])],
        choices=[(state.value, state.value) for state in State]
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link', validators=[DataRequired(), URL()]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=[(genre.value, genre.value) for genre in Genre]
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL(), Optional()]
    )
    website = StringField(
        'website', validators=[URL(), Optional()]
    )
    seeking_venue = BooleanField(
        'seeking_venue', widget=CheckboxInput()
    )
    seeking_description = StringField(
        'seeking_description', widget=TextArea()
    )
