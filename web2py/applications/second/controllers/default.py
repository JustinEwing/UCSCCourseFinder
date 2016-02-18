@auth.requires_login()
def index():
    listings = db().select(db.forsale.ALL, orderby=db.forsale.title)
    form = SQLFORM(db.forsale)
    if form.process().accepted:
        response.flash = 'your listing is posted'
    return dict(listings=listings, form=form)

def download():
    return response.download(request, db)

def user():
    return dict(form=auth())
