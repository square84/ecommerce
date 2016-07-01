from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.http import Http404

#Son para mandarlos a una vista ya sea de Login o del admin
class StaffRequiredMixin(object):
    @classmethod
    #sobre escribir el metodo view
    def as_view(self,*args, **kwargs):
        view = super(StaffRequiredMixin,self).as_view(*args, **kwargs)
        return login_required(view)

    @method_decorator(login_required)
    def dispatch(self,request,*args, **kwargs):
        if request.user.is_staff:
            return super(StaffRequiredMixin, self).dispatch(request,*args, **kwargs)
        else:
            raise Http404


class LoginRequiredMixin(object):
    @classmethod
    #sobre escribir el metodo view
    def as_view(self,*args, **kwargs):
        view = super(LoginRequiredMixin,self).as_view(*args, **kwargs)
        return login_required(view)

    @method_decorator(login_required)
    def dispatch(self,request,*args, **kwargs):
            return super(LoginRequiredMixin, self).dispatch(request,*args, **kwargs)