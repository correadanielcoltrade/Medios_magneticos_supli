import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mapeo_cuentas import MAPEO_CUENTAS_FORMULARIO, obtener_codigo_parametro_formulario
from modules.data_processor import DataProcessor


class FakeContactProvider:
    def __init__(self, contactos):
        self.contactos = contactos
        self.nits_consultados = []

    def obtener_contactos(self, nits):
        self.nits_consultados.extend(nits)
        return {str(nit): self.contactos.get(str(nit), {}) for nit in nits}


def test_parametros_csv_cargan_formato_1001():
    assert len(MAPEO_CUENTAS_FORMULARIO['1001']['cuentas_patron']) == 110
    assert obtener_codigo_parametro_formulario('1001', '5105680201') == '51056802'


def test_dividir_nombre_persona_natural_usa_orden_dian_apellidos_y_nombres():
    assert DataProcessor._dividir_nombre('13', 'PEREZ LOPEZ ANA MARIA') == [
        'PEREZ',
        'LOPEZ',
        'ANA',
        'MARIA',
        '',
    ]
    assert DataProcessor._dividir_nombre('13', 'DIAZ CARLOS') == [
        'DIAZ',
        '',
        'CARLOS',
        '',
        '',
    ]
    assert DataProcessor._dividir_nombre('31', 'CLIENTE SAS') == [
        '',
        '',
        '',
        '',
        'CLIENTE SAS',
    ]


def test_formatos_con_ubicacion_consultan_contactos_odoo_por_nit():
    contactos = {
        '900100100-1': {
            'direccion': 'CL ODOO 1 2 3',
            'dpto': '11',
            'municipio': '001',
            'pais': '169',
        },
        '10101010': {
            'direccion': 'CR ODOO 4 5 6',
            'dpto': '05',
            'municipio': '001',
            'pais': '169',
        },
    }
    provider = FakeContactProvider(contactos)

    casos = {
        '1001': {
            'Codigo': ['5105680201'],
            'Nombre de la cuenta': ['5105680201 ARL SURA'],
            'NIT del tercero': ['900100100-1'],
            'Nombre del tercero': ['PROVEEDOR SAS'],
            'Debito': [100.0],
            'Credito': [0.0],
        },
        '1008': {
            'Codigo': ['13050501'],
            'Nombre de la cuenta': ['13050501 CLIENTES NACIONALES'],
            'NIT del tercero': ['900100100-1'],
            'Nombre del tercero': ['CLIENTE SAS'],
            'Direccion': ['DIRECCION BALANCE'],
            'Dpto': ['99'],
            'Municipio': ['999'],
            'Debito': [1000.0],
            'Credito': [250.0],
        },
        '1009': {
            'Codigo': ['21051005'],
            'Nombre de la cuenta': ['21051005 ROTATIVO BANCOLOMBIA'],
            'NIT del tercero': ['900100100-1'],
            'Nombre del tercero': ['BANCOLOMBIA'],
            'Direccion': ['DIRECCION BALANCE'],
            'Dpto': ['99'],
            'Municipio': ['999'],
            'Debito': [100.0],
            'Credito': [300.0],
        },
        '2276': {
            'Codigo': ['51050601'],
            'Nombre de la cuenta': ['51050601 SUELDOS'],
            'NIT del tercero': ['10101010'],
            'Nombre del tercero': ['PEREZ LOPEZ ANA MARIA'],
            'Direccion': ['DIRECCION BALANCE'],
            'Dpto': ['99'],
            'Municipio': ['999'],
            'Debito': [2000.0],
            'Credito': [0.0],
        },
    }

    for formato, datos in casos.items():
        resultado = DataProcessor(pd.DataFrame(datos), contact_provider=provider).procesar_formato(formato)
        direccion_col = 'Direccion' if 'Direccion' in resultado.columns else 'Dirección'
        dpto_col = 'Dpto' if 'Dpto' in resultado.columns else 'Código dpto.'
        municipio_col = 'Municipio' if 'Municipio' in resultado.columns else 'Código mcp'

        assert resultado.iloc[0][direccion_col] in {'CL ODOO 1 2 3', 'CR ODOO 4 5 6'}
        assert resultado.iloc[0][dpto_col] in {'11', '05'}
        assert resultado.iloc[0][municipio_col] == '001'

    assert set(provider.nits_consultados) == {'900100100-1', '10101010'}


