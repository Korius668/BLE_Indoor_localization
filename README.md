# Analiza pomiaru 1
## Rozmieszczenie nadajników
![Rozmieszczenie nadajników](obrazy/rozmieszczenie_nadajnikow.png)
## Pozycje pomiarowe
![Pozycje pomiarowe](obrazy/pozycje_pomiarowe.png)
## Boxploty RSSI dla poszczególnych nadajników
![Boxploty RSSI - Pozycja 1](obrazy/boxplot_rssi_pozycja_1.png)
![Boxploty RSSI - Pozycja 2](obrazy/boxplot_rssi_pozycja_2.png)
![Boxploty RSSI - Pozycja 3](obrazy/boxplot_rssi_pozycja_3.png)
![Boxploty RSSI - Pozycja 4](obrazy/boxplot_rssi_pozycja_4.png)
![Boxploty RSSI - Pozycja 5](obrazy/boxplot_rssi_pozycja_5.png)
![Boxploty RSSI - Pozycja 6](obrazy/boxplot_rssi_pozycja_6.png)
![Boxploty RSSI - Pozycja 7](obrazy/boxplot_rssi_pozycja_7.png)
![Boxploty RSSI - Pozycja 8](obrazy/boxplot_rssi_pozycja_8.png)
![Boxploty RSSI - Pozycja 9](obrazy/boxplot_rssi_pozycja_9.png)
![Boxploty RSSI - Pozycja 10](obrazy/boxplot_rssi_pozycja_10.png)
![Boxploty RSSI - Pozycja 11](obrazy/boxplot_rssi_pozycja_11.png)

## Mapa z siłą sygnału (RSSI)
![Mapa RSSI - Pozycja 1](obrazy/mapa_rssi_pozycja_1.png)
![Mapa RSSI - Pozycja 2](obrazy/mapa_rssi_pozycja_2.png)
![Mapa RSSI - Pozycja 3](obrazy/mapa_rssi_pozycja_3.png)
![Mapa RSSI - Pozycja 4](obrazy/mapa_rssi_pozycja_4.png)
![Mapa RSSI - Pozycja 5](obrazy/mapa_rssi_pozycja_5.png)
![Mapa RSSI - Pozycja 6](obrazy/mapa_rssi_pozycja_6.png)
![Mapa RSSI - Pozycja 7](obrazy/mapa_rssi_pozycja_7.png)
![Mapa RSSI - Pozycja 8](obrazy/mapa_rssi_pozycja_8.png)
![Mapa RSSI - Pozycja 9](obrazy/mapa_rssi_pozycja_9.png)
![Mapa RSSI - Pozycja 10](obrazy/mapa_rssi_pozycja_10.png)
![Mapa RSSI - Pozycja 11](obrazy/mapa_rssi_pozycja_11.png)

## Odległość od nadajników
Dzięki mocy sygnału (RSSI) można oszacować odległość od nadajnika. Potrzebne jednak jest poznanie zależności między mocą sygnału a odległością.
W tym celu użyjemy wcześniej przeprowadzonych pomiarów mocy sygnału w różnych znanych pozycjach.
Dzięki temu możemy wyznaczyć zależność między mocą sygnału a odległością.
### Regresja Liniowa
Zależność między mocą sygnalu (RSSI) a odległością od nadajnika, wyznaczymy przy pomocy regresji liniowej na podstawie zebranych danych pomiarowych.
Poniższy wykres przedstawia wyniki regresji liniowej, gdzie oś X odpowiada logarytmowi odległości od nadajnika, a oś Y reprezentuje moc sygnału (RSSI w dBm).
![Regresja Liniowa](obrazy/regresja_liniowa.png)
Ten sam wykres ale z osią X w skali liniowej.
![Regresja Liniowa](obrazy/regresja_liniowa2.png)

## Algorytm minimalizacji metodą najmniejszych kwadratów
Do aproksymacji pozycji, użyty zostanie algorytm najmniejszych kwadratów

### Monte Carlo + Least Squares

Korzystając z pomiarów, dla każdego z nadajników w każdej pozycji pomiarowej, wyliczona została średnia moc sygnału.
Następnie wokół tej wartości nawygenerowano z rozkładu normalnego, populację nowych mocy sygnałów.

Kolejno przy użyciu zależności wyznaczonej wczesniej z regresji liniowej,wyliczono odległość między  odpowiada tej mocy dla tego nadajnika. Wartości tych odległości następnie użyto w algorytmie najmniejszych kwadratów w celu estymacji pozycji urządzenia pomiarowego. Poniżej przedstawiono wyniki estymacji pozycji dla każdej z 11 pozycji pomiarowych.


Algorytm wykorzystuje funkcję `calculate_residuals`, która oblicza różnicę pomiędzy:
- **rzeczywistymi odległościami** od punktu estymowanego `(x, y)` do beaconów,
a **wyliczonymi odległościami z rssi** (`distances`).

#### Wzór na odległość
Odległość od punktu `(x, y)` do beacona o współrzędnych `(x_i, y_i)` wyrażona jest wzorem euklidesowym:



\[
d_i = \sqrt{(x - x_i)^2 + (y - y_i)^2}
\]



#### Różnica
Różnica pomiędzy obliczoną odległością z wyznaczonego punktu, a tą zmierzoną z mocy:



\[
r_i = d_i - d(s_i)
\]



#### Funkcja celu
Metoda najmniejszych kwadratów minimalizuje sumę kwadratów residuów:



