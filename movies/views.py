from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.db.models import Count,Sum
from django.db.models.functions import Coalesce

# Create your views here.

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

def top_commenters(request):
    comment_counts = (
        Review.objects
        .values('user_id', 'user__username')
        .annotate(comment_count=Count('id'))
        .order_by('-comment_count','user__username')
    )
    highest = comment_counts.first()

    if highest:
        top_users = comment_counts.filter(
            comment_count=highest['comment_count']
        )
    else:
        top_users = []

    context = {
        **admin.site.each_context(request),
        'title': 'Top Commenter',
        'top_users': top_users
    }
    return render(
        request,'admin/top_commenter.html',context,
    )

def top_movies(request):
    # reference - https://www.geeksforgeeks.org/python/aggregate-vs-annotate-in-django/
    most_purchased = Movie.objects.annotate(total_purchases = Coalesce(Sum('item__quantity'),0)).order_by('-total_purchases').first()

    most_reviewed = Movie.objects.annotate(total_reviews = Count('review')).order_by('-total_reviews').first()

    context = {
        'most_purchased': most_purchased,
        'most_reviewed': most_reviewed
    }
    return render(request, 'admin/top_movies.html', context)

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment']!= '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    return redirect('movies.show', id=id)