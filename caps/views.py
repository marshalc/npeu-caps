from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from caps.models import CapsForm

# Create your views here.
def home(request):
    """
    Default homepage
    """
    return render_to_response('index.html', {}, context_instance=RequestContext(request))

@staff_member_required
def admin_view_all_csv(request):
    """
    Display a listing of all CAPS reports as a CSV file, but restrict to staff members
    """
    listing = CapsForm.objects.all().select_related()
    return render_to_response(
        'admin/list-caps.csv',
        { 'listing':listing },
        context_instance=RequestContext(request)
    )
