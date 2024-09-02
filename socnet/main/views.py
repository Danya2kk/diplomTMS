from django.http import JsonResponse, Http404
from django.contrib.contenttypes.models import ContentType
from .models import News, Tag, Comment, Reaction, Friendship
from .forms import NewsForm, TagForm, CommentForm, ReactionForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Group, GroupMembership,Status
from .forms import GroupCreateForm, GroupUpdateForm, GroupSearchForm

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


#База для статуса дружбы
PENDING = 'pending'
ACCEPTED = 'accepted'
BLOCKED = 'blocked'

STATUS_CHOICES = [
    (PENDING, 'Отправлен запрос'),
    (ACCEPTED, 'Друзья'),
    (BLOCKED, 'Заблокирован'),
]


class FriendshipListView(LoginRequiredMixin, ListView):
    model = Friendship
    template_name = 'friendship_list.html'
    context_object_name = 'friendships'

    def get_queryset(self):
        return Friendship.objects.filter(
            Q(profile_one=self.request.user.profile) | Q(profile_two=self.request.user.profile)).order_by('-created_at')


class FriendshipListView(LoginRequiredMixin, DetailView):
    model = Friendship
    template_name = 'friendship_detail.html'
    context_object_name = 'friendship'

    def get_object(self):
        friendship = super().get_object()
        if friendship.profile_one == self.request.user.profile or friendship.profile_two == self.request.user.profile:
            return friendship
        else:
            raise Http404('Друг не найден')


class FriendshipCreateView(LoginRequiredMixin, CreateView):
    model = Friendship
    fields = ['profile_two', 'description']
    template_name = 'friendship_form.html'

    def form_valid(self, form):
        form.instance.profile_one = self.request.user.profile
        form.instance.status = PENDING
        return super().form_valid(form)


class FriendshipUpdateView(LoginRequiredMixin, UpdateView, UserPassesTestMixin):
    model = Friendship
    fields = ['status', 'description']
    template_name = 'friendship_form.html'

    def test_func(self):
        friendship = self.get_object()
        return friendship.profile_one == self.request.user.profile or friendship.profile_two == self.request.user.profile


class FriendshipDeleteView(LoginRequiredMixin, DeleteView, UserPassesTestMixin):
    model = Friendship
    success_url = '/friendship/'
    template_name = 'friendship_confirm_delete.html'

    def test_func(self):
        friendship = self.get_object()
        return friendship.profile_one == self.request.user.profile or friendship.profile_two == self.request.user.profile

@login_required
def accept_friendship(request, pk):
    friendship = get_object_or_404(Friendship, pk=pk)
    if friendship.profile_two == request.user.profile:
        friendship.status = ACCEPTED
        friendship.save()
        messages.success(request, 'Запрос на дружбу принят!')
    else:
        messages.error(request, 'Вы не можете принять этот запрос.')
    return redirect('friendship-list')

@login_required
def reject_friendship(request, pk):
    friendship = get_object_or_404(Friendship, pk=pk)
    if friendship.profile_two == request.user.profile:
        friendship.delete()
        messages.success(request, 'Запрос на дружбу отклонен!')
    else:
        messages.error(request, 'Вы не можете отклонить этот запрос.')
    return redirect('friendship-list')

@login_required
def block_friendship(request, pk):
    friendship = get_object_or_404(Friendship, pk=pk)
    if friendship.profile_one == request.user.profile or friendship.profile_two == request.user.profile:
        friendship.status = BLOCKED
        friendship.save()
        messages.success(request, 'Пользователь заблокирован!')
    else:
        messages.error(request, 'Ошибка блокировки.')
    return redirect('friendship-list')

@login_required
def unblock_friendship(request, pk):
    friendship = get_object_or_404(Friendship, pk=pk)
    if friendship.profile_one == request.user.profile or friendship.profile_two == request.user.profile:
        friendship.status = PENDING
        friendship.save()
        messages.success(request, 'Пользователь разблокирован!')
    else:
        messages.error(request, 'Ошибка разблокировки.')
    return redirect('friendship-list')

class GroupListView(ListView):
    model = Group
    template_name = 'group/group_list.html'
    context_object_name = 'groups'

    def get_queryset(self):
        search_term = self.request.GET.get('search_term', None)
        if search_term:
            return Group.objects.filter(name__icontains=search_term).order_by('-created_at')
        else:
            return Group.objects.all().order_by('-created_at')

class GroupDetailView(DetailView):
    model = Group
    template_name = 'group/group_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_member'] = self.object.members.filter(profile=self.request.user.profile).exists() # Check if user is a member
        return context

@login_required
def join_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if not group.members.filter(profile=request.user.profile).exists():
        GroupMembership.objects.create(
            profile=request.user.profile,
            group=group,
            status=Status.objects.get(name='member')
        )
        messages.success(request, f'Вы присоединились к группе {group.name}.')
    else:
        messages.info(request, f'Вы уже являетесь членом группы {group.name}.')
    return redirect('group-detail', pk=pk)


@login_required
def leave_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    membership = group.members.filter(profile=request.user.profile).first()
    if membership:
        membership.delete()
        messages.success(request, f'Вы покинули группу {group.name}.')
    else:
        messages.info(request, f'Вы не являетесь членом группы {group.name}.')
    return redirect('group-detail', pk=pk)


class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupCreateForm
    template_name = 'group/group_form.html'

    def form_valid(self, form):
        form.instance.creator = self.request.user.profile
        group = form.save()
        GroupMembership.objects.create(
            profile=self.request.user.profile,
            group=group,
            status=Status.objects.get(name='admin') # Set the creator as admin
        )
        return super().form_valid(form)

class GroupUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Group
    form_class = GroupUpdateForm
    template_name = 'group/group_form.html'

    def test_func(self):
        group = self.get_object()
        return group.creator == self.request.user.profile

class GroupDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Group
    success_url = '/group/'
    template_name = 'group/group_confirm_delete.html'

    def test_func(self):
        group = self.get_object()
        return group.creator == self.request.user.profile


def group_search(request):
    form = GroupSearchForm(request.GET)
    if form.is_valid():
        search_term = form.cleaned_data['search_term']
        groups = Group.objects.filter(name__icontains=search_term).order_by('-created_at')
        return render(request, 'group/group_list.html', {'groups': groups})
    else:
        return render(request, 'group/group_list.html', {'form': form})

class StatusListView(ListView):
    model = Status
    template_name = 'status_list.html'
    context_object_name = 'statuses'

class StatusCreateView(LoginRequiredMixin, CreateView,):
    model = Status
    form_class = StatusCreateForm
    template_name = 'status_form.html'
    success_url = '/status/'

class StatusDetailView(DetailView):
    model = Status
    template_name = 'status_detail.html'

class StatusUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Status
    form_class = StatusCreateForm
    template_name = 'status_form.html'
    success_url = '/status/'

    def test_func(self):
        return self.request.user.is_superuser

class StatusDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Status
    success_url = '/status/'
    template_name = 'status_confirm_delete.html'

    def test_func(self):
        return self.request.user.is_superuser