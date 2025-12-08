import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


mapa_path = "mapa/map4.PNG"
pozycjeNadajnikow_path = "mapa/pozycjeNadajnikow.txt"
reference_points = [
        ((125, 800), (0, 0)),
        ((205,800),( 2.8,0)),
        ((140, 30),  (0.35, 27)),
    ]

df_transmitters = pd.read_csv(pozycjeNadajnikow_path, header="infer", names=None)
background = mpimg.imread(mapa_path)

def image_to_real_coords_affine(image_x, image_y, M_inv, c, f):
    adjusted_image_coords = np.array([image_x - c, image_y - f])
    real_coords = np.dot(M_inv, adjusted_image_coords)
    return real_coords[0], real_coords[1]

def plot_map(ax=None, background=background, df_transmitters=df_transmitters, reference_points=reference_points):
    height, width = background.shape[:2]
     # fig2 = plt.figure(figsize=(10, 8))
    if ax is None:
        ax = plt.gca()

    image_coords = np.array([point[0] for point in reference_points])
    real_world_coords = np.array([point[1] for point in reference_points])

    model_x = LinearRegression()
    model_x.fit(real_world_coords, image_coords[:, 0])
    a, b = model_x.coef_
    c = model_x.intercept_

    model_y = LinearRegression()
    model_y.fit(real_world_coords, image_coords[:, 1])
    d, e = model_y.coef_
    f = model_y.intercept_

    original_corners_pixels = np.array([[0, 0], [width-1, 0], [width-1, height-1], [0, height-1]])
    determinant = a * e - b * d
    M_inv = (1 / determinant) * np.array([[e, -b], [-d, a]])
    real_world_corners = np.array([image_to_real_coords_affine(px, py, M_inv, c, f) for px, py in original_corners_pixels])

    min_real_x, min_real_y = np.min(real_world_corners, axis=0)
    max_real_x, max_real_y = np.max(real_world_corners, axis=0)

    ax.imshow(background, extent=[min_real_x, max_real_x, min_real_y, max_real_y])
    return ax

def plot_transmitters_on_map(ax=None, background=background, df_transmitters=df_transmitters, reference_points=reference_points):
    if ax is None:
        fig, ax = plt.subplots(figsize=(4, 6))
    ax = plot_map(background=background, df_transmitters=df_transmitters, reference_points=reference_points)
    for i, row in df_transmitters.iterrows():
        ax.text(row['x'], row['y'], str(int(row['Id'])), color='white', fontsize=8, ha='center', va='center') # Use 'Id' column for transmitter ID and cast to int

    ax.set_title('Mapa z zaznaczonymi nadajnikami')
    ax.set_xlabel('Oś X (m)')
    ax.set_ylabel('Oś Y (m)')
    ax.set_ylim(-2, 32)

    ax.scatter(df_transmitters['x'], df_transmitters['y'], color='green', s=50, label='Nadajniki')
    ax.legend(loc='upper right')
    ax.set_aspect('equal', adjustable='box')

    
    return ax

if __name__ == "__main__":
       
    print("Pozycje nadajników:")
    print(df_transmitters)
    ax = plot_transmitters_on_map()
    plt.savefig("obrazy/rozmieszczenie_nadajnikow.png")
    plt.show()
    