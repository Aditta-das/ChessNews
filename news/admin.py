from django.contrib import admin
from django.utils.html import format_html
from .models import Article, \
    Category, TopPlayerImg, TournamentBanner, BangladeshiTopPlayer, \
    Book, Puzzle, EmailOTP, Quote, PuzzleSolve, UserProfile, BoardVision, \
    Ticket, UploadedGame, GameComment, Events, Comment, Message, MemoryPosition, \
        SecurityQuestion, Streak, Coach, CoachApplication
        

admin.site.site_header = "♟️ ChessBD Admin Panel"
admin.site.site_title = "ChessBD"
admin.site.index_title = "Welcome to ChessBD Admin Panel"


def status_badge(value, positive_words=(), negative_words=(), neutral_color="badge-gray"):
    text = str(value)
    lowered = text.lower()
    color = neutral_color
    if any(word in lowered for word in positive_words):
        color = "badge-green"
    elif any(word in lowered for word in negative_words):
        color = "badge-red"
    return format_html('<span class="badge {}">{}</span>', color, text)


@admin.register(SecurityQuestion)
class SecurityQuestionAdmin(admin.ModelAdmin):
    list_per_page = 25
    save_on_top = True


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_at')
    search_fields = ('title', 'author__username')
    ordering = ('-published_at',)
    list_filter = ('author',)
    date_hierarchy = 'published_at'
    list_per_page = 25
    save_on_top = True
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_per_page = 25
    save_on_top = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_per_page = 25


@admin.register(TopPlayerImg)
class TopPlayerImgAdmin(admin.ModelAdmin):
    list_per_page = 25


@admin.register(TournamentBanner)
class TournamentBannerAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ('title', 'show_banner', 'inside_home', 'created_at')
    list_filter = ('show_banner', 'inside_home')
    date_hierarchy = 'created_at'
    list_per_page = 25
    save_on_top = True


@admin.register(BangladeshiTopPlayer)
class BangladeshiTopPlayerAdmin(admin.ModelAdmin):
    list_per_page = 25


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_per_page = 25


@admin.register(Puzzle)
class PuzzleAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ('id', 'title', 'difficulty_badge', 'quote')
    list_filter = ('difficulty',)
    search_fields = ('title',)
    list_per_page = 25
    save_on_top = True

    def difficulty_badge(self, obj):
        return status_badge(
            obj.difficulty,
            positive_words=('easy', 'beginner', '1', '2'),
            negative_words=('hard', 'expert', 'advanced', '4', '5'),
            neutral_color="badge-amber",
        )
    difficulty_badge.short_description = "Difficulty"


@admin.register(PuzzleSolve)
class PuzzleSolveAdmin(admin.ModelAdmin):
    list_display = ('user', 'solve_puzzle', 'solved_at')
    search_fields = ('user__username',)
    date_hierarchy = 'solved_at'
    list_per_page = 25
    save_on_top = True


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_per_page = 25


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_per_page = 25


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'premium_badge', 'phone', 'trx_id', 'payment_requested_at', 'image')
    list_filter = ('is_premium',)
    search_fields = ('user__username', 'phone', 'trx_id')
    date_hierarchy = 'payment_requested_at'
    list_per_page = 25
    save_on_top = True

    def premium_badge(self, obj):
        if obj.is_premium:
            return format_html('<span class="badge badge-green">⭐ Premium</span>')
        return format_html('<span class="badge badge-gray">Free</span>')
    premium_badge.short_description = "Status"


@admin.register(BoardVision)
class BoardVisionAdmin(admin.ModelAdmin):
    list_per_page = 25


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'tournament',
        'ticket_type',
        'price',
        'payment_status_badge',
        'ticket_code',
        'checked_in_badge',
        'purchase_date',
    )
    list_filter = ('ticket_type', 'payment_status', 'is_checked_in')
    search_fields = ('user__username', 'tournament__title', 'ticket_code')
    ordering = ('-purchase_date',)
    readonly_fields = ('ticket_code', 'purchase_date')
    date_hierarchy = 'purchase_date'
    list_per_page = 25
    save_on_top = True

    fieldsets = (
        (None, {
            'fields': (
                'user',
                'tournament',
                'ticket_type',
                'price',
                'payment_status',
                'ticket_code',
                'is_checked_in',
            )
        }),
        ('Timestamps', {
            'fields': ('purchase_date',),
        }),
    )

    def payment_status_badge(self, obj):
        return status_badge(
            obj.payment_status,
            positive_words=('paid', 'success', 'complete', 'confirmed'),
            negative_words=('failed', 'pending', 'unpaid', 'rejected', 'cancel'),
        )
    payment_status_badge.short_description = "Payment Status"

    def checked_in_badge(self, obj):
        if obj.is_checked_in:
            return format_html('<span class="badge badge-green">✔ Checked In</span>')
        return format_html('<span class="badge badge-gray">Not Yet</span>')
    checked_in_badge.short_description = "Check-In"


