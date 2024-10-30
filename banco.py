import sqlite3

class Banco():
	def __init__(self, nomeBanco):
		self.nomeBanco = nomeBanco
		self.conexao = sqlite3.connect(nomeBanco)
		self.isConnOpen = True
		self.cursor = self.conexao.cursor()

	def executarComandoSQLSemRetorno(self, sql, arguments=()):
		self.cursor.execute(sql, arguments)

	def executarComandoSQLSelect(self, sql, arguments=()):
		self.cursor.execute(sql, arguments)
		return self.cursor.fetchall()

	def salvarAlteracoes(self):
		self.conexao.commit()

	def abrirConexao(self):
		self.conexao = sqlite3.connect(self.nomeBanco)
		self.isConnOpen = True

	def fecharConexao(self):
		self.conexao.close()
		self.isConnOpen = False
