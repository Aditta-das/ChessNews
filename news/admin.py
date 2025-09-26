from django.contrib import admin
from .models import Article, \
    Category, TopPlayerImg, TournamentBanner, BangladeshiTopPlayer, \
    Book, Puzzle, EmailOTP, Quote, PuzzleSolve, UserProfile, BoardVision, Tournament

admin.site.site_header = "ChessBD AdminPanel"
admin.site.site_title = "ChessBD"
admin.site.index_title = "Welcome to ChessBD Admin Panel"

admin.site.register(Article)
admin.site.register(Category)
admin.site.register(TopPlayerImg)
admin.site.register(TournamentBanner)
admin.site.register(BangladeshiTopPlayer)
admin.site.register(Book)
@admin.register(Puzzle)
class PuzzleAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ('id', 'title', 'difficulty', 'quote')
    
@admin.register(PuzzleSolve)
class PuzzleSolveAdmin(admin.ModelAdmin):
    list_display = ('user', 'solve_puzzle', 'solved_at')
admin.site.register(Quote)
admin.site.register(EmailOTP)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_premium', 'phone', 'trx_id', 'payment_requested_at', 'image')
    list_filter = ('is_premium',)
    search_fields = ('user__username', 'phone', 'trx_id')
    
admin.site.register(BoardVision)

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date')
    list_filter = ('start_date',)
    search_fields = ('title',)