from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.hashers import make_password  # Para salvar a senha com segurança
from .models import *

# --- Auxiliares e Mixins ---

def obter_usuario_logado(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return None
    return get_object_or_404(Usuario, id=usuario_id)  # Corrigido o recuo para ser executado


class LoginRequiredMixin:
    """Mixin que valida dinamicamente se o usuário está logado antes de processar a view."""
    def dispatch(self, request, *args, **kwargs):
        self.usuario_logado = obter_usuario_logado(request)
        if not self.usuario_logado:
            return redirect(reverse('login'))
        return super().dispatch(request, *args, **kwargs)  # Corrigido o recuo


class AdminRequiredMixin(LoginRequiredMixin):
    """Garante que o usuário está logado E pertence ao tipo Administrador."""
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if response.status_code == 302:
            return response

        if self.usuario_logado.tipoUsuario.nome != 'Administrador':
            messages.error(request, "Acesso negado. Esta área é restrita a administradores.")
            return redirect(reverse('dashboard_usuario'))
        return response  # Corrigido o recuo


class ComumRequiredMixin(LoginRequiredMixin):
    """Garante que o usuário está logado E pertence ao tipo Cidadão."""
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if response.status_code == 302:
            return response
            
        if self.usuario_logado.tipoUsuario.nome != 'Cidadão':
            messages.error(request, "Acesso restrito a cidadãos.")
            return redirect(reverse('admin_dashboard'))
        return response


# --- Views de Autenticação e Cadastro ---

class CadastroUsuarioView(View):
    """View responsável pelo formulário e processamento do cadastro de novos usuários."""
    
    def get(self, request):
        # Se o usuário já estiver logado, não faz sentido ele cadastrar uma nova conta pública
        if obter_usuario_logado(request):
            return redirect(reverse('dashboard_usuario'))
        return render(request, 'cadastro.html')

    def post(self, request):
        # Captura os dados do formulário HTML
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        # 1. Validação de campos vazios
        if not all([nome, email, senha, confirmar_senha]):
            messages.error(request, "Todos os campos são obrigatórios.")
            return render(request, 'cadastro.html')

        # 2. Validação de senhas idênticas
        if senha != confirmar_senha:
            messages.error(request, "As senhas não coincidem.")
            return render(request, 'cadastro.html')

        # 3. Verifica se o e-mail já está cadastrado
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está cadastrado no sistema.")
            return render(request, 'cadastro.html')

        # 4. Busca o tipo de usuário padrão (Cidadão)
        try:
            tipo_cidadao = TipoUsuario.objects.get(nome='Cidadão')
        except TipoUsuario.DoesNotExist:
            messages.error(request, "Erro de configuração do sistema: Tipo 'Cidadão' não encontrado.")
            return render(request, 'cadastro.html')

        # 5. Salva o novo usuário criptografando a senha por segurança
        Usuario.objects.create(
            nome=nome,
            email=email,
            senha=make_password(senha),  # Nunca salve senhas em texto puro!
            tipoUsuario=tipo_cidadao
        )

        messages.success(request, "Cadastro realizado com sucesso! Faça seu login.")
        return redirect(reverse('login'))