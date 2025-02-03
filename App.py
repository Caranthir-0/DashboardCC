import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import calendar

# 1. Funkcje
def process_sales_data(file_path):
    df = pd.read_csv(file_path)
    df = df.rename(columns={
        "DATA_FAKTURY": "Data",
        "PH_FAKTURA": "Handlowiec",
        "WARTOSC_PLN": "Obrót (PLN)",
        "NR_ZAMOWIENIA": "Liczba zamówień",
        "NR_FAKTURY": "Liczba faktur",
        "GRUPA": "Grupa",
        "ZYSK_BAZ": "Marża (PLN)",
        "N_GRUPA_PROD_2": "Kategoria2",
        "N_GRUPA_PROD_5": "Kategoria5"
    })
    df["Data"] = pd.to_datetime(df["Data"]).dt.date
    df = df[df['Marża (PLN)'] > 0 ]

    df_products = df.groupby(["Data", "Kategoria2", "Kategoria5"], as_index=False).agg({
        "Obrót (PLN)": "sum",
        "Liczba faktur": "sum"
    })

    df["Falowniki Encor (szt.)"] = df["Grupa"].apply(lambda x: 1 if x == "ENCOR" else 0)
    df_grouped = df.groupby(["Data", "Handlowiec"], as_index=False).agg({
        "Obrót (PLN)": "sum",
        "Marża (PLN)": "sum",
        "Liczba zamówień": "nunique",
        "Liczba faktur": "nunique",
        "Falowniki Encor (szt.)": "sum"
    })
    return df_grouped, df_products

def process_call_center_data(file_path):
    df = pd.read_csv(file_path)
    #df = df.drop(columns=['Unnamed: 27', 'Zgłoszenie', 'Routing'])
    df['MERYTORYCZNY'] = df.apply(
            lambda row: 1 if (
                row['Status w kampanii'] in [
                    "Klient niezainteresowany",
                    "Klient wstępnie zainteresowany",
                    "Klient złożył zamówienie",
                    "Zamówienie złożone podczas rozmowy"
                ] or (pd.notna(row['Grupa tematu']) and "Mikroinstalacje" in row['Temat rozmowy'])
                or (pd.notna(row['Grupa tematu']) and "CC - Call merytoryczny" in row['Temat rozmowy'])
                or  ("Call merytoryczny" in str(row['Status w kampanii']))
                #or (pd.notna(row['Grupa tematu']) and "Call merytoryczny + follow up" in row['Status w kampanii'])
    ) else 0,
    axis = 1 )
    df["Data"] = pd.to_datetime(df["Data połączenia"]).dt.date
    df_grouped = df.groupby(["Data", "Kampania", "Agent"], as_index=False).agg({
        "ID kampanii": "count",
        "Rezultat": lambda x: (x == "ANSWER").sum(),
        "MERYTORYCZNY" : "sum"
    }) 
    df_grouped = df_grouped.rename(columns={
        "ID kampanii": "Połączenia wychodzące",
        "Rezultat": "Poł. odebrane",
        "MERYTORYCZNY" : "W tym merytoryczne"
    })
    df_grouped["% merytorycznych"] = (df_grouped["W tym merytoryczne"]/ df_grouped["Połączenia wychodzące"]) * 100
    df_grouped["Poł. utracone"] = df_grouped["Połączenia wychodzące"] - df_grouped["Poł. odebrane"]
    df_grouped["% utraconych"] = (df_grouped["Poł. utracone"] / df_grouped["Połączenia wychodzące"]) * 100
    return df_grouped

def process_farmer_data(file_path):
    df = pd.read_csv(file_path)
    df = df.drop(columns=['ID klienta', 'Klient', 'Firma', 'Numer docelowy', 'Numer źródłowy',  'Agent źródłowy', 'Nagranie', 'Ocena', 'Komentarz oceny', 'Rozłączone przez', 'Zgłoszenie', 'Tagi', 'Opis rozmowy', 'Szczegóły', 'Ocena klienta', 'Komentarz klienta','Data oceny', 'recordings_cc.transferred_to','Unnamed: 31', ])
    df["Czas rozmowy"] = pd.to_timedelta(df["Czas rozmowy"]).dt.total_seconds()
    df["Czas oczekiwania"] = pd.to_timedelta(df["Czas oczekiwania"]).dt.total_seconds()
    df['Gałąź IVR'] = df['Gałąź IVR'].str.replace(r'^\[.*?\]\s*', '', regex=True)
    df['Data'] = df['Data połączenia z kolejką'].str[0:10]
    df['Data'] = pd.to_datetime(df['Data']).dt.date
    df['Godzina'] = df['Data połączenia z kolejką'].str[11:13]
    return df

