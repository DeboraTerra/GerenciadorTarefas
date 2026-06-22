from django.db import models
from django.utils import timezone

class TipoUser(models.Model):
    nome = models.CharField(max_length = 100, verbose_name="Tipo do usuário")
    def __str__(self):
        return self.nome
    class Meta:
        verbose_name = "Tipo do Usuário"
        verbose_name_plural = "Tipos de Usuários"

class Usuario(models.Model):
    user_nome = models.CharField(max_length = 100, verbose_name="Nome do usuário")
    email = models.EmailField(max_length = 100, verbose_name="Email do usuário")
    senha= models.CharField(max_length = 100, verbose_name="Senha do usuário")
    tipo = models.ForeignKey(TipoUser, on_delete = models.CASCADE, verbose_name="Tipo do usuário")
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        
class Status(models.Model):
    nome = models.CharField(max_length = 100, verbose_name="Tipo do status")
    def __str__(self):
        return self.nome
    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Status"

class Prioridade(models.Model):
    nome = models.CharField(max_length = 100, verbose_name="Tipo da prioridade")
    def __str__(self):
        return self.nome
    class Meta:
        verbose_name = "Prioridade"
        verbose_name_plural = "Prioridades"

class Categoria(models.Model):
    nome = models.CharField(max_length = 100, verbose_name="Categoria")
    def __str__(self):
        return self.nome
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
    

class Tarefa(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name="Usuário dono da tarefa", null=True, blank=True) # <- CAMPO NOVO AQUI
    titulo = models.CharField(max_length = 100, verbose_name="Titulo da Tarefa")
    descricao = models.CharField(max_length = 100, verbose_name="Descricao da Tarefa")
    dataCriacao = models.DateTimeField(default=timezone.now)
    dataConclusao = models.DateTimeField(default=timezone.now)
    status = models.ForeignKey(Status, on_delete=models.CASCADE,verbose_name="Status da Tarefa")
    prioridade = models.ForeignKey(Prioridade, on_delete=models.CASCADE,verbose_name="Prioridade da Tarefa")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE,verbose_name="Categoria da Tarefa")
    def __str__(self):
        return f'{self.titulo}, {self.descricao}, {self.dataCriacao}, {self.dataConclusao}'
    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"

class SubTarefa(models.Model):
    nome = models.CharField(max_length = 100, verbose_name="nome da subTarefa")
    descricao = models.CharField(max_length = 100, verbose_name="Descricao da subTarefa")
    tarefaMae = models.ForeignKey(Tarefa, on_delete = models.CASCADE, verbose_name = "Tarefa Mãe")
    def __str__(self):
        return f'{self.nome}, {self.descricao}'
    class Meta:
        verbose_name = "Sub tarefa"
        verbose_name_plural = "Sub Tarefas "

class Anotacao(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name="Usuário", null=True, blank=True)
    tarefaAnotada = models.ForeignKey(Tarefa, on_delete = models.CASCADE, verbose_name = "Tarefa Mãe")
    texto = models.CharField(max_length = 100, verbose_name="texto da anotação")
    dataCriacao = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f'{self.texto}, {self.dataCriacao}'
    class Meta:
        verbose_name = "Anotacao"
        verbose_name_plural = "Anotacoes"

class Anexo (models.Model):
    nome= models.CharField(max_length = 100, verbose_name="nome do arquivo")
    arquivo = models.FileField(upload_to='anexos/%Y/%m/') 
    tarefaMae = models.ForeignKey(Tarefa, on_delete=models.CASCADE)
    # Registra automaticamente a data em que o arquivo foi enviado
    data_upload = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.nome}, {self.arquivo}, {self.data_upload.strftime('%d/%m/%y')}"
    class Meta:
        verbose_name = "Anexo"
        verbose_name_plural = "Anexos"
        
class Lembrete (models.Model):
    nome=  models.CharField(max_length = 100, verbose_name="nome do Lembrete")
    disparo = models.DateTimeField()
    tarefaMae = models.ForeignKey(Tarefa, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.nome}, {self.disparo.strftime('%d/%m/%Y')}"
    class Meta:
        verbose_name = "Lembrete"
        verbose_name_plural = "Lembretes"
        
class RelatorioDesempenho(models.Model):
    StatusConcluida = models.ForeignKey(Status, on_delete= models.CASCADE, verbose_name = "Monitoramento: Status Concluído")
    titulo = models.CharField(max_length=100, verbose_name="Nome do Relatório")
    def __str__(self):
        return self.titulo
    class Meta:
        verbose_name = "Relatorio de Desempenho"

class MetaDiaria(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name="Usuário", null=True, blank=True)
    QuantidadeEsperada= models.PositiveIntegerField(default = 0, verbose_name="Quantidade de Tarefas Estipuladas:")
    data = models.DateField(default=timezone.now, verbose_name="Data da Meta")
    def __str__(self):
       return f"Meta de {self.QuantidadeEsperada} tarefas em {self.data}"
    class Meta:
        verbose_name = "Meta Diaria"
        verbose_name_plural = "Metas Diarias"
        ordering = ['-data']
 
