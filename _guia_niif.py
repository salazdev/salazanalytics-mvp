"""
_guia_niif.py — SalazAnalytics
Módulo: 📚 Guía NIIF Pymes
35 secciones explicadas en español colombiano con ejemplos prácticos,
preguntas frecuentes y errores comunes.
"""
import streamlit as st

# ── Paleta ─────────────────────────────────────────────────────────────────
BG_DARK  = "#0D1B2A"; BG_CARD = "#132030"; BORDER = "#1a3a5c"
TEXT_SEC = "#7B9BB5"; ACCENT  = "#00C2FF"; DANGER = "#FF6B6B"
SUCCESS  = "#00FFB3"; WARN    = "#FFD93D"; PURPLE = "#7B2FBE"

# ── Base de conocimiento NIIF para Pymes ───────────────────────────────────
# Cada sección: (número, título, categoría, emoji_cat, resumen, ejemplo_col, preguntas, errores)
SECCIONES = [
    {
        "num": 1, "titulo": "Pequeñas y Medianas Entidades",
        "cat": "Principios y Políticas", "emoji": "📋",
        "resumen": "Define quiénes pueden usar la NIIF para Pymes: empresas que no tienen obligación pública de rendir cuentas y publican estados financieros de propósito general para usuarios externos (socios, bancos, proveedores).",
        "ejemplo": "Una SAS en Medellín con 20 empleados que necesita presentar estados financieros al banco para un crédito de expansión. No cotiza en bolsa ni capta dinero del público, por lo tanto aplica esta norma.",
        "preguntas": [
            ("¿Mi empresa puede usar NIIF para Pymes?", "Sí, si no tiene obligación pública de rendir cuentas. Eso significa que no cotiza en bolsa ni capta ahorros del público (como bancos o seguros). La mayoría de Pymes colombianas califican."),
            ("¿Qué diferencia hay con las NIIF completas?", "Las NIIF para Pymes son más simples: menos revelaciones, opciones contables reducidas y sin algunos temas complejos como instrumentos financieros avanzados. Están diseñadas para empresas medianas con recursos contables limitados."),
        ],
        "errores": ["Aplicar NIIF completas cuando no se está obligado, generando costos innecesarios.", "Confundir Grupo 2 (NIIF Pymes) con Grupo 3 (Contabilidad Simplificada) y mezclar criterios de ambos marcos."],
    },
    {
        "num": 2, "titulo": "Conceptos y Principios Generales",
        "cat": "Principios y Políticas", "emoji": "📋",
        "resumen": "Establece los pilares de la contabilidad bajo NIIF: imagen fiel, negocio en marcha, base de acumulación (causación), materialidad, prudencia y comparabilidad. Define activos, pasivos, patrimonio, ingresos y gastos.",
        "ejemplo": "Una ferretería en Bogotá que antes registraba las ventas cuando recibía el dinero (base caja). Bajo NIIF debe registrarlas cuando entrega la mercancía al cliente, aunque el pago sea a 30 días (base causación).",
        "preguntas": [
            ("¿Qué es la base de causación?", "Significa registrar los hechos económicos cuando ocurren, no cuando se cobra o paga el dinero. Si vendes hoy pero cobras en 30 días, el ingreso va al estado de resultados hoy."),
            ("¿Qué es materialidad?", "Un hecho es material si su omisión o error podría influir en las decisiones de los usuarios. No vale la pena revelar detalles sin importancia económica, pero todo lo significativo debe estar en los estados financieros."),
        ],
        "errores": ["Mezclar base caja con base causación en el mismo período.", "Omitir revelaciones 'porque son pequeñas' sin evaluar si realmente son inmateriales."],
    },
    {
        "num": 3, "titulo": "Presentación de Estados Financieros",
        "cat": "📊 Estados Financieros", "emoji": "📊",
        "resumen": "Define el conjunto completo de estados financieros requeridos: Estado de Situación Financiera, Estado de Resultado Integral, Estado de Cambios en Patrimonio, Estado de Flujos de Efectivo y Notas. Todos deben presentarse con un período comparativo.",
        "ejemplo": "Una empresa de servicios en Cali que presenta sus estados financieros al 31 de diciembre de 2024 debe incluir también las cifras del 31 de diciembre de 2023 para que los socios puedan comparar la evolución del negocio.",
        "preguntas": [
            ("¿Cada cuánto debo presentar estados financieros?", "Mínimo una vez al año. Muchas empresas también preparan estados intermedios (trimestral o semestral) para gestión interna o requerimientos de entidades financieras."),
            ("¿Es obligatorio el período comparativo?", "Sí. La NIIF para Pymes exige presentar el período actual y el anterior para todos los estados financieros y sus notas."),
        ],
        "errores": ["Presentar solo el año actual sin comparativo.", "No incluir todas las notas requeridas pensando que solo aplican para empresas grandes."],
    },
    {
        "num": 4, "titulo": "Estado de Situación Financiera",
        "cat": "📊 Estados Financieros", "emoji": "📊",
        "resumen": "Regula el balance general bajo NIIF. Define qué es un activo (recurso controlado con beneficios futuros esperados), un pasivo (obligación presente) y el patrimonio (diferencia entre activos y pasivos). Establece la clasificación entre corriente y no corriente.",
        "ejemplo": "Una empresa de manufactura en Barranquilla lista su bodega ($800M) y maquinaria ($300M) como activos no corrientes. Las cuentas por cobrar a clientes a 60 días ($120M) van como activo corriente. El préstamo bancario a 5 años se divide: la cuota del próximo año es pasivo corriente, el resto es pasivo no corriente.",
        "preguntas": [
            ("¿Cómo clasifico un activo como corriente?", "Es corriente si esperas realizarlo (venderlo, usarlo, cobrarlo) dentro de los próximos 12 meses o dentro del ciclo normal de operación del negocio. Todo lo demás es no corriente."),
            ("¿El efectivo en cuentas de ahorro es activo corriente?", "Sí, siempre. El efectivo y equivalentes de efectivo siempre van como activo corriente, independientemente del plazo de los depósitos."),
        ],
        "errores": ["Clasificar una deuda a largo plazo toda como no corriente cuando tiene cuotas que vencen en los próximos 12 meses.", "No segregar la porción corriente de créditos hipotecarios o leasing."],
    },
    {
        "num": 5, "titulo": "Estado de Resultado Integral",
        "cat": "📊 Estados Financieros", "emoji": "📊",
        "resumen": "Regula cómo presentar los ingresos, costos y gastos del período para mostrar la utilidad o pérdida. Incluye el resultado del período más los 'otros resultados integrales' (ORI), como ajustes por revaluación de activos.",
        "ejemplo": "Una empresa exportadora en Pereira tiene una utilidad operacional de $50M, pero por la tasa de cambio sus inversiones en dólares generaron una ganancia no realizada de $8M. La utilidad neta va en el P&G; los $8M de la tasa de cambio van en ORI del patrimonio.",
        "preguntas": [
            ("¿Qué va en 'Otros Resultados Integrales'?", "Ganancias o pérdidas que no se incluyen en la utilidad del período, como diferencias por conversión de moneda extranjera, ganancias actuariales en planes de pensiones y revaluaciones de PPE si se usa ese modelo."),
            ("¿Puedo presentar un solo estado combinado?", "Sí. Puedes presentar un solo Estado de Resultado Integral que combine el P&G y los ORI, o hacerlo en dos estados separados. Ambas opciones son válidas."),
        ],
        "errores": ["Incluir partidas de ORI directamente en la utilidad del período.", "No presentar el impuesto diferido relacionado con las partidas de ORI."],
    },
    {
        "num": 6, "titulo": "Estado de Cambios en Patrimonio",
        "cat": "📊 Estados Financieros", "emoji": "📊",
        "resumen": "Muestra todos los movimientos del patrimonio durante el período: utilidades, pérdidas, dividendos decretados, aportes de capital, recompra de acciones y correcciones de errores de períodos anteriores.",
        "ejemplo": "Una SAS en Bucaramanga tenía patrimonio de $400M al inicio. Tuvo utilidad de $80M, decretó dividendos de $30M y los socios aportaron $50M de capital nuevo. El estado de cambios muestra cómo llegó a $500M al final del año.",
        "preguntas": [
            ("¿Los dividendos reducen el patrimonio?", "Sí. Cuando se decretan dividendos, se registra un pasivo (dividendos por pagar) y se reduce el patrimonio (reservas o utilidades acumuladas). El pago posterior extingue el pasivo."),
            ("¿Las correcciones de errores van en el estado de resultados?", "No. Los errores de períodos anteriores se corrigen contra las utilidades acumuladas del patrimonio (ajuste retroactivo), no por resultados del período actual."),
        ],
        "errores": ["Pasar correcciones de errores por el P&G en lugar de ajustar directamente el patrimonio.", "No revelar el motivo y cuantía de cada movimiento patrimonial en las notas."],
    },
    {
        "num": 7, "titulo": "Estado de Flujos de Efectivo",
        "cat": "📊 Estados Financieros", "emoji": "📊",
        "resumen": "Muestra cómo se generó y usó el efectivo en tres actividades: operación (el giro normal del negocio), inversión (compra/venta de activos de largo plazo) y financiación (préstamos, aportes de capital, dividendos). Puede prepararse por método directo o indirecto.",
        "ejemplo": "Una empresa distribuidora en Bogotá tuvo utilidad de $60M pero su caja bajó $20M. El flujo de efectivo explica por qué: las cuentas por cobrar crecieron $50M (los clientes no han pagado) y se compró un camión de reparto por $30M. Esto es información vital que el P&G no muestra.",
        "preguntas": [
            ("¿Método directo o indirecto?", "Ambos son válidos. El indirecto (parte de la utilidad y hace ajustes) es más común porque usa datos ya disponibles. El directo (detalla cobros y pagos reales) es más transparente pero requiere más trabajo. SalazAnalytics tiene un módulo de Flujo Indirecto para calcularlo automáticamente."),
            ("¿Los intereses pagados van en operación o financiación?", "Bajo NIIF para Pymes, los intereses pagados generalmente van en actividades de operación. Pero hay flexibilidad para clasificarlos en financiación si la empresa lo aplica de manera consistente."),
        ],
        "errores": ["Confundir utilidad con flujo de caja — una empresa puede tener utilidad y quedarse sin efectivo.", "No revelar transacciones no monetarias significativas (como compra de activos con deuda directa)."],
    },
    {
        "num": 8, "titulo": "Notas a los Estados Financieros",
        "cat": "📊 Estados Financieros", "emoji": "📊",
        "resumen": "Las notas son parte integral de los estados financieros. Explican las políticas contables usadas, detallan las cifras del balance y P&G, y revelan información que no cabe en los estados principales pero es esencial para entender la situación financiera.",
        "ejemplo": "La empresa registra en el balance 'Propiedades $500M'. La nota 8 detalla: bodega en Cali ($300M, vida útil 40 años, depreciación acumulada $75M), vehículos ($200M, vida útil 5 años, depreciación acumulada $120M). Sin las notas, el balance es incompleto.",
        "preguntas": [
            ("¿Cuáles notas son obligatorias?", "Las principales son: políticas contables, estimaciones y juicios relevantes, desglose de cada línea del balance y P&G, partes relacionadas, contingencias, compromisos y hechos posteriores al cierre."),
            ("¿Las notas deben ir en orden específico?", "La norma sugiere: primero declaración de cumplimiento con NIIF Pymes, luego resumen de políticas contables, luego notas de soporte a las cifras, y al final otra información (contingencias, partes relacionadas, etc.)."),
        ],
        "errores": ["Presentar notas genéricas copiadas de otras empresas sin adaptar a la realidad propia.", "Omitir la nota de partes relacionadas creyendo que no aplica a empresas familiares — precisamente aplica más en esos casos."],
    },
    {
        "num": 10, "titulo": "Políticas Contables, Estimaciones y Errores",
        "cat": "Principios y Políticas", "emoji": "📋",
        "resumen": "Define cómo seleccionar y aplicar políticas contables, cómo manejar cambios en políticas y estimaciones, y cómo corregir errores de períodos anteriores. Los cambios de política se aplican retroactivamente; los errores se corrigen en patrimonio.",
        "ejemplo": "Una empresa siempre depreció sus vehículos a 5 años. Ahora decide cambiar a 4 años porque la flota se desgasta más rápido. Este es un cambio de estimación (prospectivo: aplica desde ahora). Si en cambio descubren que en 2022 no registraron una factura de $50M, eso es un error y debe corregirse contra utilidades acumuladas.",
        "preguntas": [
            ("¿Diferencia entre cambio de política y cambio de estimación?", "Cambio de política: cambia la manera de contabilizar (ej: de costo a valor razonable). Se aplica retroactivamente. Cambio de estimación: cambia un supuesto técnico (ej: vida útil). Se aplica hacia adelante desde el período del cambio."),
            ("¿Cómo corrijo un error de un año anterior?", "Se ajusta el saldo de apertura de las utilidades acumuladas del período más antiguo presentado. Si el error afecta 2022 y estoy presentando 2023-2024, corrijo el patrimonio inicial de 2023 y re-expreso las cifras comparativas."),
        ],
        "errores": ["Tratar un cambio de estimación como cambio de política y re-expresar años anteriores innecesariamente.", "Pasar la corrección de errores materiales por el P&G del año actual en lugar de ajustar el patrimonio."],
    },
    {
        "num": 11, "titulo": "Instrumentos Financieros Básicos",
        "cat": "💳 Instrumentos Financieros", "emoji": "💳",
        "resumen": "Regula los activos y pasivos financieros simples: efectivo, cuentas por cobrar y pagar, préstamos, inversiones en bonos. Se miden inicialmente al precio de la transacción y posteriormente al costo amortizado. Incluye el modelo de deterioro (provisión de cartera).",
        "ejemplo": "Una empresa vende $100M a crédito a 90 días. Al cierre del trimestre, analiza la cartera y determina que $8M tienen alta probabilidad de no cobrarse (cliente con problemas de flujo). Registra una provisión de $8M que va al gasto del período. Esto es el deterioro bajo la Sección 11.",
        "preguntas": [
            ("¿Cómo calculo la provisión de cartera bajo NIIF?", "Bajo NIIF Pymes se usa el modelo de 'pérdidas crediticias incurridas': se provisiona cuando hay evidencia objetiva de deterioro (mora, problemas financieros del cliente, reestructuración). Se puede usar una matriz de provisión por antigüedad de cartera calibrada con experiencia histórica."),
            ("¿El CDT de mi empresa va en instrumentos financieros?", "Sí. Un CDT es un instrumento financiero básico medido al costo amortizado (valor inicial + intereses causados). Los intereses se reconocen en el P&G a medida que se causan, aunque no se hayan recibido aún."),
        ],
        "errores": ["Provisionar cartera solo para efectos fiscales (33% de la cartera mayor a 1 año) sin un análisis real de recuperabilidad bajo NIIF.", "No reconocer los intereses de CDTs y bonos sobre base de causación."],
    },
    {
        "num": 12, "titulo": "Otros Instrumentos Financieros",
        "cat": "💳 Instrumentos Financieros", "emoji": "💳",
        "resumen": "Aplica a instrumentos financieros más complejos que no cubre la Sección 11: derivados, inversiones en acciones cotizadas, contratos de opciones. Se miden generalmente a valor razonable con cambios en resultados.",
        "ejemplo": "Una empresa importadora en Bogotá compra dólares a futuro (forward) para cubrirse del riesgo cambiario. Este contrato de cobertura es un instrumento financiero de la Sección 12 que debe registrarse a su valor de mercado al cierre.",
        "preguntas": [
            ("¿Mi empresa de servicios tiene que aplicar la Sección 12?", "Probablemente no. La mayoría de Pymes solo tienen instrumentos básicos (cartera, préstamos, inversiones en CDTs) que caen en la Sección 11. La Sección 12 aplica si tienes derivados, coberturas o inversiones en instrumentos de capital con cotización pública."),
            ("¿Las acciones de otra empresa van en Sección 11 o 12?", "Depende. Si son acciones sin cotización pública (ej: participación en una empresa familiar) van a Sección 11. Si cotizan en bolsa, van a Sección 12 a valor razonable."),
        ],
        "errores": ["Medir acciones cotizadas al costo histórico en lugar de valor de mercado.", "Ignorar los contratos forward o swaps de tasas de interés sin registrarlos a valor razonable."],
    },
    {
        "num": 13, "titulo": "Inventarios",
        "cat": "🏭 Activos", "emoji": "🏭",
        "resumen": "Regula cómo medir y presentar las existencias: materias primas, productos en proceso y productos terminados. Se miden al costo (incluye compra + transformación + traer al lugar y condición actual) o al Valor Neto Realizable (VNR), el que sea menor.",
        "ejemplo": "Una distribuidora de electrodomésticos tiene neveras que compró a $1.2M cada una. Al cierre del año, ese modelo fue descontinuado y solo las puede vender a $900,000 neto (precio $950,000 menos costo de venta $50,000). Debe rebajar el inventario a $900,000 y registrar $300,000 de gasto por deterioro por unidad.",
        "preguntas": [
            ("¿FIFO o Promedio Ponderado?", "La NIIF para Pymes permite FIFO (primeras entradas, primeras salidas) o Promedio Ponderado. No permite LIFO (últimas entradas, primeras salidas). La elección debe aplicarse consistentemente para inventarios de similar naturaleza."),
            ("¿Qué costos incluyo en el inventario?", "El costo de adquisición incluye precio de compra + aranceles + fletes + seguros + todos los costos para poner la mercancía en condición de venta. No incluye gastos administrativos, costos de almacenamiento post-producción ni pérdidas de producción anormales."),
        ],
        "errores": ["Incluir gastos administrativos o financieros en el costo del inventario.", "No evaluar el VNR al cierre del período y mantener inventario obsoleto o deteriorado a costo."],
    },
    {
        "num": 16, "titulo": "Propiedades de Inversión",
        "cat": "🏭 Activos", "emoji": "🏭",
        "resumen": "Aplica a inmuebles (terrenos o edificios) que se tienen para arrendar a terceros o para obtener valorización, no para uso propio del negocio ni para venta en el giro ordinario. Se pueden medir al costo o al valor razonable.",
        "ejemplo": "Una empresa de transporte en Bogotá compró una bodega que arrienda a otra empresa. Esa bodega es una Propiedad de Inversión (no PPE), porque genera ingresos por arrendamiento. Si decide usar el modelo de valor razonable, debe actualizarla al precio de mercado cada año.",
        "preguntas": [
            ("¿Cómo sé si un inmueble es PPE o Propiedad de Inversión?", "Si lo usa tu empresa para producir bienes, prestar servicios o fines administrativos: es PPE (Sección 17). Si lo tienes para arrendarlo a terceros o para que se valorice: es Propiedad de Inversión (Sección 16). Si usas parte y arriendas parte, se separan los componentes."),
            ("¿El valor razonable de un inmueble requiere avalúo?", "No necesariamente un avalúo formal, pero sí una estimación fiable del precio de mercado. Muchas empresas usan avalúos de lonjas de propiedad raíz o referencias de mercado inmobiliario cada 1-3 años."),
        ],
        "errores": ["Depreciar Propiedades de Inversión medidas a valor razonable (si usas ese modelo, no se deprecian — los cambios van al P&G).", "No separar la porción del inmueble usada por la empresa (PPE) de la porción arrendada (Propiedad de Inversión)."],
    },
    {
        "num": 17, "titulo": "Propiedades, Planta y Equipo",
        "cat": "🏭 Activos", "emoji": "🏭",
        "resumen": "Regula el registro de activos físicos usados en la operación: terrenos, bodegas, maquinaria, vehículos, equipos de cómputo. Define qué costos se capitalizan, cómo depreciar y cuándo dar de baja. El modelo base es costo menos depreciación acumulada.",
        "ejemplo": "Una empresa comercializadora compra una bodega por $500M. Paga además $15M de escrituración, $8M de impuesto de registro y gasta $30M en adecuaciones para adaptarla a su operación. Costo total a capitalizar: $553M. La bodega tiene vida útil estimada de 40 años (sin terreno); la depreciación anual en línea recta es $553M ÷ 40 = $13.8M.",
        "preguntas": [
            ("¿Qué costos puedo sumar al valor de la bodega?", "Precio de compra + impuestos no recuperables (escrituración, registro) + costos directos para poner el activo en condición de uso (adecuaciones iniciales, instalación). No incluye: costos de capacitación del personal, gastos administrativos ni pérdidas iniciales de operación."),
            ("¿Cómo determino la vida útil?", "Es una estimación basada en: uso esperado del activo, desgaste físico esperado, obsolescencia técnica, límites legales o contractuales. No tiene que ser la vida útil fiscal. Una bodega puede tener vida útil contable de 40 años aunque fiscalmente se deprecie en 20."),
            ("¿Qué pasa si la bodega se desvaloriza?", "Debes evaluar indicadores de deterioro: caída del valor de mercado, cambios adversos en el entorno del negocio, daño físico. Si el valor recuperable es menor al valor en libros, registras una pérdida por deterioro (Sección 27) que va al gasto del período."),
            ("¿Puedo revaluar mis activos?", "Sí. La NIIF para Pymes permite el modelo de revaluación como alternativa al costo. Si revalúas, debes hacerlo con suficiente regularidad para que el valor en libros no difiera significativamente del valor razonable, y aplicar el mismo modelo a toda la clase de activo."),
        ],
        "errores": ["Capitalizar gastos de mantenimiento rutinario que deben ir al gasto del período.", "No separar terreno (no se deprecia) de construcción (sí se deprecia) cuando se compran juntos.", "Usar las tasas de depreciación fiscal en lugar de estimar la vida útil real del activo."],
    },
    {
        "num": 18, "titulo": "Activos Intangibles",
        "cat": "🏭 Activos", "emoji": "🏭",
        "resumen": "Regula activos no físicos identificables con vida útil definida: software, licencias, patentes, marcas adquiridas, listas de clientes. Deben ser identificables, controlados por la empresa y generadores de beneficios económicos futuros. Los intangibles generados internamente (como una marca propia) generalmente no se capitalizan.",
        "ejemplo": "Una empresa de tecnología en Medellín compra una licencia de software ERP por $80M con vigencia de 5 años. Es un intangible de vida útil definida que se amortiza linealmente: $16M por año. El logo y la marca que ellos mismos desarrollaron NO se capitaliza bajo NIIF Pymes.",
        "preguntas": [
            ("¿Puedo activar los gastos de desarrollo de mi propio software?", "Bajo NIIF para Pymes: no. La norma prohíbe capitalizar intangibles generados internamente (investigación, desarrollo propio, marcas, listas de clientes generadas internamente). Todo va a gasto. Bajo NIIF completas sí hay opciones para capitalizar la fase de desarrollo."),
            ("¿La plusvalía pagada en una compra de empresa es un intangible?", "La plusvalía (goodwill) tiene su propia sección (Sección 19). Es el exceso del precio pagado sobre el valor razonable de los activos netos adquiridos. Se amortiza en máximo 10 años si no se puede estimar la vida útil con fiabilidad."),
        ],
        "errores": ["Capitalizar gastos de publicidad o investigación de mercados como intangibles.", "No amortizar intangibles de vida útil definida argumentando que 'mantienen su valor'."],
    },
    {
        "num": 20, "titulo": "Arrendamientos",
        "cat": "🔄 Arrendamientos", "emoji": "🔄",
        "resumen": "Clasifica los arrendamientos en operativos (el arrendador retiene los riesgos y beneficios del activo — el arrendatario solo gasta) y financieros (el arrendatario asume sustancialmente todos los riesgos y beneficios — debe registrar el activo y el pasivo). La clasificación depende del fondo económico, no de la forma legal.",
        "ejemplo": "Empresa A arrienda una oficina por $5M/mes, contrato a 2 años renovable. Es arrendamiento operativo: registra $5M de gasto mensual. Empresa B toma en leasing un camión por 5 años (vida útil del camión: 5 años) con opción de compra por $1. Es arrendamiento financiero: registra el camión como activo y la deuda como pasivo.",
        "preguntas": [
            ("¿Cómo sé si mi leasing es operativo o financiero?", "Indicadores de arrendamiento financiero: el plazo cubre la mayor parte de la vida útil del activo, hay opción de compra a precio favorable, la propiedad pasa al arrendatario al final, el arrendatario puede cancelar y asume las pérdidas del arrendador, los activos son especializados para el arrendatario."),
            ("¿El arrendamiento de oficinas siempre es operativo?", "Bajo NIIF para Pymes, generalmente sí si el contrato es a corto plazo y el arrendador conserva el inmueble al final. A diferencia de NIIF 16 (NIIF completas), la NIIF para Pymes mantiene la distinción operativo/financiero y no obliga a activar todos los arrendamientos."),
        ],
        "errores": ["Clasificar un leasing financiero como operativo para no registrar el activo y el pasivo, 'mejorando' artificialmente el balance.", "No revelar en notas los pagos mínimos futuros de arrendamientos operativos significativos."],
    },
    {
        "num": 21, "titulo": "Provisiones y Contingencias",
        "cat": "👥 Pasivos y Empleados", "emoji": "👥",
        "resumen": "Una provisión se reconoce cuando existe una obligación presente (legal o implícita) resultado de un evento pasado, es probable que se requiera salida de recursos y puede estimarse confiablemente. Las contingencias pasivas probables se provisionen; las posibles solo se revelan en notas.",
        "ejemplo": "Una empresa de construcción en Bogotá tiene una demanda laboral de $200M. Su abogado estima 70% de probabilidad de perder. Debe registrar una provisión de $200M × 70% = $140M (o el mejor estimado). Si la probabilidad fuera 20%, solo lo revela en notas sin registrar contablemente.",
        "preguntas": [
            ("¿La garantía de productos es una provisión?", "Sí. Si vendes productos con garantía, al momento de la venta ya tienes una obligación implícita de cubrir posibles fallas. Debes estimar el costo esperado de garantías y registrar la provisión. El gasto va en el mismo período que la venta."),
            ("¿Una demanda laboral siempre se provisiona?", "No siempre. Solo cuando la probabilidad de perder es 'probable' (generalmente más del 50%). El criterio no es fiscal sino económico. Debes obtener el concepto del abogado responsable del caso para soportar la decisión."),
        ],
        "errores": ["No reconocer provisiones por garantías, litigios o reestructuraciones que cumplen los criterios de reconocimiento.", "Reconocer 'provisiones' por gastos futuros de operación normal, lo cual no está permitido — solo se provisionan obligaciones presentes."],
    },
    {
        "num": 23, "titulo": "Ingresos de Actividades Ordinarias",
        "cat": "💰 Ingresos y Gastos", "emoji": "💰",
        "resumen": "Regula cuándo y por cuánto reconocer los ingresos por venta de bienes, prestación de servicios, intereses, regalías y dividendos. El principio central: reconocer el ingreso cuando es probable que los beneficios económicos fluyan a la empresa y el importe puede medirse confiablemente.",
        "ejemplo": "Una constructora vende un apartamento en planos por $300M. Recibe anticipo de $60M hoy. No puede reconocer $300M como ingreso al firmar la promesa. El ingreso se reconoce cuando transfiere los riesgos y beneficios significativos al comprador (generalmente en la escrituración y entrega del inmueble).",
        "preguntas": [
            ("¿Cuándo reconozco el ingreso por venta de mercancía?", "Cuando se transfieren al comprador los riesgos y beneficios significativos de la propiedad. En la mayoría de ventas al detal esto ocurre al momento de la entrega física. En ventas a crédito, el ingreso va cuando se entrega la mercancía, no cuando se cobra."),
            ("¿Cómo registro un contrato de servicios a largo plazo?", "Se usa el método del porcentaje de terminación: reconoces ingresos proporcionalmente al avance del servicio. Si el proyecto es de $100M y está 60% terminado, reconoces $60M de ingresos aunque no hayas facturado todo."),
        ],
        "errores": ["Reconocer ingresos al momento del cobro (base caja) en lugar de la entrega del bien o servicio.", "Registrar los anticipos de clientes como ingresos — son un pasivo (ingreso diferido) hasta que se preste el servicio o entregue el bien."],
    },
    {
        "num": 25, "titulo": "Costos por Préstamos",
        "cat": "💰 Ingresos y Gastos", "emoji": "💰",
        "resumen": "Los costos por préstamos (intereses y otros costos financieros) se reconocen como gasto en el período en que se incurren. La NIIF para Pymes no permite capitalizar intereses en activos en construcción (a diferencia de las NIIF completas que sí lo permiten).",
        "ejemplo": "Una empresa financia la construcción de su planta con un crédito bancario. Los intereses que paga durante la construcción ($30M) van al gasto financiero del período, NO se suman al costo de la planta. Esto es diferente a las NIIF completas donde sí se pueden capitalizar.",
        "preguntas": [
            ("¿Puedo capitalizar los intereses de un préstamo para construir una bodega?", "No bajo NIIF para Pymes. Todos los costos por préstamos van al gasto financiero del período. Este es un punto de diferencia importante con las NIIF completas."),
            ("¿Los gastos bancarios van en costos por préstamos?", "Las comisiones y gastos de estructuración de un crédito forman parte del costo amortizado del pasivo financiero (reducen el valor inicial del préstamo y se distribuyen como gasto financiero durante la vida del crédito mediante la tasa de interés efectiva)."),
        ],
        "errores": ["Capitalizar intereses en activos en construcción bajo NIIF Pymes — esto no está permitido.", "Registrar todas las comisiones bancarias como gasto inmediato en lugar de incluirlas en el costo amortizado del préstamo."],
    },
    {
        "num": 27, "titulo": "Deterioro del Valor de los Activos",
        "cat": "🏭 Activos", "emoji": "🏭",
        "resumen": "Al cierre de cada período, la empresa debe evaluar si hay indicios de que algún activo (PPE, intangibles, inventarios, cartera) pueda haber perdido valor. Si el valor recuperable es menor al valor en libros, se reconoce una pérdida por deterioro.",
        "ejemplo": "Una empresa de transporte tiene camiones con valor en libros de $400M. Por la crisis del sector, el valor de mercado bajó a $280M y el flujo futuro descontado de operación es $310M. El valor recuperable es el mayor: $310M. La pérdida por deterioro es $400M - $310M = $90M.",
        "preguntas": [
            ("¿Cuándo debo evaluar deterioro?", "Al menos una vez al año al cierre, y en cualquier momento en que existan indicios externos (caída del valor de mercado, cambios tecnológicos, cambios legales adversos) o internos (rendimiento peor de lo esperado, planes de abandono del activo) de deterioro."),
            ("¿Qué es el valor recuperable?", "El mayor entre: el valor razonable menos costos de venta (¿cuánto obtendrías vendiéndolo hoy?) y el valor en uso (el valor presente de los flujos futuros que generará el activo). Se usa el mayor porque representa la mejor alternativa económica."),
        ],
        "errores": ["No evaluar deterioro anualmente por considerar que los activos 'están bien'.", "Calcular el deterioro solo sobre el activo individual cuando debería evaluarse sobre la Unidad Generadora de Efectivo (UGE) cuando el activo no genera flujos de forma independiente."],
    },
    {
        "num": 28, "titulo": "Beneficios a los Empleados",
        "cat": "👥 Pasivos y Empleados", "emoji": "👥",
        "resumen": "Cubre todos los pagos relacionados con el trabajo: salarios, prestaciones sociales (cesantías, intereses, primas, vacaciones), seguridad social, bonificaciones y beneficios post-empleo como pensiones. Todos deben causarse en el período en que el empleado presta el servicio.",
        "ejemplo": "Una empresa en Colombia con 15 empleados debe causar mensualmente (aunque pague en otras fechas): cesantías (8.33% del salario), intereses sobre cesantías (1% mensual sobre el saldo), prima de servicios (8.33%), vacaciones (4.17%), aportes a seguridad social y parafiscales. SalazAnalytics tiene el Simulador de Nómina para estos cálculos.",
        "preguntas": [
            ("¿Las vacaciones pendientes son un pasivo?", "Sí. Los días de vacaciones que el empleado ha causado pero no ha disfrutado representan una obligación para la empresa. Deben reconocerse como pasivo y gasto a medida que el empleado los causa, no solo cuando se pagan."),
            ("¿Los planes de pensiones aplican en Colombia?", "El sistema pensional colombiano es mixto (RPM y RAIS). Las obligaciones con la AFP o Colpensiones se registran como seguridad social corriente. Solo si la empresa tiene planes complementarios de pensiones (beneficio definido) aplica la parte compleja de la Sección 28."),
        ],
        "errores": ["Registrar las prestaciones sociales solo cuando se pagan (enero cesantías, junio/diciembre prima) en lugar de causarlas mensualmente.", "No provisionar las vacaciones acumuladas de empleados con más de un año de antigüedad."],
    },
    {
        "num": 29, "titulo": "Impuesto a las Ganancias",
        "cat": "🧾 Impuesto", "emoji": "🧾",
        "resumen": "Regula el impuesto de renta corriente (la deuda tributaria del año) y el impuesto diferido (diferencias entre la base contable y la base fiscal de activos y pasivos). El impuesto diferido captura el efecto tributario futuro de las diferencias temporarias.",
        "ejemplo": "Una empresa tiene maquinaria con valor contable de $200M (deprecia en 10 años) pero valor fiscal de $120M (fiscalmente ya depreció más rápido). La diferencia de $80M generará más impuesto en el futuro cuando se realice. Eso es un Pasivo por Impuesto Diferido de $80M × 35% = $28M.",
        "preguntas": [
            ("¿Qué diferencia hay entre impuesto corriente y diferido?", "Corriente: lo que le debes a la DIAN este año (calculado sobre renta líquida fiscal). Diferido: el impuesto 'a futuro' por diferencias entre la contabilidad NIIF y la fiscalidad colombiana. Se puede ser activo (pagarás menos impuesto después) o pasivo (pagarás más)."),
            ("¿Siempre debo calcular impuesto diferido?", "Bajo NIIF para Pymes sí, aunque con simplificaciones. Para Grupo 3 (Contabilidad Simplificada) no aplica. Las diferencias más comunes en Colombia: depreciación contable vs fiscal, provisiones no deducibles, ingresos diferidos."),
        ],
        "errores": ["Registrar como gasto de impuesto solo el valor de la declaración de renta sin calcular el diferido.", "Reconocer activos por impuesto diferido sobre pérdidas fiscales sin evaluar si es probable que haya utilidades futuras suficientes para aprovecharlas."],
    },
    {
        "num": 32, "titulo": "Hechos Posteriores al Cierre",
        "cat": "Principios y Políticas", "emoji": "📋",
        "resumen": "Eventos que ocurren entre la fecha de cierre del período y la fecha de autorización para publicación de los estados financieros. Los que confirman condiciones existentes al cierre ajustan las cifras; los que revelan condiciones nuevas solo se revelan en notas.",
        "ejemplo": "Cierre 31-dic-2024. En febrero-2025 (antes de firmar los estados): (A) el cliente principal declara quiebra — ajusta la provisión de cartera porque la condición existía al cierre. (B) Se incendia la bodega — solo se revela en notas porque es una condición nueva posterior al cierre.",
        "preguntas": [
            ("¿Hasta cuándo analizo hechos posteriores?", "Hasta la fecha en que la junta directiva o gerencia autoriza formalmente la publicación de los estados financieros. Esta fecha debe revelarse en las notas."),
            ("¿Los dividendos decretados después del cierre ajustan el balance?", "No. Los dividendos declarados después del cierre son un hecho posterior no ajustable — se revelan en notas pero no se registran como pasivo en los estados financieros del período cerrado."),
        ],
        "errores": ["Registrar como pasivo al cierre los dividendos decretados en la asamblea de marzo para los estados de diciembre.", "No revelar en notas un hecho material posterior no ajustable como una adquisición importante o una demanda nueva."],
    },
    {
        "num": 33, "titulo": "Partes Relacionadas",
        "cat": "Principios y Políticas", "emoji": "📋",
        "resumen": "Requiere revelar las transacciones con personas o entidades relacionadas: socios, directivos, familiares de estos, subsidiarias, asociadas y entidades bajo control común. La información es crítica para que los usuarios identifiquen transacciones que pueden no ser en condiciones de mercado.",
        "ejemplo": "Una SAS le arrienda la bodega a su socio mayoritario por $2M/mes cuando el mercado paga $8M/mes. Esto es una transacción con parte relacionada que debe revelarse en notas con: nombre de la parte relacionada, naturaleza de la relación, monto de la transacción y saldo pendiente.",
        "preguntas": [
            ("¿Mi empresa familiar tiene partes relacionadas?", "Casi seguro que sí. Los socios, su cónyuge, hijos, padres, y las empresas donde estos tienen participación son partes relacionadas. Las transacciones con ellos (préstamos, arriendos, ventas, servicios) deben revelarse en notas."),
            ("¿Los salarios de los directivos son partes relacionadas?", "Sí. La compensación total de los directivos clave (gerente, junta directiva) debe revelarse en notas como información de partes relacionadas. Incluye salarios, bonificaciones, beneficios en especie y cualquier otro pago."),
        ],
        "errores": ["Omitir la nota de partes relacionadas en estados financieros de empresas familiares.", "No revelar los préstamos de la empresa a socios o de socios a la empresa, que son transacciones con partes relacionadas muy comunes en Pymes colombianas."],
    },
    {
        "num": 35, "titulo": "Transición a la NIIF para las Pymes",
        "cat": "Principios y Políticas", "emoji": "📋",
        "resumen": "Establece el procedimiento para la primera vez que una empresa aplica la NIIF para Pymes: identificar la fecha de transición, preparar el balance de apertura bajo NIIF, aplicar las exenciones voluntarias y las excepciones obligatorias, y presentar la reconciliación entre el marco anterior y NIIF.",
        "ejemplo": "Empresa que llevaba contabilidad bajo los Decretos 2649/2650 (norma colombiana anterior) migra a NIIF para Pymes. Fecha de transición: 1 de enero de 2015. Primera vez que reporta: 31 de diciembre de 2016. Debe re-expresar el balance de apertura al 1-ene-2015 y presentar comparativo 2015-2016 bajo NIIF.",
        "preguntas": [
            ("¿Qué exenciones puedo aprovechar en la transición?", "Las más importantes: medir PPE a valor razonable como costo atribuido a la fecha de transición (evita recalcular depreciación histórica), no re-expresar combinaciones de negocios anteriores, usar el valor actuarial acumulado para beneficios a empleados."),
            ("¿Todavía hay empresas en transición?", "En Colombia la mayoría de Grupo 2 ya completó la transición obligatoria (2015-2016). Si una empresa nueva o una que cambió de grupo aplica NIIF por primera vez, esta sección sigue siendo relevante."),
        ],
        "errores": ["No documentar adecuadamente las decisiones tomadas en la transición y las exenciones aplicadas.", "No preparar la reconciliación entre el patrimonio bajo norma anterior y el patrimonio bajo NIIF para Pymes, requerida en las notas del primer año de aplicación."],
    },
]

