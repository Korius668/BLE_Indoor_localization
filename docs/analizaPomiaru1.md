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

## Odległość od nadajników geometryczna
Odległość od punktu `(x, y)` do nadajnika o współrzędnych `(x_i, y_i)` wyrażona jest wzorem euklidesowym:



\[
d_i = \sqrt{(x - x_i)^2 + (y - y_i)^2}
\]


## Odległości od nadajników z mocy sygnału (RSSI)
Dzięki mocy sygnału (RSSI) można oszacować odległość od nadajnika. Potrzebne jednak jest poznanie zależności między mocą sygnału a odległością.

W tym celu użyjemy wcześniej przeprowadzonych pomiarów mocy sygnału w różnych znanych pozycjach.
### Regresja Liniowa
Zależność między mocą sygnalu (RSSI) a odległością od nadajnika, wyznaczymy przy pomocy regresji liniowej na podstawie zebranych danych pomiarowych.
Poniższy wykres przedstawia wyniki regresji liniowej, gdzie oś X odpowiada logarytmowi odległości od nadajnika, a oś Y reprezentuje moc sygnału (RSSI w dBm).
![Regresja Liniowa](obrazy/regresja_liniowa.png)
Ten sam wykres ale z osią X w skali liniowej.
![Regresja Liniowa](obrazy/regresja_liniowa2.png)

Obliczoną z regresji liniowej odległość będziemy oznaczać jako: \[d(s_i)\] 
gdzie:
- $s_i$ to moc sygnału z nadajnika i(RSSI).


## Algorytm optymalizacji (Funkcja celu)

Do aproksymacji pozycji  wykorzystano iteracyjny algorytm minimalizacji błędów. Jego zadaniem jest znalezienie takich współrzędnych , dla których odległości geometryczne  są jak najbardziej zbliżone do odległości wyznaczonych z pomiarów .

### Residuum

Jako miarę błędu lokalnego (residuum) dla pojedynczego nadajnika przyjmuje się różnicę bezwzględną pomiędzy obiema odległościami:

$$r_i = | d_i - d(s_i) |$$

### Zmodyfikowana funkcja kosztu

Zamiast klasycznej metody najmniejszych kwadratów (sumy kwadratów błędów), zastosowano zmodyfikowaną funkcję celu. Residuum z klasycznego wzoru zostało dodatkowo podzielone przez moc sygnału. Pozwala to na promowanie mniejszych błędów przy większych mocach sygnału (czyli mniejszych odległościach od nadajnika), co jest korzystne z punktu widzenia dokładności lokalizacji.:

$$F(x, y) = \sum_{i=1}^{N} \frac{| d_i - d(s_i) |}{d(s_i)}$$

gdzie:
- $N$ - liczba nadajników


## Monte Carlo

Korzystając z pomiarów, dla każdego z nadajników, w każdej pozycji pomiarowej, wyliczona została średnia moc sygnału.

Następnie wokół tej wartości wygenerowano, z rozkładu normalnego, populację nowych mocy.


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


Kolejno przy użyciu zależności wyznaczonej wczesniej z regresji liniowej, wyliczono odległość odpowiadającą danej mocy. Wartości tych odległości następnie użyto w algorytmie najmniejszych kwadratów w celu estymacji pozycji urządzenia pomiarowego. 



### Algorytm least squares
![Algorytm najmniejszych kwadratów](obrazy/algorytm.png)



W celu oszacowania odległości od nadajników na podstawie zmierzonych wartości mocy sygnału (RSSI), zastosowano metodę Monte Carlo. Dla każdej z 11 pozycji pomiarowych, wygenerowano 1000 próbek mocy sygnału z rozkładu normalnego, wykorzystując średnią i odchylenie standardowe zmierzonych wartości RSSI. Następnie, korzystając z wcześniej wyznaczonej regresji liniowej, przeliczono każdą z wygenerowanych próbek mocy sygnału na odpowiadającą jej odległość od nadajnika.

Poniżej przedstawiono wyniki estymacji pozycji dla każdej z 11 pozycji pomiarowych.

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