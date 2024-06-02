import requests as rq
import pandas as pd
import json
import datetime
import os

import time

class Pesquisa():
    indice = "IPCA"

    def __init__(self, var_name: str, peso_name: str, tipo: str, classificacao: str, inicio: str, fim = None, localidades = None):
        self.var_name = var_name
        self.peso_name = peso_name
        self.inicio = inicio
        self.fim = fim
        self.tipo = tipo
        self.classificacao = classificacao
        #self.localidades = localidades
        #self.peso = peso

        #*Define self.duracao do agregado
        if self.tipo == 'atual':
            self.duracao = available_updates('IPCA_long.csv')[0]
        elif self.tipo == 'simples' or self.tipo == 'duplo':
            mes_inicio = int(inicio.split("/")[0])
            ano_inicio = int(inicio.split("/")[1])
            mes_fim = int(fim.split("/")[0])
            ano_fim = int(fim.split("/")[1])
            duracao = []

            for year in [ano_inicio]:
                for month in range(mes_inicio, 13):
                    duracao.append(f'{year}{month:02}')

            for year in range(ano_inicio + 1, ano_fim):
                for month in range(1, 13):
                    duracao.append(f'{year}{month:02}')

            for year in [ano_fim]:
                for month in range(1, mes_fim + 1):
                    duracao.append(f'{year}{month:02}')

            if '199108' in duracao:
                duracao.remove('199108')

            self.duracao = duracao

        #*Define sel.url da variavel variação ou peso
        url_split = ["https://servicodados.ibge.gov.br/api/v3/agregados/", "/periodos/>__</variaveis/", "?localidades=N1[all]&classificacao=", "[all]"]
        self.url_var = url_split[0] + var_name + url_split[1] + "63" + url_split[2] + classificacao + url_split[3]
        self.url_peso = url_split[0] + peso_name + url_split[1] + "66" + url_split[2] + classificacao + url_split[3]

def url2data(url):
#FUNÇÃO RECEBE UMA URL E RETORNA O SEU CONTEÚDO    
    
    r = rq.get(url)
    if r.status_code == 200:
        data = json.loads(r.text)
    else:
        print("Importação falhou.\n", url)
        data = 0
    
    return data

def date_me(argument):
#RECEBE ARGUMENTOS DE DATA, DECIDE O FORMATO ADEQUADO E DEVOLVE UMA LISTA COM TRÊS ITENS CONTENDO FORMATOS ["MÊS/ANO", AAAAMM, datetime.date(ANO, MÊS, 1)]

    dict_intmonth = {'1': 'janeiro',
                     '2': 'fevereiro',
                     '3': 'março',
                     '4': 'abril',
                     '5': 'maio',
                     '6': 'junho',
                     '7': 'julho',
                     '8': 'agosto',
                     '9': 'setembro',
                     '10': 'outubro',
                     '11': 'novembro',
                     '12': 'dezembro'}
    
    dict_monthint = {'janeiro': '01',
                     'fevereiro': '02',
                     'março': '03',
                     'abril': '04',
                     'maio': '05',
                     'junho': '06',
                     'julho': '07',
                     'agosto': '08',
                     'setembro': '09',
                     'outubro': '10',
                     'novembro': '11',
                     'dezembro': '12'}
    
    list = []
    strdate = None
    intdate = None
    datedate = None

    
    if isinstance(argument, str):
        if argument.isdigit():
            argument = int(argument)
        else: pass
    else: pass

    if isinstance(argument, str):
        #sets string part
        strdate = argument

        #sets integer part
        splitt = argument.split("/")
        splitt[0] = dict_monthint[splitt[0]]
        intdate = splitt[1] + splitt[0]
        intdate = int(intdate)

        #sets datetime.date part
        datedate = (int(splitt[1]), int(splitt[0]), 1)

    elif isinstance(argument, int):
        #sets string part
        strdate = dict_intmonth[str(argument%100)] + "/" + str(int(argument/100))

        #sets integer part
        intdate = argument

        #sets datetime.date part
        datedate = datetime.date(int(argument/100), argument%100, 1)

    elif isinstance(argument, datetime.date):
        #sets string part
        strdate = dict_intmonth[str(argument.month)] + "/" + str(argument.year)
        
        #sets integer part
        intdate = argument.year*100 + argument.month
        
        #sets datetime.date part
        datedate = argument

    else:
        print("Please, chesck the type of argumet you are trying to datefy.\n")

    list = [strdate, intdate, datedate]

    return list

