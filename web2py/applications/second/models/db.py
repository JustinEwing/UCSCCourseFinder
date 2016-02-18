db = DAL("sqlite://storage.sqlite")

from gluon.tools import Auth
auth = Auth(db)
auth.define_tables(username=True)

db.define_table('forsale',
                Field('name'),
                Field('email'),
                Field('phone'),
                Field('date','date'),
                Field('title', unique=True),
                Field('description','text'),
                Field('file','upload'),
                Field('status','boolean'),
                Field('price','double'),
                Field('category','text'),
                format = '%(title)s')

db.forsale.name.requires = IS_NOT_EMPTY()
db.forsale.email.requires = IS_EMAIL()
db.forsale.phone.requires = requires = IS_MATCH('^1?((-)\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$',
                                                error_message='not a phone number')
db.forsale.date.requires = IS_DATE()
db.forsale.title.requires = IS_NOT_IN_DB(db, db.forsale.title)
db.forsale.description.requires = IS_NOT_EMPTY()
db.forsale.price.requires = IS_FLOAT_IN_RANGE(0, 100000.0,
                                                error_message='The price should be in the range 0..100000')
db.forsale.category.requires = IS_IN_SET(['Car', 'Bike', 'Book', 'Music', 'Outdoors', 'Household','Misc'])
