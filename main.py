from get_pesquisas import agregado_atual, agregados_anteriores
import pandas as pd
import os

def create_tables(wp):
#FUNÇÃO CRIA AS TABELAS NECESSÁRIAS
    
    ##CRIA TABELA MASTER
    print("Criando tabela: master_IPCA.csv")  
    headersMasterIPCA = ['id', 'tipo', 'categoria', 'nome']
    dfMasterIPCA = pd.DataFrame(data = None, columns = headersMasterIPCA)
    dfMasterIPCA.to_csv(wp + 'master_IPCA.csv', sep = ';', index = False, encoding = 'latin1')
    print("Tabela master_IPCA.csv criada com sucesso")

    ##CRIA TABELA SUB
    print("Criando tabela com dados de índice, peso, participação e acumulado: IPCA_long.csv")
    headersSubIPCA = ['id', 'localizacao', 'mesref', 'variacao', 'peso', 'participacao', 'ts']
    dfSubIPCA = pd.DataFrame(data = None, columns = headersSubIPCA)
    dfSubIPCA.to_csv(wp + 'IPCA_long.csv', sep = ';', encoding = 'latin1', index_label = 'nrow')
    print("Tabela IPCA_long.csv criada com sucesso")

    return None

def initialize(a_tbs, r_tbs, wp):

    if all(item in a_tbs for item in r_tbs):
        tablesExist = True
        print("Tabelas encontradas.")
        agregado_atual()

    else:
        tablesExist = False
        print("Tabelas não encontradas. Iniciando criação.")
        create_tables(wp)
        agregados_anteriores()
        agregado_atual()

    return tablesExist

def main():

    write_path = r'.//tabelas//IPCA//'

    if not os.path.exists(write_path):
        os.makedirs(write_path)

    available_tbs = os.listdir(write_path)
    required_tbs = ['IPCA_long.csv', 'master_IPCA.csv']

    initialize(available_tbs, required_tbs, write_path)

if __name__ == "__main__":
    main()
