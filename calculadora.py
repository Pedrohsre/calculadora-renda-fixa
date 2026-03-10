"""
Módulo para cálculo de investimentos em títulos públicos
"""

from datetime import datetime
from typing import Dict, Tuple
import math


class CalculadoraInvestimentos:
    """Calculadora para investimentos em títulos públicos"""
    
    def __init__(self):
        self.dias_ano = 252  # Dias úteis em um ano
        self.taxa_custodia_b3 = 0.002  # 0,20% ao ano (0.002 em decimal)
        
    def calcular_valor_futuro(
        self, 
        valor_investido: float,
        taxa_anual: float,
        data_compra: datetime,
        data_vencimento: datetime,
        tipo_titulo: str = "prefixado"
    ) -> Dict:
        """
        Calcula o valor futuro do investimento
        
        Args:
            valor_investido: Valor a ser investido
            taxa_anual: Taxa anual do título (%)
            data_compra: Data da compra
            data_vencimento: Data de vencimento do título
            tipo_titulo: Tipo do título (prefixado, selic, ipca)
            
        Returns:
            Dicionário com informações do investimento
        """
        # Calcula dias úteis entre as datas
        dias_corridos = (data_vencimento - data_compra).days
        anos = dias_corridos / 365
        
        # Converte taxa anual para decimal
        taxa_decimal = taxa_anual / 100
        
        # Calcula valor futuro bruto
        if tipo_titulo.lower() in ['tesouro selic', 'selic']:
            # Para Tesouro Selic, usa capitalização diária
            valor_futuro_bruto = valor_investido * math.pow((1 + taxa_decimal), anos)
        elif tipo_titulo.lower() in ['tesouro ipca+', 'ipca', 'tesouro ipca']:
            # Para Tesouro IPCA+, considera a taxa real + inflação estimada
            # Aqui vamos usar uma inflação estimada de 4% ao ano
            inflacao_estimada = 0.04
            taxa_total = (1 + taxa_decimal) * (1 + inflacao_estimada) - 1
            valor_futuro_bruto = valor_investido * math.pow((1 + taxa_total), anos)
        else:
            # Para Tesouro Prefixado
            valor_futuro_bruto = valor_investido * math.pow((1 + taxa_decimal), anos)
        
        # Calcula impostos e taxas
        lucro_bruto = valor_futuro_bruto - valor_investido
        iof = self.calcular_iof(lucro_bruto, dias_corridos)
        imposto_renda = self.calcular_ir(lucro_bruto - iof, dias_corridos)
        custodia_b3 = self.calcular_custodia_b3(valor_investido, anos)
        
        # Valor líquido (descontando IR, IOF e custódia)
        valor_futuro_liquido = valor_futuro_bruto - imposto_renda - iof - custodia_b3
        
        # Rentabilidade
        rentabilidade_bruta = ((valor_futuro_bruto / valor_investido) - 1) * 100
        rentabilidade_liquida = ((valor_futuro_liquido / valor_investido) - 1) * 100
        
        return {
            'valor_investido': valor_investido,
            'valor_futuro_bruto': valor_futuro_bruto,
            'valor_futuro_liquido': valor_futuro_liquido,
            'rentabilidade_bruta': rentabilidade_bruta,
            'rentabilidade_liquida': rentabilidade_liquida,
            'imposto_renda': imposto_renda,
            'iof': iof,
            'custodia_b3': custodia_b3,
            'dias_corridos': dias_corridos,
            'anos': anos,
            'taxa_anual': taxa_anual
        }
    
    def calcular_ir(self, lucro: float, dias_corridos: int) -> float:
        """
        Calcula o Imposto de Renda sobre o lucro
        Tabela regressiva de IR para títulos públicos
        
        Args:
            lucro: Lucro do investimento
            dias_corridos: Dias corridos do investimento
            
        Returns:
            Valor do imposto de renda
        """
        if dias_corridos <= 180:
            aliquota = 0.225  # 22.5%
        elif dias_corridos <= 360:
            aliquota = 0.20   # 20%
        elif dias_corridos <= 720:
            aliquota = 0.175  # 17.5%
        else:
            aliquota = 0.15   # 15%
        
        return lucro * aliquota if lucro > 0 else 0
    
    def calcular_iof(self, lucro: float, dias_corridos: int) -> float:
        """
        Calcula o IOF (Imposto sobre Operações Financeiras)
        IOF regressivo para resgates em menos de 30 dias
        
        Args:
            lucro: Lucro do investimento
            dias_corridos: Dias corridos do investimento
            
        Returns:
            Valor do IOF
        """
        if dias_corridos >= 30 or lucro <= 0:
            return 0
        
        # Tabela regressiva de IOF (de 96% no dia 1 até 0% no dia 30)
        # Alíquota = (30 - dias) * 3,33% (aproximadamente)
        aliquota = ((30 - dias_corridos) / 30) * 0.96
        
        return lucro * aliquota
    
    def calcular_custodia_b3(self, valor_investido: float, anos: float) -> float:
        """
        Calcula a taxa de custódia da B3 para Tesouro Direto
        Taxa de 0,20% ao ano sobre o valor investido (cobrada semestralmente)
        
        Args:
            valor_investido: Valor investido
            anos: Período em anos
            
        Returns:
            Valor total da custódia no período
        """
        # Custódia de 0,20% ao ano
        custodia_total = valor_investido * self.taxa_custodia_b3 * anos
        return custodia_total
    
    def calcular_quantidade_titulos(
        self,
        valor_investido: float,
        preco_titulo: float
    ) -> Tuple[int, float]:
        """
        Calcula a quantidade de títulos que podem ser comprados
        
        Args:
            valor_investido: Valor disponível para investir
            preco_titulo: Preço unitário do título
            
        Returns:
            Tupla com (quantidade de títulos, valor total investido)
        """
        if preco_titulo <= 0:
            return 0, 0
        
        quantidade = int(valor_investido / preco_titulo)
        valor_total = quantidade * preco_titulo
        
        return quantidade, valor_total
    
    def calcular_rentabilidade_mensal(
        self,
        taxa_anual: float
    ) -> float:
        """
        Converte taxa anual em taxa mensal equivalente
        
        Args:
            taxa_anual: Taxa anual (%)
            
        Returns:
            Taxa mensal equivalente (%)
        """
        taxa_decimal = taxa_anual / 100
        taxa_mensal = (math.pow((1 + taxa_decimal), (1/12)) - 1) * 100
        return taxa_mensal
    
    def projetar_investimento_periodico(
        self,
        valor_mensal: float,
        taxa_anual: float,
        meses: int
    ) -> Dict:
        """
        Projeta investimento com aportes mensais
        
        Args:
            valor_mensal: Valor do aporte mensal
            taxa_anual: Taxa anual (%)
            meses: Número de meses
            
        Returns:
            Dicionário com projeção do investimento
        """
        taxa_mensal = self.calcular_rentabilidade_mensal(taxa_anual) / 100
        
        valor_futuro = 0
        total_investido = 0
        
        for mes in range(meses):
            total_investido += valor_mensal
            valor_futuro = (valor_futuro + valor_mensal) * (1 + taxa_mensal)
        
        lucro = valor_futuro - total_investido
        
        return {
            'total_investido': total_investido,
            'valor_futuro': valor_futuro,
            'lucro': lucro,
            'rentabilidade': (lucro / total_investido) * 100 if total_investido > 0 else 0
        }
    
    def comparar_investimentos(
        self,
        valor_investido: float,
        meses: int,
        cdi_atual: float = 14.9,
        percentual_cdb: float = 100.0,
        percentual_lci: float = 90.0,
        taxa_tesouro: float = 14.0
    ) -> Dict:
        """
        Compara diferentes tipos de investimentos de renda fixa
        
        Args:
            valor_investido: Valor a ser investido
            meses: Período em meses
            cdi_atual: Taxa CDI atual (% a.a.)
            percentual_cdb: Percentual do CDI para CDB (%)
            percentual_lci: Percentual do CDI para LCI/LCA (%)
            taxa_tesouro: Taxa do Tesouro Direto (% a.a.)
            
        Returns:
            Dicionário com resultados de cada tipo de investimento
        """
        anos = meses / 12
        dias_corridos = int(meses * 30.42)  # Média de dias por mês
        
        # 1. POUPANÇA (0,5% a.m. + TR, simplificado para 6,17% a.a. atualmente)
        taxa_poupanca = 6.17  # Taxa aproximada atual da poupança
        vf_poupanca = valor_investido * math.pow((1 + taxa_poupanca/100), anos)
        lucro_poupanca = vf_poupanca - valor_investido
        # Poupança é isenta de IR
        
        # 2. CDB (tributado)
        taxa_cdb = cdi_atual * (percentual_cdb / 100)
        vf_cdb_bruto = valor_investido * math.pow((1 + taxa_cdb/100), anos)
        lucro_cdb = vf_cdb_bruto - valor_investido
        ir_cdb = self.calcular_ir(lucro_cdb, dias_corridos)
        vf_cdb_liquido = vf_cdb_bruto - ir_cdb
        
        # 3. LCI/LCA (isento de IR)
        taxa_lci = cdi_atual * (percentual_lci / 100)
        vf_lci = valor_investido * math.pow((1 + taxa_lci/100), anos)
        lucro_lci = vf_lci - valor_investido
        # LCI é isento de IR
        
        # 4. TESOURO DIRETO (com IR e custódia)
        vf_tesouro_bruto = valor_investido * math.pow((1 + taxa_tesouro/100), anos)
        lucro_tesouro = vf_tesouro_bruto - valor_investido
        ir_tesouro = self.calcular_ir(lucro_tesouro, dias_corridos)
        custodia_tesouro = self.calcular_custodia_b3(valor_investido, anos)
        vf_tesouro_liquido = vf_tesouro_bruto - ir_tesouro - custodia_tesouro
        
        return {
            'poupanca': {
                'valor_final': vf_poupanca,
                'lucro': lucro_poupanca,
                'rentabilidade': ((vf_poupanca / valor_investido) - 1) * 100,
                'taxa': taxa_poupanca,
                'ir': 0,
                'outras_taxas': 0
            },
            'cdb': {
                'valor_final': vf_cdb_liquido,
                'lucro': lucro_cdb - ir_cdb,
                'rentabilidade': ((vf_cdb_liquido / valor_investido) - 1) * 100,
                'taxa': taxa_cdb,
                'ir': ir_cdb,
                'outras_taxas': 0
            },
            'lci': {
                'valor_final': vf_lci,
                'lucro': lucro_lci,
                'rentabilidade': ((vf_lci / valor_investido) - 1) * 100,
                'taxa': taxa_lci,
                'ir': 0,
                'outras_taxas': 0
            },
            'tesouro': {
                'valor_final': vf_tesouro_liquido,
                'lucro': lucro_tesouro - ir_tesouro - custodia_tesouro,
                'rentabilidade': ((vf_tesouro_liquido / valor_investido) - 1) * 100,
                'taxa': taxa_tesouro,
                'ir': ir_tesouro,
                'outras_taxas': custodia_tesouro
            },
            'valor_investido': valor_investido,
            'periodo_meses': meses,
            'periodo_anos': anos
        }


if __name__ == "__main__":
    # Teste do módulo
    calc = CalculadoraInvestimentos()
    
    data_compra = datetime(2026, 3, 10)
    data_vencimento = datetime(2027, 3, 1)
    
    resultado = calc.calcular_valor_futuro(
        valor_investido=10000,
        taxa_anual=13.25,
        data_compra=data_compra,
        data_vencimento=data_vencimento,
        tipo_titulo="Tesouro Selic"
    )
    
    print(f"Valor Investido: R$ {resultado['valor_investido']:,.2f}")
    print(f"Valor Futuro Bruto: R$ {resultado['valor_futuro_bruto']:,.2f}")
    print(f"Valor Futuro Líquido: R$ {resultado['valor_futuro_liquido']:,.2f}")
    print(f"Rentabilidade Líquida: {resultado['rentabilidade_liquida']:.2f}%")
