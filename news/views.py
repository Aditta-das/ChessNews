from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Article, TopPlayerImg, \
    TournamentBanner, BangladeshiTopPlayer, Book, \
        Puzzle, EmailOTP, PuzzleSolve, UserProfile, \
            BoardVision, UploadedGame, GameComment, Events, Message, MemoryPosition
from django.contrib.auth.models import User
from django.contrib.auth import logout
import requests, random, json
from .forms import EmailLoginForm, ProfileEditForm, ArticleForm, GameCommentForm
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .decorators import premium_required
from django.utils import timezone
from django.db.models import Sum, F, ExpressionWrapper, IntegerField
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST

from django.core.cache import cache
import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
import requests
from .models import Article, TopPlayerImg, BangladeshiTopPlayer, TournamentBanner, Events, UserProfile
from django.contrib.auth.models import User

@csrf_exempt
def api_world_players(request):
    """API endpoint for world players"""
    players = cache.get('world_players_api')
    if not players:
        try:
            response = requests.get(
                'https://fide-api.vercel.app/top_players/?limit=5&history=false',
                timeout=20
            )
            if response.status_code == 200:
                print(response.status_code)
                players = response.json()
                cache.set('world_players_api', players, 300)
            else:
                players = []
        except Exception as e:
            print("WORLD API ERROR:", e)
            players = []
    
    # Attach images
    world_map = {
        p.fide_id: p for p in TopPlayerImg.objects.all()
    }
    
    for player in players:
        obj = world_map.get(player.get('fide_id'))
        player['image_url'] = obj.image.url if obj and obj.image else None
        player['rank'] = int(player.get('rank', 0))
        player['rating'] = int(player.get('rating', 0))
        player['country'] = player.get('country', '')
    
    return JsonResponse({'players': players, 'success': True})


@csrf_exempt
def api_bd_players(request):
    """API endpoint for Bangladeshi players"""
    top_bd_players = cache.get('bd_players_api')
    
    if not top_bd_players:
        try:
            bd_response = requests.get(
                'https://fide.onrender.com/bangladesh_players/?limit=5',
                timeout=20
            )
            if bd_response.status_code == 200:
                top_bd_players = bd_response.json()
                cache.set('bd_players_api', top_bd_players, 300)
            else:
                top_bd_players = []
        except Exception as e:
            print("BD API ERROR:", e)
            top_bd_players = []
    
    bd_map = {
        p.fide_id: p for p in BangladeshiTopPlayer.objects.all()
    }
    
    for player in top_bd_players:
        obj = bd_map.get(player.get('fide_id'))
        player['image_url'] = obj.image.url if obj and obj.image else None
        player['rank'] = int(player.get('rank', 0))
        player['rating'] = int(player.get('rating', 0))
        player['country'] = 'BAN'
    
    return JsonResponse({'players': top_bd_players, 'success': True})


def home(request):
    # ── Big news ─────────────────────────────
    big_news = Article.objects.filter(is_big_news=True).first()
    small_news = Article.objects.order_by('-published_at')
    if big_news:
        small_news = small_news.exclude(id=big_news.id)
    small_news = small_news[:6]

    best_reporter = User.objects.order_by('-article__id').first()

    # ─────────────────────────────────────────
    # REMOVED API CALLS - Now loading via JavaScript
    # ─────────────────────────────────────────
    
    # ─────────────────────────────────────────
    # 📅 Other data (database only - fast)
    # ─────────────────────────────────────────
    banner = TournamentBanner.objects.filter(
        show_banner=True
    ).order_by('-created_at').first()

    home_banner = TournamentBanner.objects.filter(
        inside_home=True
    ).order_by('-created_at').first()

    tournaments = Events.objects.all().order_by('start')

    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            profile = None

    # ─────────────────────────────────────────
    # Render
    # ─────────────────────────────────────────
    return render(request, 'news/home.html', {
        'big_news': big_news,
        'small_news': small_news,
        'best_reporter': best_reporter,
        'banner': banner,
        'home_banner': home_banner,
        'tournaments': tournaments,
        'profile': profile,
    })

