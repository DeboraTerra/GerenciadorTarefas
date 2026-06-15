from django.contrib import admin
from .models import *

# 1. Configurando os Inlines solicitados nos requisitos
class SubTarefaInline(admin.TabularInline):
    model = SubTarefa
    extra = 1

class AnotacaoInline(admin.TabularInline):
    model = Anotacao
    extra = 1

class AnexoInline(admin.TabularInline):
    model = Anexo
    extra = 1

class LembreteInline(admin.TabularInline):
    model = Lembrete
    extra = 1

# 2. Configurando o Admin da Tarefa
@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'status', 'prioridade', 'dataConclusao')
    inlines = [SubTarefaInline, AnotacaoInline, AnexoInline, LembreteInline]

# Registrando os cadastros básicos (apenas superusuários costumam gerenciar isso)
admin.site.register(Status)
admin.site.register(Prioridade)
admin.site.register(Categoria)
admin.site.register(RelatorioDesempenho)
admin.site.register(MetaDiaria)
admin.site.register(TipoUser)
admin.site.register(Usuario)
admin.site.register(SubTarefa)
admin.site.register(Anotacao)
admin.site.register(Lembrete)