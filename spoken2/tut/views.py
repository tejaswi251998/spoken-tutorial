from django.template import loader
from django.shortcuts import get_object_or_404, render
from .forms import *
from django.contrib import messages
from .models import *
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
import datetime


def log(request):
    print(request)
    if request.method == 'POST':
        print(request.POST)
        errors = None

        #User Sign Up
        try:
            if request.POST['s2'] == 'Sign_Up':
                form = Signupform(request.POST)
                print(form.errors)

                if form.is_valid():
                    pwd = request.POST['password'] #here password is password of user which he entered
                    passw = str(pwd)

                    if len(passw) < 8:
                        error_msg3 = "Minimum length of password is 8. Please sign up again!"
                        messages.error(request, error_msg3)
                        return redirect('/')

                    elif User.objects.filter(username=request.POST.get('username')).exists():
                        error_msg4 = "User already exists! Try a different username..."
                        messages.error(request, error_msg4)
                        return redirect('/')

                    else:
                        user = User(username=request.POST['username'], password=request.POST['password'],
                                    email=request.POST['email']) # creating an object of user with specified data
                        user.set_password(request.POST['password'])
                        user.save()
                        userdetails = Userdetails(user=user, email=request.POST['email'],
                                                  password=request.POST['password'])
                        userdetails.save() #saving the user details into userdetails table in database

                        try:
                            users = User.objects.get(username=request.POST.get('username'))
                        except:
                            error_msg = "Wrong details"
                            messages.error(request, error_msg)
                            return redirect('/')
                        users = authenticate(username=users.username, password=request.POST.get('password'))
                        if users is not None:
                            login(request, users)
                            try:
                                udets = User.objects.filter(username=users.username)# getting details of specified user
                                                                            #  when he is logged in
                            except:
                                error_msg = "Wrong details"
                                messages.error(request, error_msg)
                            return render(request, 'tut/userpage.html', {'udets': udets})#return to userpage
                                                                                        # with user details
                        else:
                            return redirect('/')

                else:
                    form = Signupform()#if form is not valid it gives empty form and returns to sinup page
                    errors = form.errors
                    print(errors)
                    return redirect('/')




            #Admin Sign In
            elif request.POST['s2'] == 'Continue':
                form = Adminform(request.POST)
                print(form.errors)
                if form.is_valid():
                    user1 = request.POST.get('user1')#user1 is username of admin
                    pwd = request.POST.get('pwd')#password of admin

                    if user1 == 'tejaswi' and pwd == '123456789':
                        list1 = Userdetails.objects.all()
                        list2 = Foss.objects.all()
                        errors = None
                        print(request.POST)
                        template = loader.get_template('tut/admin.html')
                        return render(request, 'tut/admin.html', {'list2': list2, 'list1': list1})#redirecting to
                                                                                # admin page eith user,foss details
                    else:
                        error_msg2 = "Wrong Admin Credentials"
                        messages.error(request, error_msg2)
                        return redirect('/')
                else:
                    form = Adminform()
                    return redirect('/')





            #User Log In
            elif request.POST['s2'] == 'Log_In':
                try:
                    users = User.objects.get(username=request.POST.get('user2'))
                except:
                    error_msg = "Wrong details"
                    messages.error(request, error_msg)
                    return redirect('/')
                users = authenticate(username=users.username, password=request.POST.get('pass2'))

                if users is not None:
                    login(request, users)
                    f_name = ''
                    Mainlist1 = []# initialisation of list
                    list1 = Userdetails.objects.all()
                    list4 = Tutorialdetails.objects.all()
                    udets = User.objects.filter(username=users.username)

                    for k in list1:
                        if k.user == User.objects.get(username=request.POST.get('user2')):
                            f_name = k.fossname

                            if f_name is None:
                                am = 0
                            else:
                                user2 = User.objects.filter(username=request.POST.get('user2'))
                                aw = Payment.objects.get(user=Userdetails.objects.get(user=user2[0]))
                                am = aw.amount

                    for u1 in list4:
                        Dict = {}#dictionary is created
                        if u1.fossname == f_name:
                            Dict['b1'] = u1.tname
                            Dict['b2'] = u1.fossname
                            Dict['b3'] = u1.submdate
                            Dict['b4'] = u1.deadline
                            Mainlist1.append(Dict)
                    return render(request, 'tut/userpage.html', {'Mainlist1': Mainlist1, 'udets': udets,
                                                                'f_name': f_name, 'am': am})

                else:
                    error_msg2 = "Incorrect Password"
                    messages.error(request, error_msg2)
                    return redirect('/')
        except:
            pass

    else:
        return render(request, 'tut/login.html')


