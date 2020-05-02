from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Hall, Video
from .forms import VideoForm, SearchForm
from django.http import Http404, JsonResponse
import urllib
import requests
from django.forms.utils import ErrorList
from django.conf import settings

def home(request):
    recent_halls = Hall.objects.all().order_by('-pk')[:3]
    return render(request, 'halls/home.html', {'recent_halls': recent_halls})

@login_required()
def dashboard(request):
    halls = Hall.objects.filter(user = request.user)
    return render(request, 'halls/dashboard.html', {'halls': halls})

@login_required()
def add_video(request, pk):
    form = VideoForm()
    search_form = SearchForm()
    hall = Hall.objects.get(pk=pk)
    if not hall.user == request.user:
        raise Http404
    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            video = Video()
            video.url = form.cleaned_data['url']

            parsed_url = urllib.parse.urlparse(video.url)
            video_id = urllib.parse.parse_qs(parsed_url.query).get('v')
            if video_id:
                video.youtube_id = video_id[0]
                response = requests.get(f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={ video.youtube_id }&key={ settings.YOUTUBE_API_KEY }')
                json = response.json()
                video.title = json['items'][0]['snippet']['title']
                video.hall = hall
                video.save()
                return redirect('detail-hall', pk)
            else:
                errors = form._errors.setdefault('url', ErrorList())
                errors.append('Needs to be a valid YouTube Url')

    return render(request, 'halls/add_video.html', {'form': form, 'search_form': search_form, 'hall': hall})

@login_required()
def video_search(request):
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        encoded_search_term = urllib.parse.quote(search_form.cleaned_data['search_term'])
        response = requests.get(f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=4&q={ encoded_search_term }&key={ settings.YOUTUBE_API_KEY }')
        return JsonResponse(response.json())
    return JsonResponse({'error': 'Not Valid!'})

class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('dashboard')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        view = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return view

class CreateHall(LoginRequiredMixin, CreateView):
    model = Hall
    fields = ['title']
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        super(CreateHall, self).form_valid(form) #super() returns a view
        return redirect('dashboard')

class DetailHall(DetailView):
    model = Hall

class UpdateHall(LoginRequiredMixin, UpdateView):
    def get_object(self):
        hall = super(UpdateHall, self).get_object()
        if not hall.user == self.request.user:
            raise Http404
        return hall

    model = Hall
    fields = ['title']
    template_name = 'halls/update_hall.html'
    success_url = reverse_lazy('dashboard')

class DeleteHall(LoginRequiredMixin, DeleteView):
    def get_object(self):
        hall = super(DeleteHall, self).get_object()
        if not hall.user == self.request.user:
            raise Http404
        return hall

    model = Hall
    success_url = reverse_lazy('dashboard')

class DeleteVideo(LoginRequiredMixin, DeleteView):
    def get_object(self):
        video = super(DeleteVideo, self).get_object()
        if not (video.hall.user == self.request.user and video.hall.id == self.kwargs['id']):
            raise Http404
        return video

    model = Video
    success_url = reverse_lazy('dashboard')