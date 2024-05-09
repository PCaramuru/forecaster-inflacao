# forecaster-inflacao
Projeto recolhe dados mensais dos grupos, subgrupos, itens e subitens que compõem o índice oficial de inflação, disponibilizados pela API do IBGE, e transmforma os dados em um painel longo para uso em aplicações de DataVis e de inferência estatística.

INTRODUÇÂO

O objetivo da aplicação projecao_inflacao_APItoCSV_v006.py é ser capaz de obter os resultados do Índice de Preços ao Consumidor - Amplo (IPCA), por meio da API de serviço de dados divulgados pelo IBGE (https://servicodados.ibge.gov.br/api/docs/), em tempo real, assim que as informações são disponibilizadas. A aplicação também oferece a base para aplicações de inferência estatística de inflação e de projeção de resultados.

Os dados escolhidos para coleta são referentes à variação mensal de preços dos subitens, itens, subgrupos, grupos e índice geral, bem como o peso de cada um deles para a formação das médias ponderadas iteradas (as médias dos subitens formam os índices dos itens; as médias dos itens formam os subgrupos; sucessivamente...). Estes representam a maior sequência histórica ininterrupta de dados que compõem o índice oficial de inflação - desde 1989 -, e, portanto, muito valiosa para o treinamento de modelos de aprendizagem. Ainda assim, a sua aplicação para modelos estatísticos univariados perde acurácia para levantamentos que utilizem a série histórica dessazonalizada com número-índice tratada. 

Para isso, a aplicação se debruça sobre duas etapas: capturar os dados que já foram divulgados e ser capaz de atualizar a base de dados conforme novas pesquisas forem divulgadas. Para facilitar a reprodutibilidade, a escolha feita foi por inscrever os dados em um arquivo .csv, em detrimento de um banco SQL, ainda que a adaptação garantiria maior agilidade e melhor gestão dos dados.

ORIENTAÇÕES

A primeira inicialização do banco de dados é a mais demorada uma vez que as requisições à API são feitas mês a mês. A fim de se garantir maior velocidade, foram disponibilizados os dados já tratados e organizados até o mês de março de 2024 nas tabelas IPCA_long.csv e master_IPCA.csv.

Para os scripts estatísticos disponibilizados para o RStudio, convém executar primeiro o projeto (.Rproj) e depois o script em R.

COMO FUNCIONA

1. A aplicação confere se as tabelas já existem dentro do caminho especificado. Caso já existam, a aplicação pula para o passo 3b. Caso não existam, a aplicação cria o cabeçalho necessário para os dados e começa a buscar as divulgações anteriores.
	a. A tabela master_IPCA.csv reúne as informações de cada um dos subitens, itens, subgrupos, grupos e índice geral divididos por tipo, nome, categoria a que pertecem, e id - usado como identificador único.
	b. Já a tabela IPCA_long.csv é responsável por reunir os resultados da variação mensal e do peso para cálculo da média ponderada de cada item pesquisado em determinado mês. Cada linha da tabela IPCA_long.csv tem usa como identificador único o par de colunas "id" e "mês de referência".

2. A primeira a ser incluida é a série 2938, de jul/2006 a dez/2011, e, na sequência, a série 1419, de jan/2012 a dez/2019. Os dados são incluídos no banco de dados em formato de painel longo a fim de garantir a sua utilização tanto em programas de datavis (como PowerBI e Flourish), quanto de análise estatística (RStudio).

3. Na sequência a aplicação se debruça sobre a série 7060, pesquisa atualmente em curso.
	a. A fim de acessar somente os dados faltantes necessários, a aplicação realiza um novo acesso à API de calendário de divulgação de pesquisas para de computar quais divulgações feitas não estão presentes no banco de dados. As informações do calendário são salvas em um arquivo auxiliar (./tabelas/temps/calendario_ipca.csv)
	b. A aplicação gera uma lista de meses faltantes e itera cada um deles para acessar a respectiva query URL.

4. Os dados obtidos são acrescentados ao fim da tabela IPCA_long.csv. Ao longo do código, novos ids são acrescentados à tabela master_IPCA.csv.
