# Calculadora de Investimentos em Renda Fixa

**Simule seus investimentos em Tesouro Direto, CDB, LCI/LCA e Poupança de forma gratuita e com dados reais do governo.**

---

## O que é esta calculadora?

Esta é uma ferramenta gratuita que ajuda você a **calcular quanto seu dinheiro pode render** ao investir em produtos de renda fixa como Tesouro Direto, CDB, LCI/LCA e Poupança. Usamos dados oficiais do Tesouro Nacional, atualizados diariamente, para fornecer simulações realistas.

---

## O que você pode fazer com esta calculadora?

### 1️⃣ Simular Investimento no Tesouro Direto
- Escolha qualquer título público disponível (Selic, IPCA+, Prefixado, Renda+, etc.)
- Veja quanto você vai receber no vencimento
- Calcule o desconto de Imposto de Renda automaticamente
- Simule resgate antecipado (e veja se vai pagar IOF)
- Descubra o valor real da taxa de custódia B3

### 2️⃣ Comparar Investimentos
- Compare lado a lado: **Poupança vs CDB vs LCI/LCA vs Tesouro Direto**
- Veja qual investimento rende mais para seu perfil
- Entenda o impacto do Imposto de Renda
- Personalize as taxas (CDI, percentual do CDB, etc.)

### 3️⃣ Ver Todos os Títulos Disponíveis
- Lista completa com 60+ títulos públicos
- Preços e taxas atualizados diariamente
- Filtre por tipo (Selic, IPCA+, Prefixado, etc.)
- Compare as taxas em gráficos visuais

### 4️⃣ Simular Aportes Mensais
- Planeje investimentos recorrentes
- Veja quanto você terá em 5, 10 ou 20 anos
- Acompanhe a evolução mês a mês
- Compare valor investido vs valor final

---

## Como instalar e usar?

### Passo 1: Instale o Python
Se você não tem Python instalado:
- Acesse: https://www.python.org/downloads/
- Baixe a versão mais recente (3.8 ou superior)
- Durante a instalação, **marque a opção "Add Python to PATH"**

### Passo 2: Baixe esta calculadora
Opção A (Recomendado):
- Clique no botão verde **"Code"** no topo desta página
- Clique em **"Download ZIP"**
- Extraia o arquivo ZIP em uma pasta de sua preferência

Opção B (Se você já usa Git):
```bash
git clone https://github.com/Pedrohsre/calculadora-renda-fixa.git
cd calculadora-renda-fixa
```

### Passo 3: Instale as dependências
Abra o **Prompt de Comando** (Windows) ou **Terminal** (Mac/Linux) na pasta da calculadora e digite:

```bash
pip install -r requirements.txt
```

Aguarde alguns segundos enquanto os componentes necessários são baixados.

### Passo 4: Inicie a calculadora
No mesmo Prompt de Comando/Terminal, digite:

```bash
streamlit run app.py
```

**Pronto!** Sua calculadora abrirá automaticamente no navegador em: **http://localhost:8501**

---

## Como usar cada funcionalidade?

### Simulador de Investimento (Tesouro Direto)

1. No menu lateral, escolha **"Simulador de Investimento"**
2. Selecione o título que deseja investir (ex: Tesouro Selic 2031)
3. Digite quanto você quer investir (ex: R$ 1.000)
4. Confirme a data de compra
5. **Opcional:** Marque "Resgate Antecipado" se quiser resgatar antes do vencimento
6. Clique em **"Calcular Retorno"**

**Você verá:**
- Valor final bruto e líquido
- Quanto você pagará de Imposto de Renda
- Taxa de custódia da B3
- IOF (se aplicável)
- Gráfico de composição do investimento

### Comparador de Investimentos

1. No menu lateral, escolha **"Comparar Investimentos"**
2. Digite o valor que você quer investir
3. Escolha o prazo (6 meses, 1 ano, 2 anos, etc.)
4. Ajuste as taxas de referência (CDI, CDB, LCI, Tesouro)
5. Clique em **"Comparar Investimentos"**

**Você verá:**
- Cards coloridos mostrando o valor final de cada investimento
- Qual investimento rende mais
- Tabela detalhada com rentabilidade e impostos
- Gráfico de barras comparativo

### Visualizar Títulos Disponíveis

1. No menu lateral, escolha **"Visualizar Títulos Disponíveis"**
2. Use os filtros para escolher tipos específicos (Selic, IPCA+, etc.)
3. Ordene por taxa, vencimento, preço ou nome
4. Veja o gráfico comparativo de taxas

### Investimento Periódico

1. No menu lateral, escolha **"Investimento Periódico"**
2. Digite o valor do aporte mensal (ex: R$ 500)
3. Escolha por quantos meses você vai investir
4. Defina a taxa anual esperada
5. Clique em **"Calcular Projeção"**

**Você verá:**
- Total investido vs valor final
- Lucro líquido
- Gráfico de evolução mensal

---

## Dicas importantes

**Sobre Impostos:**
- **Poupança e LCI/LCA:** Isentas de Imposto de Renda
- **CDB e Tesouro Direto:** Tabela regressiva de IR (22,5% até 15%)
- **IOF:** Só paga se resgatar antes de 30 dias

**Sobre a Custódia B3:**
- Tesouro Direto cobra 0,20% ao ano de taxa de custódia
- É descontada automaticamente do seu investimento
- Calculamos isso para você!

**Sobre as Taxas:**
- Os dados são atualizados diariamente do Tesouro Nacional
- As taxas do Tesouro Direto são reais (última atualização disponível)
- CDI e outras taxas podem ser ajustadas manualmente

---

## Atualizando os dados

Os dados do Tesouro Direto são atualizados automaticamente **a cada hora**. O sistema utiliza cache inteligente que garante rapidez no carregamento e economiza recursos da API pública do governo. Isso significa que todos os usuários veem os mesmos dados atualizados durante o período de 1 hora, após o qual uma nova consulta é feita automaticamente.

---

## Informações técnicas (para desenvolvedores)

**Tecnologias utilizadas:**
- Python 3.8+
- Streamlit (interface web)
- Pandas (manipulação de dados)
- Plotly (gráficos interativos)

**Fonte de dados:**
- API oficial do Tesouro Transparente
- CSV unificado com 60+ títulos públicos
- Atualização diária automática

**Estrutura do projeto:**
```
calculadora-renda-fixa/
├── app.py              # Interface da aplicação
├── calculadora.py      # Lógica de cálculos financeiros
├── api_tesouro.py      # Integração com API do Tesouro
├── requirements.txt    # Dependências do projeto
└── README.md          # Este arquivo
```

---

## Licença

Este projeto é de código aberto. Sinta-se livre para usar, modificar e distribuir.

---

## Avisos Importantes

- Esta é uma ferramenta **educacional e informativa**
- Os valores são **simulações** baseadas em dados públicos
- **Rentabilidade passada não é garantia de rentabilidade futura**
- Consulte um profissional certificado antes de investir
- Os dados podem sofrer atrasos ou imprecisões
- Não nos responsabilizamos por decisões de investimento
