from datetime import date, timedelta
import json
import csv

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Max, Min
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from models import dictfetchall
from sales.models import *
from admin.models import *
from dashboard.settings import REGIONAL_DATA, PAGE_SIZE, EMAIL_HOST_PASSWORD
from django.db import connection
import MySQLdb
import re


# Create your views here.

regions = REGIONAL_DATA.keys()

@login_required
def api_update_budget(request):
    filters = {
        'traffic': request.GET.get('traffic'),
        'campaign_id': request.GET.get('campaign')
    }

    country = request.GET.get('country')
    not_regional = request.GET.get('regional')
    _val = request.GET.get('val')
    res = []
    if not not_regional:
        if country != 'All':
            filters['country__in'] = REGIONAL_DATA[country]
        stats = StatAdvertiserBase.objects.filter(**filters).order_by('type')
        _sorted = {}
        _types = []
        for s in stats:
            _type = s.type
            if not _sorted.get(_type):
                _sorted[_type] = []
                _types.append(_type)
            _sorted[_type].append(s)

        _val = int(_val or 0)
        for _type, _rows in _sorted.iteritems():
            each_val = int(_val / len(_rows))
            for row in _rows:
                res.append({'id': row.id, 'val': each_val})
                row.budget = each_val
                row.save()

    else:
        filters['country'] = country
        stats = StatAdvertiserBase.objects.filter(**filters).all()

        for s in stats:
            res.append({'id': s.id, 'val': _val})
            s.budget = _val
            s.save()

    return HttpResponse(json.dumps(res), content_type='application/json')

@login_required
def api_update_avail(request):
    _id = request.GET.get('id')
    _ids = request.GET.get('ids')
    _val = request.GET.get('val')
    if _id:
        stat = StatPublisherBase.objects.get(id=_id)
        if stat:
            stat.impression_avail = _val
            stat.save()

    if _ids:
        stats = StatPublisherBase.objects.filter(id__in=_ids.split(',')).all()
        for s in stats:
            s.impression_avail = _val
            s.save()

    return HttpResponse(json.dumps({'status': 'success'}), content_type='application/json')


@login_required
def api_campaign_search(request):
    term = request.GET.get('term')
    campaigns = Campaign.objects.filter(campaign__iregex=r'^%s.*' % term)
    res = []
    for c in campaigns:
        res.append({
            'id': c.campaign_id,
            'text': c.campaign,
            'slug': c.campaign
        })
    return HttpResponse(json.dumps(res), content_type='application/json')

@login_required
def api_advertiser_search(request):
    term = request.GET.get('term')
    accounts = Account.objects.filter(advertiser__iregex=r'^%s.*' % term)
    res = []
    for a in accounts:
        res.append({
            'id': a.advertiser_id,
            'text': a.advertiser,
            'slug': a.advertiser
        })
    return HttpResponse(json.dumps(res), content_type='application/json')

@login_required
@csrf_exempt
def tools_api_mail(request):
    import mandrill
    try:
        to_emails = request.POST['to'].split(',')
        if len(to_emails) > 0:
            mc = mandrill.Mandrill(EMAIL_HOST_PASSWORD)
            msg = {
                'auto_html': True,
                'text': request.POST['message'],
                'preserve_recipients': True,
                'subject': request.POST['subject']
            }
            msg['to'] = []
            msg['to'].append({'email': to_emails[0], 'type': 'to'})
            del to_emails[0]
            for email in to_emails:
                msg['to'].append({'email': email, 'type': 'cc'})
            match = re.match(r'(.*) <(.*)>', request.POST['from'])
            msg['from_email'] = match.group(2)
            msg['from_name'] = match.group(1)
            mc.messages.send(message=msg, async=False)

        return HttpResponse(json.dumps({'status': 'success'}), content_type='application/json')
    except Exception as e:
        print str(e)
        return HttpResponse(json.dumps({'status': 'error'}), content_type='application/json')