def userpg(request):
    if request.method == 'POST':
        try:
            if request.POST['s5']:
                tut_name = request.POST['tutname']
                foss_name = request.POST['fname']

                if Tutorialdetails.objects.filter(tname=tut_name, fossname=foss_name).exists():
                    tt = Tutorialdetails.objects.get(tname=tut_name, fossname=foss_name)#storing the required tutorial
                                                                                        # object
                    if tt.submdate is None:
                        tt.submdate = datetime.date.today()#assigning today's date to submission date of tutorial
                        tt.save()
                        u2 = Userdetails.objects.get(fossname=foss_name)#fetching all objects of particular foss name
                        list6 = Tutorialdetails.objects.filter(fossname=foss_name)#list of objects of particular foss name
                        c = 0
                        for i in list6:
                            if i.submdate is not None:

                                if i.submdate <= i.deadline:
                                    c = c + 1
                                    print(c)
                                    am = c * 1000
                                    amtt = Payment.objects.get(user=u2)# fetching object of particular user from amount table
                                    amtt.amount = am
                                    amtt.save()#saving amount of particular user into database
                        error_msg20 = " Tutorial Uploaded successfully.."
                        messages.error(request, error_msg20)

                    else:
                        error_msg19 = " Tutorial already Submitted"
                        messages.error(request, error_msg19)

                    Mainlist2 = []#creating another mainlist to send the data to html page as this is under another url
                    list7 = Tutorialdetails.objects.all()
                    try:
                        users = User.objects.get(username=request.POST['usernm'])
                    except:
                        pass
                    udets = User.objects.filter(username=users.username)


                    for u1 in list7:
                        Dict = {}#creating another dictionary to store data
                        if str(u1.fossname) == str(foss_name):
                            Dict['b1'] = u1.tname
                            Dict['b2'] = u1.fossname
                            Dict['b3'] = u1.submdate
                            Dict['b4'] = u1.deadline
                            Mainlist2.append(Dict)
                        else:
                            print('not exists')
                    user2 = User.objects.filter(username=request.POST['usernm'])#getting object of active user
                    aww = Payment.objects.get(user=Userdetails.objects.get(user=user2[0]))
                    amm = aww.amount
                    return render(request, 'tut/userpage.html',
                                  {'Mainlist1': Mainlist2, 'udets': udets, 'f_name': foss_name, 'am': amm})

        except:
            pass



