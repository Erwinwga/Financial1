import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import date
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from fpdf import FPDF


# Inicializar las variables de ahorro en session_state si no existen
if 'ahorro_corto_plazo' not in st.session_state:
    st.session_state.ahorro_corto_plazo = 0.0

if 'ahorro_largo_plazo' not in st.session_state:
    st.session_state.ahorro_largo_plazo = 0.0

# Configuración del diseño
st.set_page_config(layout="wide")

# Colores personalizados
primaryColor = "#0e1117"  # Color de fondo principal
menuColor = "#123456"  # Color para la zona del menú

# Estilos CSS para personalizar el fondo y las zonas
st.markdown(f"""
    <style>
    .reportview-container {{
        background-color: {primaryColor};
    }}
    .sidebar .sidebar-content {{
        background-color: {menuColor};
    }}
    </style>
    """, unsafe_allow_html=True)

# Logo
st.sidebar.image("C:/Users/AGBINVESTMENTS/OneDrive/Escritorio/AG.png", use_column_width=True)

# Título en la aplicación
st.sidebar.title("Menú de Opciones")
# Texto con tamaño de fuente personalizado
st.sidebar.markdown("<h3 style='font-size:20px;'>Selecciona tu perfil</h3>", unsafe_allow_html=True)

# Botón para limpiar la información
if st.sidebar.button("Limpiar Información"):
    # Limpiar todos los datos de la sesión
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Mostrar un enlace que redirige a la misma página para simular un reinicio
    st.markdown('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)


# Opciones de perfil
perfil = st.sidebar.radio("Selecciona tu perfil", ("Perfil Individual", "Perfil en Pareja"))

# Crear las pestañas 
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9,tab10 = st.tabs([
    "Datos Personales", "Historial de Ingresos", "Ingresos", 
    "Gastos Fijos", "Deuda","Gastos Variables", 
    "Ahorro a Corto y Largo Plazo", "Patrimonio", "Diagnóstico","Reporte Financiero Completo"
])


# Contenido de la primera pestaña: Datos Personales
with tab1:
    st.header("Datos Personales")

    # Dividir el formulario en columnas con margen ajustado a la izquierda
    col1, col2, col3 = st.columns([0.01, 1, 1])  # col1 es más pequeña para que col2 esté más a la izquierda

    with col2:  # El formulario está en la columna del medio (ajustada más a la izquierda)
        #st.markdown("<h3 style='text-align: left;'>Datos Personales</h3>", unsafe_allow_html=True)

        # Variables para controlar la edición
        if 'edit_mode' not in st.session_state:
            st.session_state.edit_mode = False

        # Función para calcular la edad a partir de la fecha de nacimiento
        def calcular_edad(fecha_nacimiento):
            today = date.today()
            edad = today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            return edad

        if st.session_state.edit_mode:
            # Cargar los valores en los widgets si estamos en modo de edición
            nombre = st.text_input("Nombre Completo", value=st.session_state.get('nombre_edit', ''), key="nombre_edit")
            fecha_nacimiento = st.date_input("Fecha de Nacimiento", value=st.session_state.get('fecha_nacimiento_edit', date.today()), key="fecha_nacimiento_edit", on_change=lambda: st.session_state.update({'edad_edit': calcular_edad(st.session_state.fecha_nacimiento_edit)}))
            edad = st.number_input("Edad", min_value=0, max_value=120, value=st.session_state.get('edad_edit', 0), key="edad_edit")
            ocupacion = st.text_input("Ocupación", value=st.session_state.get('ocupacion_edit', ''), key="ocupacion_edit")
            cantidad_hijos = st.number_input("Cantidad de Hijos", min_value=0, step=1, value=st.session_state.get('cantidad_hijos_edit', 0), key="cantidad_hijos_edit")

            # Botón para actualizar el dato personal
            if st.button("Actualizar Dato Personal"):
                st.session_state['datos_personales'][st.session_state.edit_index] = {
                    "Nombre Completo": st.session_state.nombre_edit,
                    "Edad": st.session_state.edad_edit,
                    "Fecha de Nacimiento": st.session_state.fecha_nacimiento_edit,
                    "Ocupación": st.session_state.ocupacion_edit,
                    "Cantidad de Hijos": st.session_state.cantidad_hijos_edit
                }
                st.session_state.edit_mode = False
                st.session_state.edit_index = None
        else:
            # Campos para agregar nuevos datos personales
            nombre = st.text_input("Nombre Completo", key="nombre")
            fecha_nacimiento = st.date_input("Fecha de Nacimiento", key="fecha_nacimiento", on_change=lambda: st.session_state.update({'edad': calcular_edad(st.session_state.fecha_nacimiento)}))
            edad = st.number_input("Edad", min_value=0, max_value=120, key="edad")
            ocupacion = st.text_input("Ocupación", key="ocupacion")
            cantidad_hijos = st.number_input("Cantidad de Hijos", min_value=0, step=1, key="cantidad_hijos")

            # Botón para agregar los datos personales
            if st.button("Agregar Dato Personal"):
                if 'datos_personales' not in st.session_state:
                    st.session_state['datos_personales'] = []
                st.session_state['datos_personales'].append({
                    "Nombre Completo": nombre,
                    "Edad": edad,
                    "Fecha de Nacimiento": fecha_nacimiento,
                    "Ocupación": ocupacion,
                    "Cantidad de Hijos": cantidad_hijos
                })

        # Mostrar la lista de datos personales
        if 'datos_personales' in st.session_state and st.session_state['datos_personales']:
            df_datos_personales = pd.DataFrame(st.session_state['datos_personales'])
            df_datos_personales.index = df_datos_personales.index + 1  # Ajuste para que el índice empiece desde 1
            st.table(df_datos_personales)

            # Seleccionar un índice para editar o eliminar
            seleccion_index = st.selectbox("Selecciona un índice para editar o eliminar", df_datos_personales.index) - 1  # Ajustamos el índice restando 1

            # Botón para editar el dato seleccionado
            if st.button("Editar Dato Personal"):
                dato_a_editar = st.session_state['datos_personales'][seleccion_index]
                st.session_state.edit_index = seleccion_index
                st.session_state.edit_mode = True
                st.session_state.nombre_edit = dato_a_editar["Nombre Completo"]
                st.session_state.fecha_nacimiento_edit = dato_a_editar["Fecha de Nacimiento"]
                st.session_state.edad_edit = calcular_edad(dato_a_editar["Fecha de Nacimiento"])
                st.session_state.ocupacion_edit = dato_a_editar["Ocupación"]
                st.session_state.cantidad_hijos_edit = dato_a_editar["Cantidad de Hijos"]

            # Botón para eliminar el dato seleccionado
            if st.button("Eliminar Dato Personal"):
                st.session_state['datos_personales'].pop(seleccion_index)

# Contenido de la segunda pestaña: Historial de Ingresos
with tab2:
    st.header("Historial de Ingresos")

    # Dividir el formulario en columnas con margen ajustado a la izquierda
    col1, col2, col3 = st.columns([0.01, 1, 1])  # col1 es más pequeña para que col2 esté más a la izquierda

    with col2:  # El formulario está en la columna del medio (ajustada más a la izquierda)

        # Variables para controlar la edición
        if 'edit_mode_historial_ingresos' not in st.session_state:
            st.session_state.edit_mode_historial_ingresos = False

        # Campos para que el usuario ingrese o edite datos de ingresos
        if st.session_state.edit_mode_historial_ingresos:
            descripcion = st.text_input("Descripción", value=st.session_state.get('descripcion_historial_edit', ''), key="descripcion_historial_edit")
            cantidad_mensual = st.number_input("Cantidad Mensual", min_value=0.0, value=st.session_state.get('cantidad_mensual_edit', 0.0), key="cantidad_mensual_edit")
            años = st.number_input("Años", min_value=0, value=st.session_state.get('años_edit', 0), key="años_edit")
            total = cantidad_mensual * 12 * años

            # Botón para actualizar el ingreso
            if st.button("Actualizar Ingreso", key="boton_actualizar_historial_ingreso"):
                st.session_state['historico_ingresos'][st.session_state.edit_index_historial_ingresos] = {
                    "Descripción": descripcion,
                    "Cantidad Mensual": round(cantidad_mensual, 2),
                    "AÑOS": años,
                    "TOTAL": round(total, 2)
                }
                st.session_state.edit_mode_historial_ingresos = False
                st.session_state.edit_index_historial_ingresos = None
        else:
            descripcion = st.text_input("Descripción", key="descripcion_historial_nueva")
            cantidad_mensual = st.number_input("Cantidad Mensual", min_value=0.0, key="cantidad_mensual_nueva")
            años = st.number_input("Años", min_value=0, key="años_nueva")
            total = cantidad_mensual * 12 * años

            # Botón para agregar la entrada a la tabla
            if st.button("Agregar Ingreso", key='boton_agregar_historial_ingreso'):
                if 'historico_ingresos' not in st.session_state:
                    st.session_state['historico_ingresos'] = []
                
                st.session_state['historico_ingresos'].append({
                    "Descripción": descripcion,
                    "Cantidad Mensual": round(cantidad_mensual, 2),
                    "AÑOS": años,
                    "TOTAL": round(total, 2)
                })

    # Mostrar la tabla en la segunda columna
    with col2:
        if 'historico_ingresos' in st.session_state:
            df_ingresos = pd.DataFrame(st.session_state['historico_ingresos'])
            df_ingresos.index += 1  # Ajuste para que el índice empiece desde 1
            
            # Formatear las columnas para mostrar solo dos decimales
            df_ingresos['Cantidad Mensual'] = df_ingresos['Cantidad Mensual'].astype(float).map('{:,.2f}'.format)
            df_ingresos['TOTAL'] = df_ingresos['TOTAL'].astype(float).map('{:,.2f}'.format)
            
            st.table(df_ingresos)

            # Seleccionar un índice para editar o eliminar
            seleccion_index_historial_ingresos = st.selectbox(
                "Selecciona un índice para editar o eliminar", 
                df_ingresos.index, 
                key="seleccion_index_historial_ingresos"
            ) - 1  # Ajustamos el índice restando 1

            # Botón para editar el ingreso seleccionado
            if st.button("Editar Ingreso", key="boton_editar_historial_ingreso"):
                ingreso_a_editar = st.session_state['historico_ingresos'][seleccion_index_historial_ingresos]
                st.session_state.edit_index_historial_ingresos = seleccion_index_historial_ingresos
                st.session_state.edit_mode_historial_ingresos = True
                st.session_state.descripcion_historial_edit = ingreso_a_editar["Descripción"]
                st.session_state.cantidad_mensual_edit = ingreso_a_editar["Cantidad Mensual"]
                st.session_state.años_edit = ingreso_a_editar["AÑOS"]

            # Botón para eliminar el ingreso seleccionado
            if st.button("Eliminar Ingreso", key="boton_eliminar_historial_ingreso"):
                st.session_state['historico_ingresos'].pop(seleccion_index_historial_ingresos)

            # Calcular y mostrar la suma de la columna TOTAL
            suma_total = pd.to_numeric(df_ingresos['TOTAL'].str.replace(',', ''), errors='coerce').sum()
            st.session_state['total_ingresos_historicos'] = suma_total  # Guarda el total en session_state
            st.write(f"**Total de Ingresos Históricos:** ${suma_total:,.2f}")



# Contenido de la tercera pestaña: Datos de Ingresos
with tab3:
    st.header("Datos de Ingresos")

    # Dividir el formulario en columnas con margen ajustado a la izquierda
    col1, col2, col3 = st.columns([0.01, 1, 1])  # col1 es más pequeña para que col2 esté más a la izquierda

    with col2:  # El formulario está en la columna del medio (ajustada más a la izquierda)

        # Variables para controlar la edición
        if 'edit_mode_datos_ingresos' not in st.session_state:
            st.session_state.edit_mode_datos_ingresos = False

        # Campos para que el usuario ingrese o edite datos de ingresos
        if st.session_state.edit_mode_datos_ingresos:
            ente = st.text_input("Ente", value=st.session_state.get('ente_edit', ''), key="ente_edit")
            
            # Selección de descripción predefinida
            opciones_descripcion = ["Sueldo Base", "Prima", "Bonos de alimentos", "Bonos de transporte", "Fondo de ahorro", "Otros negocios"]
            descripcion_seleccionada = st.selectbox("Selecciona un tipo de ingreso", opciones_descripcion, index=opciones_descripcion.index(st.session_state.get('descripcion_seleccionada_edit', opciones_descripcion[0])), key="descripcion_seleccionada_edit")
            
            # Campo de descripción que se autocompleta con la selección
            descripcion_ingreso = st.text_input("Descripción", value=st.session_state.get('desc_ingreso_edit', descripcion_seleccionada), key="desc_ingreso_edit")
            
            monto = st.number_input("Monto", min_value=0.0, step=0.01, value=st.session_state.get('monto_edit', 0.0), key="monto_edit")
            frecuencia = st.selectbox("Frecuencia", ["Mensual", "Quincenal", "Semanal", "Diario", "Anual"], index=["Mensual", "Quincenal", "Semanal", "Diario", "Anual"].index(st.session_state.get('frecuencia_edit', 'Mensual')), key="frecuencia_edit")
            
            # Calcular promedio mensual basado en la frecuencia
            if frecuencia == "Mensual":
                promedio_mensual = monto
            elif frecuencia == "Quincenal":
                promedio_mensual = monto * 2
            elif frecuencia == "Semanal":
                promedio_mensual = monto * 4
            elif frecuencia == "Diario":
                promedio_mensual = monto * 30
            elif frecuencia == "Anual":
                promedio_mensual = monto / 12

            # Botón para actualizar la entrada
            if st.button("Actualizar Datos de Ingreso", key="boton_actualizar_ingreso"):
                st.session_state['datos_ingresos'][st.session_state.edit_index_datos_ingresos] = {
                    "Ente": ente,
                    "Descripción": descripcion_ingreso,
                    "Monto": round(monto, 2),
                    "Frecuencia": frecuencia,
                    "Promedio Mensual": round(promedio_mensual, 2)
                }
                st.session_state.edit_mode_datos_ingresos = False
                st.session_state.edit_index_datos_ingresos = None
        else:
            ente = st.text_input("Ente", key="ente_nuevo")
            
            # Selección de descripción predefinida
            opciones_descripcion = ["Sueldo Base", "Prima", "Bonos de alimentos", "Bonos de transporte", "Fondo de ahorro", "Otros negocios"]
            descripcion_seleccionada = st.selectbox("Selecciona un tipo de ingreso", opciones_descripcion, key="descripcion_nueva")
            
            # Campo de descripción que se autocompleta con la selección
            descripcion_ingreso = st.text_input("Descripción", value=descripcion_seleccionada, key="desc_nuevo")
            
            monto = st.number_input("Monto", min_value=0.0, step=0.01, key="monto_nuevo")
            frecuencia = st.selectbox("Frecuencia", ["Mensual", "Quincenal", "Semanal", "Diario", "Anual"], key="frecuencia_nueva")
            
            # Calcular promedio mensual basado en la frecuencia
            if frecuencia == "Mensual":
                promedio_mensual = monto
            elif frecuencia == "Quincenal":
                promedio_mensual = monto * 2
            elif frecuencia == "Semanal":
                promedio_mensual = monto * 4
            elif frecuencia == "Diario":
                promedio_mensual = monto * 30
            elif frecuencia == "Anual":
                promedio_mensual = monto / 12
            
            # Botón para agregar la entrada a la tabla
            if st.button("Agregar Datos de Ingreso", key="boton_agregar_ingreso"):
                if 'datos_ingresos' not in st.session_state:
                    st.session_state['datos_ingresos'] = []
                
                st.session_state['datos_ingresos'].append({
                    "Ente": ente,
                    "Descripción": descripcion_ingreso,
                    "Monto": round(monto, 2),
                    "Frecuencia": frecuencia,
                    "Promedio Mensual": round(promedio_mensual, 2)
                })

    # Mostrar la tabla en la segunda columna
    with col2:
        if 'datos_ingresos' in st.session_state:
            df_datos_ingresos = pd.DataFrame(st.session_state['datos_ingresos'])
            df_datos_ingresos.index += 1  # Ajuste para que el índice empiece desde 1

            # Asegurar que las columnas numéricas tengan solo dos decimales
            df_datos_ingresos['Monto'] = df_datos_ingresos['Monto'].astype(float).map('{:,.2f}'.format)
            df_datos_ingresos['Promedio Mensual'] = df_datos_ingresos['Promedio Mensual'].astype(float).map('{:,.2f}'.format)

            st.table(df_datos_ingresos)

            # Seleccionar un índice para editar o eliminar
            seleccion_index_datos_ingresos = st.selectbox("Selecciona un índice para editar o eliminar", df_datos_ingresos.index, key="seleccion_index_datos_ingresos") - 1  # Ajustamos el índice restando 1

            # Botón para editar el ingreso seleccionado
            if st.button("Editar Datos de Ingreso", key="boton_editar_ingreso"):
                ingreso_a_editar = st.session_state['datos_ingresos'][seleccion_index_datos_ingresos]
                st.session_state.edit_index_datos_ingresos = seleccion_index_datos_ingresos
                st.session_state.edit_mode_datos_ingresos = True
                st.session_state.ente_edit = ingreso_a_editar["Ente"]
                st.session_state.desc_ingreso_edit = ingreso_a_editar["Descripción"]
                st.session_state.monto_edit = ingreso_a_editar["Monto"]
                st.session_state.frecuencia_edit = ingreso_a_editar["Frecuencia"]

            # Botón para eliminar el ingreso seleccionado
            if st.button("Eliminar Datos de Ingreso", key="boton_eliminar_ingreso"):
                st.session_state['datos_ingresos'].pop(seleccion_index_datos_ingresos)

            # Calcular y mostrar la suma de la columna Promedio Mensual
            suma_promedio_mensual = pd.to_numeric(df_datos_ingresos['Promedio Mensual'].str.replace(',', ''), errors='coerce').sum()
            st.write(f"**Total del Monto:** ${suma_promedio_mensual:,.2f}")


########### Contenido de la cuarta pestaña: Gastos Fijos ###########
with tab4:
    st.header("Gastos Fijos")

    # Dividir el formulario en columnas con margen ajustado a la izquierda
    col1, col2, col3 = st.columns([0.01, 1, 1])  # col1 es más pequeña para que col2 esté más a la izquierda

    with col2:  # El formulario está en la columna del medio (ajustada más a la izquierda)
        # Variables para controlar la edición
        if 'edit_mode_gastos_fijos' not in st.session_state:
            st.session_state.edit_mode_gastos_fijos = False

        # Campos para que el usuario ingrese o edite datos de gastos fijos
        if st.session_state.edit_mode_gastos_fijos:
            ente_gastos_fijos = st.text_input("Ente", value=st.session_state.get('ente_gastos_fijos_edit', ''), key="ente_gastos_fijos_edit")
            
            # Selección de descripción predefinida para gastos fijos
            opciones_gastos_fijos = [
                "Renta de vivienda", "Fondo de emergencias", "Gas", "Agua", "Energia", "Internet", "Teléfono", 
                "Seguro médico", "Pensión", "Alimentación", "Transporte", 
                "Gasto de Vehículo", "Seguro de Vehículo", "Gasto de mascota"
            ]
            descripcion_gastos_fijos = st.selectbox("Descripción", opciones_gastos_fijos, index=opciones_gastos_fijos.index(st.session_state.get('descripcion_gastos_fijos_edit', opciones_gastos_fijos[0])), key="descripcion_gastos_fijos_edit")
            
            monto_gastos_fijos = st.number_input("Monto", min_value=0.0, step=0.01, value=st.session_state.get('monto_gastos_fijos_edit', 0.0), key="monto_gastos_fijos_edit")
            frecuencia_gastos_fijos = st.selectbox("Frecuencia", ["Mensual", "Quincenal", "Semanal", "Diario", "Anual"], index=["Mensual", "Quincenal", "Semanal", "Diario", "Anual"].index(st.session_state.get('frecuencia_gastos_fijos_edit', 'Mensual')), key="frecuencia_gastos_fijos_edit")
            
            # Calcular promedio mensual basado en la frecuencia
            if frecuencia_gastos_fijos == "Mensual":
                promedio_mensual_gastos_fijos = monto_gastos_fijos
            elif frecuencia_gastos_fijos == "Quincenal":
                promedio_mensual_gastos_fijos = monto_gastos_fijos * 2
            elif frecuencia_gastos_fijos == "Semanal":
                promedio_mensual_gastos_fijos = monto_gastos_fijos * 4
            elif frecuencia_gastos_fijos == "Diario":
                promedio_mensual_gastos_fijos = monto_gastos_fijos * 30
            elif frecuencia_gastos_fijos == "Anual":
                promedio_mensual_gastos_fijos = monto_gastos_fijos / 12

            # Botón para actualizar el gasto fijo
            if st.button("Actualizar Gasto Fijo", key="boton_actualizar_gasto_fijo"):
                st.session_state['gastos_fijos'][st.session_state.edit_index_gastos_fijos] = {
                    "Ente": ente_gastos_fijos,
                    "Descripción": descripcion_gastos_fijos,
                    "Monto": round(monto_gastos_fijos, 2),
                    "Frecuencia": frecuencia_gastos_fijos,
                    "Promedio Mensual": round(promedio_mensual_gastos_fijos, 2)
                }
                st.session_state.edit_mode_gastos_fijos = False
                st.session_state.edit_index_gastos_fijos = None
        else:
            ente_gastos_fijos = st.text_input("Ente", key="ente_nuevo_gasto_fijo")
            
            # Selección de descripción predefinida para gastos fijos
            opciones_gastos_fijos = [
                "Renta de vivienda", "Fondo de emergencias", "Gas", "Agua", "Energia", "Internet", "Teléfono", 
                "Seguro médico", "Pensión", "Alimentación", "Transporte", 
                "Gasto de Vehículo", "Seguro de Vehículo", "Gasto de mascota"
            ]
            descripcion_gastos_fijos = st.selectbox("Descripción", opciones_gastos_fijos, key="descripcion_nueva_gasto_fijo")
            
            monto_gastos_fijos = st.number_input("Monto", min_value=0.0, step=0.01, key="monto_nuevo_gasto_fijo")
            frecuencia_gastos_fijos = st.selectbox("Frecuencia", ["Mensual", "Quincenal", "Semanal", "Diario", "Anual"], key="frecuencia_nueva_gasto_fijo")
            
            # Calcular promedio mensual basado en la frecuencia
            if frecuencia_gastos_fijos == "Mensual":
                promedio_mensual_gastos_fijos = monto_gastos_fijos
            elif frecuencia_gastos_fijos == "Quincenal":
                promedio_mensual_gastos_fijos = monto_gastos_fijos * 2
            elif frecuencia_gastos_fijos == "Semanal":
                promedio_mensual_gastos_fijos = monto_gastos_fijos * 4
            elif frecuencia_gastos_fijos == "Diario":
                promedio_mensual_gastos_fijos = monto_gastos_fijos * 30
            elif frecuencia_gastos_fijos == "Anual":
                promedio_mensual_gastos_fijos = monto_gastos_fijos / 12
            
            # Botón para agregar el gasto fijo a la tabla
            if st.button("Agregar Gasto Fijo", key="boton_agregar_gasto_fijo"):
                if 'gastos_fijos' not in st.session_state:
                    st.session_state['gastos_fijos'] = []
                
                st.session_state['gastos_fijos'].append({
                    "Ente": ente_gastos_fijos,
                    "Descripción": descripcion_gastos_fijos,
                    "Monto": round(monto_gastos_fijos, 2),
                    "Frecuencia": frecuencia_gastos_fijos,
                    "Promedio Mensual": round(promedio_mensual_gastos_fijos, 2)
                })

    # Mostrar la tabla de gastos fijos en la misma columna central
    with col2:
        if 'gastos_fijos' in st.session_state:
            df_gastos_fijos = pd.DataFrame(st.session_state['gastos_fijos'])
            df_gastos_fijos.index += 1  # Ajuste para que el índice empiece desde 1
            
            # Redondear los valores de las columnas "Monto" y "Promedio Mensual" a 2 decimales
            df_gastos_fijos["Monto"] = df_gastos_fijos["Monto"].apply(lambda x: f"{x:.2f}")
            df_gastos_fijos["Promedio Mensual"] = df_gastos_fijos["Promedio Mensual"].apply(lambda x: f"{x:.2f}")
            
            st.table(df_gastos_fijos)

            # Seleccionar un índice para editar o eliminar
            seleccion_index_gastos_fijos = st.selectbox("Selecciona un índice para editar o eliminar", df_gastos_fijos.index, key="seleccion_index_gastos_fijos") - 1  # Ajustamos el índice restando 1

            # Botón para editar el gasto fijo seleccionado
            if st.button("Editar Gasto Fijo", key="boton_editar_gasto_fijo"):
                gasto_fijo_a_editar = st.session_state['gastos_fijos'][seleccion_index_gastos_fijos]
                st.session_state.edit_index_gastos_fijos = seleccion_index_gastos_fijos
                st.session_state.edit_mode_gastos_fijos = True
                st.session_state.ente_gastos_fijos_edit = gasto_fijo_a_editar["Ente"]
                st.session_state.descripcion_gastos_fijos_edit = gasto_fijo_a_editar["Descripción"]
                st.session_state.monto_gastos_fijos_edit = gasto_fijo_a_editar["Monto"]
                st.session_state.frecuencia_gastos_fijos_edit = gasto_fijo_a_editar["Frecuencia"]

            # Botón para eliminar el gasto fijo seleccionado
            if st.button("Eliminar Gasto Fijo", key="boton_eliminar_gasto_fijo"):
                st.session_state['gastos_fijos'].pop(seleccion_index_gastos_fijos)

            # Calcular y mostrar la suma de la columna Promedio Mensual
            suma_promedio_mensual_gastos_fijos = df_gastos_fijos['Promedio Mensual'].astype(float).sum()
            st.write(f"**Total de Gastos Fijos:** ${suma_promedio_mensual_gastos_fijos:,.2f}")
            
            # Calcular y mostrar el porcentaje de los gastos fijos con respecto a los ingresos
            if 'datos_ingresos' in st.session_state:
                suma_promedio_mensual_ingresos = pd.DataFrame(st.session_state['datos_ingresos'])['Promedio Mensual'].sum()
                if suma_promedio_mensual_ingresos > 0:
                    porcentaje_gastos_fijos = (suma_promedio_mensual_gastos_fijos / suma_promedio_mensual_ingresos) * 100
                    st.write(f"**Porcentaje de Gastos Fijos con respecto a los Ingresos:** {porcentaje_gastos_fijos:.2f}%")


# Contenido de la sexta pestaña: Deuda
with tab5:
    st.header("Deuda")

    # Dividir el formulario en columnas con margen ajustado a la izquierda
    col1, col2, col3 = st.columns([0.01, 1, 1])  # col1 es más pequeña para que col2 esté más a la izquierda

    with col2:  # El formulario está en la columna del medio (ajustada más a la izquierda)
        # Variables para controlar la edición
        if 'edit_mode_deuda' not in st.session_state:
            st.session_state.edit_mode_deuda = False

        # Campos para que el usuario ingrese o edite datos de deuda
        if st.session_state.edit_mode_deuda:
            ente_deuda = st.text_input("Ente", value=st.session_state.get('ente_deuda_edit', ''), key="ente_deuda_edit")
            
            # Selección de descripción predefinida para deuda
            opciones_deuda = ["Préstamo", "Hipoteca", "Tarjeta de Crédito", "Préstamo Personal"]
            descripcion_deuda = st.selectbox("Descripción", opciones_deuda, index=opciones_deuda.index(st.session_state.get('descripcion_deuda_edit', opciones_deuda[0])), key="descripcion_deuda_edit")
            
            monto_deuda = st.number_input("Monto", min_value=0.0, step=0.01, value=st.session_state.get('monto_deuda_edit', 0.0), key="monto_deuda_edit")
            frecuencia_deuda = st.selectbox("Frecuencia", ["Mensual", "Quincenal", "Semanal", "Diario", "Anual"], index=["Mensual", "Quincenal", "Semanal", "Diario", "Anual"].index(st.session_state.get('frecuencia_deuda_edit', 'Mensual')), key="frecuencia_deuda_edit")
            
            # Calcular promedio mensual basado en la frecuencia
            if frecuencia_deuda == "Mensual":
                promedio_mensual_deuda = monto_deuda
            elif frecuencia_deuda == "Quincenal":
                promedio_mensual_deuda = monto_deuda * 2
            elif frecuencia_deuda == "Semanal":
                promedio_mensual_deuda = monto_deuda * 4
            elif frecuencia_deuda == "Diario":
                promedio_mensual_deuda = monto_deuda * 30
            elif frecuencia_deuda == "Anual":
                promedio_mensual_deuda = monto_deuda / 12

            # Botón para actualizar la deuda
            if st.button("Actualizar Deuda", key="boton_actualizar_deuda"):
                st.session_state['deudas'][st.session_state.edit_index_deuda] = {
                    "Ente": ente_deuda,
                    "Descripción": descripcion_deuda,
                    "Monto": round(monto_deuda, 2),
                    "Frecuencia": frecuencia_deuda,
                    "Promedio Mensual": round(promedio_mensual_deuda, 2)
                }
                st.session_state.edit_mode_deuda = False
                st.session_state.edit_index_deuda = None
        else:
            ente_deuda = st.text_input("Ente", key="ente_nuevo_deuda")
            
            # Selección de descripción predefinida para deuda
            opciones_deuda = ["Préstamo", "Hipoteca", "Tarjeta de Crédito", "Préstamo Personal"]
            descripcion_deuda = st.selectbox("Descripción", opciones_deuda, key="descripcion_nueva_deuda")
            
            monto_deuda = st.number_input("Monto", min_value=0.0, step=0.01, key="monto_nuevo_deuda")
            frecuencia_deuda = st.selectbox("Frecuencia", ["Mensual", "Quincenal", "Semanal", "Diario", "Anual"], key="frecuencia_nueva_deuda")
            
            # Calcular promedio mensual basado en la frecuencia
            if frecuencia_deuda == "Mensual":
                promedio_mensual_deuda = monto_deuda
            elif frecuencia_deuda == "Quincenal":
                promedio_mensual_deuda = monto_deuda * 2
            elif frecuencia_deuda == "Semanal":
                promedio_mensual_deuda = monto_deuda * 4
            elif frecuencia_deuda == "Diario":
                promedio_mensual_deuda = monto_deuda * 30
            elif frecuencia_deuda == "Anual":
                promedio_mensual_deuda = monto_deuda / 12
            
            # Botón para agregar la deuda a la tabla
            if st.button("Agregar Deuda", key="boton_agregar_deuda"):
                if 'deudas' not in st.session_state:
                    st.session_state['deudas'] = []
                
                st.session_state['deudas'].append({
                    "Ente": ente_deuda,
                    "Descripción": descripcion_deuda,
                    "Monto": round(monto_deuda, 2),
                    "Frecuencia": frecuencia_deuda,
                    "Promedio Mensual": round(promedio_mensual_deuda, 2)
                })

    # Mostrar la tabla de deudas en la misma columna central
    with col2:
        if 'deudas' in st.session_state:
            df_deudas = pd.DataFrame(st.session_state['deudas'])
            df_deudas.index += 1  # Ajuste para que el índice empiece desde 1
            
            # Redondear los valores de las columnas "Monto" y "Promedio Mensual" a 2 decimales
            df_deudas["Monto"] = df_deudas["Monto"].apply(lambda x: f"{x:.2f}")
            df_deudas["Promedio Mensual"] = df_deudas["Promedio Mensual"].apply(lambda x: f"{x:.2f}")
            
            st.table(df_deudas)

            # Seleccionar un índice para editar o eliminar
            seleccion_index_deuda = st.selectbox("Selecciona un índice para editar o eliminar", df_deudas.index, key="seleccion_index_deuda") - 1  # Ajustamos el índice restando 1

            # Botón para editar la deuda seleccionada
            if st.button("Editar Deuda", key="boton_editar_deuda"):
                deuda_a_editar = st.session_state['deudas'][seleccion_index_deuda]
                st.session_state.edit_index_deuda = seleccion_index_deuda
                st.session_state.edit_mode_deuda = True
                st.session_state.ente_deuda_edit = deuda_a_editar["Ente"]
                st.session_state.descripcion_deuda_edit = deuda_a_editar["Descripción"]
                st.session_state.monto_deuda_edit = deuda_a_editar["Monto"]
                st.session_state.frecuencia_deuda_edit = deuda_a_editar["Frecuencia"]

            # Botón para eliminar la deuda seleccionada
            if st.button("Eliminar Deuda", key="boton_eliminar_deuda"):
                st.session_state['deudas'].pop(seleccion_index_deuda)

            # Calcular y mostrar la suma de la columna Promedio Mensual
            suma_promedio_mensual_deudas = df_deudas['Promedio Mensual'].astype(float).sum()
            st.session_state.suma_promedio_mensual_deudas = suma_promedio_mensual_deudas  # Guardar la suma de deuda en session_state
            st.write(f"**Total de Deudas:** ${suma_promedio_mensual_deudas:,.2f}")
            
            # Calcular y mostrar el porcentaje de las deudas con respecto a los ingresos
            if 'datos_ingresos' in st.session_state:
                suma_promedio_mensual_ingresos = pd.DataFrame(st.session_state['datos_ingresos'])['Promedio Mensual'].sum()
                if suma_promedio_mensual_ingresos > 0:
                    porcentaje_deudas = (suma_promedio_mensual_deudas / suma_promedio_mensual_ingresos) * 100
                    st.write(f"**Porcentaje de Deudas con respecto a los Ingresos:** {porcentaje_deudas:.2f}%")

# Contenido de la quinta pestaña: Gastos Variables
with tab6:
    st.header("Gastos Variables")

    # Dividir el formulario en columnas con margen ajustado a la izquierda
    col1, col2, col3 = st.columns([0.01, 1, 1])  # col1 es más pequeña para que col2 esté más a la izquierda

    with col2:  # El formulario está en la columna del medio (ajustada más a la izquierda)
        # Variables para controlar la edición
        if 'edit_mode_gastos_variables' not in st.session_state:
            st.session_state.edit_mode_gastos_variables = False

        # Campos para que el usuario ingrese o edite datos de gastos variables
        if st.session_state.edit_mode_gastos_variables:
            ente_gastos_variables = st.text_input("Ente", value=st.session_state.get('ente_gastos_variables_edit', ''), key="ente_gastos_variables_edit")
            
            # Selección de descripción predefinida para gastos variables
            opciones_gastos_variables = [
                "Diversión", "Ropa", "Maquillaje y Belleza", "Gastos varios", 
                "Plataforma de Streaming y Música", "Cumpleaños", "Viajes", 
                "Mantenimiento de vivienda", "Deporte o Gym", "Medicamentos", "Navidades", "Hijos", "Familiares"
            ]
            descripcion_gastos_variables = st.selectbox("Descripción", opciones_gastos_variables, index=opciones_gastos_variables.index(st.session_state.get('descripcion_gastos_variables_edit', opciones_gastos_variables[0])), key="descripcion_gastos_variables_edit")
            
            monto_gastos_variables = st.number_input("Monto", min_value=0.0, step=0.01, value=st.session_state.get('monto_gastos_variables_edit', 0.0), key="monto_gastos_variables_edit")
            frecuencia_gastos_variables = st.selectbox("Frecuencia", ["Mensual", "Quincenal", "Semanal", "Diario", "Anual"], index=["Mensual", "Quincenal", "Semanal", "Diario", "Anual"].index(st.session_state.get('frecuencia_gastos_variables_edit', 'Mensual')), key="frecuencia_gastos_variables_edit")
            
            # Calcular promedio mensual basado en la frecuencia
            if frecuencia_gastos_variables == "Mensual":
                promedio_mensual_gastos_variables = monto_gastos_variables
            elif frecuencia_gastos_variables == "Quincenal":
                promedio_mensual_gastos_variables = monto_gastos_variables * 2
            elif frecuencia_gastos_variables == "Semanal":
                promedio_mensual_gastos_variables = monto_gastos_variables * 4
            elif frecuencia_gastos_variables == "Diario":
                promedio_mensual_gastos_variables = monto_gastos_variables * 30
            elif frecuencia_gastos_variables == "Anual":
                promedio_mensual_gastos_variables = monto_gastos_variables / 12

            # Botón para actualizar el gasto variable
            if st.button("Actualizar Gasto Variable", key="boton_actualizar_gasto_variable"):
                st.session_state['gastos_variables'][st.session_state.edit_index_gastos_variables] = {
                    "Ente": ente_gastos_variables,
                    "Descripción": descripcion_gastos_variables,
                    "Monto": round(monto_gastos_variables, 2),
                    "Frecuencia": frecuencia_gastos_variables,
                    "Promedio Mensual": round(promedio_mensual_gastos_variables, 2)
                }
                st.session_state.edit_mode_gastos_variables = False
                st.session_state.edit_index_gastos_variables = None
        else:
            ente_gastos_variables = st.text_input("Ente", key="ente_nuevo_gasto_variable")
            
            # Selección de descripción predefinida para gastos variables
            opciones_gastos_variables = [
                "Diversión", "Ropa", "Maquillaje y Belleza", "Gastos varios", 
                "Plataforma de Streaming y Música", "Cumpleaños", "Viajes", 
                "Mantenimiento de vivienda", "Deporte o Gym", "Medicamentos", "Navidades", "Hijos", "Familiares"
            ]
            descripcion_gastos_variables = st.selectbox("Descripción", opciones_gastos_variables, key="descripcion_nueva_gasto_variable")
            
            monto_gastos_variables = st.number_input("Monto", min_value=0.0, step=0.01, key="monto_nuevo_gasto_variable")
            frecuencia_gastos_variables = st.selectbox("Frecuencia", ["Mensual", "Quincenal", "Semanal", "Diario", "Anual"], key="frecuencia_nueva_gasto_variable")
            
            # Calcular promedio mensual basado en la frecuencia
            if frecuencia_gastos_variables == "Mensual":
                promedio_mensual_gastos_variables = monto_gastos_variables
            elif frecuencia_gastos_variables == "Quincenal":
                promedio_mensual_gastos_variables = monto_gastos_variables * 2
            elif frecuencia_gastos_variables == "Semanal":
                promedio_mensual_gastos_variables = monto_gastos_variables * 4
            elif frecuencia_gastos_variables == "Diario":
                promedio_mensual_gastos_variables = monto_gastos_variables * 30
            elif frecuencia_gastos_variables == "Anual":
                promedio_mensual_gastos_variables = monto_gastos_variables / 12
            
            # Botón para agregar el gasto variable a la tabla
            if st.button("Agregar Gasto Variable", key="boton_agregar_gasto_variable"):
                if 'gastos_variables' not in st.session_state:
                    st.session_state['gastos_variables'] = []
                
                st.session_state['gastos_variables'].append({
                    "Ente": ente_gastos_variables,
                    "Descripción": descripcion_gastos_variables,
                    "Monto": round(monto_gastos_variables, 2),
                    "Frecuencia": frecuencia_gastos_variables,
                    "Promedio Mensual": round(promedio_mensual_gastos_variables, 2)
                })

    # Mostrar la tabla de gastos variables
    with col2:  # La tabla también estará en la columna del medio
        if 'gastos_variables' in st.session_state:
            df_gastos_variables = pd.DataFrame(st.session_state['gastos_variables'])
            df_gastos_variables.index += 1  # Ajuste para que el índice empiece desde 1
            
            # Redondear los valores de las columnas "Monto" y "Promedio Mensual" a 2 decimales
            df_gastos_variables["Monto"] = df_gastos_variables["Monto"].apply(lambda x: f"{x:.2f}")
            df_gastos_variables["Promedio Mensual"] = df_gastos_variables["Promedio Mensual"].apply(lambda x: f"{x:.2f}")
            
            st.table(df_gastos_variables)

            # Seleccionar un índice para editar o eliminar
            seleccion_index_gastos_variables = st.selectbox("Selecciona un índice para editar o eliminar", df_gastos_variables.index, key="seleccion_index_gastos_variables") - 1  # Ajustamos el índice restando 1

            # Botón para editar el gasto variable seleccionado
            if st.button("Editar Gasto Variable", key="boton_editar_gasto_variable"):
                gasto_variable_a_editar = st.session_state['gastos_variables'][seleccion_index_gastos_variables]
                st.session_state.edit_index_gastos_variables = seleccion_index_gastos_variables
                st.session_state.edit_mode_gastos_variables = True
                st.session_state.ente_gastos_variables_edit = gasto_variable_a_editar["Ente"]
                st.session_state.descripcion_gastos_variables_edit = gasto_variable_a_editar["Descripción"]
                st.session_state.monto_gastos_variables_edit = gasto_variable_a_editar["Monto"]
                st.session_state.frecuencia_gastos_variables_edit = gasto_variable_a_editar["Frecuencia"]

            # Botón para eliminar el gasto variable seleccionado
            if st.button("Eliminar Gasto Variable", key="boton_eliminar_gasto_variable"):
                st.session_state['gastos_variables'].pop(seleccion_index_gastos_variables)

            # Calcular y mostrar la suma de la columna Promedio Mensual
            suma_promedio_mensual_gastos_variables = df_gastos_variables['Promedio Mensual'].astype(float).sum()
            st.write(f"**Total de Gastos Variables:** ${suma_promedio_mensual_gastos_variables:,.2f}")
            
            # Calcular y mostrar el porcentaje de los gastos variables con respecto a los ingresos
            if 'datos_ingresos' in st.session_state:
                suma_promedio_mensual_ingresos = pd.DataFrame(st.session_state['datos_ingresos'])['Promedio Mensual'].sum()
                if suma_promedio_mensual_ingresos > 0:
                    porcentaje_gastos_variables = (suma_promedio_mensual_gastos_variables / suma_promedio_mensual_ingresos) * 100
                    st.write(f"**Porcentaje de Gastos Variables con respecto a los Ingresos:** {porcentaje_gastos_variables:.2f}%")

   
                
# Contenido de la séptima pestaña: Ahorro a Corto y Largo Plazo
with tab7:
    st.header("Ahorro a Corto y Largo Plazo")

    # Dividir el formulario en columnas con margen ajustado a la izquierda
    col1, col2, col3 = st.columns([0.01, 1, 1])  # col1 es más pequeña para que col2 esté más a la izquierda

    with col2:  # El formulario está en la columna del medio (ajustada más a la izquierda)
        # Variables para controlar la edición
        if 'edit_mode_ahorro' not in st.session_state:
            st.session_state.edit_mode_ahorro = False

        # Campos para que el usuario ingrese o edite datos de ahorro
        if st.session_state.edit_mode_ahorro:
            ente_ahorro = st.text_input("Ente", value=st.session_state.get('ente_ahorro_edit', ''), key="ente_ahorro_edit")
            
            # Selección de descripción predefinida para ahorro
            opciones_ahorro = ["Corto Plazo", "Largo Plazo"]
            descripcion_ahorro = st.selectbox("Descripción", opciones_ahorro, index=opciones_ahorro.index(st.session_state.get('descripcion_ahorro_edit', opciones_ahorro[0])), key="descripcion_ahorro_edit")
            
            monto_ahorro = st.number_input("Monto", min_value=0.0, step=0.01, value=st.session_state.get('monto_ahorro_edit', 0.0), key="monto_ahorro_edit")
            frecuencia_ahorro = st.selectbox("Frecuencia", ["Mensual", "Quincenal", "Semanal", "Diario", "Anual"], index=["Mensual", "Quincenal", "Semanal", "Diario", "Anual"].index(st.session_state.get('frecuencia_ahorro_edit', 'Mensual')), key="frecuencia_ahorro_edit")
            
            # Calcular promedio mensual basado en la frecuencia
            if frecuencia_ahorro == "Mensual":
                promedio_mensual_ahorro = monto_ahorro
            elif frecuencia_ahorro == "Quincenal":
                promedio_mensual_ahorro = monto_ahorro * 2
            elif frecuencia_ahorro == "Semanal":
                promedio_mensual_ahorro = monto_ahorro * 4
            elif frecuencia_ahorro == "Diario":
                promedio_mensual_ahorro = monto_ahorro * 30
            elif frecuencia_ahorro == "Anual":
                promedio_mensual_ahorro = monto_ahorro / 12

            # Botón para actualizar el ahorro
            if st.button("Actualizar Ahorro", key="boton_actualizar_ahorro"):
                st.session_state['ahorro'][st.session_state.edit_index_ahorro] = {
                    "Ente": ente_ahorro,
                    "Descripción": descripcion_ahorro,
                    "Monto": round(monto_ahorro, 2),
                    "Frecuencia": frecuencia_ahorro,
                    "Promedio Mensual": round(promedio_mensual_ahorro, 2)
                }
                st.session_state.edit_mode_ahorro = False
                st.session_state.edit_index_ahorro = None

        else:
            ente_ahorro = st.text_input("Ente", key="ente_nuevo_ahorro")
            
            # Selección de descripción predefinida para ahorro
            opciones_ahorro = ["Corto Plazo", "Largo Plazo"]
            descripcion_ahorro = st.selectbox("Descripción", opciones_ahorro, key="descripcion_nueva_ahorro")
            
            monto_ahorro = st.number_input("Monto", min_value=0.0, step=0.01, key="monto_nuevo_ahorro")
            frecuencia_ahorro = st.selectbox("Frecuencia", ["Mensual", "Quincenal", "Semanal", "Diario", "Anual"], key="frecuencia_nueva_ahorro")
            
            # Calcular promedio mensual basado en la frecuencia
            if frecuencia_ahorro == "Mensual":
                promedio_mensual_ahorro = monto_ahorro
            elif frecuencia_ahorro == "Quincenal":
                promedio_mensual_ahorro = monto_ahorro * 2
            elif frecuencia_ahorro == "Semanal":
                promedio_mensual_ahorro = monto_ahorro * 4
            elif frecuencia_ahorro == "Diario":
                promedio_mensual_ahorro = monto_ahorro * 30
            elif frecuencia_ahorro == "Anual":
                promedio_mensual_ahorro = monto_ahorro / 12
            
            # Botón para agregar el ahorro a la tabla
            if st.button("Agregar Ahorro", key="boton_agregar_ahorro"):
                if 'ahorro' not in st.session_state:
                    st.session_state['ahorro'] = []
                
                st.session_state['ahorro'].append({
                    "Ente": ente_ahorro,
                    "Descripción": descripcion_ahorro,
                    "Monto": round(monto_ahorro, 2),
                    "Frecuencia": frecuencia_ahorro,
                    "Promedio Mensual": round(promedio_mensual_ahorro, 2)
                })

    # Mostrar la tabla de ahorros
    with col2:  # La tabla también estará en la columna del medio
        if 'ahorro' in st.session_state:
            df_ahorro = pd.DataFrame(st.session_state['ahorro'])
            df_ahorro.index += 1  # Ajuste para que el índice empiece desde 1
            
            # Redondear los valores de las columnas "Monto" y "Promedio Mensual" a 2 decimales
            df_ahorro["Monto"] = df_ahorro["Monto"].apply(lambda x: f"{x:.2f}")
            df_ahorro["Promedio Mensual"] = df_ahorro["Promedio Mensual"].apply(lambda x: f"{x:.2f}")
            
            st.table(df_ahorro)

            # Calcular y mostrar la suma de la columna Promedio Mensual
            suma_promedio_mensual_corto = df_ahorro[df_ahorro['Descripción'] == 'Corto Plazo']['Promedio Mensual'].astype(float).sum()
            suma_promedio_mensual_largo = df_ahorro[df_ahorro['Descripción'] == 'Largo Plazo']['Promedio Mensual'].astype(float).sum()

            st.write(f"**Total de Ahorro a Corto Plazo:** ${suma_promedio_mensual_corto:,.2f}")
            st.write(f"**Total de Ahorro a Largo Plazo:** ${suma_promedio_mensual_largo:,.2f}")

            # Calcular el total de ahorro
            total_ahorro = suma_promedio_mensual_corto + suma_promedio_mensual_largo
            st.write(f"**Total de Ahorro:** ${total_ahorro:,.2f}")
            st.session_state.total_ahorro = total_ahorro  # Guardar en session_state para usar en la pestaña 10

            # Guardar ahorros por tipo en session_state para su uso en la pestaña de distribución de gastos
            st.session_state.ahorro_corto_plazo = suma_promedio_mensual_corto
            st.session_state.ahorro_largo_plazo = suma_promedio_mensual_largo
            
            # Calcular el porcentaje de ahorro con respecto a los ingresos
            if 'datos_ingresos' in st.session_state:
                total_ingresos = pd.DataFrame(st.session_state['datos_ingresos'])['Promedio Mensual'].sum()
                porcentaje_ahorro = (total_ahorro / total_ingresos) * 100 if total_ingresos > 0 else 0
                st.write(f"**Porcentaje de Ahorro con respecto a los Ingresos:** {porcentaje_ahorro:.2f}%")
            else:
                st.warning("No se han ingresado datos de ingresos.")

            # Seleccionar un índice para editar o eliminar
            seleccion_index_ahorro = st.selectbox("Selecciona un índice para editar o eliminar", df_ahorro.index, key="seleccion_index_ahorro") - 1  # Ajustamos el índice restando 1

            # Botón para editar el ahorro seleccionado
            if st.button("Editar Ahorro", key="boton_editar_ahorro"):
                ahorro_a_editar = st.session_state['ahorro'][seleccion_index_ahorro]
                st.session_state.edit_index_ahorro = seleccion_index_ahorro
                st.session_state.edit_mode_ahorro = True
                st.session_state.ente_ahorro_edit = ahorro_a_editar["Ente"]
                st.session_state.descripcion_ahorro_edit = ahorro_a_editar["Descripción"]
                st.session_state.monto_ahorro_edit = ahorro_a_editar["Monto"]
                st.session_state.frecuencia_ahorro_edit = ahorro_a_editar["Frecuencia"]

            # Botón para eliminar el ahorro seleccionado
            if st.button("Eliminar Ahorro", key="boton_eliminar_ahorro"):
                st.session_state['ahorro'].pop(seleccion_index_ahorro)




# Contenido de la pestaña: Patrimonio
with tab8:  
    st.header("Patrimonio")
    
    # Dividir el formulario en columnas con margen ajustado a la izquierda
    col1, col2, col3 = st.columns([0.01, 1, 1])  # col1 es más pequeña para que col2 esté más a la izquierda

    with col2:  # El formulario está en la columna del medio (ajustada más a la izquierda)
        # Campos para que el usuario ingrese datos
        activo = st.text_input("Activo", key="activo")
        valor_activo = st.number_input("Valor del Activo", min_value=0.0, step=0.01, key="valor_activo")
        pasivo = st.number_input("Pasivo", min_value=0.0, step=0.01, key="pasivo")
        
        # Calcular la diferencia entre el activo y el pasivo
        diferencia = valor_activo - pasivo
        
        # Botón para agregar la entrada a la tabla
        if st.button("Agregar Patrimonio", key='boton_patrimonio'):
            if 'patrimonio' not in st.session_state:
                st.session_state['patrimonio'] = []
            
            st.session_state['patrimonio'].append({
                "Activo": activo,
                "Valor del Activo": round(valor_activo, 2),
                "Pasivo": round(pasivo, 2),
                "Patrimonio": round(diferencia, 2)
            })

    with col2:  # La tabla también estará en la columna del medio
        # Mostrar la tabla de patrimonio
        if 'patrimonio' in st.session_state:
            df_patrimonio = pd.DataFrame(st.session_state['patrimonio'])
            
            # Redondear los valores de las columnas "Valor del Activo", "Pasivo", y "Patrimonio" a 2 decimales
            df_patrimonio["Valor del Activo"] = df_patrimonio["Valor del Activo"].apply(lambda x: f"{x:.2f}")
            df_patrimonio["Pasivo"] = df_patrimonio["Pasivo"].apply(lambda x: f"{x:.2f}")
            df_patrimonio["Patrimonio"] = df_patrimonio["Patrimonio"].apply(lambda x: f"{x:.2f}")
            
            st.table(df_patrimonio)
            
            # Calcular y mostrar las sumas de las columnas
            suma_valor_activo = df_patrimonio['Valor del Activo'].astype(float).sum()
            suma_pasivo = df_patrimonio['Pasivo'].astype(float).sum()
            suma_diferencia = df_patrimonio['Patrimonio'].astype(float).sum()
            
            st.write(f"**Total de Activos:** ${suma_valor_activo:,.2f}")
            st.write(f"**Total de Pasivos:** ${suma_pasivo:,.2f}")
            st.write(f"**Total de Patrimonio:** ${suma_diferencia:,.2f}")

# Contenido de la pestaña 9: Diagnóstico
with tab9:  # Ahora la pestaña 9
    st.header("Diagnóstico")
    
    # Configuración para ajustar el tamaño de las figuras
    fig_size = 260  # Ajusta este valor para cambiar el tamaño

    # Crear los gráficos circulares (gauges) con el símbolo de porcentaje
    def crear_grafico(value, title, color):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            number={'suffix': "%"},  # Agrega el símbolo de porcentaje
            title={'text': title},
            gauge={'axis': {'range': [0, 100]},
                    'bar': {'color': color}}
        ))
        fig.update_layout(width=fig_size, height=fig_size)
        return fig

    # Gráficos para Estructura Ideal
    fig_gasto_fijo = crear_grafico(50, "Gasto Fijo", "darkblue")
    fig_gasto_variable = crear_grafico(20, "Gasto Variable", "blue")
    fig_ahorro_corto = crear_grafico(20, "Ahorro Corto P.", "darkgreen")
    fig_ahorro_largo = crear_grafico(10, "Ahorro Largo P.", "darkgreen")

    # Título de Estructura Ideal
    st.subheader("Estructura Ideal")

    # Mostrar los gráficos en una fila (uno al lado del otro)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.plotly_chart(fig_gasto_fijo, use_container_width=True)

    with col2:
        st.plotly_chart(fig_gasto_variable, use_container_width=True)

    with col3:
        st.plotly_chart(fig_ahorro_corto, use_container_width=True)

    with col4:
        st.plotly_chart(fig_ahorro_largo, use_container_width=True)
        
    st.markdown("---")  # Línea divisoria

    # Estructura Actual
    st.subheader("Estructura Actual")
    
    # Calcular los porcentajes actuales
    if 'datos_ingresos' in st.session_state:
        total_ingresos = pd.DataFrame(st.session_state['datos_ingresos'])['Promedio Mensual'].sum()
    else:
        total_ingresos = 1  # Evitar división por cero
    
    if 'gastos_fijos' in st.session_state:
        total_gastos_fijos = pd.DataFrame(st.session_state['gastos_fijos'])['Promedio Mensual'].sum()
    else:
        total_gastos_fijos = 0
    
    if 'gastos_variables' in st.session_state:
        total_gastos_variables = pd.DataFrame(st.session_state['gastos_variables'])['Promedio Mensual'].sum()
    else:
        total_gastos_variables = 0

    # Incluir el total de deudas en el cálculo de gastos fijos y totales
    if 'suma_promedio_mensual_deudas' in st.session_state:
        total_deudas = st.session_state['suma_promedio_mensual_deudas']
    else:
        total_deudas = 0

    total_gastos_fijos += total_deudas  # Sumar deudas a gastos fijos

    if 'ahorro' in st.session_state:
        df_ahorro = pd.DataFrame(st.session_state['ahorro'])
        total_ahorro_corto_plazo = df_ahorro[df_ahorro['Descripción'] == 'Corto Plazo']['Promedio Mensual'].sum()
        total_ahorro_largo_plazo = df_ahorro[df_ahorro['Descripción'] == 'Largo Plazo']['Promedio Mensual'].sum()
    else:
        total_ahorro_corto_plazo = 0
        total_ahorro_largo_plazo = 0
    
    # Calculando los porcentajes
    porcentaje_ahorro_corto = (total_ahorro_corto_plazo / total_ingresos) * 100 if total_ingresos > 0 else 0
    porcentaje_ahorro_largo = (total_ahorro_largo_plazo / total_ingresos) * 100 if total_ingresos > 0 else 0
    porcentaje_gastos_variables = (total_gastos_variables / total_ingresos) * 100 if total_ingresos > 0 else 0
    porcentaje_gastos_fijos = (total_gastos_fijos / total_ingresos) * 100 if total_ingresos > 0 else 0
    
    # Crear gráficos para Estructura Actual usando los porcentajes calculados
    fig_gasto_fijo_actual = crear_grafico(porcentaje_gastos_fijos, "Gasto Fijo", "darkblue")
    fig_gasto_variable_actual = crear_grafico(porcentaje_gastos_variables, "Gasto Variable", "blue")
    fig_ahorro_corto_actual = crear_grafico(porcentaje_ahorro_corto, "Ahorro Corto P.", "darkgreen")
    fig_ahorro_largo_actual = crear_grafico(porcentaje_ahorro_largo, "Ahorro Largo P.", "darkgreen")
    
    # Mostrar los gráficos en una fila (uno al lado del otro)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.plotly_chart(fig_gasto_fijo_actual, use_container_width=True)

    with col2:
        st.plotly_chart(fig_gasto_variable_actual, use_container_width=True)

    with col3:
        st.plotly_chart(fig_ahorro_corto_actual, use_container_width=True)

    with col4:
        st.plotly_chart(fig_ahorro_largo_actual, use_container_width=True)

    st.markdown("---")  # Línea divisoria
    
    # Cálculo de la Edad y Años Activos Restantes
    st.subheader("Proyección de Ingresos y Ahorros")
    
    # Recuperar la edad de la pestaña "Datos Personales"
    if 'edad' in st.session_state:
        edad = st.session_state['edad']
    else:
        edad = 0  # Si no hay datos, asumir 0

    anos_restantes = 65 - edad if edad < 65 else 0
    st.markdown(f"**Edad Actual:** {edad} años")
    st.markdown(f"**Años Restantes Hasta la Jubilación (65 años):** {anos_restantes} años")

    # Cálculo de Ingresos Generados y Potenciales basado en el historial de ingresos
    if 'historico_ingresos' in st.session_state:
        df_historial_ingresos = pd.DataFrame(st.session_state['historico_ingresos'])
        ingresos_historicos_totales = st.session_state.get('total_ingresos_historicos', 0)  # Utiliza el total calculado en la pestaña 2
        ingresos_anuales_actuales = df_historial_ingresos['Cantidad Mensual'].sum() * 12  # Ingresos anuales promedio
        ingresos_potenciales = ingresos_anuales_actuales * anos_restantes  # Proyección de ingresos potenciales
    else:
        ingresos_historicos_totales = 0
        ingresos_potenciales = 0

    st.markdown(f"**Ingresos Generados Hasta la Fecha:** ${ingresos_historicos_totales:,.2f}")
    st.markdown(f"**Ingresos Potenciales Hasta la Jubilación:** ${ingresos_potenciales:,.2f}")

    # Cálculo del porcentaje generado con respecto al monto potencial
    if ingresos_potenciales > 0:
        porcentaje_generado = (ingresos_historicos_totales / ingresos_potenciales) * 100
    else:
        porcentaje_generado = 0

    # Mostrar el porcentaje generado
    st.markdown(f"**Porcentaje Generado con respecto al Monto Potencial:** {porcentaje_generado:.2f}%")

    st.markdown("---")  # Línea divisoria

    # Evaluación Final de Ahorros
    st.subheader("Evaluación Final")

    # Calcular total de ahorros, gastos y mostrar ingresos
    ahorro_actual = total_ahorro_corto_plazo + total_ahorro_largo_plazo
    total_gastos = total_gastos_fijos + total_gastos_variables

    if total_ingresos > total_gastos:
        st.success("La persona está ahorrando.")
    else:
        st.warning("La persona no está ahorrando.")

    st.markdown(f"**Total Ingresos:** ${total_ingresos:,.2f}")
    st.markdown(f"**Total Ahorro Actual:** ${ahorro_actual:,.2f}")
    st.markdown(f"**Total Gastos:** ${total_gastos:,.2f}")



