from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout
from django.utils import timezone
import django
import json
import string
import random
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from admin.models import AuthUser, Account, RecoverToken
from django.http import HttpResponse
from django.core.mail import send_mail
from datetime import datetime, timedelta
# Create your views here.
@login_required
def index(request):
    # return render(request, 'index.html')
    # for now
    return redirect('demand_optimization')


def auth_login(request):
    if request.user.is_authenticated():
        return redirect('index')

    data = {}
    if request.method == 'POST':
        if request.POST.get('email') and request.POST.get('password'):
            data['email'] = request.POST['email']
            data['password'] = request.POST['password']
            user = authenticate(username=request.POST['email'],
                                password=request.POST['password'])
            if user is not None:
                django.contrib.auth.login(request, user)
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('index')
            else:
                data['login_failed'] = True

    # remember_me = Settings.SESSION_EXPIRES_AT_BROWSER_CLOSE
    return render(request, 'login.html', data)


def auth_logout(request):
    logout(request)
    return redirect('auth_login')


@login_required()
def admin_users(request):
    if request.user.type != 'admin':
        return redirect('index')
    return render(request, 'users.html', {'users': AuthUser.objects.all()})

@login_required()
def admin_edit_user(request):
    if request.user.type != 'admin':
        return redirect('index')

    user_id = int(request.GET.get('id', '-1') or -1)
    try:
        user = AuthUser.objects.get(pk=user_id)
    except:
        user = {}

    try:
        if request.POST:
            valid_fields = ['first_name', 'last_name', 'email', 'password', 'type']
            _post = {}
            for f in valid_fields:
                _post[f] = request.POST.get(f)
            if not user:
                user = _post
                AuthUser.objects.create_user(**_post)
                messages.success(request, 'Successfully added.')
                return redirect('admin_users')
            else:
                if request.POST.get('delete') == 'true':
                    user.delete()
                    messages.success(request, "Successfully deleted.")
                    return redirect('admin_users')

                for key in valid_fields:
                    if key != 'password':
                        setattr(user, key, _post[key])

                if _post['password']:
                    user.set_password(_post['password'])

                user.save()
                messages.success(request, "Successfully updated.")
    except Exception as e:
        messages.error(request, str(e))

    return render(request, 'edit_user.html', {'user': user})

@login_required
def admin_assign_advertisers(request):
    if request.user.type != 'admin':
        return redirect('index')
    if request.POST.get('data'):
        data = json.loads(request.POST.get('data'))
        for _id, val in data.iteritems():
            a = Account.objects.get(id=_id)
            if a:
                a.user_id = val
                a.save()

    return render(request, 'assign_accounts.html', {'accounts':
                                                           Account.objects.filter(type='advertiser').exclude(internal_id=None).all(),
                                                       'users': AuthUser.objects.all(), 'type': 'Advertiser'})

@login_required
def admin_assign_publishers(request):
    if request.user.type != 'admin':
        return redirect('index')
    if request.POST.get('data'):
        data = json.loads(request.POST.get('data'))
        for _id, val in data.iteritems():
            a = Account.objects.get(id=_id)
            if a:
                a.user_id = val
                a.save()

    return render(request, 'assign_accounts.html', {'accounts':
                                                           Account.objects.filter(type='publisher').exclude(internal_id=None).all(),
                                                       'users': AuthUser.objects.all(), 'type': 'Publisher'})

@csrf_exempt
def reset_password(request):
    if request.GET.get('token'):
        rt = RecoverToken.objects.filter(token=request.GET['token']).first()
        if rt:
            if rt.date_created > (timezone.now() - timedelta(days=1)):
                if request.POST.get('new_password') and request.POST.get('confirm_password'):
                    p1 = request.POST.get('new_password')
                    p2 = request.POST.get('confirm_password')
                    if p1 == p2:
                        rt.user.set_password(p1)
                        rt.user.save()
                        rt.delete()
                        messages.success(request, "Your password was reset successfully.")
                        return redirect('auth_login')
                    else:
                        messages.error(request, "Passwords are not matching. Please try again.")
                return render(request, 'reset_password.html')

        messages.error(request, "Invalid url!")
        return redirect('auth_login')

    else:
        return redirect('auth_login')

@csrf_exempt
def api_recover_password(request):
    email = request.POST.get('email')
    user = AuthUser.objects.filter(email=email).first()
    if not user:
        return HttpResponse(json.dumps({'success': False, 'msg': 'There is no user by that email.'}),
                            content_type='application/json')
    else:
        token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(64))
        link = request.build_absolute_uri("%s?token=%s" % (reverse(reset_password), token))
        msg = """
            Please click following link to reset your password.
            %s

            Please be aware that above link is valid only 24 hours and if you reset password through that link, it is not working anymore.
        """ % link
        try:
            send_mail("Reset Password", msg, "Manage.com<info@manage.com>", [email], fail_silently=False)
            row = RecoverToken(user_id=user.id, token=token)
            row.save()
            return HttpResponse(json.dumps({'success': True,
                                            'msg': 'Reset Password email was sent. Please check your mailbox.'}),
                                content_type='application/json')
        except:
            return HttpResponse(json.dumps({'success': False, 'msg': 'There was a problem while sending email.'}),
                            content_type='application/json')