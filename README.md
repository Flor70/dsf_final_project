# Flight Search & Weather Analysis ✈️☀️

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

Uma aplicação Python poderosa para buscar voos e analisar dados históricos de clima, desenvolvida por **Ario**, **Myrthe** e **Floriano**. Este projeto ajuda viajantes a encontrar os voos mais baratos para suas rotas desejadas e fornece informações históricas de clima para um melhor planejamento de viagem.

---

## Visão Geral do Projeto

**Flight Search & Weather Analysis** ajuda viajantes a planejar suas viagens:
1. Encontrando os voos mais baratos entre aeroportos de origem e destino selecionados
2. Buscando automaticamente voos nos finais de semana entre as datas selecionadas
3. Fornecendo informações detalhadas de voo (preço, companhia aérea, horários, duração, escalas)
4. Exibindo dados históricos de clima para a cidade de destino
5. Mostrando tendências históricas de preços para a rota selecionada
6. Oferecendo uma visualização integrada de voos, clima e dados de preço
7. Disponibilizando dados para download e análise adicional

A aplicação salva dados em diretórios organizados:
- **`outputs/raw_data/`**: Dados brutos de busca de voos do SerpAPI
- **`outputs/cheapest_flights/`**: Dados processados com os voos mais baratos
- **`outputs/weather_data/`**: Dados históricos de clima para cidades de destino
- **`outputs/amadeus_data/`**: Dados históricos de preços da API Amadeus

---

## Funcionalidades

### Busca de Voos
- **Rotas Personalizáveis**: Insira qualquer aeroporto de origem e destino (códigos IATA)
- **Seleção de Datas**: Escolha datas de partida e retorno
- **Foco em Finais de Semana**: Busca automaticamente voos nos finais de semana
- **Opções Mais Baratas**: Exibe os três voos mais baratos encontrados
- **Informações Detalhadas**: Mostra preço, companhia aérea, horários, duração e escalas
- **Tabela Comparativa**: Tabela fácil de usar para comparar opções de voo
- **Dados para Download**: Oferece dados de voo para download em formato JSON

### Análise de Clima
- **Dados Históricos**: Recupera dados de clima para a cidade de destino
- **Estatísticas de Temperatura**: Mostra médias de temperaturas máximas e mínimas
- **Dados de Precipitação**: Exibe padrões de chuva
- **Detalhamento Mensal**: Visualiza padrões mensais de clima
- **Comparação Ano a Ano**: Compara dados de clima ao longo dos anos
- **Dados para Download**: Oferece dados de clima brutos e agregados para download

### Análise de Preços
- **Tendências Históricas**: Mostra como os preços variam ao longo do tempo
- **Métricas de Preço**: Exibe preços mínimos, medianos e máximos para a rota
- **Avaliação de Preço**: Avalia se o preço atual é bom em comparação com dados históricos
- **Dados da Amadeus**: Utiliza a API Amadeus para obter dados confiáveis de preços

### Visualização Integrada
- **Dashboard Unificado**: Combina dados de voo, clima e preço em uma única visualização
- **Organização por Final de Semana**: Agrupa voos por final de semana para fácil comparação
- **Resumo de Clima por Final de Semana**: Exibe dados de clima uma vez por final de semana
- **Gráficos Históricos**: Mostra tendências de clima para datas específicas
- **Avaliação Visual de Preços**: Usa códigos de cores para indicar se os preços são bons ou ruins

### Interface do Usuário
- **Design Limpo**: Interface Streamlit intuitiva
- **Layout Responsivo**: Seções bem organizadas
- **Elementos Interativos**: Experiência de usuário aprimorada
- **Visualização de Dados**: Gráficos e tabelas para melhor compreensão
- **Instruções Claras**: Interface em inglês com rótulos úteis

---

## Arquitetura do Projeto

O projeto segue uma arquitetura modular com os seguintes componentes principais:

### Módulos Principais
- **`app.py`**: Ponto de entrada principal e interface Streamlit
- **`flights.py`**: Funções para buscar dados de voo do SerpAPI
- **`amadeus.py`**: Integração com a API Amadeus para dados históricos de preços

### Utilitários
- **`utils/flight_data_processor.py`**: Processamento e análise de dados de voo
- **`utils/weather_data_processor.py`**: Recuperação e processamento de dados de clima
- **`utils/cheapest_flights_display.py`**: Visualização dos voos mais baratos
- **`utils/weather_display.py`**: Visualização de dados históricos de clima
- **`utils/integrated_view.py`**: Dashboard integrado combinando todos os dados

