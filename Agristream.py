import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title("Kenya Agricultural Census Map")

st.write("Partial Distribution of Agricultural Activities in Kenya!")

# Set page config
st.set_page_config(page_title="Kenya Crop Production 2019", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('Kenya_Crop_Production_2019_Cleaned.csv')
    return df

df = load_data()

#Automatically detect data structure from CSV
national_data = df[df['county'] == 'KENYA']
counties_list = df[df['county'] != 'KENYA']['county'].unique()
num_counties = len(counties_list)
num_total_rows = len(df)

# Display data insights based on CSV
st.info(f"📊 **Data Insights:** This dataset contains {num_total_rows} total rows. "
        f"**{num_counties} counties** are represented (excluding the national 'KENYA' row which represents **national totals**).")

# Title and description
st.title("🌾 Kenya Agricultural Census Map Dashboard")
st.markdown("Explore agricultural production data across Kenya's 47 counties. Note: 'KENYA' row represents national totals.")

# Sidebar filters
st.sidebar.header("🎯 Filters & Controls")

# County selection - automatically exclude KENYA from dropdown
counties = ['All Counties'] + sorted([c for c in df['county'].unique() if pd.notna(c) and c != 'KENYA'])
selected_county = st.sidebar.selectbox("📍 Select County", counties)

if selected_county != 'All Counties':
    df_filtered = df[df['county'] == selected_county]
else:
    # Use all counties but exclude national KENYA row for county-level analysis
    df_filtered = df[df['county'] != 'KENYA']

# Crop selection for detailed analysis
crop_columns = ['maize', 'rice', 'beans', 'potatoes', 'cassava', 'sweet potatoes', 
                'bananas', 'tomatoes', 'onions', 'cabbages', 'sugarcane', 'cotton']
selected_crop = st.sidebar.selectbox("🌱 Select Crop for Analysis", crop_columns)

# Main dashboard
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Count only actual counties, not the KENYA national row
    st.metric("📊 Total Counties", num_counties)

with col2:
    # Use KENYA row for national totals
    if len(national_data) > 0:
        total_crop_production = national_data['crop production'].sum()
    else:
        total_crop_production = df[df['county'] != 'KENYA']['crop production'].sum()
    st.metric("🌾 Total Crop Production (National)", f"{total_crop_production:,.0f}")

with col3:
    # For filtered counties, sum only the selected crop (already excludes KENYA if "All Counties" selected)
    if selected_county == 'All Counties':
        selected_crop_total = df[df['county'] != 'KENYA'][selected_crop].sum()
    else:
        selected_crop_total = df_filtered[selected_crop].sum()
    st.metric(f"🥕 {selected_crop.title()}", f"{selected_crop_total:,.0f}")

with col4:
    if len(national_data) > 0:
        livestock_total = national_data['livestock production'].sum()
    else:
        livestock_total = df[df['county'] != 'KENYA']['livestock production'].sum()
    st.metric("🐄 Livestock Production (National)", f"{livestock_total:,.0f}")

st.divider()

# Display national totals from KENYA row
if len(national_data) > 0:
    st.subheader("🇰🇪 National Totals (KENYA Row)")
    national_row = national_data.iloc[0]
    
    nat_col1, nat_col2, nat_col3, nat_col4 = st.columns(4)
    with nat_col1:
        st.metric("Total Production", f"{national_row['total']:,.0f}")
    with nat_col2:
        st.metric("Farming", f"{national_row['farming']:,.0f}")
    with nat_col3:
        st.metric("Irrigation", f"{national_row['irrigation']:,.0f}")
    with nat_col4:
        st.metric("Sub-counties Tracked", len(df[df['county'] != 'KENYA']))
    
    st.divider()

# ==================== ROW 1: Top producing counties ====================
st.subheader("📈 Top 10 Crop Producing Counties")
top_counties = df[df['county'] != 'KENYA'].groupby('county')['crop production'].sum().nlargest(10).reset_index()
fig_top = px.bar(top_counties, x='crop production', y='county', 
                 orientation='h', 
                 title='Top 10 Counties by Total Crop Production',
                 labels={'crop production': 'Total Production', 'county': 'County'},
                 color='crop production',
                 color_continuous_scale='Viridis')
fig_top.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400)
st.plotly_chart(fig_top, use_container_width=True)

st.divider()

# ==================== ROW 2: Selected crop production by county ====================
st.subheader(f"🌱 {selected_crop.title()} Production by County")
crop_by_county = df[df['county'] != 'KENYA'].groupby('county')[selected_crop].sum().nlargest(12).reset_index()
fig_crop = px.bar(crop_by_county, x='county', y=selected_crop,
                  title=f'Top Counties - {selected_crop.title()} Production',
                  labels={selected_crop: 'Production Volume', 'county': 'County'},
                  color=selected_crop,
                  color_continuous_scale='Greens')
fig_crop.update_xaxes(tickangle=-45)
st.plotly_chart(fig_crop, use_container_width=True)

st.divider()

# ==================== ROW 3: Production breakdown pie chart ====================
st.subheader("📊 Production Sector Breakdown")
col1, col2 = st.columns(2)

