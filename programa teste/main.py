import json
import os 
from collections import defaultdict 
from datetime import datetime

NOME_ARQUIVO = "cardapio.json"

# TESTE COMMIT

# --- 1. FUNÇÃO DE EXIBIÇÃO FORMATADA ---
def formatar_prato(prato):
    """Retorna a string formatada de um prato, incluindo o ID e Estoque."""
    
    nome_com_id = f"[{prato['id']}] {prato['nome']}"
    
    # Adiciona o estoque na exibição
    estoque_str = f"[{prato.get('estoque', 'N/A')}]" 
    
    preco_formatado = f"R$ {prato['preco']:.2f}"
    
    # Alinha a exibição
    texto_principal = f"{nome_com_id} {estoque_str}"
    espacos = 40 - len(texto_principal) - len(preco_formatado)
    
    return f"{texto_principal} {'-' * espacos} {preco_formatado}"

# --- 2. FUNÇÃO DE FILTRO POR CATEGORIA ---
def exibir_categoria(dados_cardapio, categoria_selecionada=None):
    """Exibe o cardápio, filtrando pela categoria se ela for fornecida."""
    
    print("\n=========================================")
    print(f"      🍴 {dados_cardapio['nome_restaurante']} - Cardápio 🍴    ")
    print("      (Estoque atual é mostrado entre [ ])")
    
    if categoria_selecionada and categoria_selecionada != "TODAS":
        print(f"      Filtro: {categoria_selecionada.title()}")
    print("=========================================")

    if categoria_selecionada == "TODAS":
        categoria_selecionada = None

    for item_categoria in dados_cardapio['itens']:
        categoria = item_categoria['categoria'].upper()
        
        if categoria_selecionada is None or categoria == categoria_selecionada:
            
            print(f"\n--- {categoria} ---")
            
            for prato in item_categoria['pratos']:
                print(formatar_prato(prato))

# --- 3. FUNÇÃO DE BUSCA POR NOME ---
def buscar_prato_por_nome(dados_cardapio):
    """Busca pratos que contenham a palavra-chave fornecida pelo usuário."""
    
    termo_busca = input("Digite o nome ou parte do nome do prato que procura: ").strip().lower()
    
    if not termo_busca:
        print("Busca cancelada.")
        return

    resultados = []
    
    for item_categoria in dados_cardapio['itens']:
        categoria_nome = item_categoria['categoria']
        for prato in item_categoria['pratos']:
            if termo_busca in prato['nome'].lower():
                resultados.append({
                    "nome": prato['nome'],
                    "preco": prato['preco'],
                    "categoria": categoria_nome,
                    "id": prato['id'],
                    "estoque": prato.get('estoque', 'N/A')
                })
    
    print("\n=========================================")
    print(f"      🔍 Resultados da Busca por '{termo_busca}'")
    print("=========================================")
    
    if not resultados:
        print("\nNenhum prato encontrado com o termo fornecido.")
    else:
        for item in resultados:
            print(f"\nCategoria: {item['categoria']}")
            print(formatar_prato(item))

# --- 4. FUNÇÃO PARA SALVAR A COMANDA EM ARQUIVO ---
def salvar_comanda(comanda, pratos_por_id, total_pedido):
    """Salva o resumo da comanda em um arquivo de texto no formato Comanda_DATA.txt."""
    
    agora = datetime.now()
    nome_arquivo_saida = agora.strftime("Comanda_%Y%m%d_%H%M%S.txt")
    
    try:
        with open(nome_arquivo_saida, 'w', encoding='utf-8') as arquivo_saida:
            
            arquivo_saida.write("=========================================\n")
            arquivo_saida.write(f"  REGISTRO DE COMANDA - {agora.strftime('%d/%m/%Y %H:%M:%S')}\n")
            arquivo_saida.write("=========================================\n\n")
            
            if not comanda:
                arquivo_saida.write("Nenhum item foi adicionado ao pedido.\n")
            else:
                for item_id, quantidade in comanda.items():
                    prato = pratos_por_id[item_id]
                    subtotal = prato['preco'] * quantidade
                    linha = f"({quantidade}x) {prato['nome']} ........ R$ {subtotal:.2f}\n"
                    arquivo_saida.write(linha)
                    
                arquivo_saida.write("-----------------------------------------\n")
                arquivo_saida.write(f"TOTAL GERAL: R$ {total_pedido:.2f}\n")
                
        print(f"\n✅ SUCESSO: Comanda salva como {nome_arquivo_saida}")
        
    except Exception as e:
        print(f"❌ ERRO ao salvar o arquivo: {e}")
        print(f"Verifique se você tem permissão para escrever na pasta: {os.getcwd()}") 


