from django.shortcuts import render
from .models import Deal
from django.utils import timezone



def deals_list(request):
    today = timezone.now().date()
    active_deals = Deal.objects.filter(start_date__lte=today, end_date__gte=today)
    return render(request, 'dealsandoffers/deals_list.html', {'deals': active_deals})

from django.shortcuts import render
from .models import Deal

def deals_list(request):
    deals = Deal.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'dealsandoffers/deals_list.html', {'deals': deals})
