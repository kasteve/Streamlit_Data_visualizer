import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Title of the app
st.title("Visualize and make your presentation easy !!")

# Upload file
uploaded_file = st.file_uploader("Choose a file", type=["csv"])

if uploaded_file is not None:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)
    
    # Display the dataframe
    st.write("Dataframe:")
    st.write(df)
    
    # Define custom color map for statuses
    status_color_map = {
        "success": "green",
        "pending": "purple",
        "failed": "red"
    }
    
    # Aggregating data for channelname against status
    status_counts = df.groupby(['channel_name', 'transaction_status']).size().reset_index(name='count')
    status_totals = status_counts.groupby('channel_name')['count'].transform('sum')
    status_counts['percentage'] = (status_counts['count'] / status_totals * 100).round(2)
    # Sort by count in descending order
    status_counts = status_counts.sort_values(by='count', ascending=False)
    
    # Bar chart for channelname against status count
    st.write("Channelname vs Status Count and Percentage")
    fig1 = px.bar(status_counts, x='transaction_status', y='count', color='channel_name', 
                  text='percentage', barmode='group', 
                  title='Channelname vs Status Count and Percentage',
                  color_discrete_map=status_color_map)
    st.plotly_chart(fig1)

    # Select channel_name from the first bar chart
    selected_channel = st.selectbox('Select a channel_name to filter Payment Type Data:', status_counts['channel_name'].unique())

    # Filter the dataframe based on the selected channel_name
    filtered_df = df[df['channel_name'] == selected_channel]

    # Aggregating data for payment_type_name against transaction count for the selected channel_name
    payment_status_counts = filtered_df.groupby(['payment_type_name', 'transaction_status']).size().reset_index(name='count')
    payment_totals = payment_status_counts.groupby('payment_type_name')['count'].transform('sum')
    payment_status_counts['percentage'] = (payment_status_counts['count'] / payment_totals * 100).round(2)
    # Sort by count in descending order
    payment_status_counts = payment_status_counts.sort_values(by='count', ascending=False)

    # Get unique payment types and paginate
    unique_payment_types = payment_status_counts['payment_type_name'].unique()
    items_per_page = 10
    total_pages = len(unique_payment_types) // items_per_page + 1
    
    page = st.slider("Select Page", 1, total_pages, 1)
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    paginated_payment_types = unique_payment_types[start_idx:end_idx]
    
    # Filter data for the selected page
    paginated_payment_status_counts = payment_status_counts[payment_status_counts['payment_type_name'].isin(paginated_payment_types)]
    
    # Bar chart for payment_type_name against transaction count
    st.write(f"Payment Type Name vs Transaction Count and Percentage for Channel: {selected_channel}")
    fig2 = px.bar(paginated_payment_status_counts, x='payment_type_name', y='count', color='transaction_status', 
                  text='percentage', barmode='group', 
                  title='Payment Type Name vs Transaction Count and Percentage',
                  color_discrete_map=status_color_map)
    st.plotly_chart(fig2)
    
    # Export aggregated data to CSV
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    status_counts_csv = convert_df_to_csv(status_counts)
    payment_status_counts_csv = convert_df_to_csv(payment_status_counts)
    
    st.download_button(
        label="Download Channelname vs Status Data as CSV",
        data=status_counts_csv,
        file_name='channelname_vs_status.csv',
        mime='text/csv',
    )
    
    st.download_button(
        label="Download Payment Type Name vs Transaction Data as CSV",
        data=payment_status_counts_csv,
        file_name='payment_type_name_vs_transaction.csv',
        mime='text/csv',
    )

    # Export plots to PNG
    def fig_to_bytes(fig):
        buf = io.BytesIO()
        fig.write_image(buf, format="png")
        buf.seek(0)
        return buf.getvalue()
    
    fig1_bytes = fig_to_bytes(fig1)
    fig2_bytes = fig_to_bytes(fig2)

    st.download_button(
        label="Download Channelname vs Status Plot as PNG",
        data=fig1_bytes,
        file_name='channelname_vs_status.png',
        mime='image/png',
    )
    
    st.download_button(
        label="Download Payment Type Name vs Transaction Plot as PNG",
        data=fig2_bytes,
        file_name='payment_type_name_vs_transaction.png',
        mime='image/png',
    )
