# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """

    # this allows us to only show edit options on a given item if the logged-in user owns that item
    is_owner = (lambda row: row.seller.email == session.auth.user.email) if session.auth else False



    items_grid = SQLFORM.grid(db.listing,
                               fields=[
                                       db.listing.posted,
                                       db.listing.title,
                                       db.listing.description,
                                       db.listing.category,
                                       db.listing.price,
                                       db.listing.image,
                                       db.listing.sold,
                                       db.listing.seller
                                       ],
                               editable=is_owner, # see comment above
                               create=False, # don't let the user create directly from here
                               orderby='-posted', # sort newest to oldest
                              )


    return dict(items_grid=items_grid)

@auth.requires_login()
def create():
    add_listing = SQLFORM.factory(db.seller, db.listing,
                                   table_name="listing",
                                   # don't show the sold, posted or author fields
                                   fields=[
                                            'title',
                                            'description',
                                            'category',
                                            'price',
                                            'image',
                                            'phone'
                                           ],
                                  )

    # We don't want to ask the user for their email if they've already signed up with it - thus the following logic.
    # We know that, if they're submitting this form, they're logged in and we have their email and name - we just need
    # their phone number. So that's all we ask them for, then we create a new 'seller' object with the given number,
    # plus the info we already have from the auth-user table. (although it'd be far cleaner to alter the auth-user table
    # instead....

    if add_listing.process(detect_record_change=True).accepted:
        q = db.seller.email == session.auth.user.email
        result = db(q).select()
        if len(result.records) > 0:
            seller_id = result.records[0].seller.id
        else:
            email = session.auth.user.email
            phone = add_listing.vars.phone
            name = " ".join([session.auth.user.first_name, session.auth.user.last_name])
            seller_id = db.seller.insert(email=email, phone=phone, name=name)

        add_listing.vars.seller = seller_id
        db.listing.insert(posted=request.now,
                         title=add_listing.vars.title,
                         description=add_listing.vars.description,
                         category=add_listing.vars.category,
                         seller=seller_id,
                         image= add_listing.vars.image                         )
        response.flash='Got it! Thanks for submitting a listing!'

    return dict(add_listing=add_listing)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


