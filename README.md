# DashboardCC – Statystyki Contact Center

Niniejszy projekt stanowi aplikację webową stworzoną przy użyciu **Streamlit**. Aplikacja umożliwia przegląd i analizę danych sprzedażowych oraz danych z Contact Center (CC). Prezentuje m.in. obroty, marże, liczbę faktur, zestawienia wg handlowców, a także statystyki połączeń wychodzących, odebranych i utraconych w CC.

## Spis treści
1. [Wymagania i Instalacja](#wymagania-i-instalacja)
2. [Uruchomienie](#uruchomienie)
3. [Struktura Plików](#struktura-plików)
4. [Opis Działania](#opis-działania)
5. [Uwagi Konfiguracyjne](#uwagi-konfiguracyjne)
6. [Rozwój i Plany](#rozwój-i-plany)
7. [Autor](#autor)
8. [Licencja](#licencja)

---

## Wymagania i Instalacja
Aplikacja została stworzona w języku **Python** (zalecana wersja Python 3.8+), z wykorzystaniem bibliotek:
- **Streamlit**  
- **Pandas**  
- **Plotly**  
- **datetime** i **calendar** (wbudowane w Pythona)  

Aby uruchomić projekt lokalnie:
1. **Sklonuj to repozytorium**:
   ```bash
   git clone https://github.com/Caranthir-0/DashboardCC.git
   ```
2. **Przejdź do katalogu z projektem**:
   ```bash
   cd DashboardCC
   ```
3. **Utwórz i aktywuj wirtualne środowisko** (opcjonalnie, ale zalecane):
   ```bash
   python -m venv venv
   # Linux / macOS
   source venv/bin/activate
   # Windows
   venv\Scripts\activate
   ```
4. **Zainstaluj wymagane zależności**:
   ```bash
   pip install streamlit pandas plotly
   ```
   *(Jeśli utworzono plik `requirements.txt`, możesz zainstalować zależności poleceniem `pip install -r requirements.txt`.)*

---

## Uruchomienie
1. Upewnij się, że wszystkie pliki CSV są dostępne i że w kodzie (`load_data()` i ścieżki w `process_*_data`) masz zaktualizowane ścieżki do tych plików.
2. Uruchom aplikację poleceniem:
   ```bash
   streamlit run app.py
   ```
   *(Zakładając, że plik z kodem nazywa się `app.py`. W razie potrzeby zmień nazwę pliku lub dostosuj komendę.)*
3. Po chwili w przeglądarce otworzy się aplikacja dostępna domyślnie pod adresem:
   ```
   http://localhost:8501
   ```
4. W **Sidebar** wybierz zakładkę (np. *Sprzedaż* lub *Obsługa Klienta (CC)*), a następnie określ rok i miesiąc, dla którego chcesz zobaczyć statystyki.

---

## Struktura Plików
Przykładowy układ repozytorium może wyglądać następująco:

```
DashboardCC/
│
├─ data/
│   ├─ SalesData.csv
│   ├─ CallCenterData.csv
│   └─ TargetData.csv
│
├─ app.py                # Główny plik z kodem Streamlit
├─ logo_2021.png         # Logo wyświetlane w sidebar
├─ README.md
└─ requirements.txt      # (opcjonalnie) lista bibliotek
```

> **Uwaga:** W kodzie obecnie używane są ścieżki bezwzględne (np. `C:\Users\k.obrebski\Desktop\CCDASH\SalesData.csv`).  
> Zalecamy zmienić te ścieżki na względne (np. `data/SalesData.csv`), a następnie wgrać pliki .csv do folderu `data/` (jak w przykładzie powyżej).

---

## Opis Działania
1. **Wczytywanie danych**  
   Funkcja `load_data()` wywołuje:
   - `process_sales_data(path)` do wczytania i przetworzenia danych sprzedażowych (m.in. obroty, marże, liczby faktur).  
   - `process_call_center_data(path)` do wczytania i przetworzenia statystyk Contact Center (m.in. połączenia wychodzące, odebrane, utracone).  
   - `process_target_data(path)` do wczytania planów marży na dany miesiąc.

2. **Przetwarzanie i agregacja**  
   - Agregacje danych sprzedażowych na poziomie dni oraz handlowców: liczenie sum obrotów, marży, liczby zamówień, liczby faktur itp.  
   - Dla CC liczone są: liczba połączeń wychodzących, odebranych, utraconych, a także wskaźniki merytoryczności i procent połączeń utraconych.

3. **Prezentacja w Streamlit**  
   - **Filtry** (po miesiącu i roku) w sidebarze pozwalają zawęzić wyświetlane dane do konkretnego przedziału czasu.  
   - **Metryki** (KPI) wyświetlane są w formie „kafelków” – np. Obrót (PLN), Marża zespołu, Liczba zamówień itp.  
   - **Wykresy** generowane są przy pomocy **Plotly** (wykresy liniowe, obszarowe, słupkowe), wizualizując m.in. dzienny trend sprzedaży i rozbicie produktów.  
   - **Tabela** prezentuje szczegółowe zestawienia np. „per Handlowiec” czy „per Kampania” w CC.

---

## Uwagi Konfiguracyjne
- **Ścieżki do plików CSV:**  
  W kodzie domyślnie ustawione są lokalne ścieżki (np. `C:\Users\k.obrebski\Desktop\...`). Aby uniknąć problemów z różnymi systemami operacyjnymi czy lokalizacjami plików, **zaleca się** trzymanie CSV w folderze `data/` (lub innym folderze w repo) i używanie ścieżek względnych.
- **Logo w sidebarze**:  
  Obecnie wczytywane jest z `C:\\Users\\k.obrebski\\Desktop\\logo_2021.png`. Po przeniesieniu pliku graficznego do repozytorium (np. do głównego folderu), wystarczy zmienić w kodzie:  
  ```python
  st.sidebar.image("logo_2021.png", use_container_width=True)
  ```
- **Buforowanie danych**:  
  W Streamlit zastosowano dekorator `@st.cache_data` (od wersji Streamlit 1.18+), który przyspiesza wielokrotne wczytywanie tych samych plików CSV.  
- **Zmiana widoku**:  
  W **sidebarze** dostępny jest przełącznik `view_option`, który pozwala wybrać między statystykami *Sprzedaż* oraz *Obsługa Klienta (CC)*.

---

## Rozwój i Plany
- Rozszerzenie sekcji *Obsługa Klienta (CC)* o dodatkowe statystyki i wskaźniki (np. średni czas rozmowy, time to response itp.).
- Dostosowanie ścieżek do plików CSV w taki sposób, aby współgrały z repozytorium GitHub (np. katalog `data/`).
- Dodanie testów jednostkowych (np. **pytest**) dla funkcji przetwarzających dane.
- Możliwość przeglądania danych z większych przedziałów czasowych lub porównywania różnych miesięcy w jednym widoku.
- Wdrożenie autentykacji, aby zabezpieczyć dostęp do danych w środowisku produkcyjnym.

---

## Autor
Projekt przygotowany przez [Caranthir-0](https://github.com/Caranthir-0).  
Wszelkie sugestie i uwagi proszę zgłaszać w zakładce [Issues](https://github.com/Caranthir-0/DashboardCC/issues).

---

## Licencja
Ten projekt jest dostępny na licencji **Corab Copyright**. Szczegółowe informacje znajdziesz w pliku [LICENSE](LICENSE) (jeśli został dodany do repozytorium).

---