@login_required
def create_article(request, slug=None):
    if slug:
        # Edit mode
        article = get_object_or_404(Article, slug=slug)
        if article.author != request.user:
            return HttpResponseForbidden("You cannot edit this article.")
    else:
        article = None  # Create mode

    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article_obj = form.save(commit=False)
            if not article:  # only assign author for new article
                article_obj.author = request.user
            article_obj.save()
            return redirect('article_detail', slug=article_obj.slug)
    else:
        form = ArticleForm(instance=article)

    return render(request, "news/create_article.html", {"form": form, "editing": article is not None})


@login_required
def delete_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if article.author != request.user:
        return HttpResponseForbidden("You cannot delete this article.")

    if request.method == "POST":
        article.delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)


def all_blogs(request):
    blogs = Article.objects.all().order_by('-published_at')  # newest first
    return render(request, 'news/article_list.html', {'blogs': blogs})

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    return render(request, 'news/article_detail.html', {'article': article})

# views.py
@login_required
@require_POST
def add_article_comment(request, slug):
    article = get_object_or_404(Article, slug=slug)
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.user = request.user
        comment.save()
        
        # Render the comment HTML
        html = render_to_string(
            'news/partial/comment.html',
            {
                'comment': comment,
                'user': request.user
            },
            request=request
        )
        print(({
            'status': 'success',
            'html': html,
            'comment_count': article.comments.filter(parent__isnull=True).count(),
            'comment_id': comment.id
        }))
        return JsonResponse({
            'status': 'success',
            'html': html,
            'comment_count': article.comments.filter(parent__isnull=True).count(),
            'comment_id': comment.id
        })
    
    return JsonResponse({
        'status': 'error',
        'errors': form.errors.get_json_data()
    }, status=400)

@login_required
@require_POST
def add_article_reply(request, parent_id):
    if request.method == "POST":
        parent_comment = get_object_or_404(Comment, id=parent_id)
        content = request.POST.get("content", "").strip()
        if content:
            # Create reply
            reply = Comment.objects.create(
                user=request.user,
                article=parent_comment.article,
                content=content,
                parent=parent_comment
            )
            # Render reply HTML
            try:
                html = render_to_string(
                    "news/partial/reply.html",
                    {"reply": reply, "user": request.user},
                    request=request
                )
            except Exception as e:
                print("Error rendering reply template:", e)
                html = ""
            return JsonResponse({"status": "success", "html": html})
    return JsonResponse({"status": "error", "html": ""})  

@login_required
@require_POST
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    # Only comment owner can edit
    if request.user != comment.user:
        return JsonResponse({"status": "error", "message": "Permission denied"})

    content = request.POST.get("content", "").strip()

    if not content:
        return JsonResponse({"status": "error", "message": "Empty comment"})

    comment.content = content
    comment.save()

    return JsonResponse({
        "status": "success",
        "content": comment.content
    })

@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    print(comment)
    if request.user != comment.user:
        return JsonResponse({"status": "error"})
    comment.delete()
    return JsonResponse({"status": "success"})

@login_required
@require_POST
def delete_reply(request, reply_id):
    if request.method == "POST":
        reply = get_object_or_404(Comment, id=reply_id)
        if reply.user != request.user:
            return JsonResponse({
                "status": "error",
                "message": "Permission denied"
            })
        reply.delete()
        return JsonResponse({
            "status": "success",
            "reply_id": reply_id
        })
    return JsonResponse({"status": "error"})

@login_required
def toggle_like(request, slug):
    article = get_object_or_404(Article, slug=slug)
    user = request.user
    if user in article.likes.all():
        article.likes.remove(user)
        liked = False
    else:
        article.likes.add(user)
        liked = True
    return JsonResponse({
        'liked': liked,
        'like_count': article.likes.count()
    })

def user_blogs(request, username):
    user = get_object_or_404(User, username=username)
    blogs = Article.objects.filter(author=user).order_by('-published_at')
    return render(request, 'news/user_article.html', {'blogs': blogs, 'filtered_user': user})


def book_list(request):
    books = Book.objects.filter(is_available=True)
    return render(request, 'news/book_list.html', {'books': books})

