"""
Módulo para buscar dados dos títulos públicos via API de Dados Abertos do Tesouro Nacional
Fonte: https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto
"""

import requests
import pandas as pd
import io
from datetime import datetime
from typing import Dict


class TesouroAPI:
    """Cliente para a API do Tesouro Direto via Dados Abertos"""
    
    def __init__(self):
        # URL do CSV unificado com todos os títulos (atualizado diariamente)
        self.csv_url = "https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/precotaxatesourodireto.csv"
        # URL da API do Banco Central para taxa Selic meta (anualizada)
        # Série 432: Taxa Selic meta fixada pelo COPOM
        self.bcb_selic_url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"
        # URL da API do Banco Central para projeção de IPCA (Focus)
        # Série 13522: Expectativa IPCA para 12 meses à frente
        self.bcb_ipca_url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.13522/dados/ultimos/1?formato=json"
    
    def buscar_taxa_selic(self) -> float:
        """
        Busca a taxa Selic atual (meta) da API do Banco Central do Brasil
        
        Returns:
            Taxa Selic anual em percentual (ex: 14.90 para 14.90% a.a.)
        """
        try:
            response = requests.get(self.bcb_selic_url, timeout=10)
            response.raise_for_status()
            dados = response.json()
            
            if dados and len(dados) > 0:
                taxa_selic = float(dados[0]['valor'])
                print(f"  Taxa Selic (BCB): {taxa_selic:.2f}% a.a.")
                return taxa_selic
            else:
                print("  Aviso: Não foi possível obter taxa Selic do BCB")
                return 0.0
                
        except Exception as e:
            print(f"  Aviso: Erro ao buscar taxa Selic do BCB: {e}")
            return 0.0
    
    def buscar_projecao_ipca(self) -> float:
        """
        Busca a projeção de IPCA da API do Banco Central do Brasil (Relatório Focus)
        
        Returns:
            Projeção de IPCA anual em percentual (ex: 5.50 para 5.50% a.a.)
        """
        try:
            response = requests.get(self.bcb_ipca_url, timeout=10)
            response.raise_for_status()
            dados = response.json()
            
            if dados and len(dados) > 0:
                ipca_projetado = float(dados[0]['valor'])
                print(f"  Projeção IPCA (BCB Focus): {ipca_projetado:.2f}% a.a.")
                return ipca_projetado
            else:
                print("  Aviso: Não foi possível obter projeção IPCA, usando 5.0% padrão")
                return 5.0
                
        except Exception as e:
            print(f"  Aviso: Erro ao buscar projeção IPCA do BCB: {e}")
            print("  Usando IPCA padrão de 5.0% a.a.")
            return 5.0
        
    def buscar_titulos_tesouro_direto(self) -> pd.DataFrame:
        """
        Busca os títulos disponíveis no Tesouro Direto com preços e taxas atualizadas
        Utiliza o CSV unificado do Tesouro Transparente (Dados Abertos)
        
        Returns:
            DataFrame com informações dos títulos
        """
        try:
            print("Buscando dados atualizados do Tesouro Direto...")
            
            # Download do CSV unificado
            response = requests.get(self.csv_url, timeout=30)
            response.raise_for_status()
            
            # Ler CSV (separado por ponto-e-vírgula)
            df = pd.read_csv(io.StringIO(response.text), sep=';', decimal=',')
            
            # Converter data de referência para datetime
            df['Data Base'] = pd.to_datetime(df['Data Base'], format='%d/%m/%Y', errors='coerce')
            
            # Pegar apenas os dados mais recentes (última data disponível)
            data_mais_recente = df['Data Base'].max()
            df_recente = df[df['Data Base'] == data_mais_recente].copy()
            
            print(f"  Data dos dados: {data_mais_recente.strftime('%d/%m/%Y')}")
            
            # Buscar taxa Selic atual do BCB para ajustar taxas do Tesouro Selic
            taxa_selic_bcb = self.buscar_taxa_selic()
            
            # Padronizar os nomes das colunas e estrutura de dados
            titulos = []
            for _, row in df_recente.iterrows():
                # Extrair ano do vencimento para o nome
                try:
                    vencimento_str = row['Data Vencimento']
                    ano_vencimento = vencimento_str.split('/')[-1]
                    tipo_titulo = row['Tipo Titulo']
                    nome_titulo = f"{tipo_titulo} {ano_vencimento}"
                except:
                    nome_titulo = row.get('Tipo Titulo', 'Título')
                    vencimento_str = row.get('Data Vencimento', '')
                
                # Obter taxas base do CSV
                taxa_compra_csv = self._converter_para_float(row.get('Taxa Compra Manha'))
                taxa_venda_csv = self._converter_para_float(row.get('Taxa Venda Manha'))
                
                # Para Tesouro Selic, somar a taxa Selic atual (BCB) com o spread do CSV
                if 'Selic' in tipo_titulo and taxa_selic_bcb > 0:
                    if taxa_compra_csv is not None:
                        taxa_compra_csv += taxa_selic_bcb
                    if taxa_venda_csv is not None:
                        taxa_venda_csv += taxa_selic_bcb
                
                titulo = {
                    'nome': nome_titulo,
                    'codigo': row.get('Tipo Titulo', ''),
                    'vencimento': vencimento_str,
                    'tipo': row.get('Tipo Titulo', ''),
                    'preco_compra': self._converter_para_float(row.get('PU Compra Manha')),
                    'preco_venda': self._converter_para_float(row.get('PU Venda Manha')),
                    'taxa_compra': taxa_compra_csv,
                    'taxa_venda': taxa_venda_csv,
                    'investimento_minimo': None,  # Será calculado depois se necessário
                }
                
                # Calcular investimento mínimo (geralmente 1% do PU ou valor mínimo)
                if titulo['preco_venda']:
                    titulo['investimento_minimo'] = max(titulo['preco_venda'] * 0.01, 30.0)
                
                titulos.append(titulo)
            
            df_titulos = pd.DataFrame(titulos)
            print(f"Total: {len(df_titulos)} títulos carregados com sucesso!")
            
            return df_titulos
            
        except Exception as e:
            print(f" ERRO CRÍTICO ao buscar dados do Tesouro Direto: {e}")
            print(f"   URL: {self.csv_url}")
            print(f"   Verifique sua conexão com a internet ou o status da API do Tesouro Transparente")
            return pd.DataFrame()
    
    def _converter_para_float(self, valor) -> float:
        """
        Converte valores para float, tratando diferentes formatos
        
        Args:
            valor: Valor a ser convertido
            
        Returns:
            Float ou None se não for possível converter
        """
        if pd.isna(valor) or valor == '':
            return None
        
        try:
            # Se já for numérico
            return float(valor)
        except (ValueError, TypeError):
            try:
                # Tentar converter string com vírgula
                if isinstance(valor, str):
                    valor_limpo = valor.replace('.', '').replace(',', '.')
                    return float(valor_limpo)
            except:
                pass
        
        return None
    
    def obter_titulo_por_nome(self, df: pd.DataFrame, nome: str) -> Dict:
        """
        Obtém informações de um título específico pelo nome
        
        Args:
            df: DataFrame com os títulos
            nome: Nome do título
            
        Returns:
            Dicionário com informações do título
        """
        titulo = df[df['nome'] == nome]
        if not titulo.empty:
            return titulo.iloc[0].to_dict()
        return {}


if __name__ == "__main__":
    # Teste do módulo
    api = TesouroAPI()
    df = api.buscar_titulos_tesouro_direto()
    
    if not df.empty:
        print(f"\nAmostra dos dados:")
        print(df.head(10).to_string())
        print(f"\nTipos de títulos disponíveis:")
        print(df['tipo'].value_counts())
