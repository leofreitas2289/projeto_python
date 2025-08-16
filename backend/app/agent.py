# backend/app/agent.py

from typing import List, Dict, Any

# Mapeamento simples de tipos de entidade para nomes de campos padronizados
# Esta é a "base de conhecimento" do nosso agente.
MAPEAMENTO_ENTIDADES = {
    "PER": "Responsável",      # Pessoa
    "ORG": "Organização Envolvida", # Organização
    "LOC": "Local de Execução",   # Localidade
    "MISC": "Termo Chave"         # Miscelânea (outros termos importantes)
}

def gerar_sugestoes_de_padronizacao(resultado_analise_nlp: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Recebe o resultado da análise do NLP e gera sugestões de padronização
    com base em regras heurísticas.
    """
    sugestoes = []
    entidades_processadas = set() # Para evitar sugestões duplicadas

    entidades = resultado_analise_nlp.get("entidades_nomeadas", [])

    for entidade in entidades:
        texto_entidade = entidade.get("texto")
        tipo_entidade = entidade.get("tipo_entidade")

        # Evita processar a mesma entidade duas vezes (ex: "São Paulo" aparece 2x)
        if texto_entidade in entidades_processadas:
            continue

        # REGRA 1: Se a entidade é de um tipo conhecido, sugira um campo padronizado.
        if tipo_entidade in MAPEAMENTO_ENTIDADES:
            campo_sugerido = MAPEAMENTO_ENTIDADES[tipo_entidade]
            
            sugestao = {
                "tipo_sugestao": "CAMPO_PADRONIZADO",
                "descricao": f"O termo '{texto_entidade}' foi identificado como um(a) '{campo_sugerido}'.",
                "acao_recomendada": f"Considere adicionar o valor '{texto_entidade}' ao campo padronizado '{campo_sugerido}'."
            }
            sugestoes.append(sugestao)
            entidades_processadas.add(texto_entidade)

    # REGRA 2 (Exemplo futuro): Se encontrar palavras como "aprovar", "revisar",
    # poderia sugerir "Etapa de Aprovação" ou "Etapa de Revisão".

    # REGRA 3 (Exemplo futuro): Se não encontrar nenhuma entidade de Pessoa (PER),
    # poderia sugerir "Nenhum responsável foi identificado. Considere adicionar um."

    return sugestoes

# Bloco de teste para executar este arquivo diretamente
if __name__ == '__main__':
    # Simula um resultado que viria do nosso módulo nlp.py
    exemplo_resultado_nlp = {
        "entidades_nomeadas": [
            {"texto": "Carlos Pereira", "tipo_entidade": "PER"},
            {"texto": "Soluções Tech", "tipo_entidade": "ORG"},
            {"texto": "Porto Alegre", "tipo_entidade": "LOC"}
        ],
        "tokens": [] # Não precisamos dos tokens para este teste
    }

    print("--- Gerando sugestões para o resultado de NLP de exemplo ---")
    sugestoes_geradas = gerar_sugestoes_de_padronizacao(exemplo_resultado_nlp)

    import json
    print("\n--- Sugestões Geradas pelo Agente ---")
    print(json.dumps(sugestoes_geradas, indent=2, ensure_ascii=False))