def process_target_data(file_path):
    df_target = pd.read_csv(file_path)
    df_target = df_target.rename(columns={
        "PH_REALIZACJA": "Handlowiec",
        "ROK_MIESIAC": "Data",  
        "PLAN": "Cel Marży"
    })
    df_target["Data"] = pd.to_datetime(df_target["Data"]).dt.date
    return df_target

@st.cache_data
def load_data():
    df_sales, df_products = process_sales_data('data/SalesData.csv')
    df_cc = process_call_center_data('data/Rozmowy kampanii.csv')
    df_farmer = process_farmer_data('Rozmowy infolinii.csv')
    df_target = process_target_data('TargetData.csv')
    return df_sales, df_products, df_farmer, df_cc, df_target

st.set_page_config(page_title="CC Statystyki", layout="wide")
df_sales, df_products, df_farmer, df_cc, df_target = load_data()

#
# 2. Sidebar
st.sidebar.image('logo_2021.png', use_container_width=True)
st.sidebar.header("Opcje")
view_option = st.sidebar.selectbox("Wybierz zakładkę", ["Sprzedaż", "Obsługa Klienta"])

st.sidebar.subheader("Wybierz miesiąc i rok")
years = range(2022, 2030)
selected_year = st.sidebar.selectbox("Rok", years, index=list(years).index(datetime.today().year))
months = range(1, 13)
month_names = [
    "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
    "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"
]
default_month_index = datetime.today().month - 1
selected_month_name = st.sidebar.selectbox("Miesiąc", month_names, index=default_month_index)
month_number = month_names.index(selected_month_name) + 1

start_date = datetime(selected_year, month_number, 1).date()
end_date = datetime(selected_year, month_number, calendar.monthrange(selected_year, month_number)[1]).date()

st.markdown("<h1 style='color: #d22730;'>📊 Statystki Contact Center</h1>", unsafe_allow_html=True)

