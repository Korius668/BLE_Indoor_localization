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
![Mapa RSSI - Nadajnik 1](obrazy/mapa_rssi_nadajnik_1.png)
![Mapa RSSI - Nadajnik 2](obrazy/mapa_rssi_nadajnik_2.png)
![Mapa RSSI - Nadajnik 3](obrazy/mapa_rssi_nadajnik_3.png)
![Mapa RSSI - Nadajnik 4](obrazy/mapa_rssi_nadajnik_4.png)
![Mapa RSSI - Nadajnik 5](obrazy/mapa_rssi_nadajnik_5.png)
![Mapa RSSI - Nadajnik 6](obrazy/mapa_rssi_nadajnik_6.png)
![Mapa RSSI - Nadajnik 7](obrazy/mapa_rssi_nadajnik_7.png)
![Mapa RSSI - Nadajnik 8](obrazy/mapa_rssi_nadajnik_8.png)
![Mapa RSSI - Nadajnik 9](obrazy/mapa_rssi_nadajnik_9.png)
![Mapa RSSI - Nadajnik 10](obrazy/mapa_rssi_nadajnik_10.png)
![Mapa RSSI - Nadajnik 11](obrazy/mapa_rssi_nadajnik_11.png)
![Mapa RSSI - Nadajnik 12](obrazy/mapa_rssi_nadajnik_12.png)
## Regresja Liniowa
![Regresja Liniowa](obrazy/regresja_liniowa.png)
## Rozrzut wygenowanych próbek odległości
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

## Least Squares - Estymacja pozycji
Z pomiarów, dla każdego z nadajników w każdej pozycji pomiarowej, wyliczono średnią moc sygnału. Wokół tej wartości wygenerowano z rozkładu normalnego, populację nowych mocy sygnału. Następnie przy użyciu znanego wzoru z regresji liniowej wyliczono jaka odległość odpowiada tej mocy dla tego nadajnika. Wartości tych odległości następnie użyto w algorytmie najmniejszych kwadratów w celu estymacji pozycji urządzenia pomiarowego. Poniżej przedstawiono wyniki estymacji pozycji dla każdej z 11 pozycji pomiarowych.


### Algorytm minimalizacji metodą najmniejszych kwadratów

Algorytm wykorzystuje funkcję `calculate_residuals`, która oblicza różnicę pomiędzy:
- **rzeczywistymi odległościami** od punktu estymowanego `(x, y)` do beaconów,
- a **wyliczonymi odległościami z rssi** (`distances`).

#### Wzór na odległość
Odległość od punktu `(x, y)` do beacona o współrzędnych `(x_i, y_i)` wyrażona jest wzorem euklidesowym:



\[
d_i = \sqrt{(x - x_i)^2 + (y - y_i)^2}
\]



#### Residuła (różnica)
Residuła dla każdego beacona to różnica pomiędzy obliczoną odległością a zmierzoną:



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