def available_updates(file_name):
#FUNÇÃO PEGA OS UPDATES DISPONÍVEIS, OS JÁ FEITOS E RETORNA LISTA COM OS QUE FALTAM
     
    #UPDATES DISPONÍVEIS    
    url_calendario_ipca = "https://servicodados.ibge.gov.br/api/v3/calendario/indice-nacional-de-precos-ao-consumidor-amplo"
    calendario_ipca = url2data(url_calendario_ipca)
    df_calendario_ipca = pd.DataFrame(calendario_ipca['items'])

    #Salva uma cópia .csv do calendario de divulgações para consulta
    temp_path = r'.//tabelas//temps' 
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    df_calendario_ipca.to_csv(temp_path + "//calendario_ipca.csv",
                              sep = ';',
                              columns = df_calendario_ipca.columns,
                              header = True,
                              index = True,
                              encoding = 'utf8',
                              decimal = ',') 

    #inicializa (i) variável para calcular qual a próxima divulgação e (ii) lista para saber quais as divulgacoes já foram feitas
    dategap = datetime.timedelta(days=730)
    lista_datas_divulgacao_passadas = []
    lista_anomes_referencia_passadas = []

    #itera por todos as linhas do calendário para separar quais divulgações já aconteceram e quando será a próxima
    for index, row in df_calendario_ipca.iterrows():
        ls_divulgacao = row['data_divulgacao'].split(" ")
        ls_data_divulgacao = ls_divulgacao[0].split("/")
        ls_hora_divulgacao = ls_divulgacao[1].split(":")
        ls_divulgacao = ls_data_divulgacao + ls_hora_divulgacao
        
        #para cada item monta uma data com o dia da divulgação e um string com o ano e mês de referência
        data_divulgacao = datetime.date(int(ls_divulgacao[2]), int(ls_divulgacao[1]), int(ls_divulgacao[0]))
        anomes_referencia = datetime.date(int(row['ano_referencia_inicio']), int(row['mes_referencia_inicio']), 1)

        #se data estiver no passado, acresta à lista com as divulgações que já foram feitas
        if (data_divulgacao < datetime.date.today()) and (anomes_referencia.year >= 2020):
            lista_datas_divulgacao_passadas += [data_divulgacao]
            lista_anomes_referencia_passadas += [anomes_referencia]
        #se data estiver no futuro, calcula quando o menor timedelta para saber a próxima divulgacao
        elif datetime.date.today() < data_divulgacao:
            if data_divulgacao - datetime.date.today() < dategap:
                dategap = data_divulgacao - datetime.date.today()
                prox_divulgacao = data_divulgacao
            else:
                pass
        else:
            pass

    #formata cada item da lista de divulgações passadas para um formato legível
    lista_int_divulgacao_passadas = []
    lista_str_anomes_referencia_passadas = []
    for item in lista_datas_divulgacao_passadas:
        lista_int_divulgacao_passadas += [date_me(item)[1]]

    for item in lista_anomes_referencia_passadas:
        lista_str_anomes_referencia_passadas += [date_me(item)[0]]

    lista_str_anomes_referencia_passadas.reverse()

    #PEGA OS UPDATES JÁ FEITOS
    #Abre o arquivo .csv
    read_path = './/tabelas//IPCA//' + file_name
    df = pd.read_csv(read_path, sep = ';', encoding='latin1', index_col = 'nrow')
    succesful_updates = df['mesref'].unique()
    
    lista_str_succesful_updates = [] #formata cada item da lista de divulgações passadas para um formato legível
    for date in succesful_updates:
        lista_str_succesful_updates += [date]

    #CALCULA OS UPDATES QUE FALTAM
    missing_updates = lista_str_anomes_referencia_passadas
    for item in lista_str_succesful_updates:
        if item in missing_updates:
            missing_updates.remove(item)  #remove updates já feitos
        else:
            #print('Valor', item, 'não encontrado')
            pass

    return [missing_updates, prox_divulgacao]

def limpa_celula (value):

    try:
        clean_value = float(value)
    except:
        print("Exception caught:", value)
        clean_value = 0

    return clean_value

