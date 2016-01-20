from datetime import datetime, date, timedelta
from math import ceil
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from isoweek import Week

from sales.models import UserPlan, StatAdvertiser
from dashboard.settings import REGIONAL_DATA
from admin.models import  Account, AuthUser

# Create your views here.

regions = REGIONAL_DATA.keys()

@login_required
def sales_commission(request):
    users = AuthUser.objects.all

    accounts = Account.objects.values('region').distinct()
    groups = Account.objects.values('business_unit').distinct()

    regions = [r['region'] for r in accounts]
    groups = [r['business_unit'] for r in groups]

    m = date.today().month
    c = int(ceil(m / 3.0))

    params = {
        'user': int(request.GET.get('user', request.user.id)),
        'region': request.GET.get('region', 'all'),
        'group': request.GET.get('group', 'all'),
        'start_date': request.GET.get('start_date', date(date.today().year, c * 3 - 2, 1).strftime('%Y-%m-%d')),
        'end_date': request.GET.get('end_date', (date(date.today().year + int((c * 3 + 1) / 12), (c * 3 + 1) % 12, 1) -
                                    timedelta(days=1)).strftime('%Y-%m-%d'))
    }

    res = {}
    res['user_plan'] = UserPlan.objects.filter(user=params['user'], date_start__gte=params['start_date'],
                                               date_end__lte=params['end_date']).first()

    res['stats'] = []

    accounts = Account.objects
    if params['region'] != 'all':
        accounts = accounts.filter(region=params['region'])
    if params['group'] != 'all':
        accounts = accounts.filter(business_unit=params['group'])
    advertiser_ids = []
    for account in accounts.filter(type='advertiser').all():
        advertiser_ids.append(account.advertiser_id)
    stats = StatAdvertiser.objects.filter(date__range=[params['start_date'], params['end_date']],
                                campaign__advertiser_id__in=advertiser_ids)\
        .values('campaign__advertiser__user__first_name', 'campaign__advertiser__user__last_name') \
        .annotate(revenue=Sum('revenue'))

    for stat in stats:
        res['stats'].append({
            'name':
                (stat['campaign__advertiser__user__first_name'].title() + ' ' +
                 stat['campaign__advertiser__user__last_name'][0].title() + '.').encode('ascii', 'ignore'),
            'revenue': stat['revenue']
        })

    res['stats_sum'] = StatAdvertiser.objects.filter(date__range=[params['start_date'],
                                                       params['end_date']],
                                           campaign__advertiser_id__in=advertiser_ids) \
        .aggregate(revenue=Sum('revenue'))

    overall_revenue = Stat.objects.values('campaign__advertiser__business_unit')\
        .filter(date__range=[params['start_date'],params['end_date']], campaign__advertiser_id__in=advertiser_ids)\
        .annotate(revenue=Sum('revenue'))
    for r in overall_revenue:
        r['campaign__advertiser__business_unit'] = r['campaign__advertiser__business_unit'] \
            .encode('ascii', 'ignore')
    res['overall_revenue'] = overall_revenue
    res['overall_revenue_sum'] = StatAdvertiser.objects.filter(date__range=[params['start_date'], params['end_date']],
                                                     campaign__advertiser_id__in=advertiser_ids)\
        .aggregate(revenue=Sum('revenue'))

    commissions = StatAdvertiser.objects.filter(date__range=[params['start_date'], params['end_date']],
                                      campaign__advertiser_id__in=advertiser_ids) \
        .extra({'week': "EXTRACT(week from date)"}).values('week').annotate(revenue=Sum('revenue'),
                                                                           margin=Sum('margin')).order_by('week')

    _year = int(datetime.strptime(params['start_date'], '%Y-%m-%d').strftime('%Y'))
    for c in commissions:
        c['week'] = Week(_year, c['week'] + 1).monday().strftime('%b %-d') + '~' + Week(_year, c['week'] + 1).sunday()\
            .strftime('%b %-d')
    res['commissions'] = commissions

    return render(request, 'commission.html',
                  {'users': users, 'regions': regions, 'groups': groups,
                   'params': params, 'res': res})


