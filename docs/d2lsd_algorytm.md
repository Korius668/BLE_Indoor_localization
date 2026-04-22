```mermaid
graph TD
    

    subgraph Dane wejściowe 
        subgraph Inicjalizacja
        A[Dane startowe: <br><b>p</b>₀, <b>v</b>₀]
        M[Warunki maksymalne: <br>v<sub>max</sub>, a<sub>max</sub>]
        end
    LS
    A-->N[Dane historyczne: <br><b>p</b><sub>n-1</sub>, <b>v</b><sub>n-1</sub>]
    LS[Algorytm LS] --- LS_LABEL(["<b>p</b><sub>LS n</sub>"]) --> B
    end

    N --> B["<b>d</b> = <b>p</b><sub>LS n</sub> - <b>p</b><sub>n-1</sub>"]
    B --> C["d̂ = <b>d</b> / |<b>d</b>|"]

    B --> D["v<sub>p</sub> = min(v<sub>max</sub>, |<b>d</b>|/dt)"]
    D --> E["<b>v<sub>p</sub></b> = v<sub>p</sub> · d̂"]
    C --> E
    E --> F["d<b>v</b> = <b>v<sub>p</sub></b> - <b>v</b><sub>n-1</sub>"]

    F --> G["s = min(1, a<sub>max</sub>·dt / |d<b>v</b>|)"]
    
    G --> H["<b>v</b><sub>n</sub> = <b>v</b><sub>n-1</sub> + s · d<b>v</b>"]
    
    H --> I{"|<b>v</b><sub>n</sub>| > v<sub>max</sub>?"}
    
    I -- TAK --> J["<b>v</b><sub>n</sub> = v̂<sub>n</sub> · v<sub>max</sub>"]
    I -- NIE --> K["<b>v</b><sub>n</sub> = <b>v</b><sub>n-1</sub> · k"]
    J --> K
    K --> L["<b>p</b><sub>n</sub> = <b>p</b><sub>n-1</sub> + <b>v</b><sub>n</sub> · dt"]

    
    L -->|n = n+1| N
    style LS_LABEL fill:none,stroke:none
```
## Legenda:

- LS - algorytm najmniejszych kwadratów, który estymuje pozycję na podstawie pomiarów.
- d̂ - jednostkowy wektor kierunku ruchu, obliczany na podstawie różnicy między estymowaną pozycją a poprzednią pozycją.
- v̂<sub>n</sub> - jednostkowy wektor prędkości, obliczany na podstawie prędkości maksymalnej i prędkości estymowanej.