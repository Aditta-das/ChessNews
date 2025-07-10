from django.contrib import admin
from .models import Article, Category, TopPlayerImg, TournamentBanner, BangladeshiTopPlayer, Book, Puzzle, EmailOTP, Quote, PuzzleSolve
import requests

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