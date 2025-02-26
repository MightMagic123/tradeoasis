from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Lesson
from .forms import LessonForm

# Create your views here.
def education(request):
    lessons = Lesson.objects.all()
    return render(request, 'education.html', {'lessons': lessons})

@user_passes_test(lambda u: u.is_superuser)
def create_lesson(request):
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('education:education')
    else:
        form = LessonForm()
    return render(request, 'create_lesson.html', {'form': form})

def lesson_detail(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug)
    return render(request, 'lesson_detail.html', {'lesson': lesson})