# --- 5. FUNÇÃO PARA SALVAR O CARDÁPIO (COM ESTOQUE ATUALIZADO) ---
def salvar_cardapio(dados_cardapio):
    """Salva todo o dicionário do cardápio de volta no arquivo JSON."""
    try:
        with open(NOME_ARQUIVO, 'w', encoding='utf-8') as arquivo:
            # Usa ensure_ascii=False para garantir caracteres especiais e indent=2 para legibilidade
            json.dump(dados_cardapio, arquivo, ensure_ascii=False, indent=2)
        print("🔄 Estoque atualizado no cardapio.json.") 
    except Exception as e:
        print(f"❌ ERRO GRAVE ao salvar o cardapio.json: {e}")

# --- 6. FUNÇÃO PARA FAZER E CALCULAR PEDIDO (COM VERIFICAÇÃO DE ESTOQUE) ---
def fazer_pedido_e_calcular(dados_cardapio):
    """Permite ao garçom inserir IDs dos pratos (ID,QUANTIDADE), calcula o total e atualiza o estoque."""
    
    # Mapeia ID -> objeto Prato (para buscar dados)
    pratos_por_id = {}
    
    # Mapeia ID -> referência direta ao objeto Prato no dicionário (para modificar o estoque)
    referencia_pratos = {} 
    
    for item_categoria in dados_cardapio['itens']:
        for prato in item_categoria['pratos']: 
            prato_id = prato['id'].upper()
            pratos_por_id[prato_id] = prato 
            referencia_pratos[prato_id] = prato

    comanda = defaultdict(int) 
    total_pedido = 0.0
    
    print("\n=========================================")
    print("      🧾 NOVO PEDIDO - Comanda (COM ESTOQUE)")
    print("=========================================")
    print("Digite o ID do item e a quantidade (ex: P1, 2). Digite FIM para finalizar.")
    
    while True:
        entrada_raw = input("Item (ID[, Quantidade]): ").strip().upper()
        
        if entrada_raw == "FIM":
            break
        
        partes = entrada_raw.split(',')
        item_id = partes[0].strip()
        
        quantidade = 1
        if len(partes) > 1:
            try:
                quantidade = int(partes[1].strip())
                if quantidade <= 0:
                    print("❌ ERRO: A quantidade deve ser um número inteiro positivo.")
                    continue
            except ValueError:
                print("❌ ERRO: A quantidade deve ser um número inteiro.")
                continue

        if item_id in pratos_por_id:
            prato_info = pratos_por_id[item_id]
            prato_para_modificar = referencia_pratos[item_id] 
            estoque_atual = prato_para_modificar.get('estoque', 0) 

            # --- VERIFICAÇÃO DE ESTOQUE ---
            if estoque_atual < quantidade:
                print(f"⚠️ ESTOQUE INSUFICIENTE para {prato_info['nome']}!")
                print(f"Estoque atual: {estoque_atual}. Pedido: {quantidade}.")
                continue 
            
            # --- ATUALIZAÇÃO E DEDUÇÃO ---
            
            # Diminui a quantidade pedida no estoque do dicionário principal (por referência)
            prato_para_modificar['estoque'] -= quantidade 
            
            # Adiciona o item à comanda e calcula o total
            comanda[item_id] += quantidade
            subtotal_item = prato_info['preco'] * quantidade
            total_pedido += subtotal_item
            
            print(f"✅ Adicionado {quantidade}x: {prato_info['nome']} (Estoque restante: {prato_para_modificar['estoque']}).")
            
        else:
            print(f"❌ ERRO: ID '{item_id}' não encontrado. Verifique o cardápio.")


    # --- FINALIZAÇÃO E SALVAMENTO ---
    
    print("\n=========================================")
    print("         RESUMO DA COMANDA               ")
    print("=========================================")
    
    if not comanda:
        print("Nenhum item foi adicionado ao pedido.")
    else:
        for item_id, quantidade in comanda.items():
            prato = pratos_por_id[item_id]
            subtotal = prato['preco'] * quantidade
            print(f"({quantidade}x) {prato['nome']} ........ R$ {subtotal:.2f}")
            
        print("-----------------------------------------")
        print(f"TOTAL GERAL: R$ {total_pedido:.2f}")
        
        # 1. SALVA O ARQUIVO DE COMANDA
        salvar_comanda(comanda, pratos_por_id, total_pedido) 

        # 2. SALVA O ARQUIVO DE CARDÁPIO (com o estoque deduzido)
        salvar_cardapio(dados_cardapio)

    print("=========================================")

