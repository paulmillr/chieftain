from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from board.models import Wordfilter, DeniedIP
from board.shortcuts import add_sidebar


def is_mod(request, section_slug):
    u = request.user
    if u.is_authenticated():
        if u.is_superuser or section_slug in u.userprofile_set.get().modded():
            return True
    return False


def index(request):
    return render(request, 'modindex.html', add_sidebar())


@login_required
def wordfilter(request):
    return render(request, 'wordfilter.html', add_sidebar({
        'wordlist': Wordfilter.objects.all()
    }))


@login_required
def banlist(request):
    return render(request, 'banlist.html', add_sidebar({
        'banlist': DeniedIP.objects.all()
    }))
