import os
import random
import datetime
import argparse
from math import floor
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dashboard.settings")

    from dashboard.settings import REGIONAL_DATA

    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()

    countries = []
    for region in REGIONAL_DATA.iterkeys():
        countries.extend(REGIONAL_DATA[region])
    random.shuffle(countries)

    traffic = ['exchange', 'publisher']
    type = ['banners', 'video']
    campaign_status = [True, False]
    budget = [500, 1000, 1500, 2000]
    revenue = [30, 50, 100, 500, 1200, 1800, 2300]
    margin = [10, 20, 100, 150, 350, 550, 650, 1200]
    base = datetime.datetime.today()
    date_list = [base - datetime.timedelta(days=x) for x in range(-2, 3)]
    _oses = ['iOS', 'Android']
    from sales.models import *
    from admin.models import *
    from django.db.models.aggregates import Max, Min

    def make_users():
        print 'delete users....'
        AuthUser.objects.all().delete()
        print 'making accounts...'
        AuthUser.objects.create_user(email='joe@yahoo.com', first_name='Joe', last_name='Smith', password='password123',
                                     type='regular', id=1)
        AuthUser.objects.create_user(email='jane@yahoo.com', first_name='Jane', last_name='Doe', password='password123',
                                     type='regular', id=2)
        AuthUser.objects.create_user(email='fred@yahoo.com', first_name='Fred', last_name='Hsu', password='password333',
                                     type='admin', id=3)

    def make_accounts():
        print 'delete accounts....'
        Account.objects.all().delete()
        print 'making accounts...'
        accounts = []
        for i in range(1, 5):
            accounts.append(Account(user_id=random.choice([1, 2]), internal_id=i, type='advertiser', name='Advertiser%d' % i))
            accounts.append(Account(user_id=random.choice([1, 2]), internal_id=i, type='publisher', name='Publisher%d' % i))
            accounts.append(Account(user_id=random.choice([1, 2]), internal_id=i, type='trading_desk', name='Trading Desk%d' % i))
        Account.objects.bulk_create(accounts)

    def make_genres():
        print 'delete genres....'
        Genre.objects.all().delete()
        genres = []
        genres.append(Genre(id=0, genre_name='Unknown'))
        genres.append(Genre(id=1, genre_name='Bingo'))
        genres.append(Genre(id=2, genre_name='Slots'))
        genres.append(Genre(id=3, genre_name='Battle Card'))
        genres.append(Genre(id=4, genre_name='Dating'))
        genres.append(Genre(id=5, genre_name='Band'))
        genres.append(Genre(id=6, genre_name='Casual'))
        genres.append(Genre(id=7, genre_name='Hardcore'))
        genres.append(Genre(id=8, genre_name='Hidden Object'))
        genres.append(Genre(id=9, genre_name='Life Style'))
        print 'making genres....'
        Genre.objects.bulk_create(genres)

    def make_campaigns():
        print 'delete campaigns...'
        Campaign.objects.all().delete()
        print 'making campaigns...'
        campaigns = []
        advertiser_ids = []
        accounts = Account.objects.filter(type='advertiser').all()
        for a in accounts:
            print a
            advertiser_ids.append(a.internal_id)

        for i in range(1, 201):
            _name = 'Candy %d' % i
            _os = _oses[i % 2]
            c = Campaign(campaign=_name, os=_os, advertiser_id=random.choice(advertiser_ids),
                         genre_id=random.choice(range(0, 11)))
            campaigns.append(c)
        print 'bulk inserting campaigns....'
        Campaign.objects.bulk_create(campaigns)

    def make_stats_advertiser_base():
        print 'delete advertiser base...'
        StatAdvertiserBase.objects.all().delete()
        max_campaign_id = Campaign.objects.all().aggregate(Max('campaign_id'))['campaign_id__max']
        min_campaign_id = Campaign.objects.all().aggregate(Min('campaign_id'))['campaign_id__min']
        campaign_ids = range(min_campaign_id, max_campaign_id+1)

        for c in countries:
            print 'making advertiser base...'
            sbs = []
            for tf in traffic:
                for ty in type:
                    for camp in campaign_ids:
                        sb = StatAdvertiserBase(country=c, type=ty, traffic=tf, campaign_id=camp, budget=random.choice(budget))
                        sbs.append(sb)
            print 'bulk inserting advertiser base...'
            StatAdvertiserBase.objects.bulk_create(sbs)

    def make_stats_advertisers():
        print 'delete stats advertisers...'
        StatAdvertiser.objects.all().delete()

        max_base_id = StatAdvertiserBase.objects.all().aggregate(Max('id'))['id__max']
        min_base_id = StatAdvertiserBase.objects.all().aggregate(Min('id'))['id__min']
        base_ids = range(min_base_id, max_base_id+1)
        _len = int(len(base_ids) * 0.2)
        for d in date_list:
            stats = []
            print 'making stats advertisers...'
            for base_id in random.sample(base_ids, _len):
                stat = StatAdvertiser(date=d, base_id=base_id, campaign_status=random.choice(campaign_status),
                            revenue=random.choice(revenue), margin=random.choice(margin))
                stats.append(stat)
            print 'bulk inserting stats advertisers...'
            StatAdvertiser.objects.bulk_create(stats)

    def make_stats_publishers():
        print 'delete publisher stats base...'
        StatPublisherBase.objects.all().delete()

        publisher_ids = []
        accounts = Account.objects.filter(type='publisher').all()
        for a in accounts:
            publisher_ids.append(a.internal_id)
        _apps = App.objects.using('am').all()
        app_ids = []
        for a in _apps:
            app_ids.append(a.app_id)

        impressions_avails = [1000, 2000, 3000, 4000, 5000]
        impressions = [500, 1500, 14000, 2000, 3400]

        print 'delete publisher stats...'
        StatPublisher.objects.all().delete()

        print 'making publisher stats base...'
        static_traffics = []
        _countries = random.sample(countries, len(countries))
        for _type in type:
            for app_id in app_ids:
                publisher_id = random.choice(publisher_ids)
                g1 = random.choice(range(0, 11))
                g2 = random.choice(range(0, 11))
                _os = random.choice(_oses)
                for country in _countries:
                    stat = StatPublisherBase(publisher_id=publisher_id, app_id=app_id,
                                             advertiser_genre_id=g1, publisher_genre_id=g2,
                                             country=country,
                                             impression_avail=random.choice(impressions_avails))
                    static_traffics.append(stat)
        print 'bulk inserting publisher stats base...'
        StatPublisherBase.objects.bulk_create(static_traffics)

        print 'delete publisher stats...'
        StatPublisher.objects.all().delete()
        max_base_id = StatPublisherBase.objects.all().aggregate(Max('id'))['id__max']
        min_base_id = StatPublisherBase.objects.all().aggregate(Min('id'))['id__min']
        base_ids = range(min_base_id, max_base_id+1)
        _len = int(len(base_ids) * 0.5)
        for d in date_list:
            stats = []
            print 'making stats publishers...'
            for base_id in random.sample(base_ids, _len):
                stat = StatPublisher(date=d, base_id=base_id, impression=random.choice(impressions),
                                     revenue=random.choice(revenue), margin=random.choice(margin))
                stats.append(stat)
            print 'bulk inserting stats publishers...'
            StatPublisher.objects.bulk_create(stats)

    parser = argparse.ArgumentParser(description='Create Dummy Rows in Tables')
    parser.add_argument('table', help='choose table to migrate(all, stats, campaign, stats_base, stats_traffic)')
    args = parser.parse_args()

    table = args.table

    if table == 'all' or table == 'user':
        make_users()

    if table == 'all' or table == 'genre':
        make_genres()

    if table == 'all' or table == 'account':
        make_accounts()

    if table == 'all' or table == 'campaign':
        make_campaigns()

    if table == 'all' or table == 'advertiser':
        make_stats_advertiser_base()
        make_stats_advertisers()

    if table == 'all' or table == 'publisher':
        make_stats_publishers()