def _demand_optimization(request):
    def __get_max_date():
        st = StatAdvertiser.objects.filter(date__lte=date.today().strftime('%Y-%m-%d')).aggregate(date=Max('date'))
        if st:
            return st['date'].strftime('%Y-%m-%d')

        return date.today().strftime('%Y-%m-%d')

    params = {
        'campaign': MySQLdb.escape_string(request.GET.get('campaign', '')),
        'advertiser': MySQLdb.escape_string(request.GET.get('advertiser', '')),
        'user': int(request.GET.get('user', request.user.id if request.user.type == 'regular' else '') or 0),
        'region': MySQLdb.escape_string(request.GET.get('region', '')),
        'os': MySQLdb.escape_string(request.GET.get('os', '')),
        'genre': MySQLdb.escape_string(request.GET.get('genre', '')),
        'traffic': MySQLdb.escape_string(request.GET.get('traffic', '')),
        'type': MySQLdb.escape_string(request.GET.get('type', '')),
        'date': MySQLdb.escape_string(request.GET.get('date', __get_max_date())),
        'sort': MySQLdb.escape_string(request.GET.get('sort', '-revenue')),
        'budget__gte': int(request.GET.get('budget__gte') or 0),
        'revenue__gte': int(request.GET.get('revenue__gte') or 0),
        'export': MySQLdb.escape_string(request.GET.get('export', '')),
        'expand': request.GET.get('expand')
    }

    join_claueses = {}
    join_claueses['campaign'] = (" AND c.campaign_id = %s " % params['campaign']) if params['campaign'] else ''
    join_claueses['advertiser'] = (" AND c.advertiser_id = %s " % params['advertiser']) if params['advertiser'] \
        else ''
    join_claueses['user'] = (" AND a.user_id = %s " % params['user']) if params['user'] else ''
    join_claueses['campaign'] += (" AND c.os = '%s' " % params['os']) if params['os'] else ''
    join_claueses['genre'] = (" AND g.id=%s" % params['genre']) if params['genre'] else ''

    where = ["b.active=true"]
    if params['type']:
        where.append("b.type = '%s'" % params['type'])
    if params['traffic']:
        where.append("b.traffic='%s'" % params['traffic'])
    if params['budget__gte']:
        where.append("budget>=%s" % params['budget__gte'])
    if params['region']:
        where.append("b.country in ( %s )" % (','.join("'%s'" % cty for cty in REGIONAL_DATA[params['region']])))
    having = []
    if params['revenue__gte']:
        having.append("SUM(revenue)>=%s" % params['revenue__gte'])

    if params['budget__gte']:
        having.append("SUM(budget)>=%s" % params['budget__gte'])

    limit_clause = ''

    cursor = connection.cursor()
    if not params['export']:
        sql = """select count(*) from (select b.campaign_id, b.traffic, b.type from stats_advertiser_base b
                             left join stats_advertiser s on b.id=s.base_id and date='%s'
                             join campaigns c on c.campaign_id = b.campaign_id %s
                             join genre g on g.id = c.genre_id %s
                             join accounts a on a.internal_id = c.advertiser_id and a.type = 'advertiser' %s
                             join sales_authuser u on u.id = a.user_id %s
                              %s
                             group by b.campaign_id, traffic, b.type %s) sub""" % (params['date'], join_claueses['campaign'], join_claueses['genre'],
             join_claueses['advertiser'], join_claueses['user'], (("WHERE " + " AND ".join(where))
                                                                  if len(where) else ''),
             (("HAVING " + " AND ".join(having)) if len(having) else ''))
        cursor.execute(sql)
        total_count = cursor.fetchone()[0]
        if total_count:
            paginator = Paginator(range(0, total_count), PAGE_SIZE)
            page = int(request.GET.get('page') or 1)
            try:
                _range = paginator.page(page)
            except PageNotAnInteger:
                _range = paginator.page(1)
                page = 1
            except EmptyPage:
                _range = paginator.page(paginator.num_pages)
                page = paginator.num_pages

            params['pagination'] = {
                'count': paginator.num_pages,
                'current': page
            }

            limit_clause = "limit %d, %d" % (_range[0], PAGE_SIZE)


    additional_fields = ''
    order_by_clause = ''
    if params['sort']:
        desc = '-' in params['sort']
        field = params['sort'].replace('-', '')
        if not 'status' in params['sort']:
            order_by_clause = 'ORDER BY %s %s' % (field, 'DESC' if desc else '')
        else:
            additional_fields = ',MIN(COALESCE(campaign_status,0)) all_on, SUM(COALESCE(campaign_status,0)) all_count'
            if not '-' in params['sort']:
                order_by_clause = 'ORDER BY all_on desc, all_count desc'
            else:
                order_by_clause = 'ORDER BY all_on,all_count'

    sql = """select b.campaign_id, c.advertiser_id, campaign, traffic, b.type, c.os, g.genre_name, c.genre_id,
                             SUM(COALESCE(budget, 0)) as budget, SUM(COALESCE(revenue, 0)) as revenue,
                             u.first_name, u.last_name,
                             a.name as advertiser %s from stats_advertiser_base b
                             left join stats_advertiser s on b.id=s.base_id and date='%s'
                             join campaigns c on c.campaign_id = b.campaign_id %s
                             join genre g on g.id = c.genre_id %s
                             join accounts a on a.internal_id = c.advertiser_id and a.type = 'advertiser' %s
                             join sales_authuser u on u.id = a.user_id %s
                              %s
                             group by b.campaign_id, traffic, b.type %s %s %s """ \
          % (additional_fields, params['date'], join_claueses['campaign'], join_claueses['genre'],
             join_claueses['advertiser'], join_claueses['user'], (("WHERE " + " AND ".join(where))
                                                                  if len(where) else ''),
             (("HAVING " + " AND ".join(having)) if len(having) else ''), order_by_clause, limit_clause)

    cursor.execute(sql)
    stats = dictfetchall(cursor)
    stats_res = []
    def append_stat(_stat, region=''):
        new_row = {}
        new_row.update(_stat)
        new_row['traffic_copy'] = _stat['traffic']
        new_row['campaign_copy'] = _stat['campaign']
        new_row['os_copy'] = _stat['os']
        new_row['region'] = region
        _stat['revenue'] = round(_stat['revenue'], 0)
        _stat['budget'] = round(_stat['budget'], 0)
        new_row['percent'] = (_stat['revenue'] / _stat['budget'] * 100) if _stat['budget'] != 0 else 0
        new_row['row_id'] = _stat.get('_id', '')
        stats_res.append(new_row)

    def get_status(_stats):
        all_on = True
        least_on = False
        for stat in _stats:
            all_on = all_on and stat['campaign_status']
            least_on = least_on or stat['campaign_status']

        if all_on:
            return 'on'
        elif least_on:
            return 'limited'
        else:
            return 'off'

    index = 1


    for stat in stats:
        current_row = {}
        current_row.update(stat)
        _where = []
        _where.extend(where)
        _where.append(" b.traffic='%s'" % current_row['traffic'])
        _where.append(" b.type='%s'" % current_row['type'])
        _where.append(" b.campaign_id=%s" % current_row['campaign_id'])
        sql = """select b.country, s.campaign_status, COALESCE(s.revenue, 0) as revenue, b.budget, b.id,
                             a.name as advertiser, campaign_status from stats_advertiser_base b
                             left join stats_advertiser s on b.id=s.base_id and date='%s'
                             join campaigns c on c.campaign_id = b.campaign_id %s
                             join genre g on g.id = c.genre_id %s
                             join accounts a on a.internal_id = c.advertiser_id and a.type = 'advertiser' %s
                             join sales_authuser u on u.id = a.user_id %s
                             WHERE %s""" % (params['date'], join_claueses['campaign'], join_claueses['genre'],
                              join_claueses['advertiser'], join_claueses['user'],  " AND ".join(_where))
        cursor.execute(sql)
        sub_stats=dictfetchall(cursor)
        current_row['country'] = params['region'] if params['region'] else 'All'
        current_row['campaign_status'] = get_status(sub_stats)
        current_row['id'] = index
        current_row['parent'] = False
        current_row['_id'] = ''
        current_row['child_ids'] = ','.join([str(s['id']) for s in sub_stats])
        append_stat(current_row, params['region'])
        current_row['child_ids'] = ''

        all_parent = {}
        all_parent.update(current_row)

        if not params['region']:
            for r in regions:
                regions_rows = []
                budget = 0
                revenue = 0
                #get and append regional rows
                for s in sub_stats:
                    if s['country'] in REGIONAL_DATA[r]:
                        regions_rows.append(s)
                        budget += s['budget']
                        revenue += s['revenue']

                if regions_rows:
                    index += 1
                    current_row['country'] = r
                    current_row['revenue'] = revenue
                    current_row['budget'] = budget
                    current_row['campaign_status'] = get_status(regions_rows)
                    current_row['id'] = index
                    current_row['parent'] = all_parent['id']
                    current_row['_id'] = ''
                    current_row['child_ids'] = ','.join([str(s['id']) for s in regions_rows])
                    append_stat(current_row, r)
                    current_row['child_ids'] = ''
                    #append country level rows
                    sub_parent = {}
                    sub_parent.update(current_row)
                    for s in regions_rows:
                        index += 1
                        current_row['country'] = s['country']
                        current_row['revenue'] = s['revenue']
                        current_row['budget'] = s['budget']
                        current_row['campaign_status'] = 'on' if s['campaign_status'] else 'off'
                        current_row['id'] = index
                        current_row['parent'] = sub_parent['id']
                        current_row['_id'] = s['id']

                        append_stat(current_row)
        else:
            for s in sub_stats:
                index += 1
                current_row['country'] = s['country']
                current_row['revenue'] = s['revenue']
                current_row['budget'] = s['budget']
                current_row['campaign_status'] = 'on' if s['campaign_status'] else 'off'
                current_row['_id'] = s['id']
                current_row['id'] = index
                current_row['parent'] = all_parent['id']
                append_stat(current_row)

        index += 1

    prev_row = {}
    stat_common_fields = [
        'advertiser', 'campaign',
        'first_name', 'last_name',
        'os', 'genre_name', 'traffic', 'type']

    for _stat in stats_res:
        flag = True
        origin = {}
        origin.update(_stat)
        for f in stat_common_fields:
            if flag and prev_row.get(f) == _stat.get(f):
                _stat[f] = ''
            else:
                flag = False

        prev_row.update(origin)

    res = {
        'params': params,
        'rows': stats_res
    }

    return res