from fpdf import FPDF
from io import BytesIO
import plotly.graph_objs as go

# Contenido de la pestaña 10: Reporte
with tab10:  # Nueva pestaña para el reporte
    # Encabezado principal
    st.markdown("""
    <div style='background-color: #1a2b3c; padding: 20px;'>
        <h1 style='color: white; text-align: center; font-size: 36px;'>AG Brothers Reporte</h1>
        <h2 style='color: white; text-align: center; font-size: 28px;'>Reporte Financiero</h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")  # Línea divisoria

    # Resumen General
    st.subheader("Resumen General")
    col1, col2, col3, col4 = st.columns(4)

    # Primer grupo de etiquetas
    with col1:
        st.markdown(f"<h3>Total Ingresos:</h3> <p>${total_ingresos:,.2f}</p>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h3>Total Ahorros:</h3> <p>${ahorro_actual:,.2f}</p>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<h3>Total Gastos:</h3> <p>${total_gastos:,.2f}</p>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<h3>Porcentaje de Ahorro:</h3> <p>{(ahorro_actual / total_ingresos) * 100:.2f}%</p>", unsafe_allow_html=True)

    # Segunda fila de etiquetas (detalles de los gastos)
    col5, col6, col7 = st.columns(3)
    with col5:
        st.markdown(f"<h3>Gastos Fijos:</h3> <p>${total_gastos_fijos:,.2f}</p>", unsafe_allow_html=True)
    with col6:
        st.markdown(f"<h3>Deuda:</h3> <p>${total_deudas:,.2f}</p>", unsafe_allow_html=True)
    with col7:
        st.markdown(f"<h3>Gastos Variables:</h3> <p>${total_gastos_variables:,.2f}</p>", unsafe_allow_html=True)

    # Añadir una línea divisoria y un espaciado claro entre las secciones
    st.markdown("<hr style='border: 1px solid #333; margin-top: 30px; margin-bottom: 30px;'>", unsafe_allow_html=True)

    # Progreso hacia la Jubilación y Distribución de Gastos
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Progreso hacia la Jubilación")
        porcentaje_generado = (ingresos_historicos_totales / ingresos_potenciales) * 100 if ingresos_potenciales > 0 else 0

        fig_barra_progreso = go.Figure(go.Indicator(
            mode="gauge+number",
            value=porcentaje_generado,
            number={'suffix': "%", 'font': {'size': 40}},  # Tamaño del porcentaje
            title={'text': f"{porcentaje_generado:.2f}% Generado", 'font': {'size': 22}},
            gauge={'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                   'bar': {'color': "green"},
                   'bgcolor': "white",
                   'borderwidth': 2,
                   'bordercolor': "gray",
                   'steps': [{'range': [0, porcentaje_generado], 'color': 'lightgreen'}],
                   'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 100}}
        ))

        fig_barra_progreso.update_layout(
            margin=dict(l=20, r=20, t=50, b=50),
            height=250,
        )

        st.plotly_chart(fig_barra_progreso, use_container_width=True)

        st.markdown(f"<p style='text-align: left; color: #333333; font-size: 20px;'>Monto Total por Generar: ${ingresos_potenciales:,.2f}</p>", unsafe_allow_html=True)

    with col2:
        st.subheader("Distribución de Gastos")
        
        # Usar las variables correctas que se calculan para la estructura financiera
        porcentaje_deuda = (total_deudas / total_ingresos) * 100
        porcentaje_gastos_fijos_sin_deuda = (total_gastos_fijos / total_ingresos) * 100  
        porcentaje_gastos_variables = (total_gastos_variables / total_ingresos) * 100
        porcentaje_ahorro_corto = (total_ahorro_corto_plazo / total_ingresos) * 100
        porcentaje_ahorro_largo = (total_ahorro_largo_plazo / total_ingresos) * 100

        # Crear la gráfica de pastel con todos los porcentajes de gastos y ahorros
        labels = ['Deudas', 'Gastos Fijos', 'Gastos Variables', 'Ahorro a Corto Plazo', 'Ahorro a Largo Plazo']
        values = [porcentaje_deuda, porcentaje_gastos_fijos_sin_deuda, porcentaje_gastos_variables, porcentaje_ahorro_corto, porcentaje_ahorro_largo]

        fig_distribucion_gastos = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            textinfo='label+percent',  # Mostrar etiquetas y porcentajes en las etiquetas
            hole=.3,
            hoverinfo='label'  # Mostrar solo la etiqueta al pasar el cursor, sin el valor
        )])

        fig_distribucion_gastos.update_layout(
            margin=dict(l=20, r=20, t=50, b=50),
            height=350,
        )

        st.plotly_chart(fig_distribucion_gastos, use_container_width=True)

    st.markdown("---")  # Línea divisoria

    # Conclusiones y Recomendaciones
    st.subheader("Conclusiones y Recomendaciones")
    st.text_area("Notas y Conclusiones", placeholder="Escribe aquí tus conclusiones y recomendaciones...")

    st.markdown("---")  # Línea divisoria

    # Generar y Descargar Reporte en PDF
    st.subheader("Generar Reporte en PDF")

    # Función para crear el PDF
    def generar_pdf():
        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Reporte Financiero Completo", ln=True, align='C')

        pdf.ln(10)
        pdf.cell(200, 10, txt="Resumen General", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Total Ingresos: ${total_ingresos:,.2f}", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Total Ahorros: ${ahorro_actual:,.2f}", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Total Gastos: ${total_gastos:,.2f}", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Porcentaje de Ahorro: {(ahorro_actual / total_ingresos) * 100:.2f}%", ln=True, align='L')

        pdf.ln(10)
        pdf.cell(200, 10, txt="Distribución de Gastos", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Gastos Fijos: {porcentaje_gastos_fijos_sin_deuda:.2f}%", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Gastos Variables: {porcentaje_gastos_variables:.2f}%", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Deuda: {porcentaje_deuda:.2f}%", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Ahorro a Corto Plazo: {porcentaje_ahorro_corto:.2f}%", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Ahorro a Largo Plazo: {porcentaje_ahorro_largo:.2f}%", ln=True, align='L')

        return pdf

    if st.button("Generar PDF"):
        pdf = generar_pdf()
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        pdf_data = pdf_output.getvalue()
        st.download_button(label="Descargar PDF", data=pdf_data, file_name="reporte_financiero.pdf", mime="application/pdf")