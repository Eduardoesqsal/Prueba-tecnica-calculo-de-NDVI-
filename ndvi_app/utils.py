import rasterio
import numpy as np

# Función para cargar la imagen TIFF
def load_tiff_image(uploaded_file):
    with rasterio.open(uploaded_file) as src:
        image_data = src.read()  # Leer todas las bandas
        profile = src.profile  # Obtener el perfil de la imagen (metadata)
    return image_data, profile

# Función para calcular el NDVI
def calculate_ndvi(image_data):
    # Verifica que las bandas necesarias existan
    if image_data.shape[0] < 4:
        raise ValueError("La imagen debe tener al menos 4 bandas.")
    
    # Asumiendo que la banda 4 es la del infrarrojo cercano y la banda 3 es la del rojo
    nir_band = image_data[3]  # Banda del infrarrojo cercano (NIR)
    red_band = image_data[2]  # Banda del rojo (RED)

    # Evitar división por cero y manejo de valores NaN
    with np.errstate(divide='ignore', invalid='ignore'):
        ndvi = (nir_band - red_band) / (nir_band + red_band)
        ndvi[np.isnan(ndvi)] = 0  # Establece los NaN en 0

    return ndvi

# Función para obtener estadísticas del NDVI
def get_ndvi_stats(ndvi):
    stats = {
        'min': np.nanmin(ndvi),  # Usamos np.nanmin y np.nanmax para evitar NaN
        'max': np.nanmax(ndvi),
        'mean': np.nanmean(ndvi),
        'std': np.nanstd(ndvi)
    }
    return stats

