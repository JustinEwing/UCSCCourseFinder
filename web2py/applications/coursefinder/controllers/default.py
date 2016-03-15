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
    return dict(form=auth())

@auth.requires_login()
def search():    
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
		if sel_status == 'All Classes':
			query &= True
		else:
		    query &= db.search.status == 'Open Class'
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
				(db.search.instructor.lower().contains(var) for var in sel_instructor))
		if sel_keyword:
			query &= reduce(lambda a, b: (a | b),
				(db.search.course.lower().contains(var) for var in sel_kywrd_split))
			#Possibly add search across more fields --issues with =& and =|
			#=& knocks out previous query, =| doesn't add enough refinement
			#query &= reduce(lambda a, b: (a | b),
			#	(db.search.instructor.lower().contains(var) for var in sel_kywrd_split))

		results = db(query).select()


	return dict(form=form, results=results)

#grabs course id from ajax call, inserts or updates record in courses db
@auth.requires_login()
def save_course():
	cs_list = []
	new_list = []

	#pull course record #
	item = db.search[request.vars.id]
	cs_list.append(item.id)

	#check if user has any courses saved yet
	if db(db.courses.user_id==auth.user_id).select().first() is None:
		print 'record doesnt exist'
		db.courses.insert(user_id=auth.user_id, courses=cs_list)
	else: #else pull his record, update list:reference
		print 'update god damnit'
		row = db(db.courses.user_id==auth.user_id).select().first()
		new_list = row.courses
		if item.id not in new_list:
			new_list += cs_list
			row.update_record(courses=new_list)

	return str('Saved')

#deletes course and hides listing from account view
@auth.requires_login()
def del_course():
	print 'here i am'
	print request.vars.id
	#pull record
	item = db.search[request.vars.id[1]]
	row = db(db.courses.user_id==auth.user_id).select().first()
	new_list = row.courses
	new_list.remove(item.id)
	id = row.update_record(courses=new_list)
	#pull list, remove item, update record

	#send back jquery to be eval'ed in ajax to hide course
	return "jQuery('#del%s').slideUp()" % item.id

#need a second one for my courses page, vars get returned differently
#I have no idea why
@auth.requires_login()
def del_mycourse():
	print 'here i am'
	print request.vars.id
	#pull record
	item = db.search[request.vars.id]
	row = db(db.courses.user_id==auth.user_id).select().first()
	new_list = row.courses
	new_list.remove(item.id)
	id = row.update_record(courses=new_list)
	#pull list, remove item, update record

	#send back jquery to be eval'ed in ajax to hide course
	return "jQuery('#del%s').slideUp()" % item.id	

#overloads the default profile view
#pulls courses related to logged in user, send back set
def user():
   query = None
   results = None

   if request.args(0) == 'profile':
      if db(db.courses.user_id==auth.user_id).select().first() is  not None:
         row = db(db.courses.user_id==auth.user_id).select().first()
         query = reduce(lambda a, b: (a | b),
            (db.search.id==var for var in row.courses))
         results = db(query).select()

   return dict(form=auth(), courses=results)

#returns courses associated with logged in user for my courses page
@auth.requires_login()
def profile():
   query = None
   results = None


   if db(db.courses.user_id==auth.user_id).select().first() is  not None:
      row = db(db.courses.user_id==auth.user_id).select().first()
      if row.courses:
         query = reduce(lambda a, b: (a | b),
            (db.search.id==var for var in row.courses))
         results = db(query).select()
   return dict(courses=results)
      
     

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
