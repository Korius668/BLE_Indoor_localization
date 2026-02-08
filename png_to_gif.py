import imageio
import os

def create_gif_from_png(folder, output_path, fps=10):
    images = []
    files = sorted(os.listdir(folder))

    for file in files:
        if file.endswith(".png"):
            img = imageio.imread(os.path.join(folder, file))
            images.append(img)

    imageio.mimsave(output_path, images, fps=fps)

if __name__ == "__main__":
    create_gif_from_png("output_LS2", "output_LS2.gif", fps=2)
    create_gif_from_png("output_DLS2", "output_DLS2.gif", fps=2)
    create_gif_from_png("output_EKF2", "output_EKF2.gif", fps=2)
    create_gif_from_png("output_PF2", "output_PF2.gif", fps=2)
    create_gif_from_png("output_MLE2", "output_MLE2.gif", fps=2)