from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from .models import *

# --- Auxiliares e Mixins ---

def obter_usuario_logado(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return None
    return get_object_or_404(Usuario, id=usuario_id)


class LoginRequiredMixin:
    """Mixin que valida dinamicamente se o usuário está logado antes de processar a view."""
    def dispatch(self, request, *args, **kwargs):
        self.usuario_logado = obter_usuario_logado(request)
        if not self.usuario_logado:
            return redirect(reverse('login'))
        return super().dispatch(request, *args, **kwargs)


class CadastroUsuarioView(View):
    """View responsável pelo formulário e processamento do cadastro de novos usuários."""

    def get(self, request):
        if obter_usuario_logado(request):
            return redirect(reverse('tarefa'))
        return render(request, 'cadastro.html')

    def post(self, request):
        user_nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        if not all([user_nome, email, senha]):
            messages.error(request, "Todos os campos são obrigatórios.")
            return render(request, 'cadastro.html')

        try:
            tipo_cidadao = TipoUser.objects.get(nome='Cidadão')
        except TipoUser.DoesNotExist:
            messages.error(request, "Erro de configuração do sistema: Tipo 'Cidadão' não encontrado.")
            return render(request, 'cadastro.html')

        Usuario.objects.create(
            user_nome=user_nome,
            email=email,
            senha=make_password(senha),
            tipo=tipo_cidadao,
        )

        messages.success(request, "Cadastro realizado com sucesso! Faça seu login.")
        return redirect(reverse('login'))


class LoginView(View):
    """View responsável pelo login do usuário."""

    def get(self, request):
        usuario_logado = obter_usuario_logado(request)
        if usuario_logado:
            if usuario_logado.tipo.nome == 'Cidadão':
                return redirect(reverse('tarefa'))
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        if not email or not senha:
            messages.error(request, "Por favor, preencha e-mail e senha.")
            return render(request, 'login.html')

        try:
            usuario = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            messages.error(request, "E-mail ou senha inválidos.")
            return render(request, 'login.html')

        if check_password(senha, usuario.senha):
            request.session['usuario_id'] = usuario.id
            messages.success(request, f"Bem-vindo(a) de volta, {usuario.user_nome}!")

            if usuario.tipo.nome == 'Administrador':
                return redirect(reverse('admin:index'))
            else:
                return redirect(reverse('tarefa'))
        else:
            messages.error(request, "E-mail ou senha inválidos.")
            return render(request, 'login.html')


class LogoutView(View):
    """View responsável por encerrar a sessão do usuário."""
    def get(self, request):
        if 'usuario_id' in request.session:
            del request.session['usuario_id']
        messages.success(request, "Você saiu da sua conta.")
        return redirect(reverse('login'))


class TarefaView(LoginRequiredMixin, View):
    """Lista apenas as tarefas do usuário logado."""

    def get(self, request, *args, **kwargs):
        # Filtra somente as tarefas que pertencem ao usuário da sessão
        tarefas = Tarefa.objects.filter(usuario=self.usuario_logado)
        return render(request, 'tarefa.html', {'tarefas': tarefas})


class TarefaCriarView(LoginRequiredMixin, View):
    """Exibe o formulário de criação e processa a nova tarefa."""

    def get(self, request, *args, **kwargs):
        context = {
            'status': Status.objects.all(),
            'prioridades': Prioridade.objects.all(),
            'categorias': Categoria.objects.all(),
        }
        return render(request, 'tarefa_criar.html', context)

    def post(self, request, *args, **kwargs):
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        data_conclusao = request.POST.get('dataConclusao')
        status_id = request.POST.get('status')
        prioridade_id = request.POST.get('prioridade')
        categoria_id = request.POST.get('categoria')

        # Validação básica dos campos obrigatórios
        if not all([titulo, descricao, status_id, prioridade_id, categoria_id]):
            messages.error(request, "Por favor, preencha todos os campos obrigatórios.")
            context = {
                'status': Status.objects.all(),
                'prioridades': Prioridade.objects.all(),
                'categorias': Categoria.objects.all(),
            }
            return render(request, 'tarefa_criar.html', context)

        try:
            status_obj = Status.objects.get(id=status_id)
            prioridade_obj = Prioridade.objects.get(id=prioridade_id)
            categoria_obj = Categoria.objects.get(id=categoria_id)
        except (Status.DoesNotExist, Prioridade.DoesNotExist, Categoria.DoesNotExist):
            messages.error(request, "Seleção inválida. Tente novamente.")
            context = {
                'status': Status.objects.all(),
                'prioridades': Prioridade.objects.all(),
                'categorias': Categoria.objects.all(),
            }
            return render(request, 'tarefa_criar.html', context)

        # Monta os kwargs da tarefa — dataConclusao é opcional
        tarefa_kwargs = dict(
            usuario=self.usuario_logado,
            titulo=titulo,
            descricao=descricao,
            status=status_obj,
            prioridade=prioridade_obj,
            categoria=categoria_obj,
        )
        if data_conclusao:
            tarefa_kwargs['dataConclusao'] = data_conclusao

        Tarefa.objects.create(**tarefa_kwargs)

        messages.success(request, f'Tarefa "{titulo}" criada com sucesso!')
        return redirect(reverse('tarefa'))
    
class MetaDiariaView(LoginRequiredMixin, View):
    """Mostra e salva a meta de tarefas do dia para o usuário logado."""
 
    def get(self, request, *args, **kwargs):
        hoje = timezone.now().date()
        # Meta de hoje (se existir)
        meta_hoje = MetaDiaria.objects.filter(
            usuario=self.usuario_logado, data=hoje
        ).first()
        # Histórico das últimas metas
        historico = MetaDiaria.objects.filter(
            usuario=self.usuario_logado
        ).order_by('-data')[:10]
        context = {
            'meta_hoje': meta_hoje,
            'historico': historico,
        }
        return render(request, 'metaDiaria.html', context)
 
    def post(self, request, *args, **kwargs):
        quantidade = request.POST.get('quantidade', '').strip()
 
        if not quantidade or not quantidade.isdigit() or int(quantidade) < 1:
            messages.error(request, "Informe um número válido (mínimo 1).")
            return redirect(reverse('metaDiaria'))
 
        hoje = timezone.now().date()
        # Atualiza se já existe meta para hoje, senão cria
        meta, criada = MetaDiaria.objects.update_or_create(
            usuario=self.usuario_logado,
            data=hoje,
            defaults={'QuantidadeEsperada': int(quantidade)},
        )
        if criada:
            messages.success(request, f"Meta do dia definida: {quantidade} tarefa(s)!")
        else:
            messages.success(request, f"Meta do dia atualizada para {quantidade} tarefa(s)!")
 
        return redirect(reverse('metaDiaria'))
 
 
# ─── RELATÓRIO DE DESEMPENHO ──────────────────────────────────────────────────
 
class RelatorioDesempenhoView(LoginRequiredMixin, View):
    """
    Exibe quantas tarefas o usuário já concluiu.
    Para contar como 'concluída', o status da tarefa deve
    ter o nome 'Concluída' (cadastrado pelo admin).
    """
 
    def get(self, request, *args, **kwargs):
        # Busca os status cujo nome contenha "conclu" (case-insensitive)
        # para não depender de digitação exata
        tarefas_do_usuario = Tarefa.objects.filter(usuario=self.usuario_logado)
        total = tarefas_do_usuario.count()
 
        concluidas = tarefas_do_usuario.filter(
            status__nome__icontains='conclu'
        )
        total_concluidas = concluidas.count()
 
        pendentes = tarefas_do_usuario.exclude(
            status__nome__icontains='conclu'
        ).count()
 
        porcentagem = round((total_concluidas / total * 100), 1) if total > 0 else 0
 
        # Meta de hoje
        hoje = timezone.now().date()
        meta_hoje = MetaDiaria.objects.filter(
            usuario=self.usuario_logado, data=hoje
        ).first()
        meta_quantidade = meta_hoje.QuantidadeEsperada if meta_hoje else 0
        meta_atingida = total_concluidas >= meta_quantidade if meta_quantidade > 0 else False
 
        context = {
            'total': total,
            'total_concluidas': total_concluidas,
            'pendentes': pendentes,
            'porcentagem': porcentagem,
            'concluidas': concluidas,
            'meta_hoje': meta_hoje,
            'meta_quantidade': meta_quantidade,
            'meta_atingida': meta_atingida,
        }
        return render(request, 'relatorioDesempenho.html', context)
 
 
# ─── ANOTAÇÕES ───────────────────────────────────────────────────────────────
 
class AnotacoesView(LoginRequiredMixin, View):
    """Lista e cria anotações livres do usuário."""
 
    def get(self, request, *args, **kwargs):
        anotacoes = Anotacao.objects.filter(usuario=self.usuario_logado)
        return render(request, 'anotacoes.html', {'anotacoes': anotacoes})
 
    def post(self, request, *args, **kwargs):
        texto = request.POST.get('texto', '').strip()
 
        if not texto:
            messages.error(request, "A anotação não pode estar vazia.")
            return redirect(reverse('anotacoes'))
 
        Anotacao.objects.create(
            usuario=self.usuario_logado,
            texto=texto,
        )
        messages.success(request, "Anotação salva com sucesso!")
        return redirect(reverse('anotacoes'))
 
 
class AnotacaoDeletarView(LoginRequiredMixin, View):
    """Deleta uma anotação, garantindo que pertença ao usuário logado."""
 
    def post(self, request, pk, *args, **kwargs):
        anotacao = get_object_or_404(Anotacao, pk=pk, usuario=self.usuario_logado)
        anotacao.delete()
        messages.success(request, "Anotação removida.")
        return redirect(reverse('anotacoes'))
