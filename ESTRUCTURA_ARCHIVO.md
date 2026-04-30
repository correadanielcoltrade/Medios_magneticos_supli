# 📄 Estructura del Archivo de Balance

## Requisitos Generales

El archivo debe cumplir con estos requisitos:

✅ **Formato**: `.xlsx` (Excel)
✅ **Nombre**: Debe contener la palabra "balance"
✅ **Columnas**: Mínimo 7 columnas
✅ **Datos**: Valores numéricos en las columnas de débito/crédito

---

## Estructura Exacta

Tu archivo debe tener esta estructura con **7 columnas**:

### Encabezados (Fila 1)
| Col 1 | Col 2 | Col 3 | Col 4 | Col 5 | Col 6 | Col 7 |
|-------|-------|-------|-------|-------|-------|-------|
| **Descripción de Cuenta** | **Balance Inicial Débito** | **Balance Inicial Crédito** | **Movimiento Año Débito** | **Movimiento Año Crédito** | **Balance Final Débito** | **Balance Final Crédito** |

### Datos (Filas 2+)

```
110200 Bancos                        | 5000    |         | 2000    |         | 7000    |
210100 Cuentas por Pagar            |         | 3000    |         | 1000    |         | 4000
220100 Pasivo Corriente             |         | 2000    |         | 500     |         | 2500
510100 Gastos de Personal           | 1000    |         | 500     |         | 1500    |
2365 Retención por Pagar            |         | 100     |         | 50      |         | 150
2366 Retención IVA                  |         | 200     |         | 100     |         | 300
```

---

## Explicación de Columnas

### Columna 1: Descripción de Cuenta
- Contiene el código contable seguido de la descripción
- Ejemplo: `110200 Bancos`
- El código se extrae automáticamente para el mapeo

### Columnas 2-3: Balance Inicial
- **Columna 2**: Saldo inicial (lado débito)
- **Columna 3**: Saldo inicial (lado crédito)
- Valores numéricos separados por débito/crédito

### Columnas 4-5: Movimiento del Año
- **Columna 4**: Movimientos débito durante el año
- **Columna 5**: Movimientos crédito durante el año

### Columnas 6-7: Balance Final
- **Columna 6**: Saldo final (lado débito)
- **Columna 7**: Saldo final (lado crédito)

---

## Mapeo de Códigos de Cuenta por Formato

La aplicación mapea automáticamente los códigos de cuenta a cada formato:

### Formato 1001 - Retenciones
- **Códigos**: 2365, 2366, 2x (Pasivo corriente)
- Busca estas cuentas en tu balance

### Formato 1005 - IVA Descontable
- **Códigos**: 24050x
- Busca cuentas que empiezan con 24050

### Formato 1006 - IVA Generado
- **Códigos**: 24051x
- Busca cuentas que empiezan con 24051

### Formato 1007 - Ingresos
- **Códigos**: 4xxx
- Busca todas las cuentas de ingresos (4)

### Formato 1008 - Cuentas por Cobrar
- **Códigos**: 1205
- Busca esta cuenta específica

### Formato 1009 - Cuentas por Pagar
- **Códigos**: 2x (excepto corriente)
- Busca cuentas de pasivo

### Formato 2276 - Nómina
- **Códigos**: 5105x, 5205x
- Busca cuentas que empiezan con 5105 o 5205

---

## Ejemplo Completo

Aquí hay un ejemplo de un archivo válido:

```
Cuenta                          | BI Débito | BI Crédito | Mov D | Mov C | BF Débito | BF Crédito
110200 Bancos                  | 10000     |            | 5000  |       | 15000     |
110300 Caja                     | 2000      |            | 1000  |       | 3000      |
120100 Clientes                 | 8000      |            | 2000  |       | 10000     |
130100 Inventario              | 5000      |            | -1000 |       | 4000      |
210100 Proveedores             |           | 3000       |       | 1000  |           | 4000
220100 Cuentas Corrientes      |           | 2000       |       | 500   |           | 2500
230100 Impuestos por Pagar     |           | 1000       |       | 500   |           | 1500
2365 Retención por Pagar       |           | 500        |       | 250   |           | 750
2366 Retención IVA             |           | 300        |       | 150   |           | 450
310100 Capital Social          |           | 10000      |       |       |           | 10000
410100 Ingresos Operacionales  |           | 20000      |       | 5000  |           | 25000
510100 Gastos Personales       | 3000      |            | 1000  |       | 4000      |
510200 Gastos Administración   | 2000      |            | 500   |       | 2500      |
```

---

## Validaciones Automáticas

La aplicación valida automáticamente:

✅ El archivo es `.xlsx`
✅ El nombre contiene "balance"
✅ Hay al menos 7 columnas
✅ Las columnas de valores tienen datos numéricos
✅ No hay filas vacías que causen errores

Si alguna validación falla, verás un mensaje de error indicando el problema.

---

## Preparar tu Archivo

### Si tu archivo tiene otro nombre:
1. Renómbralo a algo como: `balance_de_sumas_y_saldos.xlsx`

### Si tu archivo tiene otra estructura:
1. Reorganiza las columnas en este orden:
   1. Descripción de Cuenta
   2. Balance Inicial Débito
   3. Balance Inicial Crédito
   4. Movimiento Débito
   5. Movimiento Crédito
   6. Balance Final Débito
   7. Balance Final Crédito

### Si tu archivo tiene más columnas:
Las columnas adicionales se ignorarán automáticamente.

### Si tu archivo tiene menos columnas:
Agrégalas y rellena con valores como corresponda.

---

## Tips

💡 **Usa formato de número**: Asegúrate de que los valores estén en formato de número (no texto)
💡 **Sin moneda**: No incluyas símbolos de moneda ($ €) en las celdas
💡 **Sin fórmulas**: Usa valores diretos, no fórmulas
💡 **Limpio**: Elimina filas y columnas vacías innecesarias
💡 **Respaldo**: Guarda un respaldo de tu archivo original

---

Para más información, consulta el README.md.
