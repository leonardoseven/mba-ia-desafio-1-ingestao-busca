from search import search_prompt

def main():
    question = input("Digite sua pergunta: ")
    response = search_prompt(question)

    if not response:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return
    
    print(response)
    main()

if __name__ == "__main__":
    main()