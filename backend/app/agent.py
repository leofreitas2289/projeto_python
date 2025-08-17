# backend/app/agent.py

from typing import List, Dict, Any
import re

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
    texto_original = resultado_analise_nlp.get("texto_original", "") # Adicionado para regras baseadas no texto completo

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
                "descricao": f"O termo \'{texto_entidade}\' foi identificado como um(a) \'{campo_sugerido}\'.",
                "acao_recomendada": f"Considere adicionar o valor \'{texto_entidade}\' ao campo padronizado \'{campo_sugerido}\'."
            }
            sugestoes.append(sugestao)
            entidades_processadas.add(texto_entidade)

    # NOVAS REGRAS DE APRIMORAMENTO

    # REGRA 2: Detecção de Datas (formato DD/MM/AAAA, DD-MM-AAAA, AAAA-MM-DD)
    # Expressão regular para datas comuns
    padrao_data = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b'
    datas_encontradas = re.findall(padrao_data, texto_original)
    for data in datas_encontradas:
        if data not in entidades_processadas: # Evita duplicidade com entidades nomeadas se houver
            sugestao = {
                "tipo_sugestao": "DATA_REFERENCIA",
                "descricao": f"Uma data \'{data}\' foi detectada na descrição.",
                "acao_recomendada": f"Considere adicionar \'{data}\' como uma data de referência ou prazo."
            }
            sugestoes.append(sugestao)
            entidades_processadas.add(data)

    # REGRA 3: Detecção de Valores Monetários (ex: R$ 1.000,00, $500, €25)
    # Expressão regular para valores monetários simples
    padrao_monetario = r'(?:R\$|US\$|€|£)\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:reais|dólares|euros|libras)'
    valores_encontrados = re.findall(padrao_monetario, texto_original, re.IGNORECASE)
    for valor in valores_encontrados:
        if valor not in entidades_processadas:
            sugestao = {
                "tipo_sugestao": "VALOR_ENVOLVIDO",
                "descricao": f"Um valor monetário \'{valor}\' foi detectado na descrição.",
                "acao_recomendada": f"Considere adicionar \'{valor}\' ao campo de valor envolvido."
            }
            sugestoes.append(sugestao)
            entidades_processadas.add(valor)

    # REGRA 4: Detecção de Palavras-chave de Status/Ação
    palavras_chave_status = {
        "aprovado": "Status do Processo",
        "revisado": "Status do Processo",
        "pendente": "Status do Processo",
        "concluído": "Status do Processo",
        "iniciado": "Status do Processo",
        "cancelado": "Status do Processo",
        "urgente": "Prioridade"
    }
    for palavra, campo_sugerido in palavras_chave_status.items():
        if re.search(r'\b' + re.escape(palavra) + r'\b', texto_original, re.IGNORECASE):
            if palavra not in entidades_processadas:
                sugestao = {
                    "tipo_sugestao": "PALAVRA_CHAVE",
                    "descricao": f"A palavra-chave \'{palavra}\' foi detectada.",
                    "acao_recomendada": f"Considere adicionar \'{palavra}\' ao campo \'{campo_sugerido}\'."
                }
                sugestoes.append(sugestao)
                entidades_processadas.add(palavra)

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
        "tokens": [], # Não precisamos dos tokens para este teste
        "texto_original": "O advogado Carlos Pereira precisa revisar o contrato da empresa Soluções Tech em Porto Alegre antes de 25/12/2025. O valor do contrato é R$ 1.500,00. O processo está pendente e é urgente."
    }

    print("--- Gerando sugestões para o resultado de NLP de exemplo ---")
    sugestoes_geradas = gerar_sugestoes_de_padronizacao(exemplo_resultado_nlp)

    import json
    print("\n--- Sugestões Geradas pelo Agente ---")
    print(json.dumps(sugestoes_geradas, indent=2, ensure_ascii=False))


