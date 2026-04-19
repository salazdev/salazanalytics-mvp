import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

PALETTE = ["#00C2FF","#7B2FBE","#00FFB3","#FF6B6B","#FFD93D","#4ECDC4"]

def load_data(f):
    try:
        sheets = pd.read_excel(f, sheet_name=None)
        return sheets
    except Exception as e:
        st.error(f"Error leyendo archivo: {e}")
        return None

def preparar_datos_restaurante(df):
    df = df.copy()
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['dia_semana'] = df['Fecha'].dt.dayofweek
    df['mes'] = df['Fecha'].dt.month
    df['dia_mes'] = df['Fecha'].dt.day
    df['semana'] = df['Fecha'].dt.isocalendar().week.astype(int)
    if 'Hora de Cobro' in df.columns:
        df['hora'] = pd.to_datetime(df['Hora de Cobro'], format='%H:%M:%S', errors='coerce').dt.hour
    return df

def show():
    st.markdown("## 🤖 Análisis Predictivo con Machine Learning")
    st.markdown("<p style='color:#7B9BB5'>Anticipa resultados, detecta patrones ocultos y toma mejores decisiones con IA.</p>", unsafe_allow_html=True)

    f = st.session_state.get("uploaded_file") if st.session_state.get("file_ext") == "xlsx" else None
    uploaded = st.file_uploader("Sube tu archivo Excel con datos históricos", type=["xlsx","xls"])
    if uploaded:
        f = uploaded
        st.session_state["uploaded_file"] = uploaded
        st.session_state["file_ext"] = "xlsx"

    if not f:
        st.info("👆 Sube un archivo Excel con datos históricos para activar el motor de predicción.")
        _mostrar_capacidades()
        return

    sheets = load_data(f)
    if not sheets:
        return

    sheet_name = st.selectbox("Selecciona la hoja de datos", list(sheets.keys()))
    df_raw = sheets[sheet_name]

    st.success(f"✅ **{len(df_raw):,} registros** cargados · {len(df_raw.columns)} columnas")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Diagnóstico",
        "📈 Predicción de Ventas",
        "👥 Segmentación de Clientes",
        "🏆 Ranking de Productos",
        "⚠️ Alertas Inteligentes",
    ])

    # ── TAB 1: DIAGNÓSTICO ────────────────────────────────────────────────────
    with tab1:
        st.markdown("### 🔍 Diagnóstico automático del negocio")
        df = preparar_datos_restaurante(df_raw)

        cols = st.columns(4)
        if 'Fecha' in df.columns:
            dias = (df['Fecha'].max() - df['Fecha'].min()).days
            cols[0].metric("Días de operación", f"{dias:,}")
        if 'Orden' in df.columns:
            cols[1].metric("Total órdenes", f"{df['Orden'].nunique():,}")
        if 'Producto' in df.columns:
            cols[2].metric("Productos distintos", f"{df['Producto'].nunique()}")
        if 'Atendió' in df.columns:
            cols[3].metric("Colaboradores", f"{df['Atendió'].nunique()}")

        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            if 'Categoria' in df.columns:
                cat_counts = df['Categoria'].value_counts().reset_index()
                cat_counts.columns = ['Categoria','Pedidos']
                fig = px.bar(cat_counts, x='Pedidos', y='Categoria', orientation='h',
                             color_discrete_sequence=PALETTE, template="plotly_dark",
                             title="Pedidos por categoría")
                fig.update_layout(paper_bgcolor="#0D1B2A", plot_bgcolor="#0D1B2A", font_color="#E8F4FD")
                st.plotly_chart(fig, use_container_width=True)

        with c2:
            if 'dia_semana' in df.columns:
                dias_nombres = ['Lun','Mar','Mié','Jue','Vie','Sáb','Dom']
                ventas_dia = df.groupby('dia_semana').size().reset_index(name='Pedidos')
                ventas_dia['Día'] = ventas_dia['dia_semana'].map(lambda x: dias_nombres[x])
                fig2 = px.bar(ventas_dia, x='Día', y='Pedidos',
                              color_discrete_sequence=["#00C2FF"], template="plotly_dark",
                              title="Actividad por día de la semana")
                fig2.update_layout(paper_bgcolor="#0D1B2A", plot_bgcolor="#0D1B2A", font_color="#E8F4FD")
                st.plotly_chart(fig2, use_container_width=True)

        if 'hora' in df.columns:
            st.markdown("### ⏰ Horas pico del restaurante")
            hora_counts = df.groupby('hora').size().reset_index(name='Pedidos')
            fig3 = px.area(hora_counts, x='hora', y='Pedidos',
                           color_discrete_sequence=["#00C2FF"], template="plotly_dark",
                           title="Distribución de pedidos por hora")
            fig3.update_layout(paper_bgcolor="#0D1B2A", plot_bgcolor="#0D1B2A", font_color="#E8F4FD",
                               xaxis_title="Hora del día", yaxis_title="Pedidos")
            fig3.update_traces(fill='tozeroy', fillcolor='rgba(0,194,255,0.15)')
            st.plotly_chart(fig3, use_container_width=True)

    # ── TAB 2: PREDICCIÓN DE VENTAS ───────────────────────────────────────────
    with tab2:
        st.markdown("### 📈 Predicción de demanda futura")
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import mean_absolute_error, r2_score
        from sklearn.model_selection import train_test_split

        df = preparar_datos_restaurante(df_raw)

        if 'Fecha' not in df.columns:
            st.warning("Se necesita una columna 'Fecha' para predecir.")
        else:
            ventas_diarias = df.groupby('Fecha').size().reset_index(name='Pedidos')
            ventas_diarias['Fecha'] = pd.to_datetime(ventas_diarias['Fecha'])
            ventas_diarias = ventas_diarias.sort_values('Fecha')
            ventas_diarias['dia_num'] = (ventas_diarias['Fecha'] - ventas_diarias['Fecha'].min()).dt.days
            ventas_diarias['dia_semana'] = ventas_diarias['Fecha'].dt.dayofweek
            ventas_diarias['mes'] = ventas_diarias['Fecha'].dt.month
            ventas_diarias['semana'] = ventas_diarias['Fecha'].dt.isocalendar().week.astype(int)

            features = ['dia_num','dia_semana','mes','semana']
            X = ventas_diarias[features]
            y = ventas_diarias['Pedidos']

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

            modelo_sel = st.selectbox("Modelo de predicción", [
                "Random Forest (recomendado)",
                "Gradient Boosting",
                "Regresión Lineal"
            ])
            dias_pred = st.slider("Días a predecir hacia el futuro", 7, 90, 30)

            if st.button("🚀 Ejecutar predicción", type="primary"):
                with st.spinner("Entrenando modelo…"):
                    if "Random Forest" in modelo_sel:
                        model = RandomForestRegressor(n_estimators=200, random_state=42)
                    elif "Gradient" in modelo_sel:
                        model = GradientBoostingRegressor(n_estimators=200, random_state=42)
                    else:
                        model = LinearRegression()

                    model.fit(X_train, y_train)
                    y_pred_test = model.predict(X_test)
                    mae = mean_absolute_error(y_test, y_pred_test)
                    r2 = r2_score(y_test, y_pred_test)

                    ultima_fecha = ventas_diarias['Fecha'].max()
                    fechas_futuras = [ultima_fecha + timedelta(days=i+1) for i in range(dias_pred)]
                    ultimo_dia_num = ventas_diarias['dia_num'].max()

                    futuro = pd.DataFrame({
                        'dia_num': [ultimo_dia_num + i + 1 for i in range(dias_pred)],
                        'dia_semana': [f.weekday() for f in fechas_futuras],
                        'mes': [f.month for f in fechas_futuras],
                        'semana': [f.isocalendar()[1] for f in fechas_futuras],
                    })
                    pred_futuro = model.predict(futuro)
                    pred_futuro = np.maximum(pred_futuro, 0)

                    m1, m2, m3 = st.columns(3)
                    m1.metric("Precisión del modelo (R²)", f"{r2:.1%}")
                    m2.metric("Error promedio diario", f"{mae:.1f} pedidos")
                    m3.metric("Pedidos estimados próx. período", f"{int(pred_futuro.sum()):,}")

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=ventas_diarias['Fecha'], y=ventas_diarias['Pedidos'],
                        mode='lines', name='Histórico', line=dict(color='#00C2FF', width=1.5)
                    ))
                    fig.add_trace(go.Scatter(
                        x=fechas_futuras, y=pred_futuro.round().astype(int),
                        mode='lines+markers', name='Predicción',
                        line=dict(color='#7B2FBE', width=2, dash='dot'),
                        marker=dict(size=5)
                    ))
                    fig.add_vrect(
                        x0=str(ultima_fecha), x1=str(fechas_futuras[-1]),
                        fillcolor="rgba(123,47,190,0.08)", layer="below", line_width=0,
                        annotation_text="Zona predicha", annotation_position="top left",
                        annotation_font_color="#7B2FBE"
                    )
                    fig.update_layout(
                        title=f"Predicción de demanda — próximos {dias_pred} días",
                        paper_bgcolor="#0D1B2A", plot_bgcolor="#0D1B2A",
                        font_color="#E8F4FD", legend=dict(bgcolor="#132030"),
                        xaxis_title="Fecha", yaxis_title="Pedidos diarios"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown("### 📋 Detalle de predicción")
                    df_pred = pd.DataFrame({
                        'Fecha': fechas_futuras,
                        'Día': [f.strftime('%A') for f in fechas_futuras],
                        'Pedidos estimados': pred_futuro.round().astype(int),
                        'Confianza': ['Alta' if r2 > 0.7 else 'Media' if r2 > 0.4 else 'Baja'] * dias_pred
                    })
                    st.dataframe(df_pred, use_container_width=True)
                    st.session_state["df_prediccion"] = df_pred

    # ── TAB 3: SEGMENTACIÓN DE CLIENTES ──────────────────────────────────────
    with tab3:
        st.markdown("### 👥 Segmentación de clientes con ML")
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler

        df = preparar_datos_restaurante(df_raw)

        if 'Tipo de Cliente' in df.columns:
            c1, c2 = st.columns(2)
            with c1:
                tipo_counts = df['Tipo de Cliente'].value_counts().reset_index()
                tipo_counts.columns = ['Tipo','Cantidad']
                fig = px.pie(tipo_counts, names='Tipo', values='Cantidad',
                             color_discrete_sequence=PALETTE, template="plotly_dark",
                             title="Composición de clientes")
                fig.update_layout(paper_bgcolor="#0D1B2A", font_color="#E8F4FD")
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                if 'Propina' in df.columns:
                    propina_tipo = df.groupby('Tipo de Cliente')['Propina'].mean().reset_index()
                    propina_tipo.columns = ['Tipo','Propina promedio']
                    propina_tipo['Propina promedio'] = (propina_tipo['Propina promedio'] * 100).round(1)
                    fig2 = px.bar(propina_tipo, x='Tipo', y='Propina promedio',
                                  color_discrete_sequence=["#00C2FF","#7B2FBE"],
                                  template="plotly_dark", title="Propina promedio por tipo de cliente (%)")
                    fig2.update_layout(paper_bgcolor="#0D1B2A", plot_bgcolor="#0D1B2A", font_color="#E8F4FD")
                    st.plotly_chart(fig2, use_container_width=True)

        if 'Atendió' in df.columns and 'Propina' in df.columns:
            st.markdown("### 🏅 Rendimiento por colaborador")
            perf = df.groupby('Atendió').agg(
                Pedidos=('Orden','nunique'),
                Propina_prom=('Propina','mean'),
                Productos_prom=('Producto','count')
            ).reset_index()
            perf['Propina_prom'] = (perf['Propina_prom'] * 100).round(1)

            fig3 = px.scatter(perf, x='Pedidos', y='Propina_prom', size='Productos_prom',
                              text='Atendió', color='Atendió',
                              color_discrete_sequence=PALETTE, template="plotly_dark",
                              title="Rendimiento: Pedidos vs Propina promedio por colaborador",
                              labels={'Propina_prom':'Propina promedio (%)','Pedidos':'Órdenes atendidas'})
            fig3.update_traces(textposition='top center')
            fig3.update_layout(paper_bgcolor="#0D1B2A", plot_bgcolor="#0D1B2A", font_color="#E8F4FD")
            st.plotly_chart(fig3, use_container_width=True)

        if 'Orden' in df.columns and 'Propina' in df.columns and 'dia_semana' in df.columns:
            st.markdown("### 🔬 Clustering de patrones de pedidos (K-Means)")
            n_clusters = st.slider("Número de segmentos", 2, 6, 3)
            orden_features = df.groupby('Orden').agg(
                Propina=('Propina','mean'),
                dia_semana=('dia_semana','first'),
                n_productos=('Producto','count'),
            ).dropna()

            if len(orden_features) > n_clusters:
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(orden_features)
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                orden_features['Segmento'] = kmeans.fit_predict(X_scaled).astype(str)

                fig4 = px.scatter(orden_features, x='n_productos', y='Propina',
                                  color='Segmento', color_discrete_sequence=PALETTE,
                                  template="plotly_dark",
                                  title=f"{n_clusters} segmentos de órdenes detectados",
                                  labels={'n_productos':'Productos por orden','Propina':'Propina'})
                fig4.update_layout(paper_bgcolor="#0D1B2A", plot_bgcolor="#0D1B2A", font_color="#E8F4FD")
                st.plotly_chart(fig4, use_container_width=True)

                resumen = orden_features.groupby('Segmento').agg(
                    Ordenes=('Propina','count'),
                    Propina_prom=('Propina','mean'),
                    Productos_prom=('n_productos','mean'),
                ).round(3)
                resumen['Propina_prom'] = (resumen['Propina_prom']*100).round(1).astype(str) + '%'
                st.dataframe(resumen, use_container_width=True)

    # ── TAB 4: RANKING DE PRODUCTOS ───────────────────────────────────────────
    with tab4:
        st.markdown("### 🏆 Inteligencia de productos")
        df = preparar_datos_restaurante(df_raw)

        if 'Producto' in df.columns:
            c1, c2 = st.columns(2)
            with c1:
                top_prod = df['Producto'].value_counts().head(10).reset_index()
                top_prod.columns = ['Producto','Pedidos']
                fig = px.bar(top_prod, x='Pedidos', y='Producto', orientation='h',
                             color='Pedidos', color_continuous_scale=['#1a3a5c','#00C2FF'],
                             template="plotly_dark", title="Top 10 productos más pedidos")
                fig.update_layout(paper_bgcolor="#0D1B2A", plot_bgcolor="#0D1B2A",
                                  font_color="#E8F4FD", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                bot_prod = df['Producto'].value_counts().tail(10).reset_index()
                bot_prod.columns = ['Producto','Pedidos']
                fig2 = px.bar(bot_prod, x='Pedidos', y='Producto', orientation='h',
                              color='Pedidos', color_continuous_scale=['#FF6B6B','#FFD93D'],
                              template="plotly_dark", title="10 productos menos pedidos")
                fig2.update_layout(paper_bgcolor="#0D1B2A", plot_bgcolor="#0D1B2A",
                                   font_color="#E8F4FD", showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

        if 'Categoria' in df.columns and 'Producto' in df.columns:
            st.markdown("### 📊 Análisis por categoría y tendencia temporal")
            cat_sel = st.selectbox("Categoría a analizar", df['Categoria'].unique())
            df_cat = df[df['Categoria'] == cat_sel]
            tend = df_cat.groupby(['Fecha','Producto']).size().reset_index(name='Pedidos')
            tend_agg = tend.groupby('Fecha')['Pedidos'].sum().reset_index()

            fig3 = px.line(tend_agg, x='Fecha', y='Pedidos',
                           color_discrete_sequence=["#00C2FF"], template="plotly_dark",
                           title=f"Tendencia de pedidos — {cat_sel}")
            fig3.update_layout(paper_bgcolor="#0D1B2A", plot_bgcolor="#0D1B2A", font_color="#E8F4FD")
            fig3.update_traces(fill='tozeroy', fillcolor='rgba(0,194,255,0.08)')
            st.plotly_chart(fig3, use_container_width=True)

            prod_cat = df_cat['Producto'].value_counts().reset_index()
            prod_cat.columns = ['Producto','Pedidos']
            fig4 = px.treemap(prod_cat, path=['Producto'], values='Pedidos',
                              color='Pedidos', color_continuous_scale=['#132030','#00C2FF'],
                              title=f"Mapa de calor — {cat_sel}")
            fig4.update_layout(paper_bgcolor="#0D1B2A", font_color="#E8F4FD")
            st.plotly_chart(fig4, use_container_width=True)

    # ── TAB 5: ALERTAS INTELIGENTES ───────────────────────────────────────────
    with tab5:
        st.markdown("### ⚠️ Sistema de alertas inteligentes")
        df = preparar_datos_restaurante(df_raw)

        alertas = []

        ventas_dia = df.groupby('Fecha').size()
        media = ventas_dia.mean()
        std = ventas_dia.std()
        dias_bajos = ventas_dia[ventas_dia < media - 1.5*std]
        if len(dias_bajos) > 0:
            alertas.append({
                "tipo": "warning",
                "icono": "⚠️",
                "titulo": f"{len(dias_bajos)} días con ventas inusualmente bajas",
                "detalle": f"Promedio normal: {media:.0f} pedidos/día. Días críticos: {', '.join([str(d.date()) for d in dias_bajos.index[:3]])}"
            })

        if 'Categoria' in df.columns:
            cat_mes = df.groupby(['mes','Categoria']).size().unstack(fill_value=0)
            for cat in cat_mes.columns:
                if cat_mes[cat].std() > cat_mes[cat].mean() * 0.3:
                    alertas.append({
                        "tipo": "info",
                        "icono": "📊",
                        "titulo": f"Alta variabilidad en categoría: {cat}",
                        "detalle": f"La demanda de {cat} varía significativamente entre meses. Considera revisar inventario."
                    })
                    break

        if 'Atendió' in df.columns and 'Propina' in df.columns:
            propina_colab = df.groupby('Atendió')['Propina'].mean()
            media_propina = propina_colab.mean()
            bajos = propina_colab[propina_colab < media_propina * 0.85]
            if len(bajos) > 0:
                alertas.append({
                    "tipo": "danger",
                    "icono": "👤",
                    "titulo": f"Colaboradores con propina debajo del promedio",
                    "detalle": f"{', '.join(bajos.index.tolist())} tienen propina promedio menor al 85% del equipo."
                })

        if 'dia_semana' in df.columns:
            ventas_semana = df.groupby('dia_semana').size()
            dia_min = ventas_semana.idxmin()
            dias_nombres = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
            alertas.append({
                "tipo": "info",
                "icono": "📅",
                "titulo": f"Día más flojo: {dias_nombres[dia_min]}",
                "detalle": f"Solo {ventas_semana[dia_min]:,} pedidos en promedio. Ideal para promociones o eventos especiales."
            })

        colores = {"warning":"#FFD93D","info":"#00C2FF","danger":"#FF6B6B"}
        for a in alertas:
            color = colores.get(a['tipo'], '#7B9BB5')
            st.markdown(f"""
            <div style="background:#132030;border-left:4px solid {color};border-radius:8px;
                        padding:1rem 1.2rem;margin-bottom:.8rem;">
                <p style="color:{color};font-weight:600;margin:0 0 .3rem;">{a['icono']} {a['titulo']}</p>
                <p style="color:#7B9BB5;font-size:.88rem;margin:0;">{a['detalle']}</p>
            </div>
            """, unsafe_allow_html=True)

        if not alertas:
            st.success("✅ No se detectaron alertas críticas en los datos.")

        st.divider()
        st.markdown("### 💡 Recomendaciones estratégicas basadas en los datos")
        if 'dia_semana' in df.columns:
            ventas_semana = df.groupby('dia_semana').size()
            dia_max = ventas_semana.idxmax()
            dias_nombres = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
            recomendaciones = [
                f"📈 **Refuerza personal los {dias_nombres[dia_max]}** — es tu día más activo con {ventas_semana[dia_max]:,} pedidos.",
                f"🎯 **Promoción en {dias_nombres[ventas_semana.idxmin()]}** — el día más tranquilo, ideal para atraer más clientes.",
            ]
            if 'Categoria' in df.columns:
                top_cat = df['Categoria'].value_counts().index[0]
                recomendaciones.append(f"⭐ **Potencia la categoría '{top_cat}'** — es tu estrella de ventas, considera ampliar el menú.")
            if 'Tipo de Cliente' in df.columns:
                nuevos = (df['Tipo de Cliente'] == 'Cliente Nuevo').mean()
                if nuevos > 0.4:
                    recomendaciones.append("🔄 **Programa de fidelización urgente** — más del 40% son clientes nuevos que no regresan.")
                else:
                    recomendaciones.append("✅ **Alta fidelización** — más del 60% son clientes recurrentes. Refuerza el programa de lealtad.")

            for r in recomendaciones:
                st.markdown(f"""
                <div style="background:#0a1520;border:1px solid #1a3a5c;border-radius:8px;
                            padding:.9rem 1.2rem;margin-bottom:.5rem;">
                    <p style="color:#E8F4FD;margin:0;font-size:.93rem;">{r}</p>
                </div>
                """, unsafe_allow_html=True)

def _mostrar_capacidades():
    st.markdown("### ¿Qué puedes predecir con esta plataforma?")
    caps = [
        ("📈","Predicción de ventas","Forecasting de demanda diaria/semanal/mensual con Random Forest y Gradient Boosting"),
        ("👥","Segmentación","Clustering K-Means para identificar perfiles de clientes y patrones de compra"),
        ("🏆","Ranking inteligente","Identifica productos estrella, en declive y oportunidades de menú"),
        ("⚠️","Alertas automáticas","Detecta días críticos, colaboradores con bajo rendimiento y anomalías"),
        ("💡","Recomendaciones","Sugerencias estratégicas basadas en los datos reales del negocio"),
    ]
    cols = st.columns(len(caps))
    for col, (icon, title, desc) in zip(cols, caps):
        with col:
            st.markdown(f"""
            <div style="background:#132030;border:1px solid #1a3a5c;border-radius:12px;
                        padding:1.2rem;text-align:center;height:180px;">
                <div style="font-size:1.8rem;">{icon}</div>
                <p style="color:#00C2FF;font-weight:600;font-size:.9rem;margin:.4rem 0 .3rem;">{title}</p>
                <p style="color:#7B9BB5;font-size:.78rem;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
