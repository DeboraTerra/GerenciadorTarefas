# seu_app/context_processors.py
from .models import Usuario

def usuario_logado_processor(request):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        try:
            # Busca o utilizador logado na sessão
            usuario = Usuario.objects.get(id=usuario_id)
            return {'usuario_logado': usuario}
        except Usuario.DoesNotExist:
            pass
    return {'usuario_logado': None}