from tqdm import tqdm
from time import sleep

for i in tqdm(range(300), desc="Rendering...",ncols=120):
    sleep(0.02)