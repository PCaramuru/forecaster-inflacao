import requests as rq
import pandas as pd
import json
import datetime
import os

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

def checks_data(data):
    #Checa se o número de observações de variação e peso são iguais
    if len(data[0].get('resultados')) != len(data[1].get('resultados')):
        print("ATENÇÃO! Número de observações de variação e peso estão desconformes.")
    else:
        for index, keys in enumerate(data[0].get('resultados')):
            #Checa se itens estão na mesma ordem:
            if str(data[0].get('resultados')[index].get('classificacoes')[0].get('categoria').values()) != str(data[1].get('resultados')[index].get('classificacoes')[0].get('categoria').values()):
                print("ATENÇÃO! Observações de variação e peso estão fora de ordem.")
    return

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

def update_tables(table_list):
#FUNÇÃO BUSCA RESULTADOS DA PESQUISA ATUAL 7060
    
    missing_updates, prox_update = available_updates(table_list[0])
    dictTipo = {1: 'GG', 2: 'SG', 4: 'II', 7: 'SI'}

    dfSubIPCALong = pd.read_csv('.//tabelas//IPCA//IPCA_long.csv', sep = ';', encoding='latin1', index_col = 'nrow')
    dfMasterIPCA = pd.read_csv('.//tabelas//IPCA//master_IPCA.csv', sep = ';', encoding='latin1')
    
    for date_int in missing_updates:
        print("Importando dados da pesquisa 7060 de", str(date_me(date_int)[0]))
        update_url = "https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/" + str(date_me(date_int)[1]) + "/variaveis/63|66?localidades=N1[all]&classificacao=315[all]"
        update_data = url2data(update_url)
        #checks_data(old_data) #chama função para conferir integridade dos dados

        for index, keys in enumerate(update_data[0].get('resultados')):
            #Atualiza Master
            raw_value = list(update_data[0].get('resultados')[index].get('classificacoes')[0].get('categoria').values())
            if len(raw_value[0].split(".")) == 1:
                raw_value[0] = '0.' + raw_value[0]
            if raw_value[0].split(".")[-2] in dfMasterIPCA['id'].tolist():
                pass
            else:
                if raw_value[0].split(".")[-2] == '0':
                    dfAppendixMasterTipo = 'IG'
                else:
                    dfAppendixMasterTipo = dictTipo[len(raw_value[0].split(".")[-2])]

                dfAppendixMaster = pd.DataFrame()
                dfAppendixMaster = pd.DataFrame({'id': [raw_value[0].split(".")[-2]],
                                                'tipo': [dfAppendixMasterTipo],
                                                'categoria': [raw_value[0].split(".")[-2][0]],
                                                'nome': [raw_value[0].split(".")[-1]]})

                dfMasterIPCA = pd.concat([dfMasterIPCA, dfAppendixMaster], join = 'outer')

            #Atualiza Sub
            dfAppendixSub = pd.DataFrame({'id': [raw_value[0].split(".")[-2]],
                                          'localizacao': update_data[0].get('resultados')[index].get('series')[0].get('localidade').get('nivel').get('nome'),
                                          'mesref': [date_me(list(update_data[0].get('resultados')[index].get('series')[0].get('serie').keys())[0])[0]],
                                          'variacao': [list(update_data[0].get('resultados')[index].get('series')[0].get('serie').values())[0].replace('.',',')],
                                          'peso': [list(update_data[1].get('resultados')[index].get('series')[0].get('serie').values())[0].replace('.',',')],
                                          'ts': [datetime.datetime.now()]})
            dfSubIPCALong = pd.concat([dfSubIPCALong, dfAppendixSub], join = 'outer')

        dfSubIPCALong.to_csv('.//tabelas//IPCA//IPCA_long.csv', sep=';', encoding='latin1', index_label = 'nrow')
        dfMasterIPCA.to_csv('.//tabelas//IPCA//master_IPCA.csv', sep = ';', index = False, encoding = 'latin1')
        print("Pesquisa 7060 de", str(date_me(date_int)[0]), "importada com sucesso.")


    return

