from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from .models import News, Tag, Comment, Reaction
from .forms import NewsForm, TagForm, CommentForm , ReactionForm

# Create your views here.
def index(request):

    context = {
        'title': 'Домашняя страница',

    }
    return render(request, 'main/index.html', context)


def chat(request):


    context = {
        'is_chat_page': 'true'
    }
    return render(request, 'main/chat.html', context)



@login_required
def news_list(request):
    news_items = News.objects.all().order_by('-created_at')
    context = {
        'news_items': news_items,
    }
    return render(request, 'news_list.html', context)


@login_required
def news_detail(request, pk):
    news_item = News.objects.get(pk=pk)
    context = {
        'news_item': news_item,
    }
    return render(request, 'news_detail.html', context)


@login_required
def news_create(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news_item = form.save(commit=False)
            news_item.profile = request.user.profile
            news_item.save()
            return redirect('news_detail')
    else:
        form = NewsForm()
    context = {
        'form': form,
    }
    return render(request, 'create_news.html', context)


@login_required
def news_edit(request, pk):
    news_item = News.objects.get(pk=pk)
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news_item)
        if form.is_valid():
            form.save()
            return redirect('news_detail', pk=news_item.pk)
    else:
        form = NewsForm(instance=news_item)
    context = {
        'form': form,
        'news_item': news_item,
    }
    return render(request, 'edit_news.html', context)


@login_required
def news_delete(request, pk):
    news_item = News.objects.get(pk=pk)
    if request.method == 'POST':
        news_item.delete()
        return redirect('news_list')
    context = {
        'news_item': news_item,
    }
    return render(request, 'delete_news.html', context)


def tag_list(request):
    tags = Tag.objects.all()
    context = {
        'tags': tags,
    }
    return render(request, 'tag_list.html', context)


def tag_detail(request, pk):
    tag = Tag.objects.get(pk=pk)
    context = {'tag': tag}
    return render(request, 'tag_detail.html', context)


def create_tag(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tag_list')
    else:
        form = TagForm()
    context = {'form': form}
    return render(request, 'create_tag.html', context)


def edit_tag(request, pk):
    tag = Tag.objects.get(pk=pk)
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            return redirect('tag_detail', pk=tag.pk)
    else:
        form = TagForm(instance=tag)
    context = {'form': form, 'tag': tag}
    return render(request, 'edit_tag.html', context)


def delete_tag(request, pk):
    tag = Tag.objects.get(pk=pk)
    if request.method == 'POST':
        tag.delete()
        return redirect('tag_list')
    context = {'tag': tag}
    return render(request, 'delete_tag.html', context)


@login_required
def comment_create(request, news_pk):
    news_item = get_object_or_404(News, pk=news_pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user.profile
            comment.news = news_item
            comment.save()
            return redirect('news_detail', pk=news_item.pk)
        else:
            form = CommentForm()
        context = {'form': form, 'news_item': news_item}
        return render(request, 'comment_create.html', context)


@login_required
def comment_edit(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user.profile != comment.author:
        return redirect('news_detail', pk=comment.news.pk)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('news_detail', pk=comment.news.pk)
        else:
            form = CommentForm(instance=comment)
        context = {'form': form, 'comment': comment}
        return render(request, 'comment_edit.html', context)


LIKE = 'like'
DISLIKE = 'dislike'
HEART = 'heart'

REACTION_CHOICES = [
    (LIKE, 'Like'),
    (DISLIKE, 'Dislike'),
    (HEART, 'Heart'),
]

@login_required
def reaction_create(request, content_type_id, object_id, reaction_type):
    content_type = ContentType.objects.get(pk=content_type_id)
    obj = content_type.get_object_for_this_type(pk=object_id)
    if request.method == 'POST':
        try:
            reaction = Reaction.objects.get(
                profile=request.user.profile,
                content_type=content_type,
                object_id=object_id,
                reaction_type=reaction_type
            )
            reaction.delete()
            response_data = {'status': 'removed'}
        except Reaction.DoesNotExist:
            Reaction.objects.create(
                profile=request.user.profile,
                content_type=content_type,
                object_id=object_id,
                reaction_type=reaction_type
            )
            response_data = {'status': 'added'}
        return JsonResponse(response_data)
    else:
        form = ReactionForm(initial={'reaction_type': reaction_type})
        context = {'form': form, 'obj': obj}
        return render(request, 'reactions/reaction_form.html', context)

@login_required
def reaction_count(request, content_type_id, object_id):
    content_type = ContentType.objects.get_for_id(content_type_id)
    obj = content_type.get_object_for_this_type(pk=object_id)
    reaction_counts = {
        reaction_type: Reaction.objects.filter(
            content_type=content_type,
            object_id=object_id,
            reaction_type=reaction_type
        ).count()
        for reaction_type in REACTION_CHOICES
    }
    return JsonResponse(reaction_counts)