@login_required
def puzzle_list(request):
    profile = request.user.userprofile  # directly use userprofile

    # If profile doesn't exist (just in case), create with free trial
    if not profile.free_premium_start:
        profile.free_premium_start = timezone.now()
        profile.save()

    # Check for active premium or free trial
    if profile.has_active_premium():
        if not profile.is_premium:
            # User is on free trial
            remaining_days = 2 - (timezone.now() - profile.free_premium_start).days
            messages.info(request, f"You're using Freemium! {remaining_days} day(s) left.")
    else:
        # Trial expired and not premium
        messages.warning(request, "Your free trial has expired. Buy premium to continue!")
        return redirect('buy_premium')

    # Fetch puzzles and solved puzzle IDs
    puzzles = Puzzle.objects.order_by('id')
    solved_ids = PuzzleSolve.objects.filter(user=request.user).values_list('solve_puzzle_id', flat=True)

    return render(request, 'news/puzzles.html', {
        'puzzles': puzzles,
        'solved_ids': list(solved_ids),
    })
    

def find_the_square(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        correct = int(request.POST.get('correct', 0))
        wrong = int(request.POST.get('wrong', 0))

        BoardVision.objects.create(
            user=request.user,
            positive_value=correct,
            negative_value=wrong
        )
        return JsonResponse({'status': 'success'})

    # Top 5 players based on score = correct - wrong
    top_players = (
        BoardVision.objects
        .values('user__username')
        .annotate(
            total_correct=Sum('positive_value'),
            total_wrong=Sum('negative_value'),
            score=ExpressionWrapper(Sum('positive_value') - Sum('negative_value'), output_field=IntegerField())
        )
        .order_by('-score')[:5]
    )

    return render(request, 'news/find_square.html', {
        'top_players': top_players
    })

    
    
    
def buy_premium(request):
    return render(request, 'news/buy_premium.html')

####################### Extra Remove after payment integration #######################
@login_required
def submit_premium_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        trx_id = request.POST.get('trx_id')

        # Save payment info to user's profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.phone = phone
        profile.trx_id = trx_id
        profile.payment_requested_at = timezone.now()
        profile.save()

        return render(request, 'news/premium_thankyou.html')

    return redirect('buy_premium')
############################################################

@login_required
@csrf_exempt
@premium_required
def mark_puzzle_solved(request, puzzle_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            time_taken = data.get('time_taken')

            puzzle = Puzzle.objects.get(pk=puzzle_id)

            solve, created = PuzzleSolve.objects.get_or_create(
                user=request.user,
                solve_puzzle=puzzle,
                defaults={'time_taken': time_taken}
            )
            solve.wrong_attempts += 1
            solve.made_mistake = True
            solve.save()
            if not created and time_taken is not None:
                solve.time_taken = time_taken
                solve.save()

            return JsonResponse({
                'status': 'ok', 
                'time_taken': time_taken, 
                'wrong_attempts': solve.wrong_attempts,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'invalid request'}, status=400)


def games(request):
    return render(request, 'news/games.html', {})



@login_required
def progress_profile(request):
    solves = PuzzleSolve.objects.filter(user=request.user).order_by('solved_at')

    # X-axis: Puzzle titles
    labels = [solve.solve_puzzle.title.split('.')[0] for solve in solves]

    # Y-axis: Time taken for each puzzle
    times = [solve.time_taken for solve in solves]
    puzzles_solved = PuzzleSolve.objects.filter(user=request.user).count()
    user_games = UploadedGame.objects.filter(uploaded_by=request.user).order_by("-created_at")
    user_blogs = Article.objects.filter(author=request.user).order_by("-published_at")
    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(times),
        'puzzles_solved': puzzles_solved,
        'average_time': round(sum(times) / len(times), 2) if times else 0,
        'user_games': user_games,
        'user_blogs': user_blogs,
    }

    return render(request, 'news/progress.html', context)



#users
def generate_otp():
    return str(random.randint(10000, 99999))


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .forms import EmailLoginForm

def register_view(request):
    form = EmailLoginForm(request.POST or None, is_register=True)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"].lower()
        password = form.cleaned_data["password"]

        username_from_email = email.split("@")[0]

        username = username_from_email
        counter = 1

        while User.objects.filter(username=username).exists():
            username = f"{username_from_email}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)
        return redirect("home")

    return render(request, "news/register.html", {"form": form})


def login_view(request):
    form = EmailLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"].lower()
        password = form.cleaned_data["password"]
        try:
            user = User.objects.get(email=email)
            user_auth = authenticate(
                request,
                username=user.username,
                password=password
            )
            if user_auth is not None:
                login(request, user_auth)
                return redirect("home")
            else:
                form.add_error("password", "Incorrect password.")
        except User.DoesNotExist:
            form.add_error("email", "No account found with this email.")
    return render(request, "news/login.html", {"form": form})

@login_required
@csrf_exempt
def edit_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            profile = form.save(commit=False)
            if 'image-clear' in request.POST:
                profile.image = None
            elif 'image' in request.FILES:
                profile.image = request.FILES['image']            
            profile.save()
            user = profile.user
            user.first_name = form.cleaned_data.get('first_name', user.first_name)
            user.last_name = form.cleaned_data.get('last_name', user.last_name)
            user.email = form.cleaned_data.get('email', user.email)
            user.save()
            return redirect('progress')
    else:
        form = ProfileEditForm(instance=profile, user=request.user)

    return render(request, 'news/edit_profile.html', {'form': form})

    
def logout_view(request):
    logout(request)
    return redirect('login') 


def custom_404(request, exception):
    return render(request, 'news/404.html', status=404)







# trial section for game upload, dont push to github
from .forms import *
from .models import UploadedGame, GameComment

@login_required
def game_page(request):
    if request.method == 'POST':
        form = UploadedGameForm(request.POST, request.FILES)
        if form.is_valid():
            game = form.save(commit=False)
            game.uploaded_by = request.user
            game.save()
            # Return saved PGN so JS can render moves
            return JsonResponse({
                'success': True,
                'title': game.title,
                'pgn': game.pgn,
                'white_player': game.white_player,
                'black_player': game.black_player,
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    else:
        form = UploadedGameForm()

    return render(request, 'news/game_page.html', {'game_form': form})

@login_required
def fetch_chesscom_games(request):
    if request.method == "POST":
        username = request.POST.get("username")
        year = request.POST.get("year")
        month = request.POST.get("month")
        if not (username and year and month):
            return JsonResponse({'success': False, 'error': 'Missing parameters'}, status=400)

        # Convert month/year to int
        try:
            year = int(year)
            month = int(month)
        except:
            return JsonResponse({'success': False, 'error': 'Invalid month/year'}, status=400)

        import requests
        url = f"https://api.chess.com/pub/player/{username}/games/{year}/{month:02d}"
        r = requests.get(url)

        if r.status_code != 200:
            return JsonResponse({'success': False, 'error': f'Failed to fetch: {r.status_code}'}, status=r.status_code)

        data = r.json()
        games_list = []
        for g in data.get("games", []):
            games_list.append({
                "white": g["white"]["username"],
                "black": g["black"]["username"],
                "url": g.get("url", "#"),
                "pgn": g.get("pgn", ""),   # ← ADD THIS
                "end_time": g.get("end_time")
            })

        return JsonResponse({'success': True, 'games': games_list})
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

@login_required
def save_chesscom_game(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        white = request.POST.get('white')
        black = request.POST.get('black')
        url = request.POST.get('url')
        end_time = request.POST.get('end_time')  # timestamp
        title = request.POST.get('title', f"{white} vs {black}")

        if not all([username, white, black, url, end_time]):
            return JsonResponse({'success': False, 'error': 'Missing data'}, status=400)

        # Save the game
        game = UploadedGame.objects.create(
            uploaded_by=request.user,
            title=title,
            pgn=request.POST.get('pgn', ''),
            white_player=white,
            black_player=black,
        )

        # Return redirect URL to game details
        return JsonResponse({
            'success': True,
            'redirect_url': reverse('game_detail', args=[game.slug_link])
        })

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def all_games(request):
    games = UploadedGame.objects.all().order_by("-created_at")
    return render(request, 'news/all_games.html', {'games': games})

def search_games(request):
    query = request.GET.get("q", "")
    games = UploadedGame.objects.filter(title__icontains=query)
    html = render_to_string("news/game_cards.html", {"games": games}, request=request)
    return JsonResponse({"html": html})



def game_detail(request, slug):
    game = get_object_or_404(UploadedGame, slug_link=slug)
    # Prepare comments
    comments = GameComment.objects.filter(game=game).values(
        'id', 'user__username', 'move_number', 'comment',
    )
    # Initialize empty form for adding comments
    form = GameCommentForm()
    
    return render(request, 'news/game_detail.html', {
        'game': game,
        'comments_json': list(comments),
        'form': form
    })

@login_required
@csrf_exempt
def add_comment(request, slug):
    if request.method == "POST":
        user = request.user
        game = get_object_or_404(UploadedGame, slug_link=slug)

        form = GameCommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = user
            new_comment.game = game
            new_comment.save()

            return JsonResponse({
                "status": "success",
                "username": user.username,
                "move_number": new_comment.move_number,
                "comment": new_comment.comment,
            })
        else:
            return JsonResponse({
                "status": "error",
                "errors": form.errors
            }, status=400)

    return JsonResponse({"status": "error"}, status=400)

# End of trial section


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import json
import hashlib
from .services.cache import cached_analyze_fen

@csrf_exempt
def analyze_position(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            fen = data.get("fen")
            
            if not fen:
                return JsonResponse({"error": "No FEN provided"}, status=400)
            
            # Generate cache key
            cache_key = f"analysis_{hashlib.md5(fen.encode()).hexdigest()}"
            
            # Try to get from cache first
            result = cache.get(cache_key)
            
            if result is None:
                # If not in cache, analyze and store
                result = cached_analyze_fen(fen)
                cache.set(cache_key, result, timeout=300)  # Cache for 5 minutes
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)




def all_events(request):
    return render(request, 'news/events.html')

def events_json(request):
    events = Events.objects.all()
    event_list = []
    for event in events:
        event_list.append({
            'title': event.title,
            'start': event.start.isoformat(),
            'end': event.end.isoformat(),
            'description': event.description,
        })
    return JsonResponse(event_list, safe=False)

def add_event(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        start = request.POST.get('start')
        end = request.POST.get('end')

        event = Events.objects.create(
            title=title,
            description=description,
            start=start,
            end=end
        )
        return JsonResponse({'status': 'success', 'event_id': event.id})
    return JsonResponse({'status': 'error'}, status=400)


import json
from django.core.serializers.json import DjangoJSONEncoder

def memory_view(request):
    positions = MemoryPosition.objects.all().values('fen')

    positions_json = json.dumps(list(positions), cls=DjangoJSONEncoder)

    return render(request, "news/memory.html", {
        "positions_json": positions_json
    })

def memory_api(request):
    mode = request.GET.get('mode', 'easy')

    if mode == 'progressive':
        positions = MemoryPosition.objects.all()
    else:
        positions = MemoryPosition.objects.filter(difficulty=mode)

    data = list(positions.values('fen', 'difficulty'))

    return JsonResponse(data, safe=False)


############################## Chat system (will be implemented) ##########################################
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
from .models import Message


# 🔹 Main Chat Page
@login_required
def chat(request, username=None):
    users = User.objects.exclude(id=request.user.id)
    other_user = None

    if username:
        other_user = User.objects.get(username=username)

    # 🔥 Send message (AJAX)
    if request.method == "POST":
        content = request.POST.get("content")

        if other_user and content:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content
            )

        return JsonResponse({"status": "ok"})

    return render(request, "news/chat/chat.html", {
        "users": users,
        "other_user": other_user
    })


# 🔹 API for realtime messages
@login_required
def get_messages(request, username):
    other_user = User.objects.get(username=username)

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by("timestamp")

    data = []

    for msg in messages:
        data.append({
            "content": msg.content,
            "is_me": msg.sender == request.user
        })

    return JsonResponse({"messages": data})
###########################################################################################