# forecaster-inflacao
Projeto recolhe dados mensais dos grupos, subgrupos, itens e subitens que compõem o índice oficial de inflação, disponibilizados pela API do IBGE, e transmforma os dados em um painel longo para uso em aplicações de DataVis e de inferência estatística.

INTRODUÇÂO

O objetivo da aplicação é obter e processar os resultados do Índice de Preços ao Consumidor - Amplo (IPCA), por meio da API de serviço de dados divulgados pelo IBGE (https://servicodados.ibge.gov.br/api/docs/), em tempo real, assim que as informações são disponibilizadas. A aplicação também oferece a base para aplicações de inferência estatística de inflação e de projeção de resultados.

Os dados escolhidos para coleta são referentes à variação mensal de preços dos subitens, itens, subgrupos, grupos e índice geral, bem como o peso de cada um deles para a formação das médias ponderadas aninhadas (as médias dos subitens formam os índices dos itens, as médias dos itens formam os subgrupos, sucessivamente...). Estes representam a maior sequência histórica ininterrupta de dados que compõem o índice oficial de inflação - desde 1989 -, e, portanto, aplicável ao treinamento de modelos de aprendizagem.

Para isso, a aplicação se debruça sobre duas etapas: capturar os dados que já foram divulgados e atualizar a base de dados conforme novas pesquisas forem divulgadas. Para facilitar a reprodutibilidade, a escolha feita foi por inscrever os dados em um arquivo .csv, em detrimento de um banco SQL, ainda que a adaptação garantiria maior agilidade e melhor gestão dos dados.

ORIENTAÇÕES

A inicialização deve ser feita a partir do script main.py que importa e reúne as bibliotecas necessárias para a coleta e armazenamento de dados.

A primeira inicialização do banco de dados é a mais demorada uma vez que as requisições à API são feitas mês a mês. A fim de se garantir mais agilidade, dados já tratados e organizados foram disponibilizados até o mês de abril de 2024 nas tabelas IPCA_long.csv e master_IPCA.csv.

Os resultados são inscritos em um arquivo .csv que utiliza "." como separador de decimais e ";" como delimitador de células.

O encoding do arquivo .csv é "latin1" para facilitar o uso de acentos e "ç". 

COMO FUNCIONA

1. A aplicação confere se as tabelas já existem dentro do caminho especificado. Caso já existam, a aplicação pula para o passo 3b. Caso não existam, a aplicação cria o cabeçalho necessário para os dados e começa a buscar as divulgações de agregados (pesquisas de preços) anteriores à atual que já tenham sido encerradas ou que passaram por mudanças.
   a. A tabela master_IPCA.csv reúne as informações de cada um dos subitens, itens, subgrupos, grupos e índice geral divididos por tipo, nome, categoria a que pertecem, e id - usado como identificador único.
   b. Já a tabela IPCA_long.csv é responsável por reunir os resultados da variação mensal e do peso para cálculo da média ponderada de cada item pesquisado em determinado mês. Cada linha da tabela IPCA_long.csv tem usa como identificador único o par de colunas "id" e "mês de referência".

2. O primeiro agregado a ser incluida é a série 1692, de julho de 1989 a dezembro de 1990, na sequência, aparecem o 58, de janeiro de 1991 a julho de 1999, depois o 655, de agosto de 1999 até junho de 2006, o agregado 2938, de jul/2006 a dez/2011, e, na sequência, a série 1419, de jan/2012 a dez/2019. Os dados são incluídos no banco de dados em formato de painel longo a fim de garantir a sua utilização tanto em programas de datavis (como PowerBI e Flourish), quanto de análise estatística (RStudio).
	a. Apesar da amplitude de dados, para fins econômicos convém utilizar os dados a partir do ano de 1993, quando há a transição para o plano Real e maior estabilidade de preços.

4. Na sequência a aplicação se debruça sobre a série 7060, pesquisa iniciada em janeiro de 2020 e atualmente em curso.
	a. A fim de acessar somente os dados faltantes necessários, a aplicação realiza um novo acesso à API de calendário de divulgação de pesquisas para de computar quais divulgações feitas não estão presentes no banco de dados. As informações do calendário são salvas em um arquivo auxiliar (./tabelas/temps/calendario_ipca.csv)
	b. A aplicação gera uma lista de meses faltantes e itera cada um deles para acessar a respectiva query URL.

5. Os dados obtidos são acrescentados ao fim da tabela IPCA_long.csv. Ao longo do código, caso haja a inclusão de novos itens na cesta de compras ideal dos brasileiros - segundo Pesquisa do Orçamento Familiar - novos ids são acrescentados ao fim da tabela master_IPCA.csv.

CHANGELOG

- Criadas regras genéricas de importação para facilitar a busca de dados de pesquisas distintas;
- Horizonte de início estendido de julho/2006 para julho de 1989
- Planilha de pesos e variações conta com um timestamp da anexação
- Acrescida uma planilha de participação de cada item medida em pontos percentuais. Exemplo: suponha que o índice geral tenha apontado avanço de 3% dos preços em determinado mês, e que um item, com peso de 50% no resultado final apontou avanço de 1%. Sua participação foi de 0,5 p.p., ou seja, 50% * 1%.

BUGS

- Entradas "..." agora são convertidas em valor inteiro 0.
- Removido processo que gerava cabeçalhos duplos para IPCA_long.csv
- Removido processo que gerava entradas duplicadas para master_IPCA.csv

ROADMAP

Nos próximos updates, gostaria de incluir:
*Coluna para o acumulado em 12 meses de cada item
*Regionalização por cidade ou região metropolitana
*Indexação de cada linha da tabela IPCA_long.csv
