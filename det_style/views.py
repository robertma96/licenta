from django.shortcuts import render, HttpResponse, redirect
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import Paintings, UserStyling
import json
from .face_detection_and_styling import face_detection
from .forms import SignUpForm, UserStylingForm
from django.contrib.auth import login, authenticate, logout
import math
from django.contrib.auth.decorators import login_required


def signup(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                return render(request, 'det_style/signup.html',
                              {'success': 'Your account has been successfully created!'})
        else:
            form = SignUpForm()
        return render(request, 'det_style/signup.html', {'form': form})
    else:
        return render(request, 'det_style/signup.html', {'message': 'You are already logged in!'})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('upload')
        else:
            return render(request, 'registration/login.html', {'error': True})
    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    return redirect('/')


def index(request):
    return render(request, 'det_style/index.html')


@login_required(login_url='login')
def style_image(request):
    current_user_id = request.user.id

    user_styling_object = UserStyling.objects.filter(user_id=current_user_id).last()

    if user_styling_object.resulted_image != '':
        styled_image_path = user_styling_object.resulted_image
        return render(request, 'det_style/upload_succesful.html', {
            'styled_image_path': styled_image_path.split('website_licenta')[1]
        })

    full_image_name = user_styling_object.uploaded_image.name.split('/')[1]
    image_path = user_styling_object.uploaded_image.path
    path_to_results = os.path.join(settings.MEDIA_ROOT)
    selected_model = user_styling_object.selected_painting.model_path
    selected_mode = user_styling_object.selected_mode
    path_to_resulted_styled_image = face_detection.face_detection(full_image_name, image_path, path_to_results,
                                                                      selected_model, selected_mode)

    user_styling_object.resulted_image = path_to_resulted_styled_image
    user_styling_object.save()

    styled_image_path = user_styling_object.resulted_image

    return render(request, 'det_style/upload_succesful.html', {
        'styled_image_path': styled_image_path.split('website_licenta')[1]
    })


@login_required(login_url='login')
def upload(request):
    paintings = Paintings.objects.all()
    paintings_url = [os.path.join(settings.MEDIA_URL, 'paintings', painting.image_path) for painting in paintings]
    for i in range(len(paintings)):
        paintings[i].image_path = paintings_url[i]
    number_of_lists_needed = math.ceil(len(paintings) / 3)
    paintings_to_send = []
    # Cate tablouri pe o linie
    end = 3
    start = 0

    for _ in range(number_of_lists_needed):
        paintings_to_send.append(paintings[start:end])
        start = end
        end = end + 3

    if request.method == 'POST':
        if len(request.FILES) == 0:
            return render(request, 'det_style/upload.html', {
                'paintings': paintings,
                'paintings_to_send': paintings_to_send,
                'file_not_selected': 'Please select a file!'
            })
        selected_mode = True
        file = request.FILES['myfile']
        painting_id = request.POST['painting_id']
        mode = request.POST['selected_mode']
        user_styling_object = UserStyling()
        selected_painting = Paintings.objects.get(pk=int(painting_id))
        if mode == 'inside':
            selected_mode = False
        elif mode == 'outside':
            selected_mode = True
        elif mode == 'only_style':
            selected_mode = 'only_style'

        user_styling_object.user = request.user
        user_styling_object.uploaded_image = file
        user_styling_object.selected_painting = selected_painting
        user_styling_object.selected_mode = selected_mode

        user_styling_object.save()

        return redirect('upload/result')

    return render(request, 'det_style/upload.html', {
        'paintings': paintings,
        'paintings_to_send': paintings_to_send
    })


def my_profile(request):
    current_user_id = request.user.id
    user_objects = UserStyling.objects.filter(user_id=current_user_id)

    my_pictures = ['media' + element.resulted_image.split('media')[1] for element in user_objects if element.resulted_image != '0']

    return render(request, 'det_style/my_profile.html', {
        'my_pictures': my_pictures
    })
