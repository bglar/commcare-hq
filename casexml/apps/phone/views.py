from django.http import HttpResponse
from django_digest.decorators import *
from casexml.apps.phone import xml
from dimagi.utils.timeout import TimeoutException
from casexml.apps.case.models import CommCareCase
from casexml.apps.phone.restore import generate_restore_payload
from casexml.apps.phone.models import User
from casexml.apps.case import const



@httpdigest
def restore(request):
    user = User.from_django_user(request.user)
    restore_id = request.GET.get('since')
    
    try:
        response = generate_restore_payload(user, restore_id)
        return HttpResponse(response, mimetype="text/xml")
    except TimeoutException:
        return HttpResponse(status=503)
    

def xml_for_case(request, case_id, version="1.0"):
    """
    Test view to get the xml for a particular case
    """
    case = CommCareCase.get(case_id)
    return HttpResponse(xml.get_case_xml(case, [const.CASE_ACTION_CREATE,
                                                const.CASE_ACTION_UPDATE],
                                         version), mimetype="text/xml")
    