# Categorías y colores
CATS = {
    "📊 Estados Financieros": ACCENT,
    "🏭 Activos": SUCCESS,
    "💳 Instrumentos Financieros": PURPLE,
    "💰 Ingresos y Gastos": WARN,
    "👥 Pasivos y Empleados": DANGER,
    "🔄 Arrendamientos": "#FF8C42",
    "🧾 Impuesto": "#C084FC",
    "Principios y Políticas": TEXT_SEC,
}

def show():
    st.markdown("## 📚 Guía NIIF Pymes")
    st.markdown(f"<p style='color:{TEXT_SEC}'>Consulta práctica de las secciones NIIF en español colombiano. "
                f"Ejemplos reales, preguntas frecuentes y errores comunes de Pymes.</p>",
                unsafe_allow_html=True)

    # ── Buscador y filtros ─────────────────────────────────────────────────
    col_s, col_f = st.columns([3, 1])
    busqueda = col_s.text_input("🔍 Buscar sección, tema o palabra clave",
                                placeholder="Ej: bodega, inventario, deterioro, cartera...",
                                key="guia_busq")
    categorias = ["Todas"] + list(CATS.keys())
    cat_sel = col_f.selectbox("Categoría", categorias, key="guia_cat",
                              label_visibility="visible")

    # ── Filtrar secciones ─────────────────────────────────────────────────
    secciones_vis = []
    for s in SECCIONES:
        if cat_sel != "Todas" and s["cat"] != cat_sel:
            continue
        if busqueda:
            texto_completo = (
                s["titulo"] + s["resumen"] + s["ejemplo"] +
                " ".join(p[0] + p[1] for p in s["preguntas"]) +
                " ".join(s["errores"])
            ).lower()
            if busqueda.lower() not in texto_completo:
                continue
        secciones_vis.append(s)

    # ── Contador ─────────────────────────────────────────────────────────
    total = len(SECCIONES)
    mostrando = len(secciones_vis)
    st.markdown(
        f"<p style='color:{TEXT_SEC};font-size:.8rem;margin:.2rem 0 .8rem'>"
        f"Mostrando {mostrando} de {total} secciones disponibles</p>",
        unsafe_allow_html=True)

    if not secciones_vis:
        st.info("No se encontraron secciones con ese criterio. Intenta con otra palabra clave.")
        return

    # ── Cards de secciones ─────────────────────────────────────────────────
    for s in secciones_vis:
        cat_color = CATS.get(s["cat"], TEXT_SEC)
        header_html = (
            f"<div style='display:flex;align-items:center;gap:.6rem'>"
            f"<span style='background:{cat_color}22;color:{cat_color};border:1px solid {cat_color}55;"
            f"border-radius:20px;padding:1px 10px;font-size:.75rem;font-weight:600'>{s['cat']}</span>"
            f"<span style='color:{TEXT_SEC};font-size:.78rem'>Sección {s['num']}</span></div>"
        )

        with st.expander(f"Sección {s['num']} — {s['titulo']}", expanded=False):
            st.markdown(header_html, unsafe_allow_html=True)
            st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

            # Resumen
            st.markdown(
                f"<div style='background:{BG_CARD};border-left:3px solid {cat_color};"
                f"border-radius:6px;padding:.8rem 1rem;margin-bottom:.7rem'>"
                f"<p style='color:{TEXT_SEC};font-size:.75rem;font-weight:600;margin:0 0 .2rem'>¿QUÉ REGULA?</p>"
                f"<p style='color:#E8F4FD;font-size:.86rem;margin:0'>{s['resumen']}</p></div>",
                unsafe_allow_html=True)

            # Ejemplo colombiano
            st.markdown(
                f"<div style='background:{BG_CARD};border-left:3px solid {WARN};"
                f"border-radius:6px;padding:.8rem 1rem;margin-bottom:.7rem'>"
                f"<p style='color:{WARN};font-size:.75rem;font-weight:600;margin:0 0 .2rem'>💼 EJEMPLO PRÁCTICO</p>"
                f"<p style='color:#E8F4FD;font-size:.86rem;margin:0'>{s['ejemplo']}</p></div>",
                unsafe_allow_html=True)

            # Preguntas frecuentes
            if s["preguntas"]:
                st.markdown(
                    f"<p style='color:{ACCENT};font-size:.8rem;font-weight:600;margin:.4rem 0 .3rem'>"
                    f"❓ Preguntas frecuentes</p>",
                    unsafe_allow_html=True)
                for pregunta, respuesta in s["preguntas"]:
                    st.markdown(
                        f"<div style='background:{BG_CARD};border:1px solid {BORDER};"
                        f"border-radius:6px;padding:.7rem 1rem;margin-bottom:.4rem'>"
                        f"<p style='color:{ACCENT};font-size:.83rem;font-weight:600;margin:0 0 .3rem'>— {pregunta}</p>"
                        f"<p style='color:#E8F4FD;font-size:.83rem;margin:0'>{respuesta}</p></div>",
                        unsafe_allow_html=True)

            # Errores comunes
            if s["errores"]:
                st.markdown(
                    f"<p style='color:{DANGER};font-size:.8rem;font-weight:600;margin:.6rem 0 .3rem'>"
                    f"⚠️ Errores comunes en Pymes colombianas</p>",
                    unsafe_allow_html=True)
                for err in s["errores"]:
                    st.markdown(
                        f"<div style='background:{DANGER}11;border-left:3px solid {DANGER};"
                        f"border-radius:4px;padding:.5rem .9rem;margin-bottom:.3rem'>"
                        f"<p style='color:#E8F4FD;font-size:.82rem;margin:0'>• {err}</p></div>",
                        unsafe_allow_html=True)

    # ── Footer informativo ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        f"<div style='background:{BG_CARD};border-left:4px solid {ACCENT};"
        f"border-radius:8px;padding:.9rem 1.2rem'>"
        f"<p style='color:{ACCENT};font-weight:600;margin:0 0 .2rem'>💼 ¿Necesitas asesoría NIIF?</p>"
        f"<p style='color:{TEXT_SEC};font-size:.84rem;margin:0'>"
        f"En SalazAnalytics te acompañamos en convergencia NIIF, elaboración de políticas contables, "
        f"re-expresión de estados financieros, auditoría bajo NIA y presentación de reportes a "
        f"Supersociedades, SIC y DIAN. Contáctanos para una propuesta a tu medida.</p></div>",
        unsafe_allow_html=True)
