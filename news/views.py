from django.shortcuts import render, get_object_or_404, redirect
from .models import Article, TopPlayerImg, TournamentBanner, BangladeshiTopPlayer, Book, Puzzle, EmailOTP, PuzzleSolve
from django.contrib.auth.models import User
from django.contrib.auth import logout
import requests, random, json
from .forms import EmailLoginForm
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

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

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    return render(request, 'news/detail.html', {'article': article})


def book_list(request):
    books = Book.objects.filter(is_available=True)
    return render(request, 'news/book_list.html', {'books': books})


def puzzle_list(request):
    puzzles = Puzzle.objects.order_by('id')
    solved_ids = []
    if request.user.is_authenticated:
        solved_ids = PuzzleSolve.objects.filter(user=request.user).values_list('solve_puzzle_id', flat=True)
    else:
        return redirect('login')
    return render(request, 'news/puzzles.html', {
        'puzzles': puzzles,
        'solved_ids': list(solved_ids),
    })


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

            if not created and time_taken is not None:
                solve.time_taken = time_taken
                solve.save()

            return JsonResponse({'status': 'ok', 'time_taken': time_taken})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'invalid request'}, status=400)


@login_required
def progress_profile(request):
    solves = PuzzleSolve.objects.filter(user=request.user).order_by('solved_at')

    # X-axis: Puzzle titles
    labels = [solve.solve_puzzle.title.split('.')[0] for solve in solves]

    # Y-axis: Time taken for each puzzle
    times = [solve.time_taken for solve in solves]

    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(times),
    }

    return render(request, 'news/progress.html', context)



#users
def generate_otp():
    return str(random.randint(10000, 99999))


def login_view(request):
    form = EmailLoginForm(request.POST or None)
    show_otp = False
    email_sent = False

    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        otp_input = request.POST.get('otp')

        try:
            user = User.objects.get(email=email)
            user_auth = authenticate(request, username=user.username, password=password)
            if user_auth is not None:
                login(request, user_auth)
                return redirect('home')
            else:
                form.add_error('password', 'Invalid password')
        except User.DoesNotExist:
            show_otp = True
            otp_obj, created = EmailOTP.objects.get_or_create(email=email)
            if created or otp_input == "":
                otp = random.randint(10000, 99999)
                otp_obj.otp = otp
                otp_obj.save()
                send_mail(
                    subject='Your OTP Code',
                    message=f'Your OTP is: {otp}',
                    from_email='adi@gmail.com',
                    recipient_list=[email],
                    fail_silently=False,
                )
                email_sent = True
            elif otp_input and otp_input == str(otp_obj.otp):
                # Validate new username
                if User.objects.filter(username=username).exists():
                    form.add_error('username', 'Username already taken')
                else:
                    user = User.objects.create_user(username=username, email=email, password=password)
                    otp_obj.delete()
                    login(request, user)
                    return redirect('home')
            else:
                form.add_error('otp', 'Invalid OTP')

    return render(request, 'news/login.html', {'form': form, 'show_otp': show_otp, 'email_sent': email_sent})

    
def logout_view(request):
    logout(request)
    return redirect('login') 