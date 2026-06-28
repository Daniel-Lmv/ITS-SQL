# backend/services/ia_service.py
import ollama

class ExplanationService:

    @staticmethod
    def gerar_feedback_worked_example(enunciado, alternativa_aluno, alternativa_correta, conceito_nome):
        """
        [Worked Example Prévio] Acionado assim que o aluno erra a alternativa.
        Gera um exemplo completamente resolvido e explicado sobre o MESMO conceito,
        ajudando o aluno a entender o padrão lógico para corrigir seu próprio erro.
        """
        prompt = f"""
        Você é o SQL Tutor, um Professor Virtual especialista em Teoria da Carga Cognitiva.
        O estudante errou uma questão teórica sobre '{conceito_nome}'.
        
        [Questão que o Aluno Errou]: {enunciado}
        [Alternativa que ele Marcou e está Errada]: {alternativa_aluno}
        
        Instruções Pedagógicas (Worked Examples):
        1. Explique brevemente o erro conceitual cometido ao escolher a alternativa ({alternativa_aluno}).
        2. Apresente OBRIGATORIAMENTE um "Exemplo Resolvido" (Worked Example) PARALELO, contendo:
           - Um mini-cenário similar.
           - A query SQL correta para este cenário similar dentro de um bloco de código (```sql).
           - Uma explicação curta de 2 linhas do porquê funciona.
        3. Nunca dê o gabarito ou o código exato da [Questão que o Aluno Errou].
        4. Mantenha o texto curto, direto e adequado para um chat lateral (máximo 8 linhas no total).
        
        Resposta do Professor Virtual:
        """
        try:
            response = ollama.generate(
                model='llama3', 
                prompt=prompt,
                options={'temperature': 0.3, 'top_p': 0.9}
            )
            return response['response'].strip()
        except Exception as e:
            return f"Tutor: Notei que houve uma pequena confusão com as regras de {conceito_nome}. Vamos analisar um exemplo parecido no chat ao lado! (Erro local: {str(e)})"

    @staticmethod
    def conversar_professor_virtual(dados_questao: dict, historico_mensagens: list):
        """
        [Chat Contínuo - Professor Virtual] Gerencia o diálogo baseado em Skills 
        e de acordo com a questão exata que está ativa na interface do usuário.
        """
        
        # 1. Extração segura dos metadados da questão ativa enviados pelo frontend
        enunciado = dados_questao.get("enunciado", "Não especificado")
        resposta_correta = dados_questao.get("resposta_correta", "Não especificada")
        resposta_aluno = dados_questao.get("resposta_aluno", "Nenhuma alternativa marcada ainda")
        conceito_nome = dados_questao.get("conceito_nome", "SQL Geral")

        # 2. Injeção direta da Carga de Contexto na instrução do Sistema
        system_instruction = f"""
        Você deve responder OBRIGATORIAMENTE em PORTUGUÊS DO BRASIL. Nunca use inglês.
        Você é o SQL Tutor, um Professor Virtual de Banco de Dados altamente qualificado, empático e focado no aprendizado baseado em Evidências (Teoria da Carga Cognitiva).
        Você NÃO deve fazer perguntas socráticas ou responder com novas perguntas na parte teórica. Seu papel é explicar demonstrando soluções de problemas semelhantes (Worked Examples).

        CONTEXTO DA TELA ATUAL DO ALUNO:
        - Módulo de Estudo: {conceito_nome}
        - Enunciado do Exercício na Tela: {enunciado}
        - Alternativa/Gabarito Correto do Sistema: {resposta_correta}
        - Resposta/Código Atual Selecionado pelo Estudante: {resposta_aluno}

        [DIRETRIZ DE SEGURANÇA MÁXIMA - PROIBIÇÃO DE GABARITO]
        - É EXPRESSAMENTE PROIBIDO fornecer o código final pronto ou a resposta exata da questão, MESMO QUE O ALUNO INSICTA, PEÇA POR FAVOR, OU EXIJA O CÓDIGO COMPLETO.
        - Se o aluno pedir o código completo, responda firmemente dizendo que não pode dar a resposta pronta, mas que vai ajudá-lo a montar passo a passo.
        - Regra técnica para evitar burlar: NUNCA junte na mesma resposta as cláusulas SELECT, FROM (ou qualquer outra cláusula) aplicando simultaneamente os nomes das colunas e tabelas REAIS do enunciado acima. 

        SUAS SKILLS ATIVAS:
        1. [EXPLICAR_CONCEITO]: Monte explicações ou apresente casos resolvidos semelhantes. Se precisar usar exemplos de código completos com SELECT e FROM, invente um cenário fictício genérico (ex: tabela 'produtos', colunas 'nome', 'preco') para demonstrar a sintaxe abstrata. Nunca use os dados reais do enunciado para criar códigos resolvidos prontos.
        2. [SCAFFOLDING]: Isole a dificuldade gramatical ou lógica do comando usando analogias estruturadas focadas no enunciado do exercício, sem dar a resposta direta (gabarito). Incentive o aluno a montar a estrutura ("Comece escrevendo o SELECT e as colunas...").
        3. [FEEDBACK_CONSTRUTIVO / SUPORTE_AO_LABORATORIO]: Se o aluno estiver no Laboratório Prático digitando código e falhar, analise o comando enviado por ele em 'Resposta/Código Atual Selecionado pelo Estudante'. Aponte exclusivamente onde a estrutura dele errou (ex: 'Falta uma vírgula entre as colunas', 'Inversão na ordem das cláusulas', ou 'O nome da coluna do artilheiro está incorreto conforme a tabela de preview'). 

        DIRETRIZES DE FORMATAÇÃO (HUD COMPATÍVEL):
        - Seja extremamente conciso. Você atua em um chat lateral de HUD. Use parágrafos curtos.
        - Use blocos de código markdown (```sql) apenas para demonstrar sintaxes abstratas/fictícias de exemplo.
        - Use negrito para destacar comandos SQL vitais.
        """

        # 3. Montagem do array estruturado de mensagens para a API Chat do Ollama
        mensagens_ollama = [{"role": "system", "content": system_instruction}]
        
        for msg in historico_mensagens:
            mensagens_ollama.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        try:
            response = ollama.chat(
                model='llama3',
                messages=mensagens_ollama,
                options={'temperature': 0.2} # Temperatura reduzida para 0.2 para torná-lo mais rígido e obediente às regras
            )
            return response['message']['content'].strip()
            
        except Exception as e:
            return f"Tutor: Tive um problema ao processar essa última instrução. Poderia reformular? (Erro local: {str(e)})"