# backend/app/nlp.py

import spacy
import json

# Carrega o modelo de linguagem para português que instalamos.
# O bloco try-except ajuda a dar uma mensagem de erro clara se o modelo não for encontrado.
try:
    #nlp = spacy.load("pt_core_web_sm")
    # Mude de "pt_core_web_sm" para "pt_core_news_sm"
    nlp = spacy.load("pt_core_news_sm")

except OSError:
    print("Modelo \'pt_core_web_sm\' não encontrado. "
          "Por favor, execute o comando de instalação do modelo novamente.")
    nlp = None

def analisar_descricao_processo(texto: str):
    """
    Função para analisar a descrição de um processo usando SpaCy.
    Extrai entidades nomeadas (NER) e tokens/lemas.
    """
    if not nlp:
        return {"error": "Modelo de NLP não está carregado."}

    # Processa o texto com o modelo SpaCy
    doc = nlp(texto)

    # Extrai as entidades nomeadas (ex: Pessoas, Organizações, Locais)
    entidades = []
    for ent in doc.ents:
        entidades.append({
            "texto": ent.text,
            "tipo_entidade": ent.label_
        })
    
    # Extrai os tokens (palavras) e seus lemas (a forma base da palavra)
    tokens_e_lemas = []
    for token in doc:
        # Ignora pontuação e espaços em branco
        if not token.is_punct and not token.is_space:
            tokens_e_lemas.append({
                "palavra": token.text,
                "lema": token.lemma_
            })

    return {
        "entidades_nomeadas": entidades,
        "tokens": tokens_e_lemas,
        "texto_original": texto # Adicionando o texto original aqui
    }

# O bloco a seguir só será executado quando rodarmos este arquivo diretamente
# com o comando: python app/nlp.py
if __name__ == "__main__":
    
    exemplo_texto = ("O colaborador João da Silva, da empresa Acme Corp, iniciou o processo de "
                     "aprovação de fatura no valor de R$ 1.500,00 em São Paulo.")
    
    print(f"--- Analisando o texto: \'{exemplo_texto}\' ---")
    
    resultado_analise = analisar_descricao_processo(exemplo_texto)
    
    # Imprime o resultado de forma legível (JSON formatado)
    print("\n--- Resultado da Análise ---")
    print(json.dumps(resultado_analise, indent=2, ensure_ascii=False))


