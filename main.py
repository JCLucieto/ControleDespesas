import os
import re
import sqlite3
import platform

from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition


# Globais

formatted_date = ''


class AlignedSpinner(Spinner):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = kwargs.get('text', '')
        self.background_normal = ''
        self.background_color = (1, 1, 1, 1)
        self.color = (0, 0, 0, 1)

    def _update_text(self, *args):
        super()._update_text(*args)
        self.text = self.values[0] if self.values else ''


class ColoredBoxLayout(BoxLayout):
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Define a cor de fundo do layout
        with self.canvas.before:
            background_normal = 'fundo.png'
            Color(0.0, 0.0, 1.0, 0.6)  # Azul claro com opacidade total
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size

#----------------------------------------------------
# Tela Principal
#----------------------------------------------------

class TelaPrincipal(Screen):
 
    def __init__(self, **kwargs):

        super(TelaPrincipal, self).__init__(**kwargs)

        layout = ColoredBoxLayout(orientation='vertical', padding=[20, 0, 0, 0], spacing=5)

        # Layout para o Label da Data
        label_data_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=35, spacing=5)
        spacer = BoxLayout(size_hint_x=None, width=-18)  # Ajuste a largura conforme necessário
        label_data_layout.add_widget(spacer)
        label_data_label = Label(text='Data (DDMMAA)', size_hint_x=None, width=140, height=35, halign='left', valign='center')
        label_data_label.bind(size=label_data_label.setter('text_size'))
        label_data_layout.add_widget(label_data_label)
        
        # Layout para o campo de data e o botão "Hoje"
        data_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=35)
        self.data_input = TextInput(hint_text='', size_hint_x=None, font_size = 20, width=220, height=35)
        hoje_button = Button(text='Hoje', size_hint=(None, None), width=106, height=35, on_press=self.pega_data)
        data_layout.add_widget(self.data_input)
        data_layout.add_widget(hoje_button)

        # Adiciona o layout do Label e o layout dos dados ao layout principal
        layout.add_widget(label_data_layout)
        layout.add_widget(data_layout)

        # Tipo
        tipo_layout = BoxLayout(orientation='vertical', spacing=0)
        tipo_label = Label(text='Tipo de Despesa', size_hint_x=None, width= 340, height=10, halign='left', valign='center')
        tipo_label.bind(size=tipo_label.setter('text_size'))
        self.tipo_spinner = AlignedSpinner(text='Selecione Uma Opção', values=('Refeição', 'Uber'), size_hint_x=None, width= 340, halign='left', valign='center')
        tipo_layout.add_widget(tipo_label)
        tipo_layout.add_widget(self.tipo_spinner)
        layout.add_widget(tipo_layout)

        # Valor
        valor_layout = BoxLayout(orientation='vertical', spacing=0)
        valor_label = Label(text='Valor (Utilize . Para Centavos)', size_hint_x=None, width= 250, height=10, halign='left', valign='center')
        valor_label.bind(size=valor_label.setter('text_size'))
        self.valor_input = TextInput(hint_text='', size_hint_x=None, font_size = 20, width= 340, height=10, input_filter='float')
        valor_layout.add_widget(valor_label)
        valor_layout.add_widget(self.valor_input)
        layout.add_widget(valor_layout)

        # Anotação
        anotacao_layout = BoxLayout(orientation='vertical', spacing=0)
        anotacao_label = Label(text='Anotação', size_hint_x=None, width= 140, height=10, halign='left', valign='center')
        anotacao_label.bind(size=anotacao_label.setter('text_size'))
        self.anotacao_input = TextInput(hint_text='', size_hint_x=None, width= 340, height=10)
        anotacao_layout.add_widget(anotacao_label)
        anotacao_layout.add_widget(self.anotacao_input)
        layout.add_widget(anotacao_layout)

        # Botões
        btn_layout = BoxLayout(orientation='horizontal', padding=[0, 15, 0, 15], spacing=10)
        # Criação dos botões Salvar, Cancelar e Pesquisar com tamanhos específicos
        save_button = Button(text='SALVAR', size_hint=(None, None), width=100, height=35, padding=[5,5,5,5], on_press=self.salvar)
        cancel_button = Button(text='CANCELAR', size_hint=(None, None), width=100, height=35, padding=[5,5,5,5], on_press=self.cancelar)
        search_button = Button(text='PESQUISAR', size_hint=(None, None), width=120, height=35, padding=[5,5,5,5], on_press=self.pesquisar)

        btn_layout.add_widget(save_button)
        btn_layout.add_widget(cancel_button)
        btn_layout.add_widget(search_button)
        layout.add_widget(btn_layout)

        # Botões
        btn_layout1 = BoxLayout(orientation='horizontal', padding=[65, 0, 0, 45], spacing=0)
        # Criação do botão Encerrar com tamanhos específicos
        exit_button = Button(text='ENCERRAR', size_hint=(None, None), width=200, height=35, on_press=self.on_stop)
        btn_layout1.add_widget(exit_button)
        layout.add_widget(btn_layout1)

        self.add_widget(layout)
    

    def navega_teladetalhes(self, instance):
        self.manager.current = 'teladetalhes'


    def pega_data(self, instance):
        # Obtém a data atual
        today = datetime.now()
        data_hoje = today.strftime('%d%m%y')  # Formata a data como ddmmaa
        self.data_input.text = data_hoje


    def salvar(self, instance):

        data = self.data_input.text
        data = data.replace('/','')
        if not self.data_valida(instance):
            self.data_input.hint_text = 'Data Inválida'
            self.data_input.text = ''
            return
        data_editada = ''
        data_editada = data[:2] + '/' + data[2:4] + '/' + '20' + data[4:6]
        data_gravacao = '20' + data[4:6] + data[2:4] + data[:2]
        
        tipo = self.tipo_spinner.text
        if (tipo == 'Selecione Uma Opção'):
            self.mostra_mensagem('ERRO', 'Selecione Tipo!')
            return

        valor = self.valor_input.text
        float_valor = 0.0
        try:
            float_valor = float(valor)
        except (ValueError, TypeError):
            self.valor_input.hint_text = 'Valor Inválido'
            self.valor_input.text = ''
            return
        if (float_valor < 0.1):
            self.valor_input.hint_text = 'Valor Inválido'
            self.valor_input.text = ''
            return
        
        anotacoes = self.anotacao_input.text
   
        try:
            # Conect a Base de Dados
            self.conn = sqlite3.connect('despesas.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                INSERT INTO Despesas (data, tipo, valor, anotacoes)
                VALUES (?, ?, ?, ?)
            ''', (data_gravacao, tipo, float_valor, anotacoes))
            self.conn.commit()
            self.mostra_mensagem('SUCESSO', 'Despesa Registrada !')
            self.cancelar(instance)
        except ValueError:
            self.mostra_menagem('ERRO', 'FALHA ao Registar a Despesa!')
        finally:
        # Fechar o cursor e a conexão, se eles foram criados
            if hasattr(self, 'cursor'):
                self.cursor.close()
            if hasattr(self, 'conn'):
                self.conn.close()


    def data_valida(self, instance):
        data = self.data_input.text
        data = data.replace('/','')
        data = re.sub(r'[^0-9]', '', data)
        if (len(data) != 6):
            return False
        dia = data[:2]
        mes = data[2:4]
        ano = data[4:6]
        if (int(dia) < 0 or int(dia) > 31):
            return False
        if (int(mes) < 0 or int(mes) > 12):
            return False
        if (int(ano) < 20):
            return False
        self.data_input.text = dia + '/' + mes + '/' + ano            
        return True


    def cancelar(self, instance):
        self.data_input.text = ''
        self.valor_input.text = ''
        self.tipo_spinner.text = 'Selecione Uma Opção'
        self.anotacao_input.text = ''


    def pesquisar(self, instance):
        try:
            # Conect a Base de Dados
            self.conn = sqlite3.connect('despesas.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute('SELECT data, tipo, valor, anotacoes FROM Despesas order by data DESC')
            despesas = self.cursor.fetchall()
            if despesas:
                despesas_formatadas = self.formata_despesas (self, despesas)
                despesas_text = '\n'.join([f'{d[0]} - {d[1]} - {d[2]} - {d[3]}' for d in despesas_formatadas])
            else:
                despesas_text = 'Nenhuma despesa registrada !'
            self.mostra_popup('Relação de Despesas Registradas', despesas_text)
        except (sqlite3.OperationalError, sqlite3.DatabaseError, sqlite3.Error):
            self.mostra_menagem('ERRO', 'Falha ao Pesquisar Despesas!')
        finally:
        # Fechar o cursor e a conexão, se eles foram criados
            if hasattr(self, 'cursor'):
                self.cursor.close()
            if hasattr(self, 'conn'):
                self.conn.close()


    def formata_despesas(self, instance, despesas):
        despesas_formatadas = list()
        for despesa in despesas:
            data = despesa[0]
            data = data[6:8] + '/' + data[4:6] + '/' + data[:4]
            tipo = despesa[1]
            valor = despesa[2]
            anotacoes = despesa[3]
            # Trunca Anotaçoes de Maior que 15
            if len(anotacoes) > 18:
                anotacoes = anotacoes[:18] + "..."
            # Formata o Valor
            valor_formatado = f"R$ {valor:,.2f}".replace('.', ',')
            nova_despesa = (data, tipo, valor_formatado, anotacoes)
            despesas_formatadas.append(nova_despesa)
        return despesas_formatadas


    def mostra_mensagem(self, title, message):

        # Layout principal do popup
        content = BoxLayout(orientation='vertical', padding = [10, 0, 0, 0], spacing=60)
        
        # Layout para o conteúdo rolável
        popup_content = BoxLayout(orientation='vertical', size_hint_y=None, padding = [0, 0, 0, 0])
        popup_content.bind(minimum_height=popup_content.setter('height'))

        # Adiciona o texto da mensagem ao layout
        message_label = Label(text=message, size_hint_y=None, height=40, halign='left', valign='middle')
        popup_content.add_widget(message_label)

        # Adiciona o popup_content ao layout principal
        content.add_widget(popup_content)

        # Espaçamento entre itens
        item_spacing = 10  # Ajuste este valor conforme necessário

        # Layout para o botão OK, centralizado
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding = [0,0,0,20])
        button_layout.add_widget(BoxLayout(size_hint_x=1))  # Espaço flexível à esquerda do botão
        ok_button = Button(text='OK', size_hint=(None, None), width=100, height=50)
        button_layout.add_widget(ok_button)  # Adiciona o botão ao layout
        button_layout.add_widget(BoxLayout(size_hint_x=1))  # Espaço flexível à direita do botão

        # Adiciona o layout do botão ao layout principal
        content.add_widget(button_layout)

        # Cria o Popup e o exibe
        popup = Popup(title = title, content = content, size_hint = (None, None), width = 300, height = 250)
        ok_button.bind(on_press=popup.dismiss)
        popup.open()


    def mostra_popup(self, title, message):
       
        # Exibe um popup com um botão OK

        # Layout principal do popup
        content = BoxLayout(orientation='vertical', padding=0, spacing=12)

        # ScrollView para rolagem
        self.scroll_view = ScrollView (size_hint = (None, None),  width = 354, height = 460, do_scroll_x=True, do_scroll_y=True)

        # Layout para o conteúdo rolável
        popup_content = BoxLayout(orientation='vertical', size_hint_y=None)
        popup_content.bind(minimum_height = popup_content.setter('height'))
       
        message_label = Label(text = message, size_hint_y = None, height = 30, halign = 'left', valign = 'middle')
        popup_content.add_widget(message_label)

        # Adiciona o layout de conteúdo ao ScrollView
        self.scroll_view.add_widget(popup_content)

        # Layout para os botões (Sobe, OK, Desce)
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)

        # Botão para rolar para esquerda
        rigth_button = Button(text='<', font_size='30sp', size_hint_x=None, width=38, height=50)
        rigth_button.bind(on_press=lambda x: self.scroll_view_right(self.scroll_view))
        button_layout.add_widget(rigth_button)

        # Botão para rolar para cima
        up_button = Button(text='Subir', font_size='15sp', size_hint_x=None, width=62, height=50)
        up_button.bind(on_press=lambda x: self.scroll_view_up(self.scroll_view))
        button_layout.add_widget(up_button)

        # Espaço flexível antes do botão OK
        button_layout.add_widget(BoxLayout(size_hint_x=1))

        # Botão OK
        ok_button = Button(text='Fechar', size_hint=(None, None), width=100, height=50)
        button_layout.add_widget(ok_button)

        # Espaço flexível após o botão OK
        button_layout.add_widget(BoxLayout(size_hint_x=1))

        # Botão para rolar para baixo
        down_button = Button(text='Descer', font_size='15sp', size_hint_x=None, width=62, height=50)
        down_button.bind(on_press=lambda x: self.scroll_view_down(self.scroll_view))
        button_layout.add_widget(down_button)

        # Botão para rolar para direita
        left_button = Button(text='>', font_size='30sp', size_hint_x=None, width=38, height=50)
        left_button.bind(on_press=lambda x: self.scroll_view_left(self.scroll_view))
        button_layout.add_widget(left_button)

        # Adiciona o ScrollView ao layout principal
        content.add_widget(self.scroll_view)

        # Adiciona o layout dos botões ao layout principal
        content.add_widget(button_layout)

        # Cria o Popup e o exibe
        popup = Popup(title=title, content=content, padding = [0, 0, 0, 10], size_hint = (None, None), width = 386, height = 600)
        ok_button.bind(on_press=popup.dismiss)

        # Adiciona uma pequena espera para garantir que o popup esteja totalmente visível antes de ajustar a rolagem
        Clock.schedule_once(self.focus_on_first_item, 0.1)
        popup.open()


    def focus_on_first_item(self, *args):
        self.scroll_view.scroll_y = 1


    def scroll_view_up(self, scroll_view):
        # Move o ScrollView para cima
        scroll_view.scroll_y = min(scroll_view.scroll_y + 0.1, 1)


    def scroll_view_down(self, scroll_view):
        # Move o ScrollView para baixo
        scroll_view.scroll_y = max(scroll_view.scroll_y - 0.1, 0)


    def scroll_view_left(self, scroll_view):
        # Move o ScrollView para a esquerda
        scroll_view.scroll_x = max(scroll_view.scroll_x - 0.1, 0)


    def scroll_view_right(self, scroll_view):
        # Move o ScrollView para a direita
        scroll_view.scroll_x = min(scroll_view.scroll_x + 0.1, 1)


    def on_stop(self):
        self.conn.close()


#----------------------------------------------------
# Tela de Login
#----------------------------------------------------

class TelaLogin(Screen):

    def __init__(self, **kwargs):
        super(TelaLogin, self).__init__(**kwargs)

        # Layout principal
        layout = ColoredBoxLayout(orientation='vertical', padding=[0, 0, 0, 0], spacing=0)

        # Título
        titulo = Label(text='Login', font_size='40sp', padding = [0,20,0,10], size_hint_y=None, height=100, halign='center')
        layout.add_widget(titulo)

        # Layout para os campos de login
        campos_layout = GridLayout(cols = 1, spacing = 60, size_hint_y = None, height = 120, padding=[80, 80, 0, 0],)

        # Container para Usuário
        usuario_layout = BoxLayout(orientation='vertical', spacing=15, padding = [30,0,0,0], size_hint_y = None, height = 60)
        label_usuario = Label(text='Usuário', size_hint = (None, None), font_size = 20, width = 80, height = 10, halign = 'left', valign = 'center')
        self.input_usuario = TextInput(size_hint = (None, None), font_size = 20, height = 40, width = 160, multiline = False)
        usuario_layout.add_widget(label_usuario)
        usuario_layout.add_widget(self.input_usuario)

        # Container para Senha
        senha_layout = BoxLayout(orientation='vertical', spacing = 15, padding = [30,0,0,0], size_hint_y = None, height = 60)
        label_senha = Label(text='Senha', size_hint = (None, None), font_size = 20, width = 80, height = 10, halign = 'left', valign = 'center')
        self.input_senha = TextInput(size_hint = (None, None), font_size = 20, height = 40, width = 160, multiline = False, password = True)
        senha_layout.add_widget(label_senha)
        senha_layout.add_widget(self.input_senha)

        campos_layout.add_widget(usuario_layout)
        campos_layout.add_widget(senha_layout)

        layout.add_widget(campos_layout)

        # Botão de login
        btn_layout = BoxLayout(orientation='horizontal', padding=[95, 0, 0, 120], spacing=0)
        entrar_button = Button(text='ENTRAR', size_hint=(None, None), width=200, height=45, on_press = self.navega_telaprincipal)
        btn_layout.add_widget(entrar_button)
        layout.add_widget(btn_layout)

        self.add_widget(layout)


    def navega_telaprincipal(self, instance):
        self.manager.current = 'telaprincipal'


#----------------------------------------------------
# Programa Principal
#----------------------------------------------------

class ControleDespesasApp(App):
   
    title = 'Controle de Despesas'

    def build(self):

         # Verifica SO
        os_name = platform.system()
        if (os_name == 'Windows'):
            Window.size = (385, 600)
            self.center_window()

        # Verifica Base de Dados
        self.verifica_tabela()

        # Instancia ScreenManager
        sm = ScreenManager()
        
        # Adiciona as Telas ao SM

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(TelaLogin(name='telalogin'))
        sm.add_widget(TelaPrincipal(name='telaprincipal'))
        
        return sm


    def verifica_tabela(self):
        # Criação da tabela se não existir
        try:
            # Conectar à base de dados
            self.conn = sqlite3.connect('despesas.db')
            self.cursor = self.conn.cursor()
            
            # Cria a tabela Despesas caso ainda não exista
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Despesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                tipo TEXT NOT NULL,
                valor REAL NOT NULL,
                anotacoes TEXT NOT NULL DEFAULT 'Nenhuma'
            )
             ''')
            
            # Confirmar a transação
            self.conn.commit()

        except sqlite3.DatabaseError:
            self.mostra_mensagem('ERRO', 'Falha na Base de Dados!')

        finally:
            # Fechar o cursor e a conexão, se eles foram criados
            if hasattr(self, 'cursor'):
                self.cursor.close()
            if hasattr(self, 'conn'):
                self.conn.close()


    def center_window(self):
 
       # Obtém o tamanho da tela
        screen_width, screen_height = Window.system_size
 
        # Obtém o tamanho da janela do aplicativo
        window_width, window_height = Window.size
 
        # Calcula as novas coordenadas para centralizar a janela
        x = (screen_width - window_width) / 2
        y = (screen_height - window_height) / 2
 
        # Define a posição da janela
        Window.left = x + 920
        Window.top = y + 290

#----------------------------------------------------
#  Ativação Programa Principal
#----------------------------------------------------

if __name__ == '__main__':

    ControleDespesasApp().run()