def test_formato_1001_filtra_por_cuentas_parametrizadas():
    df = pd.DataFrame({
        'Codigo': ['5105680201', '5105680202', '5105680203', '5105680204', '11050501'],
        'Nombre de la cuenta': [
            '5105680201 ARL SURA SUBCUENTA',
            '5105680202 ARL SURA SIN NIT',
            '5105680203 ARL SURA SIN NIT EN CERO',
            '5105680204 ARL SURA SIN NIT EN BLANCO',
            '11050501 CAJA GENERAL',
        ],
        'NIT del tercero': ['900904996-1', '', '', '', '900000000-0'],
        'Nombre del tercero': [
            'ARL SURA SA',
            'TERCERO SIN NIT',
            'TERCERO SIN NIT CERO',
            'TERCERO SIN NIT BLANCO',
            'TERCERO SIN FORMATO',
        ],
        'Debito': [125000.0, 50000.0, 0.0, '', 999999.0],
        'Credito': [0.0, 0.0, 0.0, 0.0, 0.0],
    })

    resultado = DataProcessor(df).procesar_formato('1001')
    resumen = DataProcessor(df).obtener_resumen_formato('1001')

    assert len(resultado) == 2
    assert resultado.iloc[0, 0] == '5011'
    assert resultado.iloc[0, 1] == '5105680201'
    assert resultado.iloc[0, 14] == 125000.0
    assert resultado.iloc[1, 1] == '5105680202'
    assert resultado.iloc[1, 4] == ''
    assert resultado.iloc[1, 14] == 50000.0
    assert resumen['registros'] == 2
    assert resumen['suma_debito'] == 175000.0


def test_formato_1001_excluye_cuentas_143501_sin_identificacion_ni_tipo_documento():
    df = pd.DataFrame({
        'Codigo': ['14350101', '14350102', '14350101', '14350102', '5105680201'],
        'Nombre de la cuenta': [
            '14350101 PRODUCTOS GRAVADOS CON IVA',
            '14350102 PRODUCTOS EXENTOS DE IVA',
            '14350101 PRODUCTOS GRAVADOS CON IVA',
            '14350102 PRODUCTOS EXENTOS DE IVA',
            '5105680201 ARL SURA SIN DOCUMENTO',
        ],
        'NIT del tercero': ['', '', '', '900100100-1', ''],
        'Nombre del tercero': ['', '', 'TERCERO SIN CEDULA', '', ''],
        'Debito': [100.0, 200.0, 300.0, 400.0, 500.0],
        'Credito': [0.0, 0.0, 0.0, 0.0, 0.0],
    })

    processor = DataProcessor(df)
    resultado = processor.procesar_formato('1001')
    resumen = processor.obtener_resumen_formato('1001')

    assert len(resultado) == 2
    assert resultado.iloc[:, 1].tolist() == ['14350101', '14350102']
    assert resultado.iloc[:, 14].tolist() == [300.0, 400.0]
    assert resultado.iloc[0, 3] == '13'
    assert resumen['registros'] == len(resultado)
    assert resumen['suma_debito'] == 700.0


