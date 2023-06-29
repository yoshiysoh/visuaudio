#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


# In[2]:


characters = []
colors = []
# V
character = np.array([
    [0, 4],
    [1.5, 0],
    [3, 4],
])
characters.append(character)
colors.append("k")
# i (dot)
r = 0.2
character = np.array([
    [5-r, 3+r],
    [5+r, 3+r],
    [5+r, 3-r],
    [5-r, 3-r],
    [5-r, 3+r],
])
characters.append(character)
colors.append("C0")
# i (line)
character = np.array([
    [5, 2],
    [5, 0],
])
characters.append(character)
colors.append("k")
# s
character = np.array([
    [9, 3],
    [7, 3],
    [7, 1.5],
    [9, 1.5],
    [9, 0],
    [7, 0],
])
characters.append(character)
colors.append("k")
# u
character = np.array([
    [11, 3],
    [11, 0],
    [13, 0],
    [13, 3],
])
characters.append(character)
colors.append("k")
# A (upper colors)
character = np.array([
    [15, 4],
    [18, 4],
    [18, 2],
    [15, 2],
    [15, 4],
])
characters.append(character)
colors.append("C1")
# A (lower left line)
character = np.array([
    [15, 2],
    [15, 0],
])
characters.append(character)
colors.append("C1")
# A (lower right line)
character = np.array([
    [18, 2],
    [18, 0],
])
characters.append(character)
colors.append("C1")
# u
character = np.array([
    [20, 3],
    [20, 0],
    [22, 0],
    [22, 3],
])
characters.append(character)
colors.append("k")
# d
character = np.array([
    [26, 2],
    [24, 2],
    [24, 0],
    [26, 0],
    [26, 3],
])
characters.append(character)
colors.append("C1")
# i (dot)
r = 0.2
character = np.array([
    [28-r, 3+r],
    [28+r, 3+r],
    [28+r, 3-r],
    [28-r, 3-r],
    [28-r, 3+r],
])
characters.append(character)
colors.append("C0")
# i (line)
character = np.array([
    [28, 2],
    [28, 0],
])
characters.append(character)
colors.append("k")
# O
character = np.array([
    [30, 4],
    [33, 4],
    [33, 0],
    [30, 0],
    [30, 4],
])
characters.append(character)
colors.append("C0")


# In[3]:


fig, ax = plt.subplots()
ax.axis("off")
ax.set_aspect("equal")
for character in characters:
    ax.plot(character[:, 0], character[:, 1], c="k")
fig.savefig("logo.png")


# In[4]:


fig, ax = plt.subplots()
ax.axis("off")
ax.set_aspect("equal")
for character, c in zip (characters, colors):
    ax.plot(character[:, 0], character[:, 1], c=c)
fig.savefig("logo_light.png", transparent=False)


# In[5]:


with plt.style.context("dark_background"):
    fig, ax = plt.subplots()
    ax.axis("off")
    ax.set_aspect("equal")
    for character, c in zip (characters, colors):
        if c == 'k':
            c = 'w'
        ax.plot(character[:, 0], character[:, 1], c=c)
    fig.savefig("logo_dark.png", transparent=False)


# In[6]:


logo_light = Image.open("logo_light.png")
logo_dark = Image.open("logo_dark.png")

size = logo_light.size

# left, top, right, bottom
half_light = logo_light.crop((0, 0, size[0]/2, size[1]))
half_dark = logo_dark.crop((size[0]/2, 0, size[0], size[1]))

combi = np.hstack((half_light, half_dark))
combi = Image.fromarray(combi)
combi 


# In[7]:


combi.save("logo_light_dark.png")