@login_required
def demand_optimization(request):
    res = _demand_optimization(request)

    params = res['params']

    if params['export']:
        return demand_optimization_csv(res['rows'])

    params['today'] = date.today().strftime('%Y-%m-%d')
    params['day1'] = (date.today()+timedelta(days=-1)).strftime('%Y-%m-%d')
    params['day2'] = (date.today()+timedelta(days=-2)).strftime('%Y-%m-%d')
    params['day3'] = (date.today()+timedelta(days=-3)).strftime('%Y-%m-%d')
    params['day7'] = (date.today()+timedelta(days=-7)).strftime('%Y-%m-%d')
    params['day30'] = (date.today()+timedelta(days=-30)).strftime('%Y-%m-%d')

    headings = [
        {'id': 'advertiser', 'name': 'Advertiser', 'sort': '', 'sortable': True},
        {'id': 'campaign', 'name': 'Campaign', 'sort': '', 'sortable': True},
        {'id': 'first_name', 'name': 'AM', 'order': '', 'sortable': True},
        {'id': 'os', 'name': 'OS', 'sort': '', 'sortable': True},
        {'id': 'genre_name', 'name': 'Genre', 'sort': '', 'sortable': True},
        {'id': 'traffic', 'name': 'traffic', 'sort': '', 'sortable': True},
        {'id': 'type', 'name': 'type', 'sort': '', 'sortable': True},
        {'id': '', 'name': 'Country', 'sortable': False},
        {'id': 'status', 'name': 'Status', 'sort': '', 'sortable': True},
        {'id': 'budget', 'name': 'Daily Budget', 'sort': '', 'sortable': True},
        {'id': 'revenue', 'name': 'Revenue Prev Day', 'sort': '', 'sortable': True},
        {'id': '', 'name': 'Tools', 'sortable': False},
    ]
    if params['sort']:
        for h in headings:
            if h['id'] in params['sort']:
                if '-' in params['sort']:
                    h['sort'] = 'desc'
                else:
                    h['sort'] = 'asc'
    advertisers = Account.objects.filter(type='advertiser').all()
    user_advertisers_json = {}
    for a in advertisers:
        key = str(a.user_id)
        if not user_advertisers_json.get(key):
            user_advertisers_json[key] = str(a.internal_id)

    return render(request, 'demand_optimization.html', {'users': AuthUser.objects.all, 'params': params,
                                                           'advertisers': advertisers,
                                                           'campaigns': Campaign.objects.values('campaign_id',
                                                                                                'campaign').all(),
                                                           'stats': res['rows'], 'headings': headings,
                                                           'regions': regions, 'genres': Genre.objects.all,
                                                           'ua_json': json.dumps(user_advertisers_json)})

