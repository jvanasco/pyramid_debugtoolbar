from logging import getLogger
logger = getLogger('pyramid_debugtoolbar')


from pyramid_debugtoolbar.utils import dictrepr


class AttribSafeContextObj(object):
    """returns '' when the attribute does not exist)"""
    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            log.debug("No attribute called %s found on object, returning "
                      "empty string", name)
            return ''


# `request` properties
# format is
# ( attr_, is_show_dict, is_execute_method )
request_properties = (
	('application_url', None, None),
	('authenticated_userid', None, None),
	('authorization', None, None),
	('cache_control', None, None),
	('context', None, None),
	('current_route_path', None, True),
	('current_route_url', None, True),
	('effective_principals', None, None),
	('exc_info', None, None),
	('exception', None, None),
	('locale_name', None, None),
	('matchdict', None, None),
	('matched_route', True, None),
	# ('registry', None, None),  # as a 'string' will be the python package name; as a dict will be the contents
	('root', None, None),
	('subpath', None, None),
	('traversed', None, None),
	('unauthenticated_userid', None, None),
	('view_name', None, None),
	('virtual_root_path', None, None),
	('virtual_root', None, None),
)


def safe_request(request):
	"""creates a safe request object
		ideally only one should be needed per view
	"""

	safe_request = AttribSafeContextObj()
	for (attr_, is_show_dict, is_execute_method) in sorted(request_properties):
        if not hasattr(original_request, attr_):
            continue
        value = None
        if is_show_dict:
            value = getattr(request, attr_).__dict__
        elif is_execute_method:
            value = getattr(request, attr_)()
        else:
            value = getattr(request, attr_)
        if isinstance(value, dict):
        	value = dictrepr(value)
        safe_request[attr_] = value

    safe_request['get'] = [(k, request.GET.getall(k)) for k in request.GET]
    safe_request['post'] = [(k, saferepr(v)) for k, v in request.POST.items()]

    safe_request['cookies'] = [(k, request.cookies.get(k)) for k in request.cookies]
    safe_request['environ'] = dictrepr(request.environ)

	if hasattr(request, 'session'):
	    safe_request['session'] = dictrepr(request.session)


	attr_dict = request.__dict__.copy()

	# environ is displayed separately
	del attr_dict['environ']

	# collapse this
	if 'response' in attr_dict:
		attr_dict['response'] = repr(attr_dict['response'])

    safe_request['attrs'] = dictrepr(attr_dict)


