import json, sys, re, hashlib, smtplib, base64, urllib, csv, time


from django.http import *
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.core.context_processors import csrf
from django.core.validators import email_re
from django.db.utils import IntegrityError
from django.utils.http import urlquote_plus

from models import *

p = os.path.abspath(os.path.dirname(__file__))
if(os.path.abspath(p+"/..") not in sys.path):
	sys.path.append(os.path.abspath(p+"/.."))





'''
@author: Anant Bhardwaj
@date: Sep 22, 2013
'''

kLogIn = "SESSION_LOGIN"
kName = "SESSION_NAME"

gold = {}

f = open( p + '/gold/matches.csv', 'rU')
reader = csv.reader(f)
reader.next()
for row in reader:
    gold[row[0]] = row[1]

'''
LOGIN/REGISTER
'''
def login_required(f):
    def wrap(request, *args, **kwargs):
        if kLogIn not in request.session.keys():
        	if(len(args)>0):
        		redirect_url = urlquote_plus("%s/%s" %(args[0], f.__name__))
        	else:
        		redirect_url = "home"
        	return HttpResponseRedirect("login?redirect_url=%s" %(redirect_url))
        return f(request, *args, **kwargs)
    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def login_form(request, redirect_url='', errors=[]):
    c = {'redirect_url':redirect_url, 'errors':errors}
    c.update(csrf(request))
    return render_to_response('login.html', c)


def register_form(request, redirect_url='', errors=[]):
    c = {'redirect_url':redirect_url, 'errors':errors}
    c.update(csrf(request))
    return render_to_response('register.html', c)


def login(request):
    redirect_url = 'home'
    if('redirect_url' in request.GET.keys()):
    	redirect_url = request.GET['redirect_url']
    if request.method == "POST":
    	errors = []
    	if('redirect_url' in request.POST.keys()):
    		redirect_url = request.POST['redirect_url']
        try:
            login_email = request.POST["login_email"].lower()
            login_password = hashlib.sha1(request.POST["login_password"]).hexdigest()
            user = User.objects.get(email=login_email, password=login_password)
            request.session.flush()
            request.session[kLogIn] = user.email
            request.session[kName] = user.f_name
            return HttpResponseRedirect(redirect_url)
        except User.DoesNotExist:
        	try:
        		User.objects.get(email=login_email)
        		errors.append('Wrong password.')
        	except User.DoesNotExist:
        		errors.append("Couldn't locate account with email address: %s" %(login_email))
        	return login_form(request, redirect_url = redirect_url, errors = errors) 
        except:
            errors.append('Login failed.')
            return login_form(request, redirect_url = redirect_url, errors = errors)          
    else:
        return login_form(request, redirect_url)

def register(request):
    redirect_url = 'home'
    if('redirect_url' in request.GET.keys()):
    	redirect_url = request.GET['redirect_url']
    if request.method == "POST":
    	errors = []
        try:
            error = False
            if('redirect_url' in request.POST.keys()):
				redirect_url = request.POST['redirect_url']
            email = request.POST["email"].lower()
            password = request.POST["password"]
            password2 = request.POST["password2"]
            f_name = request.POST["f_name"]
            l_name = request.POST["l_name"]
            if(email_re.match(email.strip()) == None):
            	errors.append("Invalid Email.")
            	error = True
            if(f_name.strip() == ""):
            	errors.append("Empty First Name.")
            	error = True
            if(l_name.strip() == ""):
            	errors.append("Empty Last Name.")
            	error = True
            if(password == ""):
            	errors.append("Empty Password.")
            	error = True
            if(password2 != password):
            	errors.append("Password and Confirm Password don't match.")
            	error = True

            if(error):
            	return register_form(request, redirect_url = redirect_url, errors = errors)
            hashed_password = hashlib.sha1(password).hexdigest()
            user = User(email=email, password=hashed_password, f_name=f_name, l_name=l_name)
            user.save()
            request.session.flush()
            request.session[kLogIn] = user.email
            request.session[kName] = user.f_name
            return HttpResponseRedirect(redirect_url)
        except IntegrityError:
            errors.append("Account already exists. Please Log In.")
            return register_form(request, redirect_url = redirect_url, errors = errors)
        except:
            errors.append("Some error happened while trying to create an account. Please try again.")
            return register_form(request, redirect_url = redirect_url, errors = errors)
    else:
        return register_form(request, redirect_url = redirect_url)


def logout(request):
    request.session.flush()
    if kLogIn in request.session.keys():
    	del request.session[kLogIn]
    if kName in request.session.keys():
    	del request.session[kName]
    return HttpResponseRedirect('home')


def handle_uploaded_file(f, file_name):
    file_path = p + '/user_uploads/' + file_name
    if (os.path.isfile(file_path)):
        os.rename(file_path, file_path + '_' + str(time.time()))

    with open(file_path , 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def scores(request):
    res = []
    scores = Score.objects.all()
    #dir_list = os.listdir(p + '/user_uploads/')
    for score in scores:
        #file_name = re.match('\w+', score.user.email.lower()).group() + '.csv'
        #num_submissions = len([str(f) for f in dir_list if file_name in str(f)])
        f1 = 0.0
        try:
            f1 = 2 * (score.precision * score.recall) / (score.precision + score.recall)
        except:
            pass
        res.append({
            'id': score.user.email,
            'name': score.user.f_name + ' ' + score.user.l_name,
            'precision': score.precision,
            'recall': score.recall,
            'f1': f1,
            'num_submissions': score.tries
        })
    return HttpResponse(json.dumps({'res': res}), mimetype="application/json")


def compute_score(file_name):
    count = 0
    correct_ans = []
    precision = 0.0
    recall = 0.0
    try:
        f = open( p + '/user_uploads/' + file_name, 'rU')
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            count += 1
            try:
                if(gold[row[0]] == row[1]):
                    correct_ans.append(row[0])
            except:
                pass

        precision = float(len(correct_ans)) / count
        recall = float(len(set(correct_ans))) / len(gold.keys())
    except:
        pass
    return [precision, recall]



@login_required
def home(request, errors=[]):
    c = {'name': request.session[kName], 'errors': errors}
    c.update(csrf(request))
    return render_to_response('home.html', c)

@login_required
def upload(request):
    errors = []
    error = False
    try:
        user_name = re.match('\w+', request.session[kLogIn].lower()).group()
        if('result_file' not in request.FILES):
            errors.append('Error: "results_file" missing.')
            error = True
        if('script_file' not in request.FILES):
            errors.append('Error: "script_file" missing.')
            error = True
        if (not error):
            result_file = request.FILES['result_file']
            script_file = request.FILES['script_file']
            handle_uploaded_file(result_file,  user_name + '.csv')
            handle_uploaded_file(script_file,  user_name + '_' + str(script_file) + '_' + str(time.time()))
            user = User.objects.get(email=request.session[kLogIn])
            score = compute_score(user_name + '.csv')
            try:
                user_score = Score.objects.get(user=user)
                user_score.precision = score[0]
                user_score.recall = score[1]
                user_score.tries += 1
                user_score.save()
            except Score.DoesNotExist:
                user_score = Score(user=user, precision=score[0], recall=score[1], tries = 1)
                user_score.save()
            except:
                errors.append('Error: Database error.')
                error = True
    except:
        print sys.exc_info()
        errors.append('Error: unknown error.')
        error = True
    
    if(error):
        return home(request, errors)
    else:
        return HttpResponseRedirect('home')