def test_formatos_excluyen_filas_con_valor_sin_nit_ni_nombre_tercero():
    casos = {
        '1005': ('24081001', [100.0, 999.0], [0.0, 0.0]),
        '1006': ('24080501', [0.0, 0.0], [100.0, 999.0]),
        '1007': ('41359501', [0.0, 0.0], [100.0, 999.0]),
        '1008': ('13050501', [100.0, 999.0], [0.0, 0.0]),
        '1009': ('21051005', [0.0, 0.0], [100.0, 999.0]),
        '2276': ('51050601', [100.0, 999.0], [0.0, 0.0]),
    }

    for formato, (codigo, debitos, creditos) in casos.items():
        df = pd.DataFrame({
            'Codigo': [codigo, codigo],
            'Nombre de la cuenta': [f'{codigo} CUENTA VALIDA', f'{codigo} CUENTA SIN TERCERO'],
            'NIT del tercero': ['900100100-1', ''],
            'Nombre del tercero': ['TERCERO VALIDO SAS', ''],
            'Debito': debitos,
            'Credito': creditos,
        })

        processor = DataProcessor(df)
        resultado = processor.procesar_formato(formato)
        resumen = processor.obtener_resumen_formato(formato)

        assert len(resultado) == 1
        assert resumen['registros'] == 1


def test_formato_1005_usa_debito_y_credito_segun_cuenta():
    df = pd.DataFrame({
        'Codigo': ['24081001', '24082001', '24081002', '24081005', '11050501'],
        'Nombre de la cuenta': [
            '24081001 COMPRAS AL 19%',
            '24082001 IVA EN DEVOLUCION DE VENTA 19%',
            '24081002 SERVICIOS AL 19%',
            '24081005 IMPORTACIONES AL 19%',
            '11050501 CAJA GENERAL',
        ],
        'NIT del tercero': ['900100100-1', '900200200-2', '900300300-3', None, '900400400-4'],
        'Nombre del tercero': ['PROVEEDOR SAS', 'CLIENTE SAS', 'SERVICIOS SAS', 'SIN NIT SAS', 'CAJA SAS'],
        'Debito': [1000.0, 9999.0, 2000.0, 4000.0, 3000.0],
        'Credito': [111.0, 500.0, 222.0, 444.0, 333.0],
    })

    resultado = DataProcessor(df).procesar_formato('1005')
    resumen = DataProcessor(df).obtener_resumen_formato('1005')

    assert len(resultado) == 4
    compras = resultado[resultado['Código Cuentas Contables'] == '24081001'].iloc[0]
    devolucion = resultado[resultado['Código Cuentas Contables'] == '24082001'].iloc[0]
    servicios = resultado[resultado['Código Cuentas Contables'] == '24081002'].iloc[0]

    assert compras['Impuesto descontable'] == 1000.0
    assert compras['IVA resultante devoluciones VENTAS'] == 0.0
    assert servicios['Impuesto descontable'] == 2000.0
    assert servicios['IVA resultante devoluciones VENTAS'] == 0.0
    importacion = resultado[resultado.iloc[:, 0] == '24081005'].iloc[0]
    assert importacion['Impuesto descontable'] == 4000.0
    assert devolucion['Impuesto descontable'] == 0.0
    assert devolucion['IVA resultante devoluciones VENTAS'] == 500.0
    assert resumen['registros'] == 4
    assert resumen['impuesto_descontable'] == 7000.0
    assert resumen['iva_devoluciones_ventas'] == 500.0


def test_resumen_generico_incluye_debito_credito_y_saldo():
    df = pd.DataFrame({
        'Codigo': ['24080501', '24080503', '24080501', '11050501'],
        'Nombre de la cuenta': [
            '24080501 IVA GENERADO',
            '24080503 IVA GENERADO DEVOLUCIONES',
            '24080501 IVA GENERADO SIN NIT',
            '11050501 CAJA GENERAL',
        ],
        'NIT del tercero': ['900100100-1', '900200200-2', '', '900300300-3'],
        'Nombre del tercero': ['CLIENTE SAS', 'CLIENTE DOS SAS', 'CLIENTE SIN NIT', 'CAJA SAS'],
        'Debito': [100.0, 200.0, 999.0, 300.0],
        'Credito': [1000.0, 500.0, 999.0, 600.0],
    })

    resumen = DataProcessor(df).obtener_resumen_formato('1006')

    assert resumen['registros'] == 3
    assert resumen['suma_debito'] == 1299.0
    assert resumen['suma_credito'] == 2499.0
    assert resumen['saldo'] == 1200.0


