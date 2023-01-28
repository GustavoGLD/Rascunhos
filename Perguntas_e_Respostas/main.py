import PySimpleGUI as sg

PERGUNTA = 'Qual o menor País do Mundo???'
RESPOSTA = 'Vaticano'

#Escolhendo a paleta de cor da janela
sg.theme('DarkGreen')

#Escrevendo o título
title = [sg.Text('🏆🏆 QUIZ: PERGUNTAS E RESPOSTAS!!! 🏆🏆', font=("Courier", 17, "bold"),)]

#Escrevendo a pergunta
question = [sg.Text(PERGUNTA, font=("Arial", 15, "italic"))]

#Input Resposta
answer = [sg.Text('Digite sua resposta:'), sg.InputText(key='answer')]

#Botão "Enviar Resposta"
submit = [sg.Button('Enviar Resposta', key='submit')]

#Adicionando elementos ao Layout
layout = [title, [sg.HSep(color='green')], question, answer, submit]

#Criando Janela
window = sg.Window('Quiz: O Jogo de Perguntas e Respostas', layout)

#Game Loop
while True:

    #Pegar inputs
    event, values = window.read()

    #Botão de fechar janela
    if event == sg.WIN_CLOSED:
        break

    #Se o usuário clicou em "Enviar Resposta"
    if event == 'submit':

        #Se a respota tiver correta
        if values['answer'].lower() == RESPOSTA.lower():
            sg.theme('Green')
            sg.Popup('Você acertou!', font=('Courier', 12, 'bold'), custom_text='Continuar...')

        #Se a respota tiver errada
        else:
            sg.theme('DarkRed1')
            sg.Popup('Resposta INCORRETA!', font=('Courier', 12, 'bold'), custom_text='Tentar novamente...')

window.close()
