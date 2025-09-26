from django.shortcuts import render, get_object_or_404, redirect
from .models import Article, TopPlayerImg, \
    TournamentBanner, BangladeshiTopPlayer, Book, \
        Puzzle, EmailOTP, PuzzleSolve, UserProfile, BoardVision
from django.contrib.auth.models import User
from django.contrib.auth import logout
import requests, random, json
from .forms import EmailLoginForm, ProfileEditForm, ArticleForm
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, F, ExpressionWrapper, IntegerField

def home(request):
    # Big news
    big_news = Article.objects.filter(is_big_news=True).first()
    small_news = Article.objects.exclude(id=big_news.id if big_news else None)[:6]
    best_reporter = User.objects.order_by('-article__id').first()
    
    top_bd_players = BangladeshiTopPlayer.objects.order_by('rank')

    # Fetch top players from FIDE API
    try:
        response = requests.get('https://fide-api.vercel.app/top_players/?limit=5&history=false')
        players = response.json()
    except Exception:
        players = []  # fallback empty list if API fails

    # Attach images from TopPlayerImg model to players if available
    for player in players:
        try:
            img_obj = TopPlayerImg.objects.get(fide_id=player['fide_id'])
            if img_obj.image:
                player['image_url'] = img_obj.image.url
            else:
                player['image_url'] = None
        except TopPlayerImg.DoesNotExist:
            player['image_url'] = None

    # Get the active tournament banner
    banner = TournamentBanner.objects.filter(show_banner=True).order_by('-created_at').first()

    return render(request, 'news/home.html', {
        'big_news': big_news,
        'small_news': small_news,
        'best_reporter': best_reporter,
        'players': players,
        'banner': banner,
        'top_bd_players': top_bd_players
    })

@login_required
def create_article(request):
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user  # logged-in user
            article.save()
            return redirect('article_detail', slug=article.slug)
    else:
        form = ArticleForm()

    return render(request, "news/create_article.html", {"form": form})


def all_blogs(request):
    blogs = Article.objects.all().order_by('-published_at')  # newest first
    return render(request, 'news/article_list.html', {'blogs': blogs})


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    return render(request, 'news/detail.html', {'article': article})


def book_list(request):
    books = Book.objects.filter(is_available=True)
    return render(request, 'news/book_list.html', {'books': books})

def puzzle_list(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_premium:
        return redirect('buy_premium')  # Name of your premium purchase view or page

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
    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(times),
        'puzzles_solved': puzzles_solved,
        'average_time': round(sum(times) / len(times), 2) if times else 0,
    }

    return render(request, 'news/progress.html', context)



#users
def generate_otp():
    return str(random.randint(10000, 99999))


def login_view(request):
    form = EmailLoginForm(request.POST or None)
    # show_otp = False
    # email_sent = False

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # otp_input = request.POST.get('otp')
        username_from_email = email.split('@')[0]

        try:
            user = User.objects.get(email=email)
            user_auth = authenticate(request, username=user.username, password=password)
            if user_auth is not None:
                login(request, user_auth)
                return redirect('home')
            else:
                form.add_error('password', 'Invalid password')
        except User.DoesNotExist:
            # show_otp = True
            # otp_obj, created = EmailOTP.objects.get_or_create(email=email)

            # if created or otp_input == "":
            #     otp = generate_otp()
            #     otp_obj.otp = otp
            #     otp_obj.save()
            #     send_mail(
            #         subject='Your OTP Code',
            #         message=f'Your OTP is: {otp}',
            #         from_email='adittadas00@gmail.com',
            #         recipient_list=[email],
            #         fail_silently=False,
            #     )
            #     email_sent = True

            # elif otp_input and otp_input == str(otp_obj.otp):
            if User.objects.filter(username=username_from_email).exists():
                form.add_error('email', 'Email is already linked to an account. Try logging in.')
            else:
                user = User.objects.create_user(username=username_from_email, email=email, password=password)
                # otp_obj.delete()
                login(request, user)
                return redirect('home')
            # else:
            #     form.add_error('otp', 'Invalid OTP')

    return render(request, 'news/login.html', {
        'form': form,
        # 'show_otp': show_otp,
        # 'email_sent': email_sent
    })


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