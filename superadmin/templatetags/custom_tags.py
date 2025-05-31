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
        ismenu = Previllages.objects.filter(user=request.user.id,option=menu)
        if ismenu:
            return True
        else:
            return False
    