def json_to_csv (pesq_agregado):
    dictTipo = {1: 'GG', 2: 'SG', 4: 'II', 7: 'SI'}

    for month in pesq_agregado.duracao:
        time.sleep(3) #!!# código está disparando alarme retry do servidor #!!#

        headers_dfMasterIPCA = ['id', 'tipo', 'categoria', 'nome']        
        dfMasterIPCA = pd.read_csv('.//tabelas//IPCA//master_IPCA.csv', sep = ';', encoding='latin1')
        headers_dfSubIPCALong = ['id', 'localizacao', 'mesref', 'variacao', 'peso', 'participacao', 'ts']
        dfSubIPCALong = pd.DataFrame(data = None, columns = headers_dfSubIPCALong)

        print("Importando dados da pesquisa", str(pesq_agregado.var_name), "de", date_me(str(month))[0])
        var_data = url2data(pesq_agregado.url_var.split('>__<')[0] + str(date_me(month)[1]) + pesq_agregado.url_var.split('>__<')[1])
        pes_data = url2data(pesq_agregado.url_peso.split('>__<')[0] + str(date_me(month)[1]) + pesq_agregado.url_peso.split('>__<')[1])

        for index, keys in enumerate(var_data[0].get('resultados')):
            raw_value = list(var_data[0].get('resultados')[index].get('classificacoes')[0].get('categoria').values())
            
            #*ATUALIZA MASTER
            if len(raw_value[0].split(".")) == 1:
                raw_value[0] = '0.' + raw_value[0]
            if int(raw_value[0].split(".")[0]) in dfMasterIPCA['id'].tolist():
                pass
            else:
                if raw_value[0].split(".")[0] == '0':
                    dfAppendixMasterTipo = 'IG'
                else:
                    dfAppendixMasterTipo = dictTipo[len(raw_value[0].split(".")[0])]
                
                dfAppendixMaster = pd.DataFrame(data = None, columns = headers_dfMasterIPCA)
                dfAppendixMaster = pd.DataFrame({'id': [str(raw_value[0].split(".")[0])],
                                                 'tipo': [dfAppendixMasterTipo],
                                                 'categoria': [str(raw_value[0].split(".")[0][0])],
                                                 'nome': [raw_value[0].split(".")[1]]})
                
                dfAppendixMaster.to_csv('.//tabelas//IPCA//master_IPCA.csv', sep = ';', header = False, index = False, encoding = 'latin1', mode = 'a')
                
        
            #*ATUALIZA SUB
            df_id = [raw_value[0].split(".")[-2]]
            df_localizacao = var_data[0].get('resultados')[index].get('series')[0].get('localidade').get('nivel').get('nome')
            df_mesref = [date_me(list(var_data[0].get('resultados')[index].get('series')[0].get('serie').keys())[0])[0]]
            df_variacao = limpa_celula(list(var_data[0].get('resultados')[index].get('series')[0].get('serie').values())[0])
            df_peso = limpa_celula(list(pes_data[0].get('resultados')[index].get('series')[0].get('serie').values())[0])
            try:
                df_participacao = df_variacao * df_peso / 100
            except:
                print("Exceção encontrada:", list(var_data[0].get('resultados')[index].get('series')[0].get('serie').values())[0], "*", list(pes_data[0].get('resultados')[index].get('series')[0].get('serie').values())[0], "não definido.")
                df_participacao = 0           

            dfAppendixSub = pd.DataFrame({'id': df_id,
                                          'localizacao': df_localizacao,
                                          'mesref': df_mesref,
                                          'variacao': df_variacao,
                                          'peso': df_peso,
                                          'participacao': df_participacao,
                                          'ts': [datetime.datetime.now()]})
            dfSubIPCALong = pd.concat([dfSubIPCALong, dfAppendixSub], join = 'outer')

        dfSubIPCALong.to_csv('.//tabelas//IPCA//IPCA_long.csv', sep=';', header = False, index = True, index_label = 'nrow', encoding='latin1', mode = 'a')

        print("Pesquisa", str(pesq_agregado.var_name), "de", date_me(str(month))[0], "importada com sucesso.")

    return True

def agregados_anteriores ():

    pesq_1419 = Pesquisa(var_name = "1419",
                         peso_name = "1419",
                         tipo = "simples",
                         classificacao  = "315",
                         inicio = "01/2012",
                         fim = "12/2019",
                         localidades = None)
    
    pesq_2938 = Pesquisa(var_name = "2938",
                         peso_name = "2938",
                         tipo = "simples",
                         classificacao = "315",
                         inicio = "07/2006",
                         fim = "12/2011",
                         localidades = None)
    
    pesq_655_656 = Pesquisa(var_name = "655",
                            peso_name = "656",
                            tipo = "duplo",
                            classificacao = "315",
                            inicio = "08/1999",
                            fim = "06/2006",
                            localidades = None)
    
    pesq_58_61 = Pesquisa(var_name = "58",
                          peso_name = "61",
                          tipo = "duplo",
                          classificacao = "72",
                          inicio = "01/1991",
                          fim = "07/1999",
                          localidades = None)
    
    pesq_1692_1693 = Pesquisa(var_name = "1692",
                              peso_name = "1693",
                              tipo = "duplo",
                              classificacao = "72",
                              inicio = "07/1989",
                              fim = "12/1990",
                              localidades = None)

    ls_agregados_anteriores = [pesq_1692_1693, pesq_58_61, pesq_655_656, pesq_2938, pesq_1419]
    print("Iniciando importação de agregados anteriores.")
    for item_anterior in ls_agregados_anteriores:
        json_to_csv(item_anterior)

    return None

def agregado_atual ():

        pesq_7060 = Pesquisa(var_name = "7060",
                         peso_name = "7060",
                         tipo = "atual",
                         classificacao = "315",
                         inicio = "01/2020",
                         fim = "04/2024",
                         localidades = None)
        

        ls_agregado_atual = [pesq_7060]
        print("Iniciando atualização.")
        for item_atual in ls_agregado_atual:
            json_to_csv(item_atual)
        
        return None

if __name__ == "__main__":
    agregados_anteriores()
    agregado_atual()