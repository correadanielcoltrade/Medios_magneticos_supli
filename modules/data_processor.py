import pandas as pd

from mapeo_cuentas import (
    MAPEO_CUENTAS_FORMULARIO,
    obtener_codigo_parametro_formulario,
    obtener_mapa_formato_1001,
)


class DataProcessor:
    """Procesa el balance de sumas y saldos para mapearlo a cada formato."""

    FORMATO_CONFIG = {
        '1001': {
            'nombre': 'Pagos o abonos en cuenta y retenciones practicadas',
            'descripcion': 'Plantilla DIAN del formato 1001',
            'tipo': 'formato_dian'
        },
        '1005': {
            'nombre': 'Impuesto sobre las ventas (IVA) descontable',
            'descripcion': 'IVA descontable',
            'tipo': 'iva_descontable'
        },
        '1006': {
            'nombre': 'IVA generado e impuesto al consumo',
            'descripcion': 'IVA generado',
            'tipo': 'iva_generado'
        },
        '1007': {
            'nombre': 'Ingresos recibidos',
            'descripcion': 'Ingresos operacionales',
            'tipo': 'ingresos'
        },
        '1008': {
            'nombre': 'Cuentas por cobrar al 31 de diciembre',
            'descripcion': 'Cartera de clientes',
            'tipo': 'cxc'
        },
        '1009': {
            'nombre': 'Cuentas por pagar al 31 de diciembre',
            'descripcion': 'Obligaciones con proveedores',
            'tipo': 'cxp'
        },
        '2276': {
            'nombre': 'Información de rentas de trabajo (empleados)',
            'descripcion': 'Gastos de nómina',
            'tipo': 'nomina'
        }
    }

    COLUMNAS_FORMATO_1001 = [
        'Concepto',
        'Código Cuentas Contables',
        'Descripción',
        'Tipo documento',
        'Número identificación del informado',
        'Primer apellido del informado',
        'Segundo apellido del informado',
        'Primer nombre del informado',
        'Otros nombres del informado',
        'Razón social informado',
        'Dirección',
        'Código dpto.',
        'Código mcp',
        'País de residencia o domicilio',
        'Pago o abono en cuenta deducible',
        'Pago o abono en cuenta no deducible',
        'Iva mayor valor del costo o gasto deducible',
        'Iva mayor valor del costo o gasto no deducible',
        'Retención en la fuente practicada en renta',
        'Retención en la fuente asumida en renta',
        'Retención en la fuente practicada IVA responsables de IVA',
        'Retención en la fuente practicada IVA no domiciliados',
    ]

    COLUMNAS_FORMATO_1005 = [
        'Código Cuentas Contables',
        'Descripción',
        'Naturaleza Cta.',
        'Tipo Documento',
        'Numero de identificacion',
        'DV',
        'Primer apellido del informado',
        'Segundo apellido del informado',
        'Primer nombre del informado',
        'Otros nombres del informado',
        'Razón social informado',
        'Impuesto descontable',
        'IVA resultante devoluciones VENTAS',
    ]

    COLUMNAS_FORMATO_1006 = [
        'Código Cuentas Contables',
        'Descripción',
        'Naturaleza Cta.',
        'Tipo Documento',
        'Numero de identificacion',
        'DV',
        'Primer apellido del informado',
        'Segundo apellido del informado',
        'Primer nombre del informado',
        'Otros nombres del informado',
        'Razón social informado',
        'Impuesto Generado',
        'IVA recuperado en devoluciones',
        'Impuesto al consumo',
    ]

    COLUMNAS_FORMATO_1007 = [
        'Concepto',
        'Código Cuentas Contables',
        'Descripción',
        'Tipo Documento',
        'Numero de identificacion',
        'Primer apellido del informado',
        'Segundo apellido del informado',
        'Primer nombre del informado',
        'Otros nombres del informado',
        'Razón social informado',
        'Pais',
        'Ingresos brutos recibidos',
        'Devoluciones, rebajas y descuentos',
    ]

    COLUMNAS_FORMATO_1008 = [
        'Concepto',
        'Código Cuentas Contables',
        'Descripción',
        'Tipo Documento',
        'Numero de identificacion',
        'DV',
        'Primer apellido del informado',
        'Segundo apellido del informado',
        'Primer nombre del informado',
        'Otros nombres del informado',
        'Razón social informado',
        'Direccion',
        'Dpto',
        'Municipio',
        'Pais',
        'Saldo CXC a 31 diciembre',
    ]

    COLUMNAS_FORMATO_1009 = [
        'Concepto',
        'Código Cuentas Contables',
        'Descripción',
        'Tipo Documento',
        'Número identificación del informado',
        'DV',
        'Primer apellido del informado',
        'Segundo apellido del informado',
        'Primer nombre del informado',
        'Otros nombres del informado',
        'Razón social informado',
        'Direccion',
        'Dpto',
        'Municipio',
        'Pais',
        'Saldo CXP a 31 diciembre',
    ]

    COLUMNAS_FORMATO_2276 = [
        'Entidad informante',
        'Tipo documento beneficiario',
        'Número identificación',
        'Primer apellido empleado',
        'Segundo apellido empleado',
        'Primer nombre empleado',
        'Otros nombres empleado',
        'Razón social informado',
        'Direccion',
        'Dpto',
        'Municipio',
        'País',
        'Pagos por salarios',
        'Pagos por emolumentos eclesiasticos',
        'Pagos realizados con bonos electronicos',
        'Pagos por alimentacion exceso de 41 UVT',
        'Pagos por honorarios',
        'Pagos por servicios',
        'Pagos por comisiones - A trabj Independientes',
        'Pagos por prestaciones sociales',
        'Pagos por viaticos',
        'Pagos por gastos de representación',
        'Pagos por compensaciones de trabajo asociado',
        'Apoyos economicos para educacion entregados por el estado',
        'Otros pagos',
        'Cesantias e ints, efectivamente pagadas',
        'Cesantias e ints consignadas a FONDO DE CESANTIAS',
        'Cesantias e ints reconocidas - Regimen tradicional',
        'Pension de jubilacion, vejez o invalidez',
        'Total ing brutos por rentas de trabajo y pensiones',
        'Aportes obligatorios por salud a cargo del trab',
        'Aportes obligatorios pension, FSP',
        'Aportes voluntarios a pensiones voluntarias RAIS',
        'Aportes voluntarios a pensiones voluntarias',
        'Aportes a AFC',
        'Aportes a AVC',
        'Retenciones en la fuente por pagos de rentas de trabajo',
        'IVA - Mayor vr costo o gasto',
        'RTE IVA',
        'Pagos por alimentacion hasta de 41 UVT',
        'Vr Promedio ingreso laboral ult 6 meses',
        'Tipo documento dependiente',
        'numero documento dependiente',
        'Identificacion del fideicomiso',
        'Tipo documento participe en contrato de colaboracion',
        'identificacion participe en contrato de colaboracion',
    ]

    CUENTAS_2276_VALOR_CREDITO = {
        '23650501', '23700501', '23700502', '23700504', '23700505',
        '23700506', '23700507', '23700510', '23803001', '23803002',
        '23803003', '23803004', '23803005',
    }

    COLUMNAS_VALOR_2276 = COLUMNAS_FORMATO_2276[12:41]
    UBICACION_COLUMNAS_2276 = {
        'L': 'Pagos por salarios',
        'S': 'Pagos por prestaciones sociales',
        'Y': 'Cesantias e ints, efectivamente pagadas',
        'AD': 'Aportes obligatorios por salud a cargo del trab',
        'AE': 'Aportes obligatorios pension, FSP',
        'AJ': 'Retenciones en la fuente por pagos de rentas de trabajo',
    }

    PALABRAS_EMPRESA = (
        'SAS', 'S.A.S', 'SA', 'S.A', 'LTDA', 'LTD', 'LIMITADA', 'E.U', 'EU',
        'SCS', 'SCA', 'COOPERATIVA', 'FUNDACION', 'CORPORATION', 'CORP',
        'INC', 'LLC', 'COMPANY', 'BANCO', 'EPS', 'IPS', 'UNIVERSIDAD',
        'MINISTERIO', 'ALCALDIA', 'GOBERNACION', 'DIRECCION', 'DIAN'
    )
    FRASES_EMPRESA = (
        'S EN C',
        'S. EN C.',
        'CONSORCIO',
        'UNION TEMPORAL',
    )

    def __init__(self, df):
        self.df_original = df.copy()
        self.df = self._detectar_y_limpiar_headers(df)
        self._normalize_dataframe()

    def _detectar_y_limpiar_headers(self, df):
        """Limpia encabezados decorativos cuando el archivo no viene plano."""
        print("\n[ESTRUCTURA] Detectando headers...")
        print(f"[ESTRUCTURA] Total filas en archivo: {len(df)}")
        print(f"[ESTRUCTURA] Headers actuales: {list(df.columns)}")

        cols_actuales = [str(col).lower().strip() for col in df.columns]
        tiene_codigo = any('código' in col or 'codigo' in col for col in cols_actuales)
        tiene_cuenta = any('cuenta' in col for col in cols_actuales)
        tiene_valores = any('débito' in col or 'debito' in col for col in cols_actuales) or any(
            'crédito' in col or 'credito' in col for col in cols_actuales
        )
        if tiene_cuenta and (tiene_codigo or tiene_valores):
            print("[ESTRUCTURA] Headers originales validos, sin limpieza adicional")
            return df

        for idx in range(min(10, len(df))):
            row_values = [str(v).lower().strip() for v in df.iloc[idx]]
            row_text = ' '.join(row_values)
            if any(x in row_text for x in ['código', 'codigo', 'cuenta', 'débito', 'debito', 'nit']):
                print(f"[ESTRUCTURA] Headers reales encontrados en fila {idx}")
                new_headers = [str(v).strip() for v in df.iloc[idx]]
                df_clean = df.iloc[idx + 1:].copy()
                df_clean.columns = new_headers
                return df_clean

        print("[ESTRUCTURA] No se encontraron headers decorativos, usando encabezados originales")
        return df

    def _normalize_dataframe(self):
        """Normaliza nombres de columnas y detecta los campos relevantes."""
        self.df.columns = self.df.columns.map(lambda col: str(col).strip())
        cols_lower = [str(col).lower().strip() for col in self.df.columns]

        col_codigo = self._buscar_columna(cols_lower, lambda col: 'código' in col or 'codigo' in col)
        col_cuenta = self._buscar_columna(
            cols_lower,
            lambda col: 'nombre de la cuenta' in col or ('cuenta' in col and 'descripción' not in col and 'descripcion' not in col)
        )
        col_nit = self._buscar_columna(
            cols_lower,
            lambda col: 'nit' in col or 'vat' in col or 'identificación' in col or 'identificacion' in col
        )
        col_tercero = self._buscar_columna(
            cols_lower,
            lambda col: 'nombre del tercero' in col or 'partner name' in col or 'razón social' in col or 'razon social' in col
        )
        col_debito = self._buscar_columna(cols_lower, lambda col: 'débito' in col or 'debito' in col)
        col_credito = self._buscar_columna(cols_lower, lambda col: 'crédito' in col or 'credito' in col)

        self.estructura_nueva = col_debito is not None and col_credito is not None
        self.columnas = {
            'codigo': self.df.columns[col_codigo] if col_codigo is not None else None,
            'cuenta': self.df.columns[col_cuenta] if col_cuenta is not None else None,
            'nit': self.df.columns[col_nit] if col_nit is not None else None,
            'tercero': self.df.columns[col_tercero] if col_tercero is not None else None,
            'debito': self.df.columns[col_debito] if col_debito is not None else None,
            'credito': self.df.columns[col_credito] if col_credito is not None else None,
        }

        print(f"[ESTRUCTURA] Detectada estructura: {'NUEVA' if self.estructura_nueva else 'ANTIGUA'}")
        print(f"[ESTRUCTURA] Columnas mapeadas: {self.columnas}")

    @staticmethod
    def _buscar_columna(columnas, condicion):
        for idx, col in enumerate(columnas):
            if condicion(col):
                return idx
        return None

    @staticmethod
    def _limpiar_texto(valor):
        if pd.isna(valor):
            return ''
        texto = str(valor).strip()
        if texto.lower() == 'nan':
            return ''
        return ' '.join(texto.split())

    @staticmethod
    def _limpiar_identificacion(valor):
        texto = DataProcessor._limpiar_texto(valor)
        if texto.endswith('.0'):
            texto = texto[:-2]
        return texto

    def _serie_texto(self, nombre_columna):
        if not nombre_columna or nombre_columna not in self.df.columns:
            return pd.Series([''] * len(self.df), index=self.df.index, dtype='string')
        return self.df[nombre_columna].map(self._limpiar_texto).astype('string')

    def _serie_numerica(self, nombre_columna):
        if not nombre_columna or nombre_columna not in self.df.columns:
            return pd.Series([0.0] * len(self.df), index=self.df.index, dtype='float64')
        return pd.to_numeric(self.df[nombre_columna], errors='coerce').fillna(0.0)

    def _serie_nit_limpio(self):
        return self._serie_texto(self.columnas['nit']).map(self._limpiar_identificacion)

    def _serie_columna_opcional(self, *aliases):
        aliases_norm = {
            self._limpiar_texto(alias).lower()
            for alias in aliases
            if self._limpiar_texto(alias)
        }
        for columna in self.df.columns:
            if self._limpiar_texto(columna).lower() in aliases_norm:
                return self._serie_texto(columna)
        return pd.Series([''] * len(self.df), index=self.df.index, dtype='string')

    def _mascara_nit_valido(self):
        return self._serie_nit_limpio().ne('')

    def _serie_codigo_normalizado(self):
        codigo = self._serie_texto(self.columnas['codigo']).str.replace(r'\.0$', '', regex=True)
        cuenta = self._serie_texto(self.columnas['cuenta'])
        codigo_en_cuenta = cuenta.str.extract(r'^(\d+)')[0].fillna('')
        return codigo.mask(codigo.eq(''), codigo_en_cuenta).astype('string')

    def _serie_descripcion_limpia(self):
        cuenta = self._serie_texto(self.columnas['cuenta'])
        return cuenta.str.replace(r'^\d+\s*', '', regex=True).str.strip()

    def _obtener_cuentas_formulario(self, codigo_formulario):
        if codigo_formulario in MAPEO_CUENTAS_FORMULARIO:
            return set(MAPEO_CUENTAS_FORMULARIO[codigo_formulario]['cuentas_patron'])
        return set()

    @staticmethod
    def _cuenta_aplica_formulario(codigo_formulario, codigo_cuenta):
        return bool(obtener_codigo_parametro_formulario(codigo_formulario, codigo_cuenta))

    def _mascara_resumen_formato(self, codigo_formato, codigo_norm, debito, credito):
        codigo_parametro = codigo_norm.map(
            lambda codigo: obtener_codigo_parametro_formulario(codigo_formato, codigo)
        )
        mascara = codigo_parametro.ne('')

        if codigo_formato == '1001':
            return mascara, codigo_parametro

        if codigo_formato == '1007':
            parametros_1007 = MAPEO_CUENTAS_FORMULARIO.get('1007', {}).get('parametros', {})
            naturaleza = codigo_parametro.map(
                lambda codigo: parametros_1007.get(codigo, {}).get('naturaleza', '')
            )
            return mascara & naturaleza.ne('NO'), codigo_parametro

        mascara = mascara & self._mascara_nit_valido()

        if codigo_formato in {'1008', '1009'}:
            mascara = mascara & ((debito != 0) | (credito != 0))

        if codigo_formato == '2276':
            parametros_2276 = MAPEO_CUENTAS_FORMULARIO.get('2276', {}).get('parametros', {})
            columna_valor = codigo_parametro.map(
                lambda codigo: self.UBICACION_COLUMNAS_2276.get(
                    self._extraer_codigo_ubicacion(parametros_2276.get(codigo, {}).get('ubicacion', '')),
                    ''
                )
            )
            mascara = mascara & ((debito != 0) | (credito != 0)) & columna_valor.ne('')

        return mascara, codigo_parametro

    def _saldo_resumen_formato(self, codigo_formato, codigo_parametro, mascara, debito, credito):
        if codigo_formato == '1008':
            return float((debito[mascara] - credito[mascara]).sum())
        if codigo_formato == '1009':
            return float((credito[mascara] - debito[mascara]).sum())
        if codigo_formato == '2276':
            usa_credito = codigo_parametro.isin(self.CUENTAS_2276_VALOR_CREDITO)
            valores = debito.where(~usa_credito, credito)
            return float(valores[mascara].sum())
        return float((debito[mascara] - credito[mascara]).abs().sum())

    def obtener_resumen_formato(self, codigo_formato):
        if codigo_formato not in self.FORMATO_CONFIG:
            raise ValueError(f"Formato {codigo_formato} no válido")

        codigo_norm = self._serie_codigo_normalizado()
        debito = self._serie_numerica(self.columnas['debito'])
        credito = self._serie_numerica(self.columnas['credito'])
        mascara, codigo_parametro = self._mascara_resumen_formato(codigo_formato, codigo_norm, debito, credito)

        resumen = {
            'filas_balance': int(len(self.df)),
            'registros': int(mascara.sum()),
            'suma_debito': float(debito[mascara].sum()),
            'suma_credito': float(credito[mascara].sum()),
            'saldo': self._saldo_resumen_formato(codigo_formato, codigo_parametro, mascara, debito, credito),
            'cuentas_distintas': int(codigo_norm[mascara].nunique()),
            'cuentas_parametrizadas': len(self._obtener_cuentas_formulario(codigo_formato)),
        }

        if codigo_formato == '1005':
            mascara_devoluciones = mascara & codigo_parametro.eq('24082001')
            mascara_descontable = mascara & ~mascara_devoluciones
            resumen.update({
                'impuesto_descontable': float(debito[mascara_descontable].sum()),
                'iva_devoluciones_ventas': float(credito[mascara_devoluciones].sum()),
            })

        return resumen

    def procesar_formato(self, codigo_formato):
        if codigo_formato not in self.FORMATO_CONFIG:
            raise ValueError(f"Formato {codigo_formato} no válido")

        print(f"\n[DESCARGA] Iniciando procesamiento de Formato {codigo_formato}")

        if codigo_formato == '1001':
            return self._procesar_formato_1001()
        if codigo_formato == '1005':
            return self._procesar_formato_1005()
        if codigo_formato == '1006':
            return self._procesar_formato_1006()
        if codigo_formato == '1007':
            return self._procesar_formato_1007()
        if codigo_formato == '1008':
            return self._procesar_formato_1008()
        if codigo_formato == '1009':
            return self._procesar_formato_1009()
        if codigo_formato == '2276':
            return self._procesar_formato_2276()

        cuentas_validas = self._obtener_cuentas_formulario(codigo_formato)
        print(f"[DEBUG] Formato {codigo_formato}: {len(cuentas_validas)} cuentas válidas")

        if not cuentas_validas:
            print(f"[WARNING] No hay cuentas definidas para formato {codigo_formato}")
            return pd.DataFrame()

        if self.estructura_nueva:
            return self._procesar_formato_nuevo(codigo_formato, cuentas_validas)
        return self._procesar_formato_antiguo(codigo_formato, cuentas_validas)

    def _procesar_formato_1001(self):
        """Construye el formato 1001 con la estructura DIAN esperada."""
        mapa_1001 = obtener_mapa_formato_1001()
        codigo_norm = self._serie_codigo_normalizado()
        descripcion_balance = self._serie_descripcion_limpia()
        nit = self._serie_nit_limpio()
        tercero = self._serie_texto(self.columnas['tercero'])
        debito = self._serie_numerica(self.columnas['debito'])
        credito = self._serie_numerica(self.columnas['credito'])

        df_1001 = pd.DataFrame({
            'codigo_normalizado': codigo_norm,
            'descripcion_balance': descripcion_balance,
            'nit': nit,
            'tercero': tercero,
            'debito': debito,
            'credito': credito,
        })

        df_1001['codigo_parametro'] = df_1001['codigo_normalizado'].map(
            lambda codigo: obtener_codigo_parametro_formulario('1001', codigo)
        )
        df_1001 = df_1001[df_1001['codigo_parametro'].ne('')].copy()
        if df_1001.empty:
            return pd.DataFrame(columns=self.COLUMNAS_FORMATO_1001)

        df_1001['Concepto'] = df_1001['codigo_parametro'].map(
            lambda codigo: mapa_1001[codigo]['concepto']
        )
        df_1001['Código Cuentas Contables'] = df_1001['codigo_normalizado']
        df_1001['Descripción'] = df_1001['codigo_parametro'].map(
            lambda codigo: mapa_1001[codigo]['descripcion']
        )
        df_1001['Descripción'] = df_1001['Descripción'].fillna(df_1001['descripcion_balance'])

        df_1001['Tipo documento'] = df_1001.apply(
            lambda row: self._inferir_tipo_documento(row['nit'], row['tercero']),
            axis=1
        )
        df_1001['Número identificación del informado'] = df_1001['nit']

        nombres = df_1001.apply(
            lambda row: self._dividir_nombre(row['Tipo documento'], row['tercero']),
            axis=1,
            result_type='expand'
        )
        nombres.columns = [
            'Primer apellido del informado',
            'Segundo apellido del informado',
            'Primer nombre del informado',
            'Otros nombres del informado',
            'Razón social informado',
        ]
        df_1001 = pd.concat([df_1001, nombres], axis=1)

        df_1001['Dirección'] = ''
        df_1001['Código dpto.'] = ''
        df_1001['Código mcp'] = ''
        df_1001['País de residencia o domicilio'] = ''
        df_1001['Pago o abono en cuenta deducible'] = df_1001['debito']
        df_1001['Pago o abono en cuenta no deducible'] = 0.0
        df_1001['Iva mayor valor del costo o gasto deducible'] = 0.0
        df_1001['Iva mayor valor del costo o gasto no deducible'] = 0.0
        df_1001['Retención en la fuente practicada en renta'] = 0.0
        df_1001['Retención en la fuente asumida en renta'] = 0.0
        df_1001['Retención en la fuente practicada IVA responsables de IVA'] = 0.0
        df_1001['Retención en la fuente practicada IVA no domiciliados'] = 0.0

        resultado = df_1001[self.COLUMNAS_FORMATO_1001].reset_index(drop=True)
        print(f"[4/5] Datos procesados para 1001: {len(resultado)} filas")
        return resultado

    def _procesar_formato_1005(self):
        """Construye el formato 1005 con la estructura esperada."""
        parametros_1005 = MAPEO_CUENTAS_FORMULARIO.get('1005', {}).get('parametros', {})
        codigo_norm = self._serie_codigo_normalizado()
        nit = self._serie_nit_limpio()
        tercero = self._serie_texto(self.columnas['tercero'])
        debito = self._serie_numerica(self.columnas['debito'])
        credito = self._serie_numerica(self.columnas['credito'])

        df_1005 = pd.DataFrame({
            'codigo_normalizado': codigo_norm,
            'nit': nit,
            'tercero': tercero,
            'debito': debito,
            'credito': credito,
        })
        df_1005['codigo_parametro'] = df_1005['codigo_normalizado'].map(
            lambda codigo: obtener_codigo_parametro_formulario('1005', codigo)
        )
        df_1005 = df_1005[
            df_1005['codigo_parametro'].ne('') & df_1005['nit'].ne('')
        ].copy()
        if df_1005.empty:
            return pd.DataFrame(columns=self.COLUMNAS_FORMATO_1005)

        df_1005['Código Cuentas Contables'] = df_1005['codigo_parametro']
        df_1005['Descripción'] = df_1005['codigo_parametro'].map(
            lambda codigo: parametros_1005[codigo]['descripcion']
        )
        df_1005['Naturaleza Cta.'] = df_1005['codigo_parametro'].map(
            lambda codigo: parametros_1005[codigo]['naturaleza']
        )
        df_1005['Tipo Documento'] = df_1005.apply(
            lambda row: self._inferir_tipo_documento(row['nit'], row['tercero']),
            axis=1
        )
        df_1005['Numero de identificacion'] = df_1005['nit']
        df_1005['DV'] = ''

        nombres = df_1005.apply(
            lambda row: self._dividir_nombre(row['Tipo Documento'], row['tercero']),
            axis=1,
            result_type='expand'
        )
        nombres.columns = [
            'Primer apellido del informado',
            'Segundo apellido del informado',
            'Primer nombre del informado',
            'Otros nombres del informado',
            'Razón social informado',
        ]
        df_1005 = pd.concat([df_1005, nombres], axis=1)

        es_devolucion_venta = df_1005['codigo_parametro'].eq('24082001')
        df_1005['Impuesto descontable'] = df_1005['debito'].where(~es_devolucion_venta, 0.0)
        df_1005['IVA resultante devoluciones VENTAS'] = df_1005['credito'].where(es_devolucion_venta, 0.0)

        resultado = df_1005[self.COLUMNAS_FORMATO_1005].reset_index(drop=True)
        print(f"[4/5] Datos procesados para 1005: {len(resultado)} filas")
        return resultado

    def _procesar_formato_1006(self):
        """Construye el formato 1006 con la estructura esperada."""
        parametros_1006 = MAPEO_CUENTAS_FORMULARIO.get('1006', {}).get('parametros', {})
        codigo_norm = self._serie_codigo_normalizado()
        nit = self._serie_nit_limpio()
        tercero = self._serie_texto(self.columnas['tercero'])
        debito = self._serie_numerica(self.columnas['debito'])
        credito = self._serie_numerica(self.columnas['credito'])

        df_1006 = pd.DataFrame({
            'codigo_normalizado': codigo_norm,
            'nit': nit,
            'tercero': tercero,
            'debito': debito,
            'credito': credito,
        })
        df_1006['codigo_parametro'] = df_1006['codigo_normalizado'].map(
            lambda codigo: obtener_codigo_parametro_formulario('1006', codigo)
        )
        df_1006 = df_1006[
            df_1006['codigo_parametro'].ne('') & df_1006['nit'].ne('')
        ].copy()
        if df_1006.empty:
            return pd.DataFrame(columns=self.COLUMNAS_FORMATO_1006)

        df_1006['Código Cuentas Contables'] = df_1006['codigo_parametro']
        df_1006['Descripción'] = df_1006['codigo_parametro'].map(
            lambda codigo: parametros_1006[codigo]['descripcion']
        )
        df_1006['Naturaleza Cta.'] = df_1006['codigo_parametro'].map(
            lambda codigo: parametros_1006[codigo]['naturaleza']
        )
        df_1006['Tipo Documento'] = df_1006.apply(
            lambda row: self._inferir_tipo_documento(row['nit'], row['tercero']),
            axis=1
        )
        df_1006['Numero de identificacion'] = df_1006['nit']
        df_1006['DV'] = ''

        nombres = df_1006.apply(
            lambda row: self._dividir_nombre(row['Tipo Documento'], row['tercero']),
            axis=1,
            result_type='expand'
        )
        nombres.columns = [
            'Primer apellido del informado',
            'Segundo apellido del informado',
            'Primer nombre del informado',
            'Otros nombres del informado',
            'Razón social informado',
        ]
        df_1006 = pd.concat([df_1006, nombres], axis=1)

        # Lógica especial para cuentas 24080501 y 24080503
        es_24080501 = df_1006['codigo_parametro'].eq('24080501')
        es_24080503 = df_1006['codigo_parametro'].eq('24080503')

        # Cuenta 24080501: solo toma CRÉDITO
        # Cuenta 24080503: solo toma DÉBITO
        df_1006['Impuesto Generado'] = df_1006['debito'].where(es_24080503, 0.0)
        df_1006.loc[es_24080501, 'Impuesto Generado'] = 0.0

        df_1006['IVA recuperado en devoluciones'] = df_1006['credito'].where(es_24080501, 0.0)
        df_1006.loc[es_24080503, 'IVA recuperado en devoluciones'] = 0.0

        df_1006['Impuesto al consumo'] = 0.0

        resultado = df_1006[self.COLUMNAS_FORMATO_1006].reset_index(drop=True)
        print(f"[4/5] Datos procesados para 1006: {len(resultado)} filas")
        return resultado

    def _procesar_formato_1007(self):
        """Construye el formato 1007 con la estructura esperada."""
        parametros_1007 = MAPEO_CUENTAS_FORMULARIO.get('1007', {}).get('parametros', {})
        codigo_norm = self._serie_codigo_normalizado()
        nit = self._serie_nit_limpio()
        tercero = self._serie_texto(self.columnas['tercero'])
        debito = self._serie_numerica(self.columnas['debito'])
        credito = self._serie_numerica(self.columnas['credito'])

        df_1007 = pd.DataFrame({
            'codigo_normalizado': codigo_norm,
            'nit': nit,
            'tercero': tercero,
            'debito': debito,
            'credito': credito,
        })
        df_1007['codigo_parametro'] = df_1007['codigo_normalizado'].map(
            lambda codigo: obtener_codigo_parametro_formulario('1007', codigo)
        )
        # Para 1007, no filtrar por NIT - permite procesar cuentas sin tercero especifico
        df_1007 = df_1007[df_1007['codigo_parametro'].ne('')].copy()
        if df_1007.empty:
            return pd.DataFrame(columns=self.COLUMNAS_FORMATO_1007)

        df_1007['naturaleza'] = df_1007['codigo_parametro'].map(
            lambda codigo: parametros_1007[codigo]['naturaleza']
        )

        # Filtrar cuentas con naturaleza 'NO' (como 421020) - ESTA ES LA ÚNICA EXCEPCIÓN
        df_1007 = df_1007[df_1007['naturaleza'] != 'NO'].copy()
        if df_1007.empty:
            return pd.DataFrame(columns=self.COLUMNAS_FORMATO_1007)

        df_1007['Concepto'] = df_1007['codigo_parametro'].map(
            lambda codigo: parametros_1007[codigo]['concepto']
        )
        df_1007['Código Cuentas Contables'] = df_1007['codigo_parametro']
        df_1007['Descripción'] = df_1007['codigo_parametro'].map(
            lambda codigo: parametros_1007[codigo]['descripcion']
        )
        df_1007['Tipo Documento'] = df_1007.apply(
            lambda row: self._inferir_tipo_documento(row['nit'], row['tercero']),
            axis=1
        )
        df_1007['Numero de identificacion'] = df_1007['nit']

        nombres = df_1007.apply(
            lambda row: self._dividir_nombre(row['Tipo Documento'], row['tercero']),
            axis=1,
            result_type='expand'
        )
        nombres.columns = [
            'Primer apellido del informado',
            'Segundo apellido del informado',
            'Primer nombre del informado',
            'Otros nombres del informado',
            'Razón social informado',
        ]
        df_1007 = pd.concat([df_1007, nombres], axis=1)

        df_1007['Pais'] = ''

        # Lógica especial para cuentas 41750501, 41750502, 41750503
        es_41750501 = df_1007['codigo_parametro'].eq('41750501')
        es_41750502 = df_1007['codigo_parametro'].eq('41750502')
        es_41750503 = df_1007['codigo_parametro'].eq('41750503')
        es_especial = es_41750501 | es_41750502 | es_41750503

        # Cuentas especiales (417505xx): toman solo DÉBITO
        # Demás cuentas (42xxxx): toman solo CRÉDITO
        df_1007['Ingresos brutos recibidos'] = df_1007['credito'].where(~es_especial, 0.0)
        df_1007['Devoluciones, rebajas y descuentos'] = df_1007['debito'].where(es_especial, 0.0)

        resultado = df_1007[self.COLUMNAS_FORMATO_1007].reset_index(drop=True)
        print(f"[4/5] Datos procesados para 1007: {len(resultado)} filas")
        return resultado

    def _procesar_formato_1008(self):
        """Construye el formato 1008 con saldo CXC calculado como debito menos credito."""
        parametros_1008 = MAPEO_CUENTAS_FORMULARIO.get('1008', {}).get('parametros', {})
        codigo_norm = self._serie_codigo_normalizado()
        nit = self._serie_nit_limpio()
        tercero = self._serie_texto(self.columnas['tercero'])
        debito = self._serie_numerica(self.columnas['debito'])
        credito = self._serie_numerica(self.columnas['credito'])

        df_1008 = pd.DataFrame({
            'codigo_normalizado': codigo_norm,
            'nit': nit,
            'tercero': tercero,
            'debito': debito,
            'credito': credito,
            'direccion': self._serie_columna_opcional('Direccion', 'Dirección'),
            'dpto': self._serie_columna_opcional('Dpto', 'Departamento', 'Código dpto.', 'Codigo dpto.'),
            'municipio': self._serie_columna_opcional('Municipio', 'Código mcp', 'Codigo mcp'),
            'pais': self._serie_columna_opcional('Pais', 'País'),
        })
        df_1008['codigo_parametro'] = df_1008['codigo_normalizado'].map(
            lambda codigo: obtener_codigo_parametro_formulario('1008', codigo)
        )
        df_1008 = df_1008[
            df_1008['codigo_parametro'].ne('')
            & df_1008['nit'].ne('')
            & ((df_1008['debito'] != 0) | (df_1008['credito'] != 0))
        ].copy()
        if df_1008.empty:
            return pd.DataFrame(columns=self.COLUMNAS_FORMATO_1008)

        df_1008['Concepto'] = df_1008['codigo_parametro'].map(
            lambda codigo: parametros_1008[codigo]['concepto']
        )
        df_1008['Código Cuentas Contables'] = df_1008['codigo_parametro']
        df_1008['Descripción'] = df_1008['codigo_parametro'].map(
            lambda codigo: parametros_1008[codigo]['descripcion']
        )
        df_1008['Tipo Documento'] = df_1008.apply(
            lambda row: self._inferir_tipo_documento(row['nit'], row['tercero']),
            axis=1
        )
        df_1008['Numero de identificacion'] = df_1008['nit']
        df_1008['DV'] = ''

        nombres = df_1008.apply(
            lambda row: self._dividir_nombre(row['Tipo Documento'], row['tercero']),
            axis=1,
            result_type='expand'
        )
        nombres.columns = [
            'Primer apellido del informado',
            'Segundo apellido del informado',
            'Primer nombre del informado',
            'Otros nombres del informado',
            'Razón social informado',
        ]
        df_1008 = pd.concat([df_1008, nombres], axis=1)

        df_1008['Direccion'] = df_1008['direccion']
        df_1008['Dpto'] = df_1008['dpto']
        df_1008['Municipio'] = df_1008['municipio']
        df_1008['Pais'] = df_1008['pais']
        df_1008['Saldo CXC a 31 diciembre'] = df_1008['debito'] - df_1008['credito']

        resultado = df_1008[self.COLUMNAS_FORMATO_1008].reset_index(drop=True)
        print(f"[4/5] Datos procesados para 1008: {len(resultado)} filas")
        return resultado

    def _procesar_formato_1009(self):
        """Construye el formato 1009 con saldo CXP calculado como credito menos debito."""
        parametros_1009 = MAPEO_CUENTAS_FORMULARIO.get('1009', {}).get('parametros', {})
        codigo_norm = self._serie_codigo_normalizado()
        nit = self._serie_nit_limpio()
        tercero = self._serie_texto(self.columnas['tercero'])
        debito = self._serie_numerica(self.columnas['debito'])
        credito = self._serie_numerica(self.columnas['credito'])

        df_1009 = pd.DataFrame({
            'codigo_normalizado': codigo_norm,
            'nit': nit,
            'tercero': tercero,
            'debito': debito,
            'credito': credito,
            'direccion': self._serie_columna_opcional('Direccion', 'Dirección'),
            'dpto': self._serie_columna_opcional('Dpto', 'Departamento', 'Código dpto.', 'Codigo dpto.'),
            'municipio': self._serie_columna_opcional('Municipio', 'Código mcp', 'Codigo mcp'),
            'pais': self._serie_columna_opcional('Pais', 'País'),
        })
        df_1009['codigo_parametro'] = df_1009['codigo_normalizado'].map(
            lambda codigo: obtener_codigo_parametro_formulario('1009', codigo)
        )
        df_1009 = df_1009[
            df_1009['codigo_parametro'].ne('')
            & df_1009['nit'].ne('')
            & ((df_1009['debito'] != 0) | (df_1009['credito'] != 0))
        ].copy()
        if df_1009.empty:
            return pd.DataFrame(columns=self.COLUMNAS_FORMATO_1009)

        df_1009['Concepto'] = df_1009['codigo_parametro'].map(
            lambda codigo: parametros_1009[codigo]['concepto']
        )
        df_1009['Código Cuentas Contables'] = df_1009['codigo_parametro']
        df_1009['Descripción'] = df_1009['codigo_parametro'].map(
            lambda codigo: parametros_1009[codigo]['descripcion']
        )
        df_1009['Tipo Documento'] = df_1009.apply(
            lambda row: self._inferir_tipo_documento(row['nit'], row['tercero']),
            axis=1
        )
        df_1009['Número identificación del informado'] = df_1009['nit']
        df_1009['DV'] = ''

        nombres = df_1009.apply(
            lambda row: self._dividir_nombre(row['Tipo Documento'], row['tercero']),
            axis=1,
            result_type='expand'
        )
        nombres.columns = [
            'Primer apellido del informado',
            'Segundo apellido del informado',
            'Primer nombre del informado',
            'Otros nombres del informado',
            'Razón social informado',
        ]
        df_1009 = pd.concat([df_1009, nombres], axis=1)

        df_1009['Direccion'] = df_1009['direccion']
        df_1009['Dpto'] = df_1009['dpto']
        df_1009['Municipio'] = df_1009['municipio']
        df_1009['Pais'] = df_1009['pais']
        df_1009['Saldo CXP a 31 diciembre'] = df_1009['credito'] - df_1009['debito']

        resultado = df_1009[self.COLUMNAS_FORMATO_1009].reset_index(drop=True)
        print(f"[4/5] Datos procesados para 1009: {len(resultado)} filas")
        return resultado

    @staticmethod
    def _extraer_codigo_ubicacion(texto):
        texto = DataProcessor._limpiar_texto(texto)
        if not texto.startswith('(') or ')' not in texto:
            return ''
        return texto[1:texto.index(')')].strip()

    def _procesar_formato_2276(self):
        """Construye el formato 2276 usando credito para cuentas C y debito para las demas."""
        parametros_2276 = MAPEO_CUENTAS_FORMULARIO.get('2276', {}).get('parametros', {})
        codigo_norm = self._serie_codigo_normalizado()
        nit = self._serie_nit_limpio()
        tercero = self._serie_texto(self.columnas['tercero'])
        debito = self._serie_numerica(self.columnas['debito'])
        credito = self._serie_numerica(self.columnas['credito'])

        df_2276 = pd.DataFrame({
            'codigo_normalizado': codigo_norm,
            'nit': nit,
            'tercero': tercero,
            'debito': debito,
            'credito': credito,
            'direccion': self._serie_columna_opcional('Direccion', 'Dirección'),
            'dpto': self._serie_columna_opcional('Dpto', 'Departamento', 'Código dpto.', 'Codigo dpto.'),
            'municipio': self._serie_columna_opcional('Municipio', 'Código mcp', 'Codigo mcp'),
            'pais': self._serie_columna_opcional('Pais', 'País'),
        })
        df_2276['codigo_parametro'] = df_2276['codigo_normalizado'].map(
            lambda codigo: obtener_codigo_parametro_formulario('2276', codigo)
        )
        df_2276 = df_2276[
            df_2276['codigo_parametro'].ne('')
            & df_2276['nit'].ne('')
            & ((df_2276['debito'] != 0) | (df_2276['credito'] != 0))
        ].copy()
        if df_2276.empty:
            return pd.DataFrame(columns=self.COLUMNAS_FORMATO_2276)

        df_2276['columna_valor'] = df_2276['codigo_parametro'].map(
            lambda codigo: self.UBICACION_COLUMNAS_2276.get(
                self._extraer_codigo_ubicacion(parametros_2276[codigo]['ubicacion']),
                ''
            )
        )
        df_2276 = df_2276[df_2276['columna_valor'].ne('')].copy()
        if df_2276.empty:
            return pd.DataFrame(columns=self.COLUMNAS_FORMATO_2276)

        usa_credito = df_2276['codigo_parametro'].isin(self.CUENTAS_2276_VALOR_CREDITO)
        df_2276['valor'] = df_2276['debito'].where(~usa_credito, df_2276['credito'])

        resultado = pd.DataFrame(0.0, index=df_2276.index, columns=self.COLUMNAS_VALOR_2276)
        resultado.insert(0, 'País', df_2276['pais'])
        resultado.insert(0, 'Municipio', df_2276['municipio'])
        resultado.insert(0, 'Dpto', df_2276['dpto'])
        resultado.insert(0, 'Direccion', df_2276['direccion'])

        tipo_doc = df_2276.apply(
            lambda row: self._inferir_tipo_documento(row['nit'], row['tercero']),
            axis=1
        )
        nombres = df_2276.assign(tipo_doc=tipo_doc).apply(
            lambda row: self._dividir_nombre(row['tipo_doc'], row['tercero']),
            axis=1,
            result_type='expand'
        )
        nombres.columns = [
            'Primer apellido empleado',
            'Segundo apellido empleado',
            'Primer nombre empleado',
            'Otros nombres empleado',
            'Razón social informado',
        ]

        resultado.insert(0, 'Razón social informado', nombres['Razón social informado'])
        resultado.insert(0, 'Otros nombres empleado', nombres['Otros nombres empleado'])
        resultado.insert(0, 'Primer nombre empleado', nombres['Primer nombre empleado'])
        resultado.insert(0, 'Segundo apellido empleado', nombres['Segundo apellido empleado'])
        resultado.insert(0, 'Primer apellido empleado', nombres['Primer apellido empleado'])
        resultado.insert(0, 'Número identificación', df_2276['nit'])
        resultado.insert(0, 'Tipo documento beneficiario', tipo_doc)
        resultado.insert(0, 'Entidad informante', '')

        for columna in self.COLUMNAS_FORMATO_2276[41:]:
            resultado[columna] = ''

        for idx, row in df_2276.iterrows():
            resultado.at[idx, row['columna_valor']] = row['valor']

        resultado = resultado[self.COLUMNAS_FORMATO_2276].reset_index(drop=True)
        print(f"[4/5] Datos procesados para 2276: {len(resultado)} filas")
        return resultado

    def _procesar_formato_nuevo(self, codigo_formato, cuentas_validas):
        datos_formato = []

        col_codigo = self.columnas['codigo']
        col_cuenta = self.columnas['cuenta']
        col_nit = self.columnas['nit']
        col_nit = self.columnas['nit']
        col_debito = self.columnas['debito']
        col_credito = self.columnas['credito']

        print(f"[4/5] Procesando datos para formato {codigo_formato}...")

        total_filas = len(self.df)
        filas_coincidentes = 0
        codigo_actual = None

        for _, row in self.df.iterrows():
            codigo = self._limpiar_texto(row[col_codigo]) if col_codigo else ""
            nombre_cuenta = self._limpiar_texto(row[col_cuenta]) if col_cuenta else ""
            nit = self._limpiar_identificacion(row[col_nit]) if col_nit else ""

            if not nit:
                continue

            if codigo.endswith('.0'):
                codigo = codigo[:-2]

            if not codigo and nombre_cuenta:
                partes = nombre_cuenta.split()
                if partes and partes[0].isdigit():
                    codigo = partes[0]
                elif codigo_actual:
                    codigo = codigo_actual

            if codigo and codigo.isdigit():
                codigo_actual = codigo

            if not self._cuenta_aplica_formulario(codigo_formato, codigo):
                continue

            debito = pd.to_numeric(row[col_debito], errors='coerce') if col_debito else 0
            credito = pd.to_numeric(row[col_credito], errors='coerce') if col_credito else 0
            debito = 0 if pd.isna(debito) else float(debito)
            credito = 0 if pd.isna(credito) else float(credito)

            if debito != 0 or credito != 0:
                datos_formato.append({
                    'Código': codigo,
                    'Cuenta': nombre_cuenta,
                    'Débito': debito,
                    'Crédito': credito,
                    'Saldo': abs(debito - credito)
                })
                filas_coincidentes += 1

        print(f"[4/5] Datos procesados: {filas_coincidentes} filas encontradas de {total_filas} totales")

        df_formato = pd.DataFrame(datos_formato) if datos_formato else pd.DataFrame()
        if not df_formato.empty:
            totales = {
                'Código': 'TOTAL',
                'Cuenta': 'Suma de saldos',
                'Débito': df_formato['Débito'].sum(),
                'Crédito': df_formato['Crédito'].sum(),
                'Saldo': df_formato['Saldo'].sum()
            }
            df_formato = pd.concat([df_formato, pd.DataFrame([totales])], ignore_index=True)

        return df_formato

    def _procesar_formato_antiguo(self, codigo_formato, cuentas_validas):
        datos_formato = []

        col_codigo = self.columnas['codigo']
        col_cuenta = self.columnas['cuenta']

        print(f"[4/5] Procesando datos para formato {codigo_formato}...")

        for _, row in self.df.iterrows():
            codigo = self._limpiar_texto(row[col_codigo]) if col_codigo else ""
            nombre_cuenta = self._limpiar_texto(row[col_cuenta]) if col_cuenta else ""
            nit = self._limpiar_identificacion(row[col_nit]) if col_nit else ""

            if not nit:
                continue

            if codigo.endswith('.0'):
                codigo = codigo[:-2]

            if self._cuenta_aplica_formulario(codigo_formato, codigo):
                datos_formato.append({
                    'Código': codigo,
                    'Cuenta': nombre_cuenta,
                    'Saldo': 0
                })

        print(f"[4/5] Datos procesados: {len(datos_formato)} filas encontradas")

        df_formato = pd.DataFrame(datos_formato) if datos_formato else pd.DataFrame()
        if not df_formato.empty:
            totales = {
                'Código': 'TOTAL',
                'Cuenta': 'Suma de saldos',
                'Saldo': 0
            }
            df_formato = pd.concat([df_formato, pd.DataFrame([totales])], ignore_index=True)

        return df_formato

    def validar_estructura(self):
        errores = []

        if self.df.empty:
            errores.append("El archivo está vacío")

        cols_lower = [str(col).lower() for col in self.df.columns]
        if not any('código' in col or 'codigo' in col for col in cols_lower):
            errores.append("No se encontró columna de Código")

        if not any('cuenta' in col for col in cols_lower):
            errores.append("No se encontró columna de Cuenta")

        if self.estructura_nueva:
            if not any('débito' in col or 'debito' in col for col in cols_lower):
                errores.append("No se encontró columna de Débito")
            if not any('crédito' in col or 'credito' in col for col in cols_lower):
                errores.append("No se encontró columna de Crédito")

        return len(errores) == 0, errores

    @classmethod
    def _inferir_tipo_documento(cls, numero, razon_social):
        numero = cls._limpiar_identificacion(numero)
        razon_social = cls._limpiar_texto(razon_social).upper()
        razon_social_tokens = set(
            razon_social.replace('.', ' ').replace(',', ' ').replace('-', ' ').split()
        )

        if not numero and not razon_social:
            return ''
        if '-' in numero:
            return '31'
        if any(frase in razon_social for frase in cls.FRASES_EMPRESA):
            return '31'
        if any(palabra in razon_social_tokens for palabra in cls.PALABRAS_EMPRESA):
            return '31'
        return '13'

    @classmethod
    def _dividir_nombre(cls, tipo_doc, razon_social):
        razon_social = cls._limpiar_texto(razon_social)
        if not razon_social:
            return ['', '', '', '', '']

        if tipo_doc == '31':
            return ['', '', '', '', razon_social]

        partes = razon_social.split()
        if len(partes) == 1:
            return ['', '', partes[0], '', '']
        if len(partes) == 2:
            return [partes[1], '', partes[0], '', '']
        if len(partes) == 3:
            return [partes[1], partes[2], partes[0], '', '']

        primer_nombre = partes[0]
        otros_nombres = ' '.join(partes[1:-2])
        primer_apellido = partes[-2]
        segundo_apellido = partes[-1]
        return [primer_apellido, segundo_apellido, primer_nombre, otros_nombres, '']
