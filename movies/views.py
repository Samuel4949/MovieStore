from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, MovieRequest
from .forms import MovieRequestForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def movie_requests(request):
    if request.method == 'POST':
        form = MovieRequestForm(request.POST)
        if form.is_valid():
            movie_request = form.save(commit=False)
            movie_request.user = request.user
            movie_request.save()
            messages.success(request, 'Movie request submitted successfully!')
            return redirect('movies.movie_requests')
    else:
        form = MovieRequestForm()
    
    # Get all movie requests for the current user
    user_requests = MovieRequest.objects.filter(user=request.user).order_by('-date_requested')
    
    template_data = {
        'title': 'Movie Requests',
        'form': form,
        'user_requests': user_requests
    }
    return render(request, 'movies/movie_requests.html', {'template_data': template_data})

@login_required
def delete_movie_request(request, request_id):
    movie_request = get_object_or_404(MovieRequest, id=request_id, user=request.user)
    movie_request.delete()
    messages.success(request, 'Movie request deleted successfully!')
    return redirect('movies.movie_requests')


def petitions(request):
    """Public page where users can see all movie requests (petitions), create new ones,
    and vote for requests."""
    if request.method == 'POST':
        # reuse the MovieRequestForm for creating petitions
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to submit a petition or vote.')
            return redirect('movies.petitions')
        form = MovieRequestForm(request.POST)
        if form.is_valid():
            movie_request = form.save(commit=False)
            movie_request.user = request.user
            movie_request.save()
            messages.success(request, 'Petition submitted successfully!')
            return redirect('movies.petitions')
    else:
        form = MovieRequestForm()

    all_requests = MovieRequest.objects.all().order_by('-date_requested')
    # annotate each request with whether the current user has voted (templates can't call methods with args)
    for r in all_requests:
        r.user_has_voted = r.has_user_voted(request.user) if request.user.is_authenticated else False

    template_data = {
        'title': 'Petitions',
        'form': form,
        'all_requests': all_requests
    }
    return render(request, 'movies/petitions.html', {'template_data': template_data})


@login_required
def vote_petition(request, request_id):
    """Toggle vote for a petition by the current user."""
    movie_request = get_object_or_404(MovieRequest, id=request_id)
    user = request.user
    if movie_request.has_user_voted(user):
        movie_request.votes.remove(user)
        messages.success(request, f'You removed your vote for "{movie_request.movie_name}"')
    else:
        movie_request.votes.add(user)
        messages.success(request, f'You voted for "{movie_request.movie_name}"')
    return redirect('movies.petitions')
