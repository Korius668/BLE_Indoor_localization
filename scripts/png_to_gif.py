import os

import imageio


def create_gif_from_png(filename, output_folder, fps=10):
    # Always save to gif/ directory from repository root

    output_path = os.path.join("gif",filename)
    
    images = []
    files = sorted(os.listdir(os.path.join("outputs",output_folder)))

    for file in files:
        if file.endswith(".png"):
            img = imageio.imread(os.path.join(output_folder, file))
            images.append(img)

    imageio.mimsave(output_path, images, fps=fps)

if __name__ == "__main__":
    create_gif_from_png("LS2.gif","output_LS2",fps=5)
    create_gif_from_png("DLS2.gif","output_DLS2",fps=5)
    create_gif_from_png("EKF2.gif","output_EKF2",fps=5)
    create_gif_from_png("PF2.gif","output_PF2",fps=5)
    create_gif_from_png("MLE2.gif","output_MLE2",fps=5)