# --- 7. FUNÇÃO PARA REPOR ESTOQUE ---
def repor_estoque(dados_cardapio):
    """Permite ao usuário repor o estoque de um item existente no cardápio."""
    
    referencia_pratos = {} 
    for item_categoria in dados_cardapio['itens']:
        for prato in item_categoria['pratos']:
            referencia_pratos[prato['id'].upper()] = prato

    print("\n=========================================")
    print("      🛒 REPOSIÇÃO DE ESTOQUE          ")
    print("=========================================")

    item_id = input("Digite o ID do item a ser reposto (ex: P1): ").strip().upper()

    if item_id in referencia_pratos:
        prato = referencia_pratos[item_id]
        print(f"\nItem selecionado: {prato['nome']} (Estoque Atual: {prato.get('estoque', 0)})")
        
        try:
            quantidade_repous = int(input("Quantas unidades deseja adicionar ao estoque? "))
            
            if quantidade_repous <= 0:
                print("❌ ERRO: A quantidade de reposição deve ser um número inteiro positivo.")
                return

            # Atualiza o estoque
            prato['estoque'] += quantidade_repous
            
            print(f"✅ Reposição de {quantidade_repous} unidades concluída para {prato['nome']}.")
            print(f"Novo Estoque: {prato['estoque']}")

            # Salva a alteração permanentemente no JSON
            salvar_cardapio(dados_cardapio)
            
        except ValueError:
            print("❌ ERRO: A quantidade deve ser um número inteiro.")
            
    else:
        print(f"❌ ERRO: ID '{item_id}' não encontrado.")


# --- 8. FUNÇÃO DE MENU PRINCIPAL ---
def menu_de_opcoes(dados_cardapio):
    """Apresenta as opções de filtro, busca, pedido e reposição."""
    
    categorias_disponiveis = ["TODAS"]
    for item in dados_cardapio['itens']:
        categorias_disponiveis.append(item['categoria'].upper())
    
    while True:
        print("\n=========================================")
        print("     MENU PRINCIPAL - Opções do Garçom")
        print("=========================================")
        
        for i, cat in enumerate(categorias_disponiveis):
            print(f"[{i + 1}] Ver Categoria: {cat.title()}")
            
        # Opções adicionais
        indice_busca = len(categorias_disponiveis) + 1
        indice_pedido = len(categorias_disponiveis) + 2
        indice_reposicao = len(categorias_disponiveis) + 3 

        print(f"[{indice_busca}] Buscar prato por Nome") 
        print(f"[{indice_pedido}] Fazer um Novo Pedido (Comanda)")
        print(f"[{indice_reposicao}] Repor Estoque (Gestão)") 
        
        print("[0] Sair do Programa")
        print("-----------------------------------------")
        
        escolha = input("Digite o número da sua escolha: ").strip()
        
        try:
            escolha_indice = int(escolha)
            
            if escolha_indice == 0:
                print("Saindo do programa. Até mais!")
                return None, None
            
            if escolha_indice == indice_busca:
                return "BUSCA", None
            
            if escolha_indice == indice_pedido:
                return "PEDIDO", None 
            
            if escolha_indice == indice_reposicao: 
                return "REPOSICAO", None
            
            if 1 <= escolha_indice <= len(categorias_disponiveis):
                return "FILTRO", categorias_disponiveis[escolha_indice - 1] 
            else:
                print("Opção inválida. Tente novamente.")
                
        except ValueError:
            print("Entrada inválida. Por favor, digite apenas o número.")

# --- 9. LÓGICA PRINCIPAL (EXECUÇÃO) ---
if not os.path.exists(NOME_ARQUIVO):
    print(f"ERRO: O arquivo '{NOME_ARQUIVO}' não foi encontrado.")
else:
    try:
        # Abertura e carregamento do JSON
        with open(NOME_ARQUIVO, 'r', encoding='utf-8') as arquivo:
            dados_cardapio = json.load(arquivo) 

        # Loop principal do menu
        while True:
            acao, valor = menu_de_opcoes(dados_cardapio)
            
            if acao is None:
                break
            
            if acao == "FILTRO":
                exibir_categoria(dados_cardapio, valor)
            
            elif acao == "BUSCA":
                buscar_prato_por_nome(dados_cardapio)
            
            elif acao == "PEDIDO":
                fazer_pedido_e_calcular(dados_cardapio)
            
            elif acao == "REPOSICAO":
                repor_estoque(dados_cardapio)
                
    except json.JSONDecodeError as e:
        print(f"ERRO DE SINTAXE JSON: Verifique o arquivo cardapio.json. Detalhes: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")