with col1:
    # National breakdown using KENYA row
    if len(national_data) > 0:
        sectors = ['Crop', 'Livestock', 'Aquaculture', 'Fishing']
        sector_data = [national_data['crop production'].sum(), 
                      national_data['livestock production'].sum(),
                      national_data['aquaculture'].sum(), 
                      national_data['fishing'].sum()]
        fig_pie = px.pie(names=sectors, values=sector_data, 
                        title='National Production by Sector (KENYA)',
                        color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # County-specific breakdown (if county selected)
    if selected_county != 'All Counties':
        county_data = df_filtered.iloc[0]
        sectors_county = ['Crop', 'Livestock', 'Aquaculture', 'Fishing']
        values_county = [county_data['crop production'], county_data['livestock production'],
                        county_data['aquaculture'], county_data['fishing']]
        fig_pie_county = px.pie(names=sectors_county, values=values_county,
                               title=f'{selected_county} - Production by Sector',
                               color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_pie_county, use_container_width=True)
    else:
        st.info("💡 Select a county from the sidebar to see its sector breakdown")

st.divider()

# ==================== ROW 4: Comparison of major crops ====================
st.subheader("🥬 Top Crops Comparison")
top_crops = ['maize', 'beans', 'potatoes', 'cassava', 'bananas', 'tomatoes']
crops_data = []
for crop in crop_columns:
    # Only sum county data, NOT the KENYA national row (to avoid double-counting)
    crops_data.append({'Crop': crop.title(), 'Production': df[df['county'] != 'KENYA'][crop].sum()})
crops_df = pd.DataFrame(crops_data).sort_values('Production', ascending=False).head(6)

fig_crops = px.bar(crops_df, x='Crop', y='Production',
                   title='Total Production - Top 6 Crops',
                   labels={'Production': 'Total Volume'},
                   color='Production',
                   color_continuous_scale='Sunset')
st.plotly_chart(fig_crops, use_container_width=True)

st.divider()

# ==================== ROW 5: Livestock comparison ====================
st.subheader("🐄 Livestock Production by County")
livestock_cols = ['exotic cattle 0dairy', 'exotic cattle 0beef', 'indigenous cattle', 
                  'sheep', 'goats', 'pigs']
livestock_by_county = df[df['county'] != 'KENYA'].groupby('county')[livestock_cols].sum().sum(axis=1).nlargest(10).reset_index(name='Total')
livestock_by_county.columns = ['county', 'Total Livestock']

fig_livestock = px.bar(livestock_by_county, x='county', y='Total Livestock',
                       title='Top 10 Counties - Total Livestock Production',
                       labels={'Total Livestock': 'Total Units', 'county': 'County'},
                       color='Total Livestock',
                       color_continuous_scale='Reds')
fig_livestock.update_xaxes(tickangle=-45)
st.plotly_chart(fig_livestock, use_container_width=True)

st.divider()

# ==================== ROW 6: Detailed data table ====================
st.subheader("📋 Detailed County Data")
if selected_county != 'All Counties':
    st.write(f"**Data for {selected_county}**")
    display_cols = ['county', 'sub county', 'crop production', 'livestock production', 
                    'aquaculture', selected_crop]
    # Simplified data display without style.format()
    df_display = df_filtered[display_cols].copy()
    st.dataframe(df_display, use_container_width=True)
else:
    display_cols = ['county', 'sub county', 'crop production', 'livestock production', 'aquaculture']
    # Show only counties, not KENYA national row
    df_display = df[df['county'] != 'KENYA'][display_cols].head(25).copy()
    st.dataframe(df_display, use_container_width=True)

st.divider()

# ==================== ROW 7: Statistics ====================
st.subheader("📊 Key Statistics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_production = df[df['county'] != 'KENYA'].groupby('county')['crop production'].sum().mean()
    st.metric("Avg County Crop Prod.", f"{avg_production:,.0f}")

with col2:
    max_production = df[df['county'] != 'KENYA'].groupby('county')['crop production'].sum().max()
    st.metric("Max County Crop Prod.", f"{max_production:,.0f}")

with col3:
    sub_counties = len(df[df['county'] != 'KENYA'])
    st.metric("Total Data Rows", sub_counties)

with col4:
    if len(national_data) > 0:
        total_val = national_data['total'].sum()
        livestock_pct = (national_data['livestock production'].sum() / total_val) * 100 if total_val > 0 else 0
        st.metric("Livestock % of Total", f"{livestock_pct:.1f}%")
    else:
        st.metric("Livestock % of Total", "N/A")

st.divider()

# ==================== ROW 8: Download data ====================
st.subheader("📥 Download Data")
col1, col2, col3 = st.columns(3)

with col1:
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Full Dataset (CSV)",
        data=csv,
        file_name="Kenya_Crop_Production_2019.csv",
        mime="text/csv"
    )

with col2:
    if selected_county != 'All Counties':
        csv_county = df_filtered.to_csv(index=False)
        st.download_button(
            label=f"Download {selected_county} Data (CSV)",
            data=csv_county,
            file_name=f"{selected_county}_Crop_Production.csv",
            mime="text/csv"
        )

with col3:
    if len(national_data) > 0:
        csv_national = national_data.to_csv(index=False)
        st.download_button(
            label="Download National Totals (CSV)",
            data=csv_national,
            file_name="Kenya_National_Totals.csv",
            mime="text/csv"
        )

st.divider()

# Footer
st.markdown("---")
st.markdown("📊 **Data Source:** Kenya Crop Production 2019 | Built with Streamlit & Plotly")
st.markdown(f"✅ **Auto-detected:** {num_counties} counties + 1 National Totals row (KENYA)")
