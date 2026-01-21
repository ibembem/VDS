import streamlit as st
import plotly.express as px
import pandas as pd
from streamlit_plotly_events import plotly_events

st.set_page_config(layout="wide")
st.title("Global Tourism Impact Dashboard")

# 1. Загрузка данных
df = df_final_cleaned.copy()

# 2. Создаем основную карту
fig_map = px.choropleth(
    df, 
    locations="ISO3_Code", 
    color="Tourism_Density",
    hover_name="Country_Name",
    title="Global Tourism Density (Выделите страны инструментом Lasso)",
    color_continuous_scale=px.colors.sequential.Plasma
)
fig_map.update_layout(clickmode='event+select', margin={"r":0,"t":40,"l":0,"b":0})

# 3. Отображаем карту и ловим события выбора (Brushing)
# select_event вернет список словарей с данными о выбранных точках
selected_points = plotly_events(fig_map, select_event=True, key="map")

# 4. Логика фильтрации (Linking)
if selected_points:
    # Извлекаем ISO коды выбранных стран
    selected_iso = [p['location'] for p in selected_points if 'location' in p]
    filtered_df = df[df['ISO3_Code'].isin(selected_iso)]
else:
    # Если ничего не выбрано, показываем всё
    filtered_df = df

# 5. Отрисовка нижних графиков
col1, col2, col3 = st.columns(3)

with col1:
    fig1 = px.scatter(filtered_df, x="GDP_per_capita", y="Inbound_Tourists", 
                     hover_name="Country_Name", title="Wealth vs. Volume", 
                     log_x=True, template="plotly_white")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Добавляем обработку ошибки, если данных слишком мало для регрессии
    try:
        fig2 = px.scatter(filtered_df, x="Population_Density", y="Tourism_Density", 
                         trendline="ols", hover_name="Country_Name",
                         title="Density Correlation (Model)", template="plotly_white")
    except:
        fig2 = px.scatter(filtered_df, x="Population_Density", y="Tourism_Density", 
                         hover_name="Country_Name", title="Density Correlation")
    st.plotly_chart(fig2, use_container_width=True)

with col3:
    top_10 = filtered_df.nlargest(10, 'Tourists_per_Resident')
    fig3 = px.bar(top_10, x="Country_Name", y="Tourists_per_Resident", 
                  title="Top 10 Local Burden", template="plotly_white")
    st.plotly_chart(fig3, use_container_width=True)
