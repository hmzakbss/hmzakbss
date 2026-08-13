import os
import requests
import matplotlib.pyplot as plt
import numpy as np

USERNAME = "hmzakbss"
TOKEN = os.getenv("GH_TOKEN")

headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

def get_language_stats():
    print("Repolar taranıyor...")
    repos_url = f"https://api.github.com/users/hmzakbss/repos?per_page=100"
    repos = requests.get(repos_url, headers=headers).json()
    
    languages = {}
    for repo in repos:
        # Forklanmış repoları dahil etmiyoruz
        if not repo.get('fork') and repo.get('languages_url'):
            repo_langs = requests.get(repo['languages_url'], headers=headers).json()
            for lang, bytes_count in repo_langs.items():
                languages[lang] = languages.get(lang, 0) + bytes_count
                
    return languages

def draw_bubble_chart(languages):
    if not languages:
        print("Dil verisi bulunamadı.")
        return

    # En çok kullanılan ilk 15 dili alalım (kalabalığı önlemek için)
    sorted_langs = dict(sorted(languages.items(), key=lambda item: item[1], reverse=True)[:15])
    
    labels = list(sorted_langs.keys())
    sizes = list(sorted_langs.values())
    
    # Bubble boyutlarını normalize edelim
    max_size = max(sizes)
    normalized_sizes = [(s / max_size) * 8000 for s in sizes]
    
    # NumPy ile bubble'lar için rastgele ama estetik koordinatlar oluşturalım
    np.random.seed(42) 
    x = np.random.rand(len(labels))
    y = np.random.rand(len(labels))
    colors = np.random.rand(len(labels))
    
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, s=normalized_sizes, c=colors, alpha=0.6, cmap="viridis", edgecolors="white", linewidth=2)
    
    for i, label in enumerate(labels):
        plt.annotate(label, (x[i], y[i]), ha='center', va='center', 
                     fontsize=10, weight='bold', color='black')
    
    plt.axis('off')
    plt.title("GitHub Language Usage", fontsize=16, weight='bold', color='#333333')
    
    # SVG olarak kaydediyoruz (README'de en net bu şekilde görünür)
    plt.savefig("languages_bubble.svg", format="svg", bbox_inches='tight', transparent=True)
    print("languages_bubble.svg başarıyla oluşturuldu!")

if __name__ == "__main__":
    langs = get_language_stats()
    draw_bubble_chart(langs)