def demand_optimization_csv(rows):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Demand Optimization Report.csv"'
    response['Content-Type'] = 'text/csv'
    writer = csv.writer(response)
    writer.writerow(['Advertiser', 'Campaign', 'AM', 'OS', 'Genre', 'traffic', 'type', 'Country', 'Status',
                     'Daily Budget', 'Revenue Prev Day'])

    for r in rows:
        _name = ''
        if r['first_name'] and r['last_name']:
            _name = ''.join([r['first_name'], '.',
                             r['last_name'][0]])

        writer.writerow([
            r['advertiser'],
            r['campaign'],
            _name,
            r['os'],
            r['genre_name'],
            r['traffic'],
            r['type'],
            r['country'],
            r['campaign_status'],
            r['budget'],
            r['revenue']
        ])

    return response


def _supply_optimization(request):
    def __get_max_date():
        st = StatPublisher.objects.filter(date__lte=date.today().strftime('%Y-%m-%d')).aggregate(date=Max('date'))
        if st:
            return st['date'].strftime('%Y-%m-%d')

        return date.today().strftime('%Y-%m-%d')

    params = {
        'user': int(request.GET.get('user', request.user.id if request.user.type == 'regular' else '') or 0),
        'publisher': request.GET.get('publisher', ''),
        'app': request.GET.get('app', ''),
        'region': request.GET.get('region', ''),
        'os': request.GET.get('os', ''),
        'publisher_genre': request.GET.get('publisher_genre', ''),
        'advertiser_genre': request.GET.get('advertiser_genre', ''),
        #'type': request.GET.get('type', ''),
        'impression_avail': int(request.GET.get('impression_avail', '') or 0),
        'impression': int(request.GET.get('impression', '') or 0),
        'revenue': int(request.GET.get('revenue', '') or 0),
        'date': request.GET.get('date', __get_max_date()),
        'sort': request.GET.get('sort', '-revenue'),
        'export': request.GET.get('export', ''),
        'expand': request.GET.get('expand'),
    }

    join_claueses = {}
    join_claueses['user'] = (" AND a.user_id = %s " % params['user']) if params['user'] else ''
    join_claueses['advertiser_genre'] = (" AND ag.id=%s" % params['advertiser_genre']) if params['advertiser_genre'] else ''
    join_claueses['publisher_genre'] = (" AND pg.id=%s" % params['publisher_genre']) if params['publisher_genre'] else ''
    join_claueses['account'] = (" AND a.internal_id=%s " % params['publisher']) if params['publisher'] else ''

    where = ["b.active=true"]
    #if params['type']:
    #    where.append("b.type = '%s'" % params['type'])
    if params['region']:
        where.append("b.country in ( %s )" % (','.join("'%s'" % cty for cty in REGIONAL_DATA[params['region']])))
    if params['app']:
        where.append("b.app_id = %s" % params['app'])
    if params['os']:
        where.append("app.os = '%s'" % params['os'])

    having = []
    if params['impression_avail']:
        having.append("SUM(COALESCE(b.impression_avail,0)) >= %s" % params['impression_avail'])
    if params['impression']:
        having.append("SUM(COALESCE(s.impression,0)) >= %s" % params['impression'])
    if params['revenue']:
        having.append("SUM(COALESCE(s.revenue,0)) >= %s" % params['revenue'])
    having_clause = ''
    if len(having):
        having_clause = "HAVING %s" % " AND ".join(having)

    limit_clause = ''
    cursor = connection.cursor()
    if not params['export']:
        sql = """ select count(*) from (select b.app_id, b.publisher_genre_id, b.advertiser_genre_id from stats_publisher_base b
                                          left join stats_publisher s on b.id=s.base_id and date='%s'
                                          join am.app app on app.app_id = b.app_id
                                          join genre ag on ag.id=b.advertiser_genre_id %s
                                          join genre pg on pg.id=b.publisher_genre_id %s
                                          join accounts a on a.internal_id = b.publisher_id and a.type='publisher' %s
                                          join sales_authuser u on u.id = a.user_id %s
                                          WHERE %s
                                          group by b.app_id, b.publisher_genre_id, b.advertiser_genre_id %s) sub """ \
              % (params['date'], join_claueses['advertiser_genre'], join_claueses['publisher_genre'],
                  join_claueses['account'], join_claueses['user'], ' AND '.join(where), having_clause)
        cursor.execute(sql)
        total_count = cursor.fetchone()[0]
        if total_count:
            paginator = Paginator(range(0, total_count), PAGE_SIZE)
            page = int(request.GET.get('page') or 1)
            try:
                _range = paginator.page(page)
            except PageNotAnInteger:
                _range = paginator.page(1)
                page = 1
            except EmptyPage:
                _range = paginator.page(paginator.num_pages)
                page = paginator.num_pages

            params['pagination'] = {
                'count': paginator.num_pages,
                'current': page
            }

            limit_clause = "limit %d, %d" % (_range[0], PAGE_SIZE)

    order_by_clause = ''
    additional_fields = ''
    if params['sort']:
        desc = '-' in params['sort']
        field = params['sort'].replace('-', '')
        if not 'status' in params['sort']:
            order_by_clause = 'ORDER BY %s %s' % (field, 'DESC' if desc else '')
        else:
            additional_fields = ',MIN(COALESCE(s.status,0)) all_on, SUM(COALESCE(s.status,0)) all_count'
            if not '-' in params['sort']:
                order_by_clause = 'ORDER BY all_on desc, all_count desc'
            else:
                order_by_clause = 'ORDER BY all_on,all_count'

    sql = """select a.name as publisher, b.publisher_id, b.app_id, b.publisher_genre_id, b.advertiser_genre_id, app.app as app_name,
                    u.first_name, u.last_name, app.os, pg.genre_name as publisher_genre,
                    ag.genre_name as advertiser_genre, SUM(COALESCE(b.impression_avail, 0)) as impression_avail,
                    SUM(COALESCE(s.impression, 0)) as impressions, SUM(COALESCE(s.revenue, 0)) as revenue,
                    SUM(COALESCE(s.margin, 0)) as margin %s from stats_publisher_base b
                                          left join stats_publisher s on b.id=s.base_id and date='%s'
                                          join am.app app on app.app_id = b.app_id
                                          join genre ag on ag.id=b.advertiser_genre_id %s
                                          join genre pg on pg.id=b.publisher_genre_id %s
                                          join accounts a on a.internal_id = b.publisher_id and a.type='publisher' %s
                                          join sales_authuser u on u.id = a.user_id %s
                                          WHERE %s
                                          group by b.app_id, b.publisher_genre_id, b.advertiser_genre_id
                                          %s %s %s""" % (additional_fields, params['date'], join_claueses['advertiser_genre'],
    join_claueses['publisher_genre'], join_claueses['account'], join_claueses['user'], " AND ".join(where),
    having_clause, order_by_clause, limit_clause)
    cursor.execute(sql)
    stats = dictfetchall(cursor)

    stats_res = []

    def append_stat(_stat, region = ''):
        new_row = {}
        new_row.update(_stat)
        if region:
            new_row['region'] = region
        new_row['origin_os'] = _stat['os']
        new_row['origin_app_name'] = _stat['app_name']
        new_row['origin_publisher'] = _stat['publisher']
        new_row['origin_publisher_genre'] = _stat['publisher_genre']
        new_row['origin_advertiser_genre'] = _stat['advertiser_genre']
        new_row['percent'] = (_stat['revenue'] / _stat['margin'] * 100) if _stat['margin'] != 0 else 0
        new_row['row_id'] = _stat.get('_id', '')
        stats_res.append(new_row)

    def get_status(_stats):
        all_on = True
        least_on = False
        for stat in _stats:
            all_on = all_on and stat['status']
            least_on = least_on or stat['status']

        if all_on:
            return 'on'
        elif least_on:
            return 'limited'
        else:
            return 'off'

    index = 1

    for stat in stats:
        current_row = {}
        current_row.update(stat)
        _where = []
        _where.extend(where)
        _where.append(" b.app_id=%s" % current_row['app_id'])
        #_where.append(" b.app_name='%s'" % current_row['app_name'])
        #_where.append(" b.os = '%s'" % current_row['os'])
        _where.append(" b.publisher_genre_id=%s" % current_row['publisher_genre_id'])
        _where.append(" b.advertiser_genre_id=%s" % current_row['advertiser_genre_id'])
        #_where.append(" b.type='%s'" % current_row['type'])


        sql = """select b.id, b.country, s.status, b.impression_avail, COALESCE(s.impression,0) as impressions,
                  COALESCE(s.revenue,0) as revenue, COALESCE(s.margin,0) as margin from stats_publisher_base b
                                          left join stats_publisher s on b.id=s.base_id and date='%s'
                                          join am.app app on app.app_id = b.app_id
                                          join genre ag on ag.id=b.advertiser_genre_id %s
                                          join genre pg on pg.id=b.publisher_genre_id %s
                                          join accounts a on a.internal_id = b.publisher_id and a.type='publisher' %s
                                          join sales_authuser u on u.id = a.user_id %s
                                          WHERE %s """ % (params['date'], join_claueses['advertiser_genre'],
                                                   join_claueses['publisher_genre'], join_claueses['account'],
                                                   join_claueses['user'], " AND ".join(_where))
        cursor.execute(sql)
        sub_stats = dictfetchall(cursor)
        current_row['country'] = params['region'] if params['region'] else 'All'
        current_row['status'] = get_status(sub_stats)
        current_row['id'] = index
        current_row['parent'] = False
        current_row['_id'] = ''
        current_row['child_ids'] = ','.join([str(s['id']) for s in sub_stats])
        append_stat(current_row, params['region'])
        current_row['child_ids'] = ''
        all_parent = {}
        all_parent.update(current_row)

        if not params['region']:
            for r in regions:
                regions_rows = []
                revenue = 0
                margin = 0
                impression_avail = 0
                impressions = 0
                #get and append regional rows
                for s in sub_stats:
                    if s['country'] in REGIONAL_DATA[r]:
                        regions_rows.append(s)
                        revenue += s['revenue']
                        margin += s['margin']
                        impression_avail += s['impression_avail']
                        impressions += s['impressions']

                if regions_rows:
                    index += 1
                    current_row['country'] = r
                    current_row['revenue'] = revenue
                    current_row['margin'] = margin
                    current_row['impression_avail'] = impression_avail
                    current_row['impressions'] = impressions
                    current_row['status'] = get_status(regions_rows)
                    current_row['id'] = index
                    current_row['parent'] = all_parent['id']
                    current_row['_id'] = ''
                    current_row['child_ids'] = ','.join([str(s['id']) for s in regions_rows])
                    append_stat(current_row, r)
                    current_row['child_ids'] = ''
                    #append country level rows
                    sub_parent = {}
                    sub_parent.update(current_row)
                    for s in regions_rows:
                        index += 1
                        current_row['country'] = s['country']
                        current_row['revenue'] = s['revenue']
                        current_row['margin'] = s['margin']
                        current_row['impression_avail'] = s['impression_avail']
                        current_row['impressions'] = s['impressions']
                        current_row['status'] = 'on' if s['status'] else 'off'
                        current_row['id'] = index
                        current_row['parent'] = sub_parent['id']
                        current_row['_id'] = s['id']
                        append_stat(current_row)
        else:
            for s in sub_stats:
                index += 1
                current_row['country'] = s['country']
                current_row['revenue'] = s['revenue']
                current_row['margin'] = s['margin']
                current_row['impression_avail'] = s['impression_avail']
                current_row['impressions'] = s['impressions']
                current_row['status'] = 'on' if s['status'] else 'off'
                current_row['_id'] = s['id']
                current_row['id'] = index
                current_row['parent'] = all_parent['id']
                append_stat(current_row)
        index += 1

    prev_row = {}
    stat_common_fields = [
        'publisher', 'app_name', 'first_name', 'last_name', 'os', 'publisher_genre', 'advertiser_genre']

    for _stat in stats_res:
        flag = True
        origin = {}
        origin.update(_stat)
        for f in stat_common_fields:
            if flag and prev_row.get(f) == _stat.get(f):
                _stat[f] = ''
            else:
                flag = False

        prev_row.update(origin)

    res = {
        'params': params,
        'rows': stats_res
    }

    return res


