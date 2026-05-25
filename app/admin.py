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
    exclude = ('usuario',) # Escondemos o campo usuário para preenchê-lo automaticamente

    # Sobrescrevemos o método para salvar a tarefa com o usuário logado automaticamente
    def save_model(self, request, obj, form, change):
        if not obj.pk: # Se for uma tarefa nova
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

    # Sobrescrevemos a visualização para o usuário ver apenas as próprias tarefas
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs # Superusuários (você) veem tudo
        return qs.filter(usuario=request.user) # Usuários comuns veem apenas as deles

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