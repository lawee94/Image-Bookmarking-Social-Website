from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from .forms import ImageCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Image
from common.decorators import ajax_required
from actions.utils import create_action
from django.conf import settings
import redis

r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

@login_required 
def image_create(request):
    if request.method == 'POST':
        form = ImageCreationForm(data=request.POST)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'bookmarked image', new_item)
            messages.success(request, 'Image Added Succesfully' )
            return redirect(new_item.get_absolute_url())
        messages.error(request, 'Error bookmaking the image')
    else:
        form = ImageCreationForm(data=request.GET)
    return render(request, 'create.html', {'form': form, 'section': 'Image'})

def image_detail(request, pk, slug):
    image = get_object_or_404(Image, pk=pk, slug=slug)
    #increment totlal image views by
    total_views = r.incr('Image:{}:views'.format(image.id))
    # increment image ranking by 1
    r.zincrby('image_ranking', 1, image.id)
    return render(request,  'detail.html', {'section': 'images', 'image': image, 'total_views': total_views})
 
@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
                create_action(request.user, 'dislikes', image)
            return JsonResponse({'status':'ok'})
        except:
            pass
    return JsonResponse({'status':'ko'})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # If the request is AJAX and the page is out of range
            # return an empty page
            return HttpResponse('')
        # If page is out of range deliver last page of results
        images = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request, 'list_ajax.html', {'section': 'images', 'images': images})
    return render(request, 'list.html', {'section': 'images', 'images': images})

@login_required
def image_ranking(request):
    # get image ranking dictionary
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]
  
    # get most viewed images
    most_viewed = list(Image.objects.filter( id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(request, 'ranking.html', {'section': 'images', 'most_viewed': most_viewed})