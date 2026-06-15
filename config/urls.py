from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', CadastroUsuarioView.as_view(), name='cadastro'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('tarefa/', TarefaView.as_view(), name='tarefa'),
    path('tarefa_criar/', TarefaCriarView.as_view(), name='tarefa_criar'),
    path('metaDiaria/', MetaDiariaView.as_view(), name='metaDiaria'),
    path('relatorioDesempenho/', RelatorioDesempenhoView.as_view(), name='relatorioDesempenho'),
    path('anotacoes/', AnotacoesView.as_view(), name='anotacoes'),
    path('anotacoes/deletar/<int:pk>/', AnotacaoDeletarView.as_view(), name='anotacao_deletar'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)