### Fluxo de Dados
1. O usuário insere parâmetros de busca (origem, destino, datas)
2. A aplicação busca voos usando SerpAPI
3. Os dados de voo são processados para encontrar os voos mais baratos
4. Dados históricos de clima são recuperados para o destino
5. Dados históricos de preços são obtidos da API Amadeus
6. Todos os dados são combinados em uma visualização integrada

---

## Detalhes Técnicos

### APIs Utilizadas
- **SerpAPI**: Para buscar dados de voo de várias fontes
- **Open-Meteo**: Para dados históricos de clima
- **Amadeus**: Para tendências históricas de preços

### Processamento de Dados
- **Pandas**: Usado extensivamente para manipulação e análise de dados
- **Matplotlib/Seaborn**: Para visualizações de dados
- **JSON/CSV**: Para armazenamento e intercâmbio de dados

### Visualização
- **Streamlit**: Framework principal para a interface do usuário
- **Componentes Personalizados**: Cards, tabelas e gráficos para exibição de dados
- **Layout Responsivo**: Adaptável a diferentes tamanhos de tela

---

## Pré-requisitos

- **Python 3.8+**
- **Dependências**: Instale via `pip install -r requirements.txt`
- **Chaves de API**:
  - **SerpAPI**: Obtenha sua chave em [serpapi.com](https://serpapi.com)
  - **Amadeus**: Registre-se em [developers.amadeus.com](https://developers.amadeus.com)

---

## Instalação

1. **Clone o Repositório**:
   ```bash
   git clone https://github.com/Flor70/dsf_final_project.git
   cd dsf_final_project
   ```

2. **Instale as Dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as Chaves de API**:
   - Crie um arquivo `.env` na raiz do projeto
   - Adicione suas chaves de API:
     ```
     SERPAPI_KEY=sua_chave_serpapi
     AMADEUS_API_KEY=sua_chave_amadeus
     AMADEUS_API_SECRET=seu_segredo_amadeus
     ```

4. **Execute a Aplicação**:
   ```bash
   streamlit run app.py
   ```

---

## Guia para Apresentação

Ao apresentar este projeto, considere destacar os seguintes pontos:

### 1. Problema e Solução
- **Problema**: Viajantes frequentemente enfrentam dificuldades para encontrar voos baratos e prever condições climáticas
- **Solução**: Uma ferramenta integrada que combina busca de voos, análise de clima e tendências de preços

### 2. Demonstração do Fluxo de Usuário
- Mostre como um usuário insere dados de origem, destino e datas
- Demonstre como a aplicação busca voos nos finais de semana
- Exiba os resultados de voos mais baratos
- Mostre a visualização de dados de clima
- Destaque a visualização integrada

### 3. Aspectos Técnicos Notáveis
- Integração de múltiplas APIs (SerpAPI, Open-Meteo, Amadeus)
- Processamento e análise de dados com Pandas
- Visualizações interativas com Streamlit
- Arquitetura modular e extensível

### 4. Valor para o Usuário
- Economia de tempo na busca de voos
- Tomada de decisão informada com base em dados históricos
- Planejamento de viagem aprimorado com informações de clima
- Interface intuitiva e fácil de usar

---

## Atualizações Recentes

- **Visualização Integrada**: Adicionado dashboard que combina dados de voo, clima e preço
- **Análise de Clima por Final de Semana**: Melhorada a exibição de dados de clima para mostrar uma vez por final de semana
- **Integração com Amadeus**: Implementada exibição de tendências históricas de preços
- **UI Aprimorada**: Interface de usuário redesenhada para melhor experiência
- **Arquitetura Modular**: Código refatorado para facilitar manutenção e extensão

---

## Melhorias Pendentes

Como detalhado em nosso documento [Project Status](project_status.md), estamos trabalhando em:

1. **Aprimoramento da Visualização de Dados de Clima**: Melhorando gráficos e adicionando informações específicas de clima para finais de semana
2. **Integração de API de Busca de Voos**: Garantindo recuperação adequada de dados de voos de ida e volta
3. **Otimização de Desempenho**: Melhorando o tempo de resposta e a eficiência da aplicação
4. **Melhorias Adicionais**: Melhor tratamento de erros, cache e mais opções de filtragem

---

## Contribuidores

- **Ario**
- **Myrthe**
- **Floriano**

---

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.
