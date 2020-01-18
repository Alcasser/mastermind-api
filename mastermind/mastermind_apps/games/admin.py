from django.contrib import admin

from mastermind_apps.games.models import Game, Code, Peg


class PegInLine(admin.StackedInline):
    model = Peg
    max_num = 4
    min_num = 4


class CodeAdmin(admin.ModelAdmin):
    inlines = [PegInLine]


admin.site.register(Game)
admin.site.register(Code, CodeAdmin)
admin.site.register(Peg)