# 3. Zakładki
if view_option == "Sprzedaż":
    st.subheader("Sekcja: Sprzedaż")
    
    # Filtrowanie sprzedaży na wybrany miesiąc
    df_sales_filtered = df_sales[
        (df_sales["Data"] >= start_date) & (df_sales["Data"] <= end_date)
    ]
        
    # Filtrowanie produktów na wybrany miesiąc
    df_products_filtered = df_products[
        (df_products["Data"] >= start_date) & (df_products["Data"] <= end_date)
    ]
    
    
    # Filtrowanie planu na wybrany miesiąc (jeśli w pliku jest 1 wiersz na 2023-05-01, itp.)
    df_target_filtered = df_target[
        (df_target["Data"] >= start_date) & (df_target["Data"] <= end_date)
    ]

    
    
    # KPI sprzedaż
    total_sprzedaz = int(df_sales_filtered["Obrót (PLN)"].sum())
    total_marza = int(df_sales_filtered["Marża (PLN)"].sum())
    total_cel = int(df_target_filtered['Cel Marży'][df_target_filtered['TYP'] == 'Zespołowy'].sum())
    total_zamowienia = int(df_sales_filtered["Liczba zamówień"].sum())
    total_transakcje = int(df_sales_filtered["Liczba faktur"].sum())
    total_encor = int(df_sales_filtered["Falowniki Encor (szt.)"].sum())

    # KPI cel (jeśli jest 1 wiersz, bierzemy iloc[0]; jeśli kilka – może sum(), itp.)
    #if not df_target_filtered.empty:
    #    total_cel = df_target_filtered["Cel Marży"].sum()
    #else:
    #    total_cel = 0
    
    # Kafelki
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Obrót (PLN)", value=f"{total_sprzedaz:,.0f}".replace(",", "'"))
    with col2:
        st.metric("Marża zespołu (PLN)", value=f"{total_marza:,.0f}".replace(",", "'"))
    with col3:
        st.metric("Cel zespołu (marża)", value=f"{total_cel:,.0f}".replace(",", "'"))
    with col4:
        st.metric("Liczba zamównień", value=f"{total_zamowienia}".replace(",", "'"))
    with col5:
        st.metric("Liczba faktur", value=f"{total_transakcje}".replace(",", "'"))
    with col6:
        st.metric("w tym Encor", value=f"{total_encor}".replace(",", "'"))

    # Trend sprzedaży
    dzienna_sprzedaz = df_sales_filtered.groupby("Data")["Marża (PLN)"].sum().reset_index()
    dzienny_obrót = df_sales_filtered.groupby("Data")["Obrót (PLN)"].sum().reset_index()
    
    kumulatywna_sprzedaz = dzienna_sprzedaz.copy()
    kumulatywna_sprzedaz["Kumulatywnie"] = kumulatywna_sprzedaz["Marża (PLN)"].cumsum()

    st.write("### Trend dzienny Sprzedaży")
    colA, colB = st.columns(2)
    with colA:
        fig_daily_sales = go.Figure()
        fig_daily_sales.add_trace(
            go.Scatter(
                x=dzienna_sprzedaz["Data"],
                y=dzienna_sprzedaz["Marża (PLN)"],
                name="Marża",
                mode="lines+markers",
                line=dict(color="#d22730"),
                #yaxis="y2"   # wskazanie użycia drugiej osi
            )
        )
        #fig_daily_sales.update_traces(line=dict(color="#d22730"), mode="lines+markers" )
        fig_daily_sales.add_trace(
            go.Scatter(
                x=dzienny_obrót["Data"],
                y=dzienny_obrót["Obrót (PLN)"],
                name="Obrót",
                mode="lines+markers",
                line=dict(color="blue"),
                yaxis="y2"   # wskazanie użycia drugiej osi
            )
        )
        fig_daily_sales.update_layout(
            yaxis2=dict(
                overlaying="y",
                side="right",
            )
        )
        st.plotly_chart(fig_daily_sales, use_container_width=True)
    with colB:
        fig_cumulative_sales = px.area(
            kumulatywna_sprzedaz, 
            x="Data", 
            y="Kumulatywnie", 
            title="Trend Kumulatywny Marży",
            labels={"Kumulatywnie": "Marża kumulatywnie", "Data": "Data"}
        )
        fig_cumulative_sales.update_traces(line=dict(color="#d22730"))
        st.plotly_chart(fig_cumulative_sales, use_container_width=True)

    # Tabela – podsumowanie po handlowcach
    handlowiec_grouped = df_sales_filtered.groupby("Handlowiec", as_index=False).agg({
        "Obrót (PLN)": "sum",
        "Marża (PLN)": "sum",
        "Liczba faktur": "sum",
        "Falowniki Encor (szt.)": "sum"
    })

    df_cc_filtered = df_cc[
        (df_cc["Data"] >= start_date) & (df_cc["Data"] <= end_date)
    ]
    
    po_kolejkach = df_cc_filtered.groupby("Agent", as_index=False).agg({
        "Połączenia wychodzące": "sum",
        "Poł. odebrane": "sum",
        "W tym merytoryczne":"sum",
        "% merytorycznych":"mean"

    })

    # Wykonanie left join
    df_merged = handlowiec_grouped.merge(
        po_kolejkach,
        how="left",  # Left join
        left_on="Handlowiec",  # Klucz w lewej tabeli
        right_on="Agent"  # Klucz w prawej tabeli
    )


    df_merged = df_merged.drop(columns=["Agent"])
    df_merged = df_merged.rename(columns={'Falowniki Encor (szt.)': 'Encor(szt.)', 'Liczba faktur': 'Faktury'})

    # -- Sekcja z tabelą i wykresem obok --
    col_chart, col_tab = st.columns([1, 1])  # podział ekranu: lewa (tabela), prawa (wykres)
    
    with col_tab:
        # Wyświetlenie tabeli
        st.write("### Zestawienie per Handlowiec")
        st.dataframe(df_merged.style.format({
            "Obrót (PLN)": "{:,.0f}",
            "Marża (PLN)": "{:,.0f}",
            "Faktury": "{:,.0f}",
            "w tym Encor": "{:,.0f}",
            "Połączenia wychodzące": "{:,.0f}",
            "Poł. odebrane": "{:,.0f}",
            "W tym merytoryczne":"{:,.0f}",
            "% merytorycznych":"{:,.0f}"
        }))
    
    with col_chart:
        # 1. Filtrowanie tylko na wybrane wartości
        df_filtered_for_chart = df_products_filtered[
            df_products_filtered["Kategoria2"].isin(["DYSTRYBUCJA", "PRODUKCJA"])
        ]

        # 2. Grupowanie po Kategoria2 i Kategoria5
        df_grouped = df_filtered_for_chart.groupby(["Kategoria2", "Kategoria5"], as_index=False)["Obrót (PLN)"].sum()
        df_grouped['Kategoria2'] = df_grouped['Kategoria2'].replace('PRODUKCJA', 'KONTRUKCJE')

        # 3. Tworzymy wykres słupkowy grupowany
        fig_group = px.bar(
            df_grouped,
            x="Kategoria2",
            y="Obrót (PLN)",
            color="Kategoria5",
            title="Sprzedaż produktów wg rodzaju",
            barmode="group"
        )
        st.plotly_chart(fig_group, use_container_width=True)



