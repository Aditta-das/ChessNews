from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=200)
    content = CKEditor5Field('Text', config_name='extends')
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    published_at = models.DateTimeField(auto_now_add=True)
    is_big_news = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_big_news:
        # Unmark all other articles
            Article.objects.filter(is_big_news=True).exclude(pk=self.pk).update(is_big_news=False)

        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class TopPlayerImg(models.Model):
    name = models.CharField(max_length=100)
    fide_id = models.CharField(max_length=20, unique=True)
    image = models.ImageField(upload_to='player_images/', null=True, blank=True)

    def __str__(self):
        return self.name


class TournamentBanner(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='banners/')
    link = models.URLField(blank=True, null=True)
    show_banner = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.show_banner:
            TournamentBanner.objects.filter(show_banner=True).exclude(pk=self.pk).update(show_banner=False)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.title


class BangladeshiTopPlayer(models.Model):
    RANK_CHOICES = [(i, str(i)) for i in range(1, 11)]  # 1 to 10

    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='bangladesh_players/', null=True, blank=True)
    fide_rating = models.PositiveIntegerField()
    rank = models.PositiveSmallIntegerField(choices=RANK_CHOICES, unique=True)

    def __str__(self):
        return f"#{self.rank} - {self.name}"



class Book(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=200)
    author_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)  # e.g., 99999.99
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Book.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



chess_move_validator = RegexValidator(
    regex=r'^([PNBRQK]?[a-h]?[1-8]?x?[a-h][1-8](=[NBRQ])?[+#]?\.?\s*)+$',
    message="Solution must be valid SAN moves, like 'Rxh2+ Kxh2 Rh8#'"
)

class Puzzle(models.Model):
    TURN_CHOICES = [
        ('w', 'White to play'),
        ('b', 'Black to play')
    ]
    
    title = models.CharField(max_length=100)
    fen = models.CharField(max_length=100)
    turn = models.CharField(max_length=1, choices=TURN_CHOICES, default='w')
    solution = models.TextField(
        help_text="Moves in SAN, like 'Rxh2+ Kxh2 Rh8#'",
        validators=[chess_move_validator]
    )
    difficulty = models.CharField(max_length=10, choices=[
        ('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')
    ])
    quote = models.ForeignKey(
        'Quote',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.title}"

    def save(self, *args, **kwargs):
        parts = self.fen.strip().split()
        if len(parts) == 6:
            parts[1] = self.turn
            self.fen = ' '.join(parts)
        else:
            print(f"⚠️ Warning: FEN is invalid: {self.fen}")
        super().save(*args, **kwargs)     
    
    
class PuzzleSolve(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    solve_puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    solved_at = models.DateTimeField(auto_now_add=True)
    time_taken = models.IntegerField(null=True, blank=True)
    made_mistake = models.BooleanField(default=False)
    wrong_attempts = models.IntegerField(default=0)  # ✅ New field

    class Meta:
        unique_together = ('user', 'solve_puzzle')

    def __str__(self):
        return f"{self.user.username} solved {self.solve_puzzle.title}"


    
class Quote(models.Model):
    name = models.CharField(max_length=50)
    Quote = CKEditor5Field('Text', config_name='extends')
    
    def __str__(self):
        return self.name
    
class BoardVision(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    positive_value = models.PositiveIntegerField(default=0)
    negative_value = models.PositiveIntegerField(default=0) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.positive_value}✓ / {self.negative_value}✗"

# users
class EmailOTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.otp}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_premium = models.BooleanField(default=False)
    
    # Payment info
    phone = models.CharField(max_length=20, blank=True, null=True)
    trx_id = models.CharField("Transaction ID", max_length=100, blank=True, null=True)
    payment_requested_at = models.DateTimeField(blank=True, null=True)

    # ✅ Profile Image
    image = models.ImageField(upload_to="profile_images/", default="profile_images/default.png", blank=True, null=True)
    bio = models.CharField(max_length=200, blank=True, null=True, default="Add Description Here")
    
    def __str__(self):
        return f"{self.user} - Premium: {self.is_premium}"
    
    def save(self, *args, **kwargs):
        if not self.image:
            self.image = 'profile_images/default.png'
        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance)