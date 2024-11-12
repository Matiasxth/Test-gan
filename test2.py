# -*- coding: utf-8 -*-
"""Test2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1L1vA2CDeQK3Qtx0sPu2HkiNadYeac6wo
"""

!pip install torch torchvision matplotlib

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from torchvision.utils import save_image, make_grid
import matplotlib.pyplot as plt
import numpy as np
import os
from tqdm.notebook import tqdm

# Configuración de GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Usando dispositivo: {device}")

class Generator(nn.Module):
    def __init__(self, latent_dim):
        super(Generator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(128, 256),
            nn.BatchNorm1d(256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(256, 512),
            nn.BatchNorm1d(512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(512, 1024),
            nn.BatchNorm1d(1024),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(1024, 28*28),
            nn.Tanh()
        )

    def forward(self, x):
        x = self.model(x)
        x = x.view(x.size(0), 1, 28, 28)
        return x

class Discriminator(nn.Module):
    def __init__(self):
        super(Discriminator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(28*28, 512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        x = x.view(x.size(0), -1)
        return self.model(x)

# Parámetros
latent_dim = 100
batch_size = 64
num_epochs = 50
learning_rate = 0.0002

# Inicialización de modelos
generator = Generator(latent_dim).to(device)
discriminator = Discriminator().to(device)

# Optimización
optimizer_G = optim.Adam(generator.parameters(), lr=learning_rate, betas=(0.5, 0.999))
optimizer_D = optim.Adam(discriminator.parameters(), lr=learning_rate, betas=(0.5, 0.999))
criterion = nn.BCELoss()
# Parámetros
latent_dim = 100
batch_size = 64
num_epochs = 50
learning_rate = 0.0002

# Inicialización de modelos
generator = Generator(latent_dim).to(device)
discriminator = Discriminator().to(device)

# Optimización
optimizer_G = optim.Adam(generator.parameters(), lr=learning_rate, betas=(0.5, 0.999))
optimizer_D = optim.Adam(discriminator.parameters(), lr=learning_rate, betas=(0.5, 0.999))
criterion = nn.BCELoss()

from torchvision import datasets

# Transformación del dataset
transform = transforms.Compose([
    transforms.Resize(28),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])

# Carga del dataset
dataloader = torch.utils.data.DataLoader(
    datasets.MNIST('.', train=True, download=True, transform=transform),
    batch_size=batch_size, shuffle=True
)

# Crear carpeta para guardar imágenes generadas
os.makedirs("images", exist_ok=True)

for epoch in range(num_epochs):
    for i, (imgs, _) in enumerate(tqdm(dataloader, desc=f"Epoch {epoch+1}/{num_epochs}")):

        # Configura etiquetas reales y falsas
        real_labels = torch.ones((imgs.size(0), 1)).to(device)
        fake_labels = torch.zeros((imgs.size(0), 1)).to(device)

        # Entrena el Discriminador
        optimizer_D.zero_grad()
        real_imgs = imgs.to(device)
        real_loss = criterion(discriminator(real_imgs), real_labels)

        z = torch.randn(imgs.size(0), latent_dim).to(device)
        fake_imgs = generator(z)
        fake_loss = criterion(discriminator(fake_imgs.detach()), fake_labels)

        d_loss = real_loss + fake_loss
        d_loss.backward()
        optimizer_D.step()

        # Entrena el Generador
        optimizer_G.zero_grad()
        g_loss = criterion(discriminator(fake_imgs), real_labels)
        g_loss.backward()
        optimizer_G.step()

    # Guarda y muestra imágenes generadas al final de cada época
    print(f"Epoch {epoch+1}/{num_epochs} | D Loss: {d_loss.item()} | G Loss: {g_loss.item()}")
    save_image(fake_imgs[:25], f"images/{epoch+1}.png", nrow=5, normalize=True)

import PIL.Image as Image
from IPython.display import display

# Mostrar la última imagen generada
display(Image.open(f"images/{num_epochs}.png"))