from repository.forms import RegistrationForm
from repository.models import Repository, DigitalEvidence, ElectronicEvidence, fileStorage
from repository.serializers import RepositorySerializers, UserSerializer, DigitalEvidenceSerializers, \
    ElectronicEvidenceSerializers
from rest_framework import generics
from .models import User
from rest_framework import permissions
from repository.permissions import IsOwnerOrReadOnly, IsOwnerOrReadOnlyEvidence
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import  redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import shutil, os


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'repositorys': reverse('repository-list', request=request, format=format)})


class RepositoryList(generics.ListCreateAPIView):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializers

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)


class RepositoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializers

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)


class DigitalList(generics.ListCreateAPIView):
    queryset = DigitalEvidence.objects.all()
    serializer_class = DigitalEvidenceSerializers

    def perform_create(self, serializer):
        serializer.save(repository__user=self.request.user)

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnlyEvidence)


class DigitalDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = DigitalEvidence.objects.all()
    serializer_class = DigitalEvidenceSerializers

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnlyEvidence)


class ElectronicList(generics.ListCreateAPIView):
    queryset = ElectronicEvidence.objects.all()
    serializer_class = ElectronicEvidenceSerializers

    def perform_create(self, serializer):
        serializer.save(repository__user=self.request.user)

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnlyEvidence)


class ElectronicDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ElectronicEvidence.objects.all()
    serializer_class = ElectronicEvidenceSerializers

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnlyEvidence)


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@csrf_exempt
def login(request):
    """
    Log in view
    """
    title = "Login User"
    if request.method == 'POST':
        user = authenticate(email=request.POST['email'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                try:
                    django_login(request, user)
                    request.session['email'] = user.email
                    return redirect('/')
                except:
                    messages.add_message(request, messages.INFO, 'Akun ini belum terhubung dengan database')
            else:
                messages.add_message(request, messages.INFO, 'User Belum terverifikasi')
        else:
            messages.add_message(request, messages.INFO, 'Username atau password anda salah')

    return render(request, 'login.html', {"title": title})


@login_required(login_url=settings.LOGIN)
def homepage(request):
    title = "Homepage"

    user = User.objects.get(email=request.session['email'])
    content = Repository.objects.filter(user_id=user.id)

    if content.count() == 0:
        messages.add_message(request, messages.INFO, "Nothing File")

    context = {
        "title": title,
        "user": user,
        "content": content,
    }

    return render(request, "homepage.html", context)


@login_required(login_url=settings.LOGIN)
def viewRepo(request):
    title = "Homepage"

    user = User.objects.get(email=request.session['email'])
    content = Repository.objects.filter(user_id=user.id)

    paginator = Paginator(content, 6)
    page = request.GET.get('page')

    try:
        content = paginator.page(page)
    except PageNotAnInteger:
        content = paginator.page(1)
    except EmptyPage:
        content = paginator.page(paginator.num_pages)


    context = {
        "title": title,
        "user": user,
        "content": content,
    }

    return render(request, "repository.html", context)


@login_required(login_url=settings.LOGIN)
def addRepo(request):
    user = User.objects.get(email=request.session['email'])
    content = Repository.objects.filter(user_id=user.id)
    pk = request.POST['id_repository']

    notSave = False

    if request.method == 'POST':
        for con in content:
            if str(user.id)+str(request.POST['id_repository']) == con.id_repository:
                messages.add_message(request, messages.ERROR, "Id Repository Existing")
                notSave = True
            else:
                pass

        if notSave:
            return redirect('/')
        else:
            new = Repository(
                repository_name=request.POST['repository_name'],
                id_repository=str(user.id) + str(pk),
                user_id=user.id,
            )
            new.save()
            return redirect('/repository/view/edit/' + str(user.id) + str(pk) + '/')


@login_required(login_url=settings.LOGIN)
def detail(request, pk):
    title = "Detail "
    user = User.objects.get(email=request.session['email'])
    content = "nothing"
    digital = ""
    electronic = ""
    try:
        repo = Repository.objects.get(id_repository=pk)
        if repo.user_id != user.id:
            messages.add_message(request, messages.INFO, "Nothing File")
            content = "nothing"
        else:
            content = Repository.objects.get(id_repository=pk)
            digital = DigitalEvidence.objects.filter(repository_id=pk)
            electronic = ElectronicEvidence.objects.filter(repository_id=pk)
    except Exception:
        messages.add_message(request, messages.INFO, "Nothing File")

    context = {
        "title": title,
        "content": content,
        "digital": digital,
        "electronic": electronic,
    }
    return render(request, "detail.html", context)


@login_required(login_url=settings.LOGIN)
def editRepo(request, pk):

    title = "Edit " + pk
    user = User.objects.get(email=request.session['email'])

    content = "nothing"
    digital = ""
    electronic = ""

    try:
        content = Repository.objects.get(id_repository=pk)

        if content.user_id != user.id:
            messages.add_message(request, messages.INFO, "Nothing File")
            content = "nothing"
        else:
            digital = DigitalEvidence.objects.filter(repository_id=pk)
            electronic = ElectronicEvidence.objects.filter(repository_id=pk)
            if request.method == 'POST':

                if request.POST['date'] is '':
                    date = content.date
                else:
                    date = request.POST['date']

                data = Repository(
                    id_repository=request.POST['id_repository'],
                    repository_name=request.POST['repository_name'],
                    user_id=user.id,
                    date=date,
                    created=content.created,
                    info=request.POST['info'],
                )
                data.save()
                repo = messages.add_message(request, messages.INFO, "Repository Updated")
                return redirect('/repository/view/edit/' + pk + '/', repo)
    except Exception:
        messages.add_message(request, messages.INFO, "Nothing File")


    context = {
        "title": title,
        "content": content,
        "digital": digital,
        "electronic": electronic,

    }

    return render(request, "edit.html", context)


@login_required(login_url=settings.LOGIN)
def delRepo(request):
    if request.method == 'POST':
        user = User.objects.get(email=request.session['email'])
        pk = request.POST['id_repository']

        digital = DigitalEvidence.objects.filter(repository_id=pk)
        for dig in digital:
            dig.delete()

        electronic = ElectronicEvidence.objects.filter(repository_id=pk)

        for el in electronic:
            el.delete()

        repo = Repository.objects.get(id_repository=pk)
        repo.delete()

        dir = os.path.join(settings.MEDIA_ROOT, "upload/user/"+str(user.id)+"/"+str(pk)+"/")

        try:
            shutil.rmtree(dir, ignore_errors=False, onerror=None)
        except FileNotFoundError:
            pass


        messages.add_message(request, messages.INFO, pk + " Deleted")

        return redirect('/repository/view/edit/' + pk + '/')


@login_required(login_url=settings.LOGIN)
def addDigital(request):
    if request.method == 'POST':
        digital = DigitalEvidence(
            repository_id=request.POST['repository_id'],
            file=request.FILES.get('evidence'),
            info_file=request.POST['info'],
            filename=request.POST['filename'],
        )
        digital.save()
        pk = request.POST['repository_id']
        messages.add_message(request, messages.INFO, "Digital Saved")
        return redirect('/repository/view/edit/' + pk + '/')


@login_required(login_url=settings.LOGIN)
def addElectronic(request):
    if request.method == 'POST':
        electronic = ElectronicEvidence(
            repository_id=request.POST['repository_id'],
            file=request.FILES.get('evidence'),
            info_file=request.POST['info'],
            filename=request.POST['filename'],
        )
        electronic.save()
        pk = request.POST['repository_id']
        messages.add_message(request, messages.INFO, "Electronic Saved")
        return redirect('/repository/view/edit/' + pk + '/')


@login_required(login_url=settings.LOGIN)
def deleteDigital(request):
    if request.method == 'POST':
        digital = DigitalEvidence.objects.get(id=request.POST['id'])
        digital.delete()

        pk = request.POST['repository_id']
        messages.add_message(request, messages.INFO, request.POST['filename'] + " Digital Deleted")
        return redirect('/repository/view/edit/' + pk + '/')


@login_required(login_url=settings.LOGIN)
def deleteElectronic(request):
    if request.method == 'POST':
        electronic = ElectronicEvidence.objects.get(id=request.POST['id'])

        electronic.delete()
        pk = request.POST['repository_id']
        messages.add_message(request, messages.INFO, request.POST['filename'] + " Electronic Deleted")
        return redirect('/repository/view/edit/' + pk + '/')


@csrf_exempt
def reg(request):
    """
    User registration view.
    :param request:
    :return:
    """

    title = "Register"

    if request.method == 'POST':
        if request.POST['password1'] != request.POST['password2']:
            messages.add_message(request, messages.ERROR, "Passwords don't match. Please enter both fields again.")
        else:
            form = RegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                return redirect('/register/success/')

    return render(request, "register.html", {"title": title})


def register_success(request):
    return render(request, 'success.html')


def logout(request):
    django_logout(request)
    return redirect('/')