def test_resumen_1007_cuenta_las_mismas_filas_generadas():
    df = pd.DataFrame({
        'Codigo': ['41359501', '41750501', '421020', '11050501'],
        'Nombre de la cuenta': [
            '41359501 PRODUCTOS GRAVADOS 19%',
            '41750501 PRODUCTOS GRAVADOS AL 19%',
            '421020 DIFERENCIA EN CAMBIO',
            '11050501 CAJA GENERAL',
        ],
        'NIT del tercero': ['900100100-1', '', '900200200-2', '900300300-3'],
        'Nombre del tercero': ['CLIENTE SAS', 'SIN NIT', 'DIFERENCIA SAS', 'CAJA SAS'],
        'Debito': [100.0, 400.0, 700.0, 1.0],
        'Credito': [1000.0, 50.0, 700.0, 2.0],
    })

    processor = DataProcessor(df)
    resultado = processor.procesar_formato('1007')
    resumen = processor.obtener_resumen_formato('1007')

    assert len(resultado) == 2
    assert resumen['registros'] == len(resultado)
    assert resumen['cuentas_distintas'] == 2


def test_formato_1008_calcula_saldo_cxc_debito_menos_credito():
    df = pd.DataFrame({
        'Codigo': ['13050501', '13309501', '13050501', '24080501'],
        'Nombre de la cuenta': [
            '13050501 CLIENTES NACIONALES',
            '13309501 OTROS',
            '13050501 CLIENTES SIN NIT',
            '24080501 IVA GENERADO',
        ],
        'NIT del tercero': ['900100100-1', '900200200-2', '', '900300300-3'],
        'Nombre del tercero': ['CLIENTE SAS', 'TERCERO NATURAL', 'SIN NIT SAS', 'CLIENTE IVA SAS'],
        'Direccion': ['CL 1 2 3', 'CR 4 5 6', 'SIN NIT', 'CL IVA'],
        'Dpto': ['11', '76', '05', '08'],
        'Municipio': ['001', '001', '001', '001'],
        'Debito': [1000.0, 200.0, 999.0, 300.0],
        'Credito': [250.0, 500.0, 999.0, 600.0],
    })

    resultado = DataProcessor(df).procesar_formato('1008')
    resumen = DataProcessor(df).obtener_resumen_formato('1008')

    assert list(resultado.columns) == DataProcessor.COLUMNAS_FORMATO_1008
    assert len(resultado) == 3
    assert resumen['registros'] == len(resultado)
    assert resumen['saldo'] == 450.0

    cliente = resultado[resultado['Numero de identificacion'] == '900100100-1'].iloc[0]
    tercero = resultado[resultado['Numero de identificacion'] == '900200200-2'].iloc[0]

    assert cliente['Concepto'] == '1315'
    assert cliente['Código Cuentas Contables'] == '13050501'
    assert cliente['Saldo CXC a 31 diciembre'] == 750.0
    assert cliente['Direccion'] == 'CL 1 2 3'
    assert tercero['Concepto'] == '1317'
    assert tercero['Saldo CXC a 31 diciembre'] == -300.0


