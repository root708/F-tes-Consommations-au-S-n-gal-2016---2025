# Fêtes et consommation au Sénégal : dix ans d'achats à la loupe (2016-2025)

Projet d'analyse de données et de prévision de la demande autour des grandes fêtes du Sénégal (Tabaski, Korité, Magal de Touba, Maouloud, Tamkharit, Pâques, Pèlerinage de Popenguine, Noël, Ramadan).

Réalisé dans le cadre du cours **Python avancé · L3 IA** à l'**ISM École d'ingénieurs**.
**Auteur :** Papa Arona SENE

## Objectif

Mesurer l'effet des fêtes sur les ventes d'un réseau de 10 points de vente et de 15 catégories de produits, prévoir la demande un an à l'avance, comprendre l'endettement des ménages après la fête, puis produire un plan quotidien pour 2026.

## Contenu du notebook

Le notebook `fetes_conso_senegal.ipynb` est organisé en 7 parties, chacune terminée par une conclusion.

| Partie | Thème | Idée clé |
|---|---|---|
| 1 | Audit et nettoyage | 300 doublons, 530 catégories mal saisies, 1 060 quantités manquantes, 29 négatives, 36 aberrantes, 8 jours manquants. Les pics de fête sont conservés, les erreurs imputées (530 490 lignes propres). |
| 2 | Variables d'événement | Jours avant/après chaque fête calculés avec `merge_asof` sur les 3 653 dates uniques, sans boucle sur les lignes. |
| 3 | Mesure des uplifts | Vente moyenne dans la fenêtre d'achat ÷ référence J-60 à J-31, par fête et par catégorie, avec traitement des chevauchements entre fêtes. |
| 4 | Prévision à un an | Baselines naïves, Ridge et HistGradientBoosting (perte de Poisson), évalués par WAPE. |
| 5 | Endettement après la fête | Régression logistique et HGB, importance par permutation, test d'équité sans religion ni confrérie. |
| 6 | Profils de dépense | K-means (k=3) sur les parts de dépense et l'effort budgétaire des ménages en 2025. |
| 7 | Plan 2026 | Grille 365 jours × 10 magasins × 15 catégories (54 750 lignes), intervalles par régression quantile, effet des promotions. |

## Principaux résultats

- **La Tabaski recule de 10 à 11 jours par an** : une variable « mois » est donc trompeuse. La distance en jours à la prochaine fête reste valable.
- **Uplifts médians marquants** : moutons ×10,6 pour la Tabaski, dattes ×4,1 pour la Korité, jouets ×4,0 pour Noël.
- **Magal et Maouloud sont des effets locaux** : le Magal multiplie par 2,5 le chiffre d'affaires de Touba mais à peine celui de Dakar (×1,06). Un modèle national les gommerait.
- **Chevauchements** : en 2025, l'uplift « Popenguine » des moutons passe de 7,6 à 0,45 une fois les jours de la Tabaski retirés. On mesurait la Tabaski.
- **Prévision (test 2025, évalué une seule fois)** : WAPE de 0,159 sur l'année et 0,160 en fenêtres d'événement pour HGB, contre 0,233 pour la meilleure baseline naïve dans les fenêtres, soit environ 31 % d'erreur en moins.
- **Endettement** : 44,9 % des ménages s'endettent après la Tabaski, et 45,8 % de ceux qui financent par crédit. ROC AUC d'environ 0,82. Retirer la religion et la confrérie ne change pas les performances.
- **Segmentation** : 80 % de ménages acheteurs de mouton, 15 % de ruraux modestes sans mouton (les plus fragiles), 5 % à petit effort.

## Découpage temporel

Entraînement 2016-2023, validation 2024, test 2025. Le modèle final est réentraîné sur 2016-2025 pour prévoir 2026.

## Données

Le notebook lit cinq fichiers CSV qui ne sont **pas inclus** dans ce dépôt :

- `ventes_journalieres.csv`
- `categories.csv`
- `magasins.csv`
- `calendrier_evenements.csv`
- `enquete_menages.csv`

Place-les dans le dossier `data/`, puis adapte la variable `DATA_DIR` au début de la partie 1, et `OUT_DIR` dans la partie 7 :

```python
DATA_DIR = Path("data")
OUT_DIR = Path("outputs")
```

## Installation et lancement

```bash
git clone https://github.com/<ton-user>/fetes-conso-senegal.git
cd fetes-conso-senegal
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook fetes_conso_senegal.ipynb
```

Python 3.9 ou plus récent est nécessaire.

## Tableau de bord

Une fois le notebook exécuté (il génère `outputs/prevision_2026.csv`), lance l'application Streamlit :

```bash
python -m streamlit run app.py
```

Elle permet de filtrer la prévision 2026 par catégorie, point de vente et période, et d'exporter le résultat.

## Sortie produite

`outputs/prevision_2026.csv` : prévision quotidienne 2026 (`prevu`) et plafond P90 (`q90`) pour chaque magasin et chaque catégorie.

## Limites

- Aucune promotion ni variation de prix n'est supposée pour 2026.
- La date exacte d'une fête musulmane peut bouger d'un jour.
- Le facteur de correction des pics, estimé sur la seule année 2025, est bruité.
- Le plafond P90 d'une fenêtre est une somme de quantiles quotidiens, donc supérieur au vrai quantile du total.

## Stack

Python, pandas, NumPy, scikit-learn, matplotlib, seaborn, Jupyter, Streamlit.
