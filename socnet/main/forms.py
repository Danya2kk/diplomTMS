from django import forms
from .models import News, Tag, Comment, Reaction, Friendship, Profile, Group, GroupMembership, Status


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'tags', 'is_published']
        widgets = {
            'tags': forms.CheckboxSelectMultiple,
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class ReactionForm(forms.ModelForm):
    class Meta:
        model = Reaction
        fields = ['reaction_type']
        widgets = {
            'reaction_type': forms.RadioSelect,
        }


class FriendshipCreateForm(forms.ModelForm):
    class Meta:
        model = Friendship
        fields = ['profile_two', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_two'].queryset = Profile.objects.exclude(user=self.instance.profile_one.user)


class FriendshipUpdateForm(forms.ModelForm):
    class Meta:
        model = Friendship
        fields = ['status', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class FriendshipSearchForm(forms.Form):
    search_term = forms.CharField(label='Поиск', required=False)


class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'photo', 'group_type', 'rules']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'rules': forms.Textarea(attrs={'rows': 3}),
            'group_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.fields['creator'].initial = kwargs.get('user').profile


class GroupUpdateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'photo', 'group_type', 'rules']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'rules': forms.Textarea(attrs={'rows': 3}),
            'group_type': forms.Select(choices=GROUP_TYPES),
        }


class GroupSearchForm(forms.Form):
    search_term = forms.CharField(label='Поиск', required=False)


class StatusCreateForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