@admin.register(UploadedGame)
class UploadedGameAdmin(admin.ModelAdmin):
    list_per_page = 25


@admin.register(GameComment)
class GameCommentAdmin(admin.ModelAdmin):
    list_per_page = 25


@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = ('title', 'start', 'end', 'url')
    search_fields = ('title', 'description')
    date_hierarchy = 'start'
    ordering = ('-start',)
    list_per_page = 25
    save_on_top = True


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_per_page = 25


@admin.register(MemoryPosition)
class MemoryPositionAdmin(admin.ModelAdmin):
    list_per_page = 25


@admin.register(Streak)
class StreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'streak')
    search_fields = ('user__username',)
    ordering = ('-streak',)
    list_per_page = 25
    

from .models import ChessPuzzle, DailyPuzzle, ChessPuzzleSolve


@admin.register(ChessPuzzle)
class ChessPuzzleAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "difficulty", "turn", "created_at")
    list_filter = ("difficulty", "turn")
    search_fields = ("title", "fen")


@admin.register(DailyPuzzle)
class DailyPuzzleAdmin(admin.ModelAdmin):
    list_display = ("date", "puzzle", "created_at")
    list_filter = ("date",)
    autocomplete_fields = ("puzzle",)
    ordering = ("-date",)

@admin.register(ChessPuzzleSolve)
class ChessPuzzleSolveAdmin(admin.ModelAdmin):
    list_display = ("user", "daily_puzzle", "solved_at", "time_taken", "made_mistake", "wrong_attempts")
    list_filter = ("made_mistake",)
    search_fields = ("user__username",)
    


from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ("photo_thumb", "display_name", "role", "rating", "is_active", "order")
    list_display_links = ("photo_thumb", "display_name")
    list_editable = ("order", "is_active")
    list_filter = ("is_active", "title")
    search_fields = ("name", "role")
    ordering = ("order", "-rating")
 
    fieldsets = (
        ("Identity", {
            "fields": ("title", "name", "role", "photo")
        }),
        ("Profile", {
            "fields": ("rating", "bio")
        }),
        ("Display", {
            "fields": ("order", "is_active")
        }),
    )
    readonly_fields = ("created_at", "updated_at")
 
    def display_name(self, obj):
        return str(obj)
    display_name.short_description = "Name"
 
    def photo_thumb(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:36px;height:36px;object-fit:cover;">',
                obj.photo.url,
            )
        return "—"
    photo_thumb.short_description = ""
 
 
@admin.register(CoachApplication)
class CoachApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "fide_title", "fide_rating", "status", "coach_link", "submitted_at")
    list_editable = ("status",)
    list_filter = ("status", "fide_title")
    search_fields = ("full_name", "email", "playing_history", "coaching_experience")
    ordering = ("-submitted_at",)
    readonly_fields = ("submitted_at", "created_coach")
 
    fieldsets = (
        ("Applicant", {
            "fields": ("full_name", "email", "phone")
        }),
        ("Chess background", {
            "fields": ("fide_title", "fide_rating", "playing_history", "coaching_experience")
        }),
        ("Application", {
            "fields": ("message", "status", "created_coach", "submitted_at")
        }),
    )
 
    actions = ["mark_reviewed", "mark_accepted", "mark_rejected"]
 
    def coach_link(self, obj):
        if obj.created_coach_id:
            url = reverse("admin:news_coach_change", args=[obj.created_coach_id])
            return format_html('<a href="{}">{}</a>', url, obj.created_coach)
        return "—"
    coach_link.short_description = "Coach profile"
 
    @admin.action(description="Mark selected applications as reviewed")
    def mark_reviewed(self, request, queryset):
        queryset.update(status="reviewed")
 
    @admin.action(description="Mark selected applications as accepted")
    def mark_accepted(self, request, queryset):
        # Looping and calling .save() (instead of queryset.update()) so each
        # instance's save() hook runs and auto-creates its Coach profile.
        created = 0
        for application in queryset:
            was_accepted = application.status == "accepted"
            application.status = "accepted"
            application.save()
            if not was_accepted:
                created += 1
        self.message_user(
            request,
            f"Accepted {queryset.count()} application(s). "
            f"{created} new inactive coach profile(s) were created — "
            f"fill in a role and photo, then mark each active from the Coaches page."
        )
 
    @admin.action(description="Mark selected applications as rejected")
    def mark_rejected(self, request, queryset):
        queryset.update(status="rejected")