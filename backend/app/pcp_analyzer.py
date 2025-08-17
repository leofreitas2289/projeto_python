# backend/app/pcp_analyzer.py

from typing import List, Dict
from .schemas import Process, ProcessStep, PcpOptimizationResponse

def analisar_e_otimizar_processo_pcp(processo: Process) -> PcpOptimizationResponse:
    """
    Analisa um processo produtivo e gera sugestões de otimização baseadas em PCP.
    """
    gargalos_identificados = []
    sugestoes_otimizacao = []
    metricas_desempenho_esperadas = {}

    # 1. Análise de Gargalos
    # Identifica a etapa com a menor capacidade produtiva
    if processo.steps:
        gargalo_step = min(processo.steps, key=lambda step: step.capacity_per_hour)
        gargalos_identificados.append(f"A etapa \'{gargalo_step.name}\' é um gargalo com capacidade de {gargalo_step.capacity_per_hour} unidades/hora.")
        sugestoes_otimizacao.append(f"Considere aumentar a capacidade da etapa \'{gargalo_step.name}\' para otimizar o fluxo de produção.")

    # 2. Cálculo de Tempo de Ciclo Total e Capacidade
    total_duration_minutes = sum(step.duration_minutes for step in processo.steps)
    total_capacity_per_hour = min(step.capacity_per_hour for step in processo.steps) if processo.steps else 0

    metricas_desempenho_esperadas["tempo_ciclo_total_minutos"] = total_duration_minutes
    metricas_desempenho_esperadas["capacidade_maxima_unidades_por_hora"] = total_capacity_per_hour

    # 3. Sugestões de Otimização (Exemplos)
    if processo.target_quantity and total_capacity_per_hour > 0:
        tempo_necessario_horas = processo.target_quantity / total_capacity_per_hour
        sugestoes_otimizacao.append(f"Para produzir {processo.target_quantity} unidades, o tempo mínimo estimado é de {tempo_necessario_horas:.2f} horas.")
        if tempo_necessario_horas * 24 > processo.deadline_days:
            sugestoes_otimizacao.append(f"O prazo de {processo.deadline_days} dias pode ser apertado para a quantidade alvo. Considere ajustar a meta ou a capacidade.")

    # Exemplo de sugestão baseada em tipo de processo
    if processo.process_type.lower() == "manufatura":
        sugestoes_otimizacao.append("Avalie a implementação de técnicas de Lean Manufacturing para reduzir desperdícios.")
    elif processo.process_type.lower() == "serviço":
        sugestoes_otimizacao.append("Considere a padronização de procedimentos para melhorar a eficiência do serviço.")

    return PcpOptimizationResponse(
        gargalos_identificados=gargalos_identificados,
        sugestoes_otimizacao=sugestoes_otimizacao,
        metricas_desempenho_esperadas=metricas_desempenho_esperadas
    )



