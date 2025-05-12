import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from utils import load_tiff_image, calculate_ndvi, get_ndvi_stats

st.set_page_config(page_title="NDVI Satelital", layout="wide")

# Función para mostrar la imagen RGB
def show_rgb_image(image_data):
    rgb = np.dstack((image_data[2], image_data[1], image_data[0]))  # R, G, B
    rgb = rgb.astype(np.float32)
    rgb = 255 * ((rgb - np.min(rgb)) / (np.ptp(rgb) + 1e-6))  # Normalizar
    return rgb.astype(np.uint8)

# Título principal
st.markdown("# 🛰️ Análisis de Imágenes Satelitales con NDVI")
st.markdown("Una herramienta interactiva para el análisis de vegetación usando imágenes multiespectrales en formato TIFF.")
st.markdown("---")

uploaded_file = st.file_uploader("📤 Sube una imagen TIFF multiespectral", type=["tif", "tiff"])

if uploaded_file is not None:
    image_data, profile = load_tiff_image(uploaded_file)
    rgb_image = show_rgb_image(image_data)

    # Control de zoom
    zoom_level = st.slider("🔍 Ajusta el nivel de zoom", 1, 5, 1)  # Control para el zoom de la imagen
    zoomed_image = np.array(Image.fromarray(rgb_image).resize(
        (rgb_image.shape[1] * zoom_level, rgb_image.shape[0] * zoom_level), Image.Resampling.LANCZOS))

    # Tabs para separar el flujo de análisis
    tab1, tab2, tab3 = st.tabs(["🌄 Vista RGB", "🖱️ Selección ROI", "📊 Resultados NDVI"])

    with tab1:
        st.subheader("Visualización RGB de la imagen satelital")
        st.image(zoomed_image, channels="RGB", use_column_width=True)
        st.markdown("---")

    with tab2:
        st.subheader("Selecciona un área de interés (ROI)")
        st.markdown("Usa el mouse para dibujar un rectángulo sobre la imagen.")
        canvas_result = st_canvas(
            fill_color="rgba(255, 0, 0, 0.3)",
            stroke_width=2,
            stroke_color="green",
            background_image=Image.fromarray(zoomed_image),
            update_streamlit=True,
            height=zoomed_image.shape[0],
            width=zoomed_image.shape[1],
            drawing_mode="rect",
            key="canvas",
            display_toolbar=False  # 👈 Esto oculta la barrita desplegable del zoom
        )

    with tab3:
        if canvas_result.json_data and canvas_result.json_data["objects"]:
            shape = canvas_result.json_data["objects"][0]
            left = int(shape["left"])
            top = int(shape["top"])
            width = int(shape["width"])
            height = int(shape["height"])

            # Ajustar las coordenadas para la imagen original (sin zoom)
            left_original = int(left / zoom_level)
            top_original = int(top / zoom_level)
            width_original = int(width / zoom_level)
            height_original = int(height / zoom_level)

            if left_original + width_original <= image_data.shape[2] and top_original + height_original <= image_data.shape[1]:
                region = image_data[:, top_original:top_original + height_original, left_original:left_original + width_original]
                
                # Calcular NDVI
                ndvi = calculate_ndvi(region)
                stats = get_ndvi_stats(ndvi)

                # Cuadro de estadísticas más pequeño y organizado
                st.subheader("📊 Resultados NDVI")
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.metric("🔻 NDVI Mínimo", f"{stats['min']:.3f}")
                    st.metric("📉 Desviación Estándar", f"{stats['std']:.3f}")
                with col2:
                    st.metric("🔺 NDVI Máximo", f"{stats['max']:.3f}")
                    st.metric("📈 Promedio", f"{stats['mean']:.3f}")

                st.subheader("🌱 Mapa de calor NDVI del área")
                fig, ax = plt.subplots(figsize=(8, 6))
                cax = ax.imshow(ndvi, cmap='YlGn', interpolation='nearest')
                ax.set_title("NDVI ROI", fontsize=12)
                ax.axis("off")
                fig.colorbar(cax, ax=ax, shrink=0.8)
                st.pyplot(fig)
            else:
                st.warning("⚠️ El área seleccionada excede el tamaño de la imagen.")
else:
    st.info("Por favor sube una imagen en formato TIFF para comenzar.")
