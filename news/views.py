from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
import chess.pgn
from io import StringIO
from .models import Article, TopPlayerImg, \
    TournamentBanner, BangladeshiTopPlayer, Book, \
        Puzzle, EmailOTP, PuzzleSolve, UserProfile, \
            BoardVision, UploadedGame, GameComment, Events, Message, \
                MemoryPosition, ChessPuzzleSolve, DailyPuzzle, Coach
from django.contrib.auth.models import User
from django.contrib.auth import logout
import requests, random, json
from .forms import EmailLoginForm, ProfileEditForm, ArticleForm, GameCommentForm
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .decorators import premium_required
from django.utils import timezone
from django.db.models import Sum, F, ExpressionWrapper, IntegerField
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.views.decorators.cache import never_cache
from .services.engine import analyze_fen, analyze_fens

@csrf_exempt
def api_world_players(request):
    players = cache.get('world_players_api')
    if not players:
        try:
            response = requests.get(
                # 'https://fide-v4.vercel.app/top_players?limit=5',
                'http://0.0.0.0:10000/top_players?limit=5',
                timeout=20
            )
            if response.status_code == 200:
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
    top_bd_players = cache.get('bd_players_api')
    
    if not top_bd_players:
        try:
            bd_response = requests.get(
                # 'https://fide-v4.vercel.app/top_country_players?limit=5&country=BAN&gender=M',
                'http://0.0.0.0:10000/top_country_players?limit=5&country=BAN&gender=M',
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

# Add these two new views to your views.py

@csrf_exempt
def api_world_women_players(request):
    players = cache.get('world_women_players_api')
    if not players:
        try:
            response = requests.get(
                # 'https://fide-v4.vercel.app/top_players?limit=5&gender=women',
                'http://0.0.0.0:10000/top_players?limit=5&gender=women',
                timeout=20
            )
            if response.status_code == 200:
                players = response.json()
                print(players)
                cache.set('world_women_players_api', players, 300)
            else:
                players = []
        except Exception as e:
            print("WORLD WOMEN API ERROR:", e)
            players = []

    world_map = {p.fide_id: p for p in TopPlayerImg.objects.all()}

    for player in players:
        obj = world_map.get(player.get('fide_id'))
        player['image_url'] = obj.image.url if obj and obj.image else None
        player['rank']    = int(player.get('rank', 0))
        player['rating']  = int(player.get('rating', 0))
        player['country'] = player.get('country', '')

    return JsonResponse({'players': players, 'success': True})


@csrf_exempt
def api_bd_women_players(request):
    players = cache.get('bd_women_players_api')
    if not players:
        try:
            response = requests.get(
                # 'https://fide-v4.vercel.app/top_country_players?limit=5&country=BAN&gender=F',
                'http://0.0.0.0:10000/top_country_players?limit=5&country=BAN&gender=F',
                timeout=20
            )
            if response.status_code == 200:
                players = response.json()
                cache.set('bd_women_players_api', players, 300)
            else:
                players = []
        except Exception as e:
            print("BD WOMEN API ERROR:", e)
            players = []

    bd_map = {p.fide_id: p for p in BangladeshiTopPlayer.objects.all()}

    for player in players:
        obj = bd_map.get(player.get('fide_id'))
        player['image_url'] = obj.image.url if obj and obj.image else None
        player['rank']    = int(player.get('rank', 0))
        player['rating']  = int(player.get('rating', 0))
        player['country'] = 'BAN'

    return JsonResponse({'players': players, 'success': True})

from django.utils import timezone
from datetime import date
def home(request):
    # ── Big news ─────────────────────────────
    big_news = Article.objects.filter(is_big_news=True).first()
    small_news = Article.objects.order_by('-published_at')
    if big_news:
        small_news = small_news.exclude(id=big_news.id)
    small_news = small_news[:6]

    best_reporter = User.objects.order_by('-article__id').first()

    banner = TournamentBanner.objects.filter(
        show_banner=True
    ).order_by('-created_at').first()

    home_banner = TournamentBanner.objects.filter(
        inside_home=True
    ).order_by('-created_at').first()
    
    today = timezone.localdate()

    first_day = date(today.year, today.month, 1)

    if today.month == 12:
        next_month = date(today.year + 1, 1, 1)
    else:
        next_month = date(today.year, today.month + 1, 1)

    tournaments = Events.objects.filter(
        start__lt=next_month,
        end__date__gte=first_day
    ).order_by("start")
    
    daily_entry = DailyPuzzle.objects.select_related('puzzle').filter(
        date=today
    ).first()

    daily_puzzle = daily_entry.puzzle if daily_entry else None
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            profile = None

    # ─────────────────────────────────────────
    # Render
    # ─────────────────────────────────────────
    return render(request, 'news/home1.html', {
        'big_news': big_news,
        'small_news': small_news,
        'best_reporter': best_reporter,
        'banner': banner,
        'home_banner': home_banner,
        'tournaments': tournaments,
        'profile': profile,
        'daily_puzzle': daily_puzzle,
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


# def games(request):
#     return render(request, 'news/games.html', {})



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
from .forms import ForgotStep1Form
from .forms import ForgotStep2Form
from .models import SecurityQuestion
from .forms import ResetPasswordForm

def register_view(request):
    form = EmailLoginForm(request.POST or None, is_register=True)
 
    if request.method == "POST" and form.is_valid():
        email    = form.cleaned_data["email"].lower()
        password = form.cleaned_data["password"]
 
        base = email.split("@")[0]
        username, counter = base, 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1
 
        user = User.objects.create_user(username=username, email=email, password=password)
 
        # Save security question (posted as sq_question / sq_answer)
        question = request.POST.get("sq_question", "").strip()
        answer   = request.POST.get("sq_answer",   "").strip().lower()
        if question and answer:
            SecurityQuestion.objects.create(user=user, question=question, answer=answer)
 
        login(request, user)
        return redirect("home")
 
    return render(request, "news/register.html", {"form": form})
 
 
def forgot_step1(request):
    form = ForgotStep1Form(request.POST or None)
    if request.method == "POST" and form.is_valid():
        request.session["pw_reset_email"] = form.cleaned_data["email"]
        request.session.pop("pw_reset_verified", None)
        return redirect("forgot_step2")
    return render(request, "news/forgot_step1.html", {"form": form})
 
 
def forgot_step2(request):

    email = request.session.get("pw_reset_email")
    if not email:
        return redirect("forgot_step1")
 
    try:
        user = User.objects.get(email=email)
        sq   = user.security_question
    except Exception:
        request.session.pop("pw_reset_email", None)
        return redirect("forgot_step1")
 
    form  = ForgotStep2Form(request.POST or None)
    error = None
 
    if request.method == "POST" and form.is_valid():
        if sq.check_answer(form.cleaned_data["answer"]):
            request.session["pw_reset_verified"] = True
            return redirect("forgot_reset")
        else:
            error = "Incorrect answer. Please try again."
 
    return render(request, "news/forgot_step2.html", {
        "form": form, "question": sq.get_question_display(), "error": error,
    })
 
 
def forgot_reset(request):
    
    email    = request.session.get("pw_reset_email")
    verified = request.session.get("pw_reset_verified")
 
    if not email or not verified:
        return redirect("forgot_step1")
 
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return redirect("forgot_step1")
 
    form = ResetPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user.set_password(form.cleaned_data["new_password"])
        user.save()
        request.session.pop("pw_reset_email",    None)
        request.session.pop("pw_reset_verified", None)
        messages.success(request, "Password reset successfully. Please log in.")
        return redirect("login")
 
    return render(request, "news/forgot_reset.html", {"form": form})


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
                form.add_error("password", "Incorrect email or password.")
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

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.templatetags.static import static

from .forms import UploadedGameForm
from .models import UploadedGame

import requests
import chess
import chess.pgn

from io import StringIO


# ============================================================
# Player thumbnail helper
# ============================================================

def get_player_thumbnail(player_name):
    """
    Find player by name from FastAPI and return the Django
    static URL for the player's thumbnail.

    Example:

        API:
            playerImages/carlsen__magnus.jpeg

        Returns:
            /static/playerImages/carlsen__magnus.jpeg

    If player is not found, returns None.
    """

    if not player_name:
        return None

    player_name = player_name.strip()

    if not player_name:
        return None

    try:
        response = requests.get(
            "http://127.0.0.1:10000/players/by-name",
            params={
                "name": player_name
            },
            timeout=5
        )

        if response.status_code != 200:
            return None

        data = response.json()
        # Expected response:
        #
        # {
        #   "ok": true,
        #   "err": null,
        #   "data": [
        #       {
        #           "name": "Carlsen, Magnus",
        #           "thumbUrl": "playerImages/carlsen__magnus.jpeg"
        #       }
        #   ]
        # }

        if not data.get("ok"):
            return None

        players = data.get("data")
        # if not isinstance(players, list):
        #     return None

        # if not players:
        #     return None

        # # First matching result
        # player = players[0]
        # print(player)
        print("========== PLAYER ==========")
        print(players)

        if not isinstance(players, dict):
            print("PLAYER DATA IS NOT A DICT")
            return None

        player = players

        print("PLAYER:", player)

        thumb_url = player.get("thumbUrl")

        print("THUMB URL:", thumb_url)

        if not thumb_url:
            print("NO THUMB URL")
            return None

        # IMPORTANT:
        # Do NOT use the 127.0.0.1 URL in the browser.
        # Convert:
        #
        # http://127.0.0.1:10000/playerImages/carlsen__magnus.jpeg
        #
        # to:
        #
        # /static/playerImages/carlsen__magnus.jpeg

        if thumb_url.startswith("http://127.0.0.1:10000/"):
            thumb_url = thumb_url.replace(
                "http://127.0.0.1:10000/",
                "/static/",
                1
            )

        elif thumb_url.startswith("/playerImages/"):
            thumb_url = "/static" + thumb_url

        elif thumb_url.startswith("playerImages/"):
            thumb_url = "/static/" + thumb_url

        print("FINAL IMAGE URL:", thumb_url)

        return thumb_url

    except requests.RequestException as e:
        print(
            f"[player thumbnail] API request failed for "
            f"{player_name}: {e}"
        )
        return None

    except Exception as e:
        print(
            f"[player thumbnail] Error for "
            f"{player_name}: {e}"
        )
        return None


# ============================================================
# Game page
# ============================================================

@login_required
def game_page(request):

    if request.method == 'POST':

        form = UploadedGameForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            game = form.save(commit=False)

            # Attach current user
            game.uploaded_by = request.user

            # Save game
            game.save()

            # Redirect to game detail
            return redirect(
                'game_detail',
                slug=game.slug_link
            )

        # Invalid form
        return render(
            request,
            'news/game_page.html',
            {
                'game_form': form
            }
        )

    # GET
    form = UploadedGameForm()

    return render(
        request,
        'news/game_page.html',
        {
            'game_form': form
        }
    )


# ============================================================
# Upload PGN file
# ============================================================

@login_required
def upload_pgn_file(request):

    if request.method != "POST":

        return JsonResponse({
            "success": False,
            "error": "Invalid request"
        })

    file = request.FILES.get("file")

    if not file:

        return JsonResponse({
            "success": False,
            "error": "No PGN file selected"
        })

    try:

        pgn_text = file.read().decode("utf-8")

        pgn_io = StringIO(pgn_text)

        game = chess.pgn.read_game(pgn_io)

        # No game
        if game is None:

            return JsonResponse({
                "success": False,
                "error": "Invalid PGN file"
            })

        # Check second game
        second_game = chess.pgn.read_game(pgn_io)

        if second_game:

            return JsonResponse({
                "success": False,
                "error":
                    "This file contains multiple games. "
                    "Upload one game only."
            })

        white = game.headers.get(
            "White",
            ""
        )

        black = game.headers.get(
            "Black",
            ""
        )

        title = f"{white} vs {black}"

        uploaded_game = UploadedGame.objects.create(
            uploaded_by=request.user,
            title=title,
            pgn=pgn_text,
            white_player=white,
            black_player=black
        )

        return JsonResponse({
            "success": True,
            "redirect_url": reverse(
                "game_detail",
                args=[
                    uploaded_game.slug_link
                ]
            )
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "error": str(e)
        })


# ============================================================
# Fetch Chess.com games
# ============================================================

@login_required
def fetch_chesscom_games(request):

    if request.method != "POST":

        return JsonResponse({
            'success': False,
            'error': 'Invalid method'
        }, status=405)

    username = request.POST.get("username")
    year = request.POST.get("year")
    month = request.POST.get("month")

    if not username or not year or not month:

        return JsonResponse({
            'success': False,
            'error': 'Missing parameters'
        }, status=400)

    try:

        year = int(year)
        month = int(month)

    except (ValueError, TypeError):

        return JsonResponse({
            'success': False,
            'error': 'Invalid month/year'
        }, status=400)

    url = (
        f"https://api.chess.com/pub/player/"
        f"{username}/games/{year}/{month:02d}"
    )

    try:

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "ChessNewsBD/1.0"
            }
        )

    except requests.RequestException as e:

        return JsonResponse({
            'success': False,
            'error': f'Connection failed: {str(e)}'
        }, status=502)

    if response.status_code != 200:

        return JsonResponse({
            'success': False,
            'error':
                f'Failed to fetch: {response.status_code}'
        }, status=response.status_code)

    data = response.json()

    games_list = []

    for game in data.get("games", []):

        games_list.append({
            "white":
                game.get("white", {}).get(
                    "username",
                    ""
                ),

            "black":
                game.get("black", {}).get(
                    "username",
                    ""
                ),

            "url":
                game.get(
                    "url",
                    "#"
                ),

            "pgn":
                game.get(
                    "pgn",
                    ""
                ),

            "end_time":
                game.get(
                    "end_time"
                ),
        })

    return JsonResponse({
        'success': True,
        'games': games_list
    })


# ============================================================
# Save Chess.com game
# ============================================================

@login_required
def save_chesscom_game(request):

    if request.method != 'POST':

        return JsonResponse({
            'success': False,
            'error': 'Invalid request'
        }, status=405)

    username = request.POST.get(
        'username'
    )

    white = request.POST.get(
        'white'
    )

    black = request.POST.get(
        'black'
    )

    url = request.POST.get(
        'url'
    )

    end_time = request.POST.get(
        'end_time'
    )

    pgn = request.POST.get(
        'pgn',
        ''
    )

    title = request.POST.get(
        'title'
    )

    if not title:

        title = f"{white} vs {black}"

    # Validate
    if not all([
        username,
        white,
        black,
        url,
        end_time
    ]):

        return JsonResponse({
            'success': False,
            'error': 'Missing data'
        }, status=400)

    # Create game
    game = UploadedGame.objects.create(
        uploaded_by=request.user,
        title=title,
        pgn=pgn,
        white_player=white,
        black_player=black,
    )

    return JsonResponse({
        'success': True,
        'redirect_url': reverse(
            'game_detail',
            args=[
                game.slug_link
            ]
        )
    })


def all_games(request):
    games = UploadedGame.objects.all().order_by("-created_at")
    return render(request, 'news/all_games.html', {'games': games})

def search_games(request):
    query = request.GET.get("q", "")
    games = UploadedGame.objects.filter(title__icontains=query)
    html = render_to_string("news/game_cards.html", {"games": games}, request=request)
    return JsonResponse({"html": html})



@csrf_exempt
@require_POST
def analyze_position(request):

    try:

        data = json.loads(request.body)

        fen = data.get("fen")

        if not fen:

            return JsonResponse({
                "error": "FEN is required"
            }, status=400)


        result = analyze_fen(
            fen,
            include_best_move=True
        )


        return JsonResponse(result)


    except Exception as e:

        return JsonResponse({
            "error": str(e)
        }, status=500)

@csrf_exempt
@require_POST
def analyze_game(request):

    try:

        data = json.loads(request.body)

        fens = data.get("fens", [])


        if not isinstance(fens, list):

            return JsonResponse({
                "error": "fens must be a list"
            }, status=400)


        if not fens:

            return JsonResponse({
                "results": []
            })


        if len(fens) > 1000:

            return JsonResponse({
                "error": "Too many positions"
            }, status=400)


        results = analyze_fens(fens)


        return JsonResponse({
            "results": results
        })


    except Exception as e:

        return JsonResponse({
            "error": str(e)
        }, status=500)
        

def game_detail(request, slug):
    game = get_object_or_404(
        UploadedGame,
        slug_link=slug
    )

    comments = GameComment.objects.filter(
        game=game
    ).values(
        'id',
        'user__username',
        'move_number',
        'comment',
    )

    form = GameCommentForm()

    white_player_image = get_player_thumbnail(
        game.white_player
    )

    black_player_image = get_player_thumbnail(
        game.black_player
    )

    return render(
        request,
        'news/game_detail2.html',
        {
            'game': game,
            'comments_json': list(comments),
            'form': form,
            'white_player_image': white_player_image,
            'black_player_image': black_player_image,
        }
    )

from .services.engine import *

@csrf_exempt
@require_POST
def classify_game(request):

    try:

        data = json.loads(request.body)

        fens = data.get("fens", [])
        moves_uci = data.get("moves", [])

        if not isinstance(fens, list) or not isinstance(moves_uci, list):
            return JsonResponse({"error": "fens and moves must be lists"}, status=400)

        if len(fens) != len(moves_uci) + 1:
            return JsonResponse({
                "error": "fens must have exactly one more entry than moves"
            }, status=400)

        if len(moves_uci) > 400:
            return JsonResponse({"error": "Too many moves"}, status=400)

        classifications = analyze_game_with_classification(fens, moves_uci)

        return JsonResponse({"classifications": classifications})

    except Exception as e:

        return JsonResponse({"error": str(e)}, status=500)

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


def all_events(request):
    return render(request, "news/events.html")


def events_json(request):
    start_param = request.GET.get('start')
    end_param   = request.GET.get('end')
 
    qs = Events.objects.all().order_by('start')
    if start_param:
        try:
            from datetime import datetime, timezone
            start_dt = datetime.fromisoformat(start_param.replace('Z', '+00:00'))
            qs = qs.filter(end__gte=start_dt)
        except (ValueError, AttributeError):
            pass
 
    if end_param:
        try:
            from datetime import datetime, timezone
            end_dt = datetime.fromisoformat(end_param.replace('Z', '+00:00'))
            qs = qs.filter(start__lte=end_dt)
        except (ValueError, AttributeError):
            pass
 
    events = []
    for e in qs:
        events.append({
            'id':    e.id,
            'title': e.title,
            'start': e.start.isoformat(),
            'end':   e.end.isoformat(),
            'allDay': False,
            'extendedProps': {
                'source':      'db',
                'description': e.description or '',
                'url':         e.url or '',
                'location':    '',
            }
        })
 
    return JsonResponse(events, safe=False)


@csrf_exempt
def add_event(request):
    """
    Creates a new Event from the calendar modal.
    POST fields: title, description, start, end, url
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'error': 'POST required'}, status=405)
 
    from datetime import datetime, timezone as dt_tz
 
    title       = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    start_str   = request.POST.get('start', '').strip()
    end_str     = request.POST.get('end', '').strip()
    url         = request.POST.get('url', '').strip() or None
 
    if not title:
        return JsonResponse({'status': 'error', 'error': 'Title is required'}, status=400)
 
    if not start_str or not end_str:
        return JsonResponse({'status': 'error', 'error': 'Start and end are required'}, status=400)
 
    try:
        # datetime-local input: "2026-04-17T14:30"
        start_dt = datetime.fromisoformat(start_str)
        end_dt   = datetime.fromisoformat(end_str)
 
        # Make timezone-aware if your DB uses aware datetimes
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=dt_tz.utc)
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=dt_tz.utc)
 
        # Sanity: swap if end < start
        if end_dt < start_dt:
            start_dt, end_dt = end_dt, start_dt
 
    except ValueError as e:
        return JsonResponse({'status': 'error', 'error': f'Invalid date: {e}'}, status=400)
 
    event = Events.objects.create(
        title=title,
        description=description or None,
        start=start_dt,
        end=end_dt,
        url=url,
    )
 
    return JsonResponse({
        'status':   'success',
        'event_id': event.id,
        'title':    event.title,
        'start':    event.start.isoformat(),
        'end':      event.end.isoformat(),
    })

def api_events_data(request):
    cache_key = "events_api"
    data = cache.get(cache_key)
    if not data:
        try:
            response = requests.get(
                "http://0.0.0.0:10000/tournaments",
                timeout=20
            )
            if response.status_code == 200:
                data = response.json()
                cache.set(cache_key, data, 60*24*7)
            else:
                data = {"tournaments": []}
        except Exception as e:
            print("EVENTS API ERROR:", e)
            data = {"tournaments": []}

    return JsonResponse(data)

def api_bd_events_data(request):
    cache_key = "bd_events_api"
    data = cache.get(cache_key)
    if not data:
        try:
            response = requests.get(
                "http://0.0.0.0:10000/get_country_tournaments",
                timeout=20
            )
            if response.status_code == 200:
                data = response.json()
                cache.set(cache_key, data, 60*24*7)
            else:
                data = {"country_tournaments": []}
        except Exception as e:
            print("EVENTS API ERROR:", e)
            data = {"country_tournaments": []}

    return JsonResponse(data)

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


# news/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import DailyPuzzle, ChessPuzzleSolve


def daily_puzzle_view(request):
    today = timezone.localdate()
    daily = (
        DailyPuzzle.objects
        .select_related("puzzle")
        .filter(date=today)
        .first()
    )

    if daily is None:
        return render(request, "news/no_puzzle.html", {"today": today})

    solve = None
    if request.user.is_authenticated:
        solve = daily.solves.filter(user=request.user).first()

    puzzle = daily.puzzle
    explanations = {
        item["san"]: item.get("explanation", "")
        for item in (puzzle.move_explanations or [])
    }

    context = {
        "daily": daily,
        "puzzle": puzzle,
        "solve": solve,
        "puzzle_json": {
            "title": puzzle.title,
            "player1": puzzle.player1,
            "player2": puzzle.player2,
            "fen": puzzle.fen,
            "turn": puzzle.turn,
            "difficulty": puzzle.get_difficulty_display(),
            "hint": puzzle.hint or "",
            "solution_moves": puzzle.solution_moves,
            "move_explanations": explanations,
        },
    }
    return render(request, "news/daily_puzzle.html", context)


@login_required
def submit_solve_view(request, daily_id):
    if request.method != "POST":
        return redirect("daily-puzzle")

    daily = get_object_or_404(DailyPuzzle, pk=daily_id)

    def to_int(value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    wrong_attempts = to_int(request.POST.get("wrong_attempts"), 0)

    ChessPuzzleSolve.objects.get_or_create(
        user=request.user,
        daily_puzzle=daily,
        defaults={
            "time_taken": to_int(request.POST.get("time_taken"), None),
            "wrong_attempts": wrong_attempts,
            "hints_used": to_int(request.POST.get("hints_used"), 0),
            "made_mistake": wrong_attempts > 0,
        },
    )

    messages.success(request, "Result saved.")
    return redirect("daily-puzzle")


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



def PlayBot(request):
    return render(request, "news/playbot.html", {
        
    })
###########################################################################################


def coach_list(request):
    coaches = Coach.objects.filter(is_active=True).order_by("order", "-rating")
    return render(request, "news/academy/coach.html", {"coaches": coaches})


def coach_apply(request):
    if request.method == "POST":
        form = CoachApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Thanks — your application has been submitted. We'll be in touch."
            )
            return redirect("coach_list")
    else:
        form = CoachApplicationForm()
 
    return render(request, "news/academy/coach_apply.html", {"form": form})