import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
import json

database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

'''
db_drop_and_create_all()
    drops the database tables and starts fresh
    can be used to initialize a clean database
    !!NOTE you can change the database_filename variable to have multiple verisons of a database
'''
def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

'''
Drink
a persistent drink entity, extends the base SQLAlchemy Model
'''
class Drink(db.Model):
    # Autoincrementing, unique primary key
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    # String Title
    title = Column(String(80), unique=True)
    # the ingredients blob - this stores a lazy json blob
    # the required datatype is [{'color': string, 'name':string, 'parts':number}]
    recipe =  Column(String(180), nullable=False)

    '''
    __init__()
        initialize a new Drink object
    '''
    def __init__(self, title, recipe):
        self.title = title
        self.recipe = recipe

    '''
    short()
        short form representation of the Drink model
    '''
    def short(self):
        recipes = json.loads(self.recipe)
        short_recipe = [{'color': recipe.get('color'), 'parts': recipe.get('parts')} for recipe in recipes]
        return {
            'id': self.id,
            'title': self.title,
            'recipe': short_recipe
        }

    '''
    long()
        long form representation of the Drink model
    '''
    def long(self):
        return {
            'id': self.id,
            'title': self.title,
            'recipe': json.loads(self.recipe)
        }

    '''
    validate_recipe()
        make sure that recipe contains the correct data
    '''
    def validate_recipe(self):
        recipes_json = json.loads(self.recipe)
        recipes = []

        if not isinstance(recipes, list):
            recipes.append(recipes)
        else:
            recipes = recipes_json

        for recipe in recipes:
            recipe_name = recipe.get('name')
            recipe_color = recipe.get('color')
            recipe_parts = recipe.get('parts')
            # print(isinstance(recipe_name, str), isinstance(recipe_color, str), isinstance(recipe_parts, int))
            if not (isinstance(recipe_name, str) and isinstance(recipe_color, str) and isinstance(recipe_parts, int)):
                raise Exception('wrong recipe')

        self.recipe = json.dumps(recipes)

    '''
    insert()
        inserts a new model into a database
        the model must have a unique name
        the model must have a unique id or null id
        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.insert()
    '''
    def insert(self):
        self.validate_recipe()
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a new model into a database
        the model must exist in the database
        EXAMPLE
            drink = Drink(title=req_title, recipe=req_recipe)
            drink.delete()
    '''
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a new model into a database
        the model must exist in the database
        EXAMPLE
            drink = Drink.query.filter(Drink.id == id).one_or_none()
            drink.title = 'Black Coffee'
            drink.update()
    '''
    def update(self):
        self.validate_recipe()
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.short())