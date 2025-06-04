from django import template
from superadmin.models import *

register = template.Library()


@register.simple_tag()
def check_prev(id):
    return Previllages.objects.filter(user=id)
    

@register.simple_tag()
def check_previllage(request,menu):
    if request.user.user_type == 1:
        return True
    else:
        ismenu = Previllages.objects.filter(user=request.user.id,option=menu).first()
        if ismenu:
            return ismenu
        else:
            return None
    

@register.simple_tag()
def get_followup_status(id):
    lead = LeadsDetails.objects.filter(lead=id).order_by('-id').first()
    if lead:
        return lead.status
    else:
        return 'Open'
    

@register.simple_tag()
def attendance(id):
    print(id)
    lead = StaffTimings.objects.filter(staff=id).order_by('id')
    print(lead)
    if lead:
        return lead
    else:
        pass
    