def supply_optimization_csv(rows):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="traffic-campaign.csv"'
    response['Content-Type'] = 'text/csv'
    writer = csv.writer(response)
    writer.writerow(['Publisher', 'App / Placement', 'AM', 'OS', 'Publisher Genre', 'Advertiser Genre', 'Type',
                     'Country', 'Status', 'Daily Avails', 'Prev Day Filled', 'Revenue Prev Day', 'Margin Prev Day'])

    for r in rows:
        _name = ''
        if r['first_name'] and r['last_name']:
            _name = ''.join([r['first_name'], '.',
                             r['last_name'][0]])

        writer.writerow([
            r['publisher'],
            r['app_name'],
            _name,
            r['os'],
            r['publisher_genre'],
            r['advertiser_genre'],
            #r['type'],
            r['country'],
            r['status'],
            r['impression_avail'],
            r['impressions'],
            r['revenue'],
            r['margin']
        ])

    return response

@login_required
def supply_optimization(request):
    res = _supply_optimization(request)

    params = res['params']
    if params['export']:
        return supply_optimization_csv(res['rows'])

    params['today'] = date.today().strftime('%Y-%m-%d')
    params['day1'] = (date.today()+timedelta(days=-1)).strftime('%Y-%m-%d')
    params['day2'] = (date.today()+timedelta(days=-2)).strftime('%Y-%m-%d')
    params['day3'] = (date.today()+timedelta(days=-3)).strftime('%Y-%m-%d')
    params['day7'] = (date.today()+timedelta(days=-7)).strftime('%Y-%m-%d')
    params['day30'] = (date.today()+timedelta(days=-30)).strftime('%Y-%m-%d')

    headings = [
        {'id': 'a.name', 'name': 'Publisher', 'sort': '', 'sortable': True},
        {'id': 'app_name', 'name': 'App / Placement', 'sort': '', 'sortable': True},
        {'id': 'first_name', 'name': 'AM', 'order': '', 'sortable': True},
        {'id': 'os', 'name': 'OS', 'sort': '', 'sortable': True},
        {'id': 'pg.genre_name', 'name': 'Publisher Genre', 'sort': '', 'sortable': True},
        {'id': 'ag.genre_name', 'name': 'Advertiser Genre', 'sort': '', 'sortable': True},
        #{'id': 'b.type', 'name': 'Type', 'sort': '', 'sortable': True},
        {'id': '', 'name': 'Country', 'sortable': False},
        {'id': 'status', 'name': 'Status', 'sort': '', 'sortable': True},
        {'id': 'impression_avail', 'name': 'Daily Avails', 'sort': '', 'sortable': True},
        {'id': 'impressions', 'name': 'Prev Day Filled', 'sort': '', 'sortable': True},
        {'id': 'revenue', 'name': 'Revenue Prev Day', 'sort': '', 'sortable': True},
        {'id': 'margin', 'name': 'Margin Prev Day', 'sort': '', 'sortable': True},
        {'id': '', 'name': 'Tools', 'sortable': False},
    ]
    if params['sort']:
        for h in headings:
            if h['id'] in params['sort']:
                if '-' in params['sort']:
                    h['sort'] = 'desc'
                else:
                    h['sort'] = 'asc'
    apps = App.objects.using('am').values('app_id', 'app').distinct().all()
    publishers = Account.objects.filter(type='publisher').all()
    _json = {}
    for p in publishers:
        key = str(p.user_id)
        if not _json.get(key):
            _json[key] = str(p.id)

    return render(request, 'supply_optimization.html', {'users': AuthUser.objects.all, 'params': params,
                                                           'stats': res['rows'], 'headings': headings,
                                                           'regions': regions, 'genres': Genre.objects.all,
                                                           'publishers': publishers,
                                                           'apps': apps, 'up_json': json.dumps(_json)})


