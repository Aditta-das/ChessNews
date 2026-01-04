from django.contrib import admin
from .models import Article, \
    Category, TopPlayerImg, TournamentBanner, BangladeshiTopPlayer, \
    Book, Puzzle, EmailOTP, Quote, PuzzleSolve, UserProfile, BoardVision, Tournament, Ticket

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
    list_display = ('title', 'start_date', 'end_date', 'link')
    search_fields = ('title',)
    ordering = ('start_date',)
    list_filter = ('start_date', 'end_date')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'tournament',
        'ticket_type',
        'price',
        'payment_status',
        'ticket_code',
        'is_checked_in',
        'purchase_date',
    )
    list_filter = ('ticket_type', 'payment_status', 'is_checked_in')
    search_fields = ('user__username', 'tournament__title', 'ticket_code')
    ordering = ('-purchase_date',)
    readonly_fields = ('ticket_code', 'purchase_date')

    def ticket_code_link(self, obj):
        return f"<b>{obj.ticket_code}</b>"
    ticket_code_link.allow_tags = True
    ticket_code_link.short_description = "Ticket Code"

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
    
    
# Trial
from .models import UploadedGame, GameComment

admin.site.register(UploadedGame)
admin.site.register(GameComment)