elif view_option == "Obsługa Klienta":
    st.subheader("Sekcja: Obsługa Klienta")

    # Filter data first
    df_farmer_filtered = df_farmer[
        (df_farmer["Data"] >= start_date) & 
        (df_farmer["Data"] <= end_date)
    ]
    
    # Filter CC agents
    df_farmer_cc = df_farmer_filtered[df_farmer_filtered['Grupa agentów'] == "Agenci CC"]
    
    # KPI Calculations
    połączenia_CC = df_farmer_filtered.shape[0]
    połączenia_Other = df_farmer_cc.shape[0]
    połączenia_callback = df_farmer['Oddzwonienie z'].notna().sum()

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Połączenia kolejki CC", f"{połączenia_CC}".replace(",", "'"))
    with col2:
        st.metric("Połączenia innych kolejek", f"{połączenia_Other}".replace(",", "'"))
    with col3:
        st.metric("Poł. wymagające oddzwonienia", f"{połączenia_callback}".replace(",", "'"))

    # IVR Analysis
    col1, col2 = st.columns([1, 1])
    
    # Clean IVR branches again for safety
    df_farmer_cc['Gałąź IVR'] = df_farmer_cc['Gałąź IVR'].str.replace(
        r'^\[.*?\]\s*|-.*$', 
        '', 
        regex=True
    )
    
    #backend
    df_IVR = df_farmer_cc.groupby('Gałąź IVR').agg({
        'ID rozmowy': 'count',
        'Czas rozmowy': 'mean',
        'Czas oczekiwania': 'mean' 
    }).reset_index().rename(columns={
        'ID rozmowy': 'Ilość',
        'Czas rozmowy': 'Śr. czas połączenia (s)',
        'Czas oczekiwania': 'Śr. czas oczekiwania (s)'
    }).sort_values('Ilość', ascending=False)

    df_Agenci = df_farmer_cc.groupby('Agent').agg({
        'ID rozmowy': 'count',
        'Czas rozmowy': 'mean',
        'Czas oczekiwania': 'mean' 
    }).reset_index().rename(columns={
        'ID rozmowy': 'Ilość',
        'Czas rozmowy': 'Śr. czas połączenia (s)',
        'Czas oczekiwania': 'Śr. czas oczekiwania (s)'
    }).sort_values('Ilość', ascending=False)
    
    df_godz = df_farmer_cc.groupby('Godzina')['ID rozmowy'].count().reset_index()
    df_godz['Godzina'] = df_godz['Godzina'].astype('int')
    df_godz['ID rozmowy'] = df_godz['ID rozmowy'] / 30
    df_godz['Przedział'] = df_godz['Godzina'].apply(lambda x: f'{str(x)}-{str(x+1)}')
    # Layout
    col1, col2 = st.columns(2)
    with col1: 
        st.write("### Rozbicie w podziale na kolejki IVR")
        # Display formatted table
        st.dataframe(
            df_IVR.style.format({
                'Śr. czas połączenia (s)': '{:.1f}'.replace(",", "'"),
                'Śr. czas oczekiwania (s)': '{:.1f}'.replace(",", "'")
            }),
            height=400
        )
    with col2:
        st.write("### Rozbicie w podziale na Agentów")
        st.dataframe(
            df_Agenci.style.format({
                'Śr. czas połączenia (s)': '{:.1f}'.replace(",", "'"),
                'Śr. czas oczekiwania (s)': '{:.1f}'.replace(",", "'")
            }),
            height=400
        )
    fig_hours = go.Figure(data=[go.Bar(
        x=df_godz['Godzina'],
        y=df_godz['ID rozmowy'],
        text = df_godz['Przedział'],
        marker=dict(color='#d22730')
        
        )])

    # Customize layout (optional)
    fig_hours.update_layout(
        xaxis_title='Godzina',
        yaxis_title='Śr. Ilość Połączeń',
    )

    # Show the figure
    st.write("### Dzienne średnie natężenie ruchu")
    st.plotly_chart(fig_hours, use_container_width=True)