\[
F(x, y) = \sum_{i=1}^{N} \left( \sqrt{(x - x_i)^2 + (y - y_i)^2} - d(s_i) \right)^2
\]

gdzie:
- \( (x, y) \) – szukana pozycja,
- \( (x_i, y_i) \) – współrzędne beaconów,
- \( d_i^{measured} \) – zmierzona odległość do beacona.

#### Własna wersja

\[
F(x, y) = \sum_{i=1}^{N} \frac{| d_i - d(s_i) |}{d(s_i)}
\]
Zamiana kwadratu residuów bierzemy ich wartość absolutną.Zwiększa to rozdzielczość.

Podzielenie przez odległość sprawia, że residua dużych odległości są uważane za mniej istotne, dlatego są mniej redukowane, a algorytm zbliża się bardziej do nadajników z mocniejszą mocą sygnału.




#### Działanie algorytmu
1. **Start** od początkowego przybliżenia `initial_guess`.
2. **Obliczenie residuów** dla wszystkich beaconów.
3. **Minimalizacja** sumy kwadratów residuów przy użyciu `least_squares`.
4. **Wynik** – najlepsze przybliżenie pozycji `(x, y)`, które najbardziej pasuje do zmierzonych odległości.

# Algorytm least squares

```mermaid
flowchart TD

    A[\Pomiar mocy sygnałów nadajników w jednej pozycji/] --> B[Wyliczenie średniej mocy sygnału dla każdego z nadajników]
    B -.-> C[\Generowanie populacji mocy sygnału z rozkładu normalnego/]
    
    F[Losowanie pozycji początkowej] --> G
    C --> H[Obliczanie odległości z mocy sygnału przy pomocy regresji liniowej]
    E[Pozycje beaconów]--> G[Obliczenie odległości do każdego z beaconów]
    H--> J[Obliczenie residuów]
    G-->J
    J -->K[Minimalizacja sumy kwadratów residuów]
    K --> M[Wynik: najlepsze przybliżenie pozycji x,y]
```


## Metoda monte carlo do wyznaczenia odległości

W celu oszacowania odległości od nadajników na podstawie zmierzonych wartości mocy sygnału (RSSI), zastosowano metodę Monte Carlo. Dla każdej z 11 pozycji pomiarowych, wygenerowano 1000 próbek mocy sygnału z rozkładu normalnego, wykorzystując średnią i odchylenie standardowe zmierzonych wartości RSSI. Następnie, korzystając z wcześniej wyznaczonej regresji liniowej, przeliczono każdą z wygenerowanych próbek mocy sygnału na odpowiadającą jej odległość od nadajnika.


![Rozrzut wygenowanych próbek odległości - pozycji 1](obrazy/rozrzut_wygenowanych_probek_odleglosci_pozycji_1.png)
![Rozrzut wygenowanych próbek odległości - pozycji 2](obrazy/rozrzut_wygenowanych_probek_odleglosci_pozycji_2.png)
![Rozrzut wygenowanych próbek odległości - pozycji 3](obrazy/rozrzut_wygenowanych_probek_odleglosci_pozycji_3.png)
![Rozrzut wygenowanych próbek odległości - pozycji 4](obrazy/rozrzut_wygenowanych_probek_odleglosci_pozycji_4.png)
![Rozrzut wygenowanych próbek odległości - pozycji 5](obrazy/rozrzut_wygenowanych_probek_odleglosci_pozycji_5.png)
![Rozrzut wygenowanych próbek odległości - pozycji 6](obrazy/rozrzut_wygenowanych_probek_odleglosci_pozycji_6.png)
![Rozrzut wygenowanych próbek odległości - pozycji 7](obrazy/rozrzut_wygenowanych_probek_odleglosci_pozycji_7.png)
![Rozrzut wygenowanych próbek odległości - pozycji 8](obrazy/rozrzut_wygenowanych_probek_odleglosci_pozycji_8.png)
![Rozrzut wygenowanych próbek odległości - pozycji 9](obrazy/rozrzut_wygenowanych_probek_odleglosci_pozycji_9.png)
![Rozrzut wygenowanych próbek odległości - pozycji 10](obrazy/rozrzut_wygenowanych_probek_odleglosci_pozycji_10.png)
![Rozrzut wygenowanych próbek odległości - pozycji 11](obrazy/rozrzut_wygenowanych_probek_odleglosci_pozycji_11.png)

![Least Squares - Estymacja pozycji - 1](obrazy/least_squares_estymacja_pozycji_1.png)
![Least Squares - Estymacja pozycji - 2](obrazy/least_squares_estymacja_pozycji_2.png)
![Least Squares - Estymacja pozycji - 3](obrazy/least_squares_estymacja_pozycji_3.png)
![Least Squares - Estymacja pozycji - 4](obrazy/least_squares_estymacja_pozycji_4.png)
![Least Squares - Estymacja pozycji - 5](obrazy/least_squares_estymacja_pozycji_5.png)
![Least Squares - Estymacja pozycji - 6](obrazy/least_squares_estymacja_pozycji_6.png)
![Least Squares - Estymacja pozycji - 7](obrazy/least_squares_estymacja_pozycji_7.png)
![Least Squares - Estymacja pozycji - 8](obrazy/least_squares_estymacja_pozycji_8.png)
![Least Squares - Estymacja pozycji - 9](obrazy/least_squares_estymacja_pozycji_9.png)
![Least Squares - Estymacja pozycji - 10](obrazy/least_squares_estymacja_pozycji_10.png)
![Least Squares - Estymacja pozycji - 11](obrazy/least_squares_estymacja_pozycji_11.png)