def test_formato_1009_calcula_saldo_cxp_credito_menos_debito():
    df = pd.DataFrame({
        'Codigo': ['21051005', '22100501', '21051005', '13050501'],
        'Nombre de la cuenta': [
            '21051005 ROTATIVO BANCOLOMBIA',
            '22100501 PROVEEDORES DEL EXTERIOR',
            '21051005 ROTATIVO SIN NIT',
            '13050501 CLIENTES NACIONALES',
        ],
        'NIT del tercero': ['890903938-8', '900200200-2', '', '900300300-3'],
        'Nombre del tercero': ['BANCOLOMBIA', 'PROVEEDOR SAS', 'SIN NIT SAS', 'CLIENTE SAS'],
        'Direccion': ['CR 48 26 85', 'CL 2 3 4', 'SIN NIT', 'CL CLIENTE'],
        'Dpto': ['05', '11', '76', '08'],
        'Municipio': ['169', '001', '001', '001'],
        'Debito': [1000.0, 500.0, 999.0, 300.0],
        'Credito': [250.0, 2000.0, 999.0, 600.0],
    })

    resultado = DataProcessor(df).procesar_formato('1009')
    resumen = DataProcessor(df).obtener_resumen_formato('1009')

    assert list(resultado.columns) == DataProcessor.COLUMNAS_FORMATO_1009
    assert len(resultado) == 3
    assert resumen['registros'] == len(resultado)
    assert resumen['saldo'] == 750.0

    banco = resultado[resultado['Número identificación del informado'] == '890903938-8'].iloc[0]
    proveedor = resultado[resultado['Número identificación del informado'] == '900200200-2'].iloc[0]

    assert banco['Concepto'] == '2203'
    assert banco['Código Cuentas Contables'] == '21051005'
    assert banco['Saldo CXP a 31 diciembre'] == -750.0
    assert banco['Direccion'] == 'CR 48 26 85'
    assert proveedor['Concepto'] == '2201'
    assert proveedor['Saldo CXP a 31 diciembre'] == 1500.0


def test_formato_2276_usa_credito_para_cuentas_especiales_y_debito_para_las_demas():
    df = pd.DataFrame({
        'Codigo': ['23650501', '51050601', '25101001', '23803001', '13050501', '51050601'],
        'Nombre de la cuenta': [
            '23650501 RENTAS DE TRABAJO',
            '51050601 SUELDOS',
            '25101001 CESANTIAS CONSOLIDADAS',
            '23803001 PORVENIR',
            '13050501 CLIENTES NACIONALES',
            '51050601 SUELDOS SIN NIT',
        ],
        'NIT del tercero': ['900100100-1', '10101010', '20202020', '800200200-2', '900300300-3', ''],
        'Nombre del tercero': [
            'RETENCIONES SAS',
            'PEREZ LOPEZ ANA MARIA',
            'DIAZ CARLOS',
            'PORVENIR SA',
            'CLIENTE SAS',
            'SIN NIT',
        ],
        'Direccion': ['CL 1', 'CL 2', 'CL 3', 'CL 4', 'CL 5', 'CL 6'],
        'Dpto': ['11', '11', '11', '11', '11', '11'],
        'Municipio': ['001', '001', '001', '001', '001', '001'],
        'Debito': [100.0, 2000.0, 3000.0, 400.0, 500.0, 6000.0],
        'Credito': [700.0, 50.0, 60.0, 900.0, 800.0, 10.0],
    })

    resultado = DataProcessor(df).procesar_formato('2276')
    resumen = DataProcessor(df).obtener_resumen_formato('2276')

    assert list(resultado.columns) == DataProcessor.COLUMNAS_FORMATO_2276
    assert len(resultado) == 5
    assert resumen['registros'] == len(resultado)
    assert resumen['saldo'] == 12600.0

    retencion = resultado[resultado['Número identificación'] == '900100100-1'].iloc[0]
    salario = resultado[resultado['Número identificación'] == '10101010'].iloc[0]
    cesantias = resultado[resultado['Número identificación'] == '20202020'].iloc[0]
    pension = resultado[resultado['Número identificación'] == '800200200-2'].iloc[0]

    assert retencion['Retenciones en la fuente por pagos de rentas de trabajo'] == 700.0
    assert retencion['Pagos por salarios'] == 0.0
    assert salario['Pagos por salarios'] == 2000.0
    assert salario['Primer apellido empleado'] == 'PEREZ'
    assert salario['Segundo apellido empleado'] == 'LOPEZ'
    assert salario['Primer nombre empleado'] == 'ANA'
    assert salario['Otros nombres empleado'] == 'MARIA'
    assert cesantias['Cesantias e ints, efectivamente pagadas'] == 3000.0
    assert pension['Aportes obligatorios pension, FSP'] == 900.0
