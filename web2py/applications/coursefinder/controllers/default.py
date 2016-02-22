# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################


current_term = '2016 Winter'
term = ['2016 Spring', '2016 Winter', '2016 Summer', '2016 Fall'] 
status = ['Open Classes', 'All Classes']
subject = ['All Subjects', 'Computer Engineering', 'Computer Science']
units = ['All', '2', '5']


def index():
	default_term = current_term
	default_stat = 'All Classes'
	default_subject = 'All Subjects'
	default_instructor = None

	form = SQLFORM.factory(
		Field('term', default=default_term, requires=IS_IN_SET(term)),
		Field('status', default=default_stat, requires=IS_IN_SET(status)),
		Field('subject', default=default_subject, requires=IS_IN_SET(subject)),
		Field('course', type='string'),
		Field('instructor', type='string', default=default_instructor),
		Field('keyword', type='string'),
		formstyle='bootstrap3_stacked',
		submit_button="Search")
		
	query = None
	results = None

	if form.process(keepvalues=True, onsuccess = None).accepted:
		sel_term = form.vars.term
		sel_status = form.vars.status
		sel_subject = form.vars.subject
		sel_course_num = form.vars.course.lower().split()
		sel_instructor = form.vars.instructor.lower().split()
		sel_keyword    = form.vars.keyword
		sel_kywrd_split = sel_keyword.lower().split()

		if sel_term:	
			query = db.search.term == sel_term
		if sel_status:
			query &= db.search.status == sel_status
		if sel_subject == 'All Subjects':
			query &= True
		else:
			if sel_subject == 'Computer Science':
				query &= db.search.course.contains('CMPS')
			elif sel_subject == 'Computer Engineering':
				query &= db.search.course.contains('CMPE')
		if sel_course_num:
			query &= reduce(lambda a, b: (a & b),
				(db.search.course.lower().contains(var) for var in sel_course_num))

		if sel_instructor:
			query &= reduce(lambda a, b: (a | b),
				(db.search.instructor.contains(var) for var in sel_instructor))
		if sel_keyword:
			query &= reduce(lambda a, b: (a | b),
				(db.search.course.lower().contains(var) for var in sel_kywrd_split))

		#Future: Let keyword search among multuple catagories -- Fuzzy matching?
		#	query &= reduce(lambda a, b: (a | b),
		#		(db.search.instructor.lower() == var.lower() for var in sel_kywrd_split))

		results = db(query).select()


	return dict(form=form, results=results)

def index_bak():
	form = FORM((TABLE(
		TR('Term: ', SELECT(term, _term='term', requires=IS_IN_SET(term))),
		TR('Status: ', SELECT(status, status='status', default='All Classes', requires=IS_IN_SET(status))),
		TR('Subject: ',SELECT(subject, _subject='subject', default='All Subjects', requires=IS_IN_SET(subject))),
		TR('Course Number: ',INPUT(_course_number='Course Number')),
		TR('Instructor: ',  INPUT(_instructor='Instructor'),
		TR('Units: ', SELECT(units, _units='Units', requires=IS_IN_SET(units))),
		TR(INPUT(_type='submit'), _action=URL(search_results))))))


	if form.process(formname='test').accepted:
		redirect(URL('search_results', vars=form.vars))


	return dict(form=form)

def search_results():
	return dict(request=request)

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