def admindata(request):
    if request.method == 'POST':

        try:
            list1 = Userdetails.objects.all()
            list2 = Foss.objects.all()
            errors = None
            # if submit foss button is selected
            if request.POST['s3'] == 'Submit_Foss':
                form = Createform(request.POST)
                print(form.errors)
                if form.is_valid():
                    tutt = [request.POST.get('tutorial1'), request.POST.get('tutorial2'), request.POST.get('tutorial3'),
                            request.POST.get('tutorial4'), request.POST.get('tutorial5'), request.POST.get('tutorial6'),
                            request.POST.get('tutorial7'), request.POST.get('tutorial8'), request.POST.get('tutorial9'),
                            request.POST.get('tutorial10')]# all tutorials are stored into a array

                    seen = []#an emty array is created
                    #this for loop is to check whether two tutorial names are same or not if same returns error message
                    #else tutorials are stored into foss
                    for tt in tutt:
                        if tt in seen:
                            error_msg12 = "Tutorial names can't be same... Please correct it!!"
                            messages.error(request, error_msg12)
                            return render(request, 'tut/admin.html', {'list1': list1, 'list2': list2})
                        else:
                            seen.append(tt)

                if Foss.objects.filter(fossname=request.POST.get('fossid')).exists():#as one foss is assigned to only
                #  one user this if checks this condition before creating another foss
                    error_msg11 = "Foss already exists! Try a different name..."
                    messages.error(request, error_msg11)
                    return render(request, 'tut/admin.html', {'list1': list1, 'list2': list2})


                elif form.is_valid():
                    foss22 = Foss(fossname=request.POST['fossid'])
                    foss22.save()#saving foss name to Foss table in database
                    #tutorial objects are created
                    t1 = Tutorialdetails(fossname=foss22, tname=request.POST['tutorial1'],
                                         deadline=request.POST['deadline1'])
                    #t1.save()
                    t2 = Tutorialdetails(fossname=foss22, tname=request.POST['tutorial2'],
                                         deadline=request.POST['deadline2'])
                    #t2.save()
                    t3 = Tutorialdetails(fossname=foss22, tname=request.POST['tutorial3'],
                                         deadline=request.POST['deadline3'])
                    #t3.save()
                    t4 = Tutorialdetails(fossname=foss22, tname=request.POST['tutorial4'],
                                         deadline=request.POST['deadline4'])
                    #4.save()
                    t5 = Tutorialdetails(fossname=foss22, tname=request.POST['tutorial5'],
                                         deadline=request.POST['deadline5'])
                    #5.save()
                    t6 = Tutorialdetails(fossname=foss22, tname=request.POST['tutorial6'],
                                         deadline=request.POST['deadline6'])
                    #t6.save()
                    t7 = Tutorialdetails(fossname=foss22, tname=request.POST['tutorial7'],
                                         deadline=request.POST['deadline7'])
                    #t7.save()
                    t8 = Tutorialdetails(fossname=foss22, tname=request.POST['tutorial8'],
                                         deadline=request.POST['deadline8'])
                    #t8.save()
                    t9 = Tutorialdetails(fossname=foss22, tname=request.POST['tutorial9'],
                                         deadline=request.POST['deadline9'])
                    #t9.save()
                    t10 = Tutorialdetails(fossname=foss22, tname=request.POST['tutorial10'],
                                          deadline=request.POST['deadline10'])
                    #t10.save()
                    if t1 is not None and t2 is not None and t3 is not None and t4 is not None and t5 is not None\
                            and t6 is not None and t7 is not None and t8 is not None and t9 is not None and t10\
                            is not None:#if tutorial objects are not none then they are saved into database and foss is created
                        t1.save()
                        t2.save()
                        t3.save()
                        t4.save()
                        t5.save()
                        t6.save()
                        t7.save()
                        t8.save()
                        t9.save()
                        t10.save()
                        error_msg9 = "Foss Created Successfully..!"
                        messages.error(request, error_msg9)
                        return render(request, 'tut/admin.html', {'list1': list1, 'list2': list2})
                    else:
                        error_msg13 = "Please enter valid format of date....!"
                        messages.error(request, error_msg13)
                        return render(request, 'tut/admin.html', {'list1': list1, 'list2': list2})

                else:
                    error_msg5 = "Data not saved.. Some format is worng..!"
                    messages.error(request, error_msg5)
                    return render(request, 'tut/admin.html', {'list1': list1, 'list2': list2})
            # if assign foss is selected
            elif request.POST['s3'] == 'Assign_Foss':
                form = Assignform(request.POST)
                print(form.errors)
                list5 = Userdetails.objects.all()
                for u in list5:
                    if u.user == User.objects.get(username=request.POST.get('userassn')) and u.fossname is not None:# if
                                                            #  user enterd has already being assigned by foss
                        error_msg14 = "Foss already assigned!"
                        messages.error(request, error_msg14)
                        return render(request, 'tut/admin.html', {'list1': list1, 'list2': list2})

                if Userdetails.objects.filter(fossname=request.POST.get('fossassn')).exists():#if fossname entered has
                                                                    #  already being assigned to another user
                    error_msg16 = "This Foss has been already assigned to a user!"
                    messages.error(request, error_msg16)
                    return render(request, 'tut/admin.html', {'list1': list1, 'list2': list2})

                elif form.is_valid():
                    use1 = User.objects.only('username').get(username=request.POST['userassn'])
                    use = Foss.objects.only('fossname').get(fossname=request.POST['fossassn'])
                    obj = Userdetails(user=use1, fossname=use)
                    obj.save()# user fossname is stored into database and foss is assigned
                    obj2 = Payment(user_id=use1.id)#as user as being assigned with tutorials his payment
                                                            #  is created with null
                    obj2.save()
                    error_msg10 = "Foss Assigned Successfully..!"
                    messages.error(request, error_msg10)
                    return render(request, 'tut/admin.html', {'list1': list1, 'list2': list2})

                else:
                    form = Assignform()
                    errors = form.errors
                    print(errors)
                    error_msg11 = "Something is wrong...!"
                    messages.error(request, error_msg11)
                    return render(request, 'tut/admin.html', {'list1': list1, 'list2': list2})

        except:
            pass

        try:
            if request.POST['s4']:#if a particular user is selected to know his details
                list1 = Userdetails.objects.all()
                list4 = Tutorialdetails.objects.all()
                Mainlist = []
                for u in list1:
                    if u.user == User.objects.get(username=request.POST.get('s4')):
                        foss_name = u.fossname

                if foss_name is not None:
                    for u1 in list4:
                        Dict = {}
                        if u1.fossname == foss_name:
                            Dict['a1'] = u1.tname
                            Dict['a2'] = u1.fossname
                            Dict['a3'] = u1.submdate
                            Dict['a4'] = u1.deadline
                            Mainlist.append(Dict)
                        else:
                            error_msg6 = "please choose the user"
                    user2 = User.objects.filter(username=request.POST.get('s4'))
                    aw = Payment.objects.get(user=Userdetails.objects.get(user=user2[0]))#fetching amount details of
                            #  required user
                    am = aw.amount

                else:
                    return render(request, 'tut/admin.html', {'list1': list1, 'list2': list2})
                return render(request, 'tut/admin.html', {'Mainlist': Mainlist, 'list1': list1,
                                                          'list2': list2, 'am': am})

        except:
            pass