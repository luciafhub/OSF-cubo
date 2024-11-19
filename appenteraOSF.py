import streamlit as st
import pandas as pd
import altair as alt
import requests

# Configuración inicial
osf_token = 'TVJALoFX8HrZ5YEbXeEMYYDBb9EL30qdDf2hA6jbXSOzb8C3P2QDxPY8LCAgnBgBax99n9'
project_id = 'h2te3'
headers = {'Authorization': f'Bearer {osf_token}'}

# Función para cargar archivos desde OSF
@st.cache_data(ttl=60)  # Cachear los datos para mejorar rendimiento y actualizar cada minuto
def cargar_datos_desde_osf(file_id):
    url = f'https://files.osf.io/v1/resources/{project_id}/providers/osfstorage/{file_id}/?direct=true'
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Verificar si hubo un error en la descarga
    return pd.read_csv(pd.compat.StringIO(response.text))

# IDs de los archivos en OSF (actualízalos con los correctos)
file_ids = {
    "Enfermeras": "osfstorage/6729eeb4b7aee73e2402757d",  # Reemplaza con el file_id real
    "Medidas": "osfstorage/6729eec61bad4ca7a3baa1aa",        # Reemplaza con el file_id real
    "Pacientes_Enfermeras": "osfstorage/672a0d0f1728a8447dbaa565"  # Reemplaza con el file_id real
}

# Cargar cada tabla
enfermeras = cargar_datos_desde_osf(file_ids["Enfermeras"])
medidas = cargar_datos_desde_osf(file_ids["Medidas"])
pacientes_enfermeras = cargar_datos_desde_osf(file_ids["Pacientes_Enfermeras"])

# Título de la aplicación
st.title("Prueba - Cubolab")

# Menú de selección de tabla
tabla_seleccionada = st.selectbox("Selecciona la tabla para analizar:", 
                    ["Enfermeras", "Medidas", "Pacientes_Enfermeras"])

# Mostrar y analizar cada tabla en función de la selección

if tabla_seleccionada == "Enfermeras":
    st.write("### Tabla: Enfermeras")
    st.dataframe(enfermeras.head())

    analisis = st.selectbox("Selecciona el análisis para Enfermeras:", 
                            ["Distribución por Sexo", "Distribución por Rol", "Edad por Rol", "Rol por Sexo y Edad"])

    if analisis == "Distribución por Sexo":
        st.write("Distribución de Enfermeras por Sexo")
        st.bar_chart(enfermeras["sexo"].value_counts())

    elif analisis == "Distribución por Rol":
        st.write("Distribución de Enfermeras por Rol")
        st.bar_chart(enfermeras["rol"].value_counts())

    elif analisis == "Edad por Rol":
        st.write("Distribución de Edad por Rol")
        chart = alt.Chart(enfermeras).mark_boxplot().encode(
            x='rol:N',
            y='edad:Q',
            color='rol:N'
        )
        st.altair_chart(chart, use_container_width=True)

    elif analisis == "Rol por Sexo y Edad":
        st.write("### Análisis de Rol según Sexo y Edad")
        
        def grafico_rol_por_sexo(rol_nombre, df):
            st.write(f"**Distribución de Sexo para el rol: {rol_nombre}**")
            data_rol = df[df['rol'] == rol_nombre]
            sexo_counts = data_rol['sexo'].value_counts()
            st.write(alt.Chart(pd.DataFrame({'Sexo': sexo_counts.index, 'Cantidad': sexo_counts.values})).mark_arc().encode(
                theta='Cantidad',
                color='Sexo',
                tooltip=['Sexo', 'Cantidad']
            ).properties(title=f"Distribución de Sexo para {rol_nombre}"))

        for rol_nombre in enfermeras['rol'].unique():
            grafico_rol_por_sexo(rol_nombre, enfermeras)


elif tabla_seleccionada == "Medidas":
    st.write("### Tabla: Medidas")
    st.dataframe(medidas.head())

    analisis = st.selectbox("Selecciona el análisis para Medidas:", 
                            ["Estado Emocional de Pacientes", "Niveles de Batería", "Evolución del Estado de Ánimo de un Paciente"])

    if analisis == "Estado Emocional de Pacientes":
        st.write("Distribución del Estado Emocional de los Pacientes")
        st.bar_chart(medidas["emocion"].value_counts())

    elif analisis == "Niveles de Batería":
        st.write("Distribución de los Niveles de Batería de los Sensores")
        chart = alt.Chart(medidas).mark_bar().encode(
            x=alt.X("bateria:Q", bin=True),
            y='count()'
        )
        st.altair_chart(chart, use_container_width=True)

    elif analisis == "Evolución del Estado de Ánimo de un Paciente":
        st.write("### Evolución del Estado de Ánimo de un Paciente")
        
        paciente_id = st.text_input("Introduce el ID del paciente que deseas consultar:", value="1")
        paciente_data = medidas[medidas['id_paciente'] == int(paciente_id)]

        if not paciente_data.empty:
            paciente_data['fecha'] = pd.to_datetime(paciente_data['fecha'])
            paciente_data = paciente_data.sort_values(by='fecha')
            chart = alt.Chart(paciente_data).mark_line().encode(
                x='fecha:T',
                y='emocion:Q',
                tooltip=['fecha:T', 'emocion:Q']
            ).properties(
                title=f"Evolución del Estado de Ánimo del Paciente {paciente_id}"
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.write(f"No se encontraron datos para el paciente con ID {paciente_id}.")


elif tabla_seleccionada == "Pacientes_Enfermeras":
    st.write("### Tabla: Pacientes_Enfermeras")
    pacientes_enfermeras = cargar_datos_desde_osf(file_ids["Pacientes_Enfermeras"])  # Recargar para obtener la última versión
    st.dataframe(pacientes_enfermeras)

    analisis = st.selectbox("Selecciona el análisis para Pacientes_Enfermeras:", 
                            ["Cantidad de Pacientes por Enfermera", "Enfermeras Asignadas a Pacientes"])

    if analisis == "Cantidad de Pacientes por Enfermera":
        st.write("Distribución de Pacientes por Enfermera")
        conteo_enfermeras = pacientes_enfermeras["id_enfermera"].value_counts().reset_index()
        conteo_enfermeras.columns = ['id_enfermera', 'cantidad_pacientes']
        st.bar_chart(conteo_enfermeras.set_index('id_enfermera'))

    elif analisis == "Enfermeras Asignadas a Pacientes":
        st.write("Distribución de Enfermeras asignadas por Paciente")
        conteo_pacientes = pacientes_enfermeras["id_paciente"].value_counts().reset_index()
        conteo_pacientes.columns = ['id_paciente', 'cantidad_enfermeras']
        st.bar_chart(conteo_pacientes.set_index('id_paciente'))