def divulg_anter():
#FUNÇÃO BUSCA DIVULGAÇÕES ANTERIORES DE OUTRAS PESQUISAS PARA AMPLIAR BASE

    dictPerPes = {2938: [200607,200608,200609,200610,200611,200612,200701,200702,200703,200704,200705,200706,200707,200708,200709,200710,200711,200712,200801,200802,200803,200804,200805,200806,200807,200808,200809,200810,200811,200812,200901,200902,200903,200904,200905,200906,200907,200908,200909,200910,200911,200912,201001,201002,201003,201004,201005,201006,201007,201008,201009,201010,201011,201012,201101,201102,201103,201104,201105,201106,201107,201108,201109,201110,201111,201112],
                  1419: [201201, 201202,201203,201204,201205,201206,201207,201208,201209,201210,201211,201212,201301,201302,201303,201304,201305,201306,201307,201308,201309,201310,201311,201312,201401,201402,201403,201404,201405,201406,201407,201408,201409,201410,201411,201412,201501,201502,201503,201504,201505,201506,201507,201508,201509,201510,201511,201512,201601,201602,201603,201604,201605,201606,201607,201608,201609,201610,201611,201612,201701,201702,201703,201704,201705,201706,201707,201708,201709,201710,201711,201712,201801,201802,201803,201804,201805,201806,201807,201808,201809,201810,201811,201812,201901,201902,201903,201904,201905,201906,201907,201908,201909,201910,201911,201912]}

    dictTipo = {1: 'GG', 2: 'SG', 4: 'II', 7: 'SI'}

    for dictPes in dictPerPes.keys():
        dfSubIPCALong = pd.read_csv('.//tabelas//IPCA//IPCA_long.csv', sep = ';', encoding='latin1', index_col = 'nrow')
        dfMasterIPCA = pd.read_csv('.//tabelas//IPCA//master_IPCA.csv', sep = ';', encoding='latin1')

        for dictPer in dictPerPes[dictPes]:
            print("Importando dados da pesquisa", str(dictPes), "de", date_me(str(dictPer))[0])
            url = "https://servicodados.ibge.gov.br/api/v3/agregados/" + str(dictPes) + "/periodos/" + str(dictPer) + "/variaveis/63|66?localidades=N1[all]&classificacao=315[all]"
            old_data = url2data(url)
            #checks_data(old_data) #chama função para conferir integridade dos dados

            for index, keys in enumerate(old_data[0].get('resultados')):
                #Atualiza Master
                raw_value = list(old_data[0].get('resultados')[index].get('classificacoes')[0].get('categoria').values())
                if len(raw_value[0].split(".")) == 1:
                    raw_value[0] = '0.' + raw_value[0]
                if raw_value[0].split(".")[-2] in dfMasterIPCA['id'].tolist():
                    pass
                else:
                    if raw_value[0].split(".")[-2] == '0':
                        dfAppendixMasterTipo = 'IG'
                    else:
                        dfAppendixMasterTipo = dictTipo[len(raw_value[0].split(".")[-2])]

                    dfAppendixMaster = pd.DataFrame()
                    dfAppendixMaster = pd.DataFrame({'id': [raw_value[0].split(".")[-2]],
                                                    'tipo': [dfAppendixMasterTipo],
                                                    'categoria': [raw_value[0].split(".")[-2][0]],
                                                    'nome': [raw_value[0].split(".")[-1]]})

                    dfMasterIPCA = pd.concat([dfMasterIPCA, dfAppendixMaster], join = 'outer')
            
                #Atualiza Sub
                dfAppendixSub = pd.DataFrame({'id': [raw_value[0].split(".")[-2]],
                                              'localizacao': old_data[0].get('resultados')[index].get('series')[0].get('localidade').get('nivel').get('nome'),
                                              'mesref': [date_me(list(old_data[0].get('resultados')[index].get('series')[0].get('serie').keys())[0])[0]],
                                              'variacao': [list(old_data[0].get('resultados')[index].get('series')[0].get('serie').values())[0].replace('.',',')],
                                              'peso': [list(old_data[1].get('resultados')[index].get('series')[0].get('serie').values())[0].replace('.',',')],
                                              'ts': [datetime.datetime.now()]})
                dfSubIPCALong = pd.concat([dfSubIPCALong, dfAppendixSub], join = 'outer')

            dfSubIPCALong.to_csv('.//tabelas//IPCA//IPCA_long.csv', sep=';', encoding='latin1', index_label = 'nrow')
            dfMasterIPCA.to_csv('.//tabelas//IPCA//master_IPCA.csv', sep = ';', index = False, encoding = 'latin1')
            print("Pesquisa", str(dictPes), "de", date_me(str(dictPer))[0], "importada com sucesso.")

    return

def create_tables(wp):
#FUNÇÃO CRIA AS TABELAS NECESSÁRIAS
    
    ##CRIA TABELA MASTER
    print(" Criando tabela: master_IPCA.csv")  
    headersMasterIPCA = ['id', 'tipo', 'categoria', 'nome']
    dfMasterIPCA = pd.DataFrame(data = None, columns = headersMasterIPCA)
    dfMasterIPCA.to_csv(wp + 'master_IPCA.csv', sep = ';', index = False, encoding = 'latin1')
    print(" Tabela master_IPCA.csv criada com sucesso")

    ##CRIA TABELA SUB
    print(" Criando tabela com dados de índice, peso, participação e acumulado: IPCA_long.csv")
    headersSubIPCA = ['id', 'localizacao', 'mesref', 'variacao', 'peso', 'ts']
    dfSubIPCA = pd.DataFrame(data = None, columns = headersSubIPCA)
    dfSubIPCA.to_csv(wp + 'IPCA_long.csv', sep = ';', encoding='latin1', index_label = 'nrow')
    print("  Tabela IPCA_long.csv criada com sucesso")

    return

def init(ats, rts, wp):
##FUNÇÃO CHECA SE TABELAS NECESSÁRIAS JÁ EXISTEM E CHAMA CRIAÇÃO
    
    if all(item in ats for item in rts):
        tablesExist = True
        print("Tabelas encontradas.")

    else:
        tablesExist = False
        print("Tabelas não encontradas. Iniciando criação.")
        create_tables(wp)
        divulg_anter()

    return tablesExist

def main():

    write_path = r'.//tabelas//IPCA//'

    if not os.path.exists(write_path):
        os.makedirs(write_path)

    available_tbs = os.listdir(write_path)
    required_tbs = ['IPCA_long.csv', 'master_IPCA.csv']

    init(available_tbs, required_tbs, write_path)
    update_tables(required_tbs)

if __name__ == "__main__":
    main()