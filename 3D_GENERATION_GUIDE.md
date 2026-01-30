# 🎨 3D Model Generation avec Tripo AI

## Configuration

### 1. Obtenez votre clé API Tripo

1. Allez sur https://platform.tripo3d.ai/
2. Créez un compte
3. Copiez votre API key

### 2. Configurez la clé API

Éditez `Backend/.env`:

```
TRIPO_API_KEY=votre_clé_api_ici
```

### 3. Installez les dépendances

```bash
cd Backend
pip install python-dotenv requests
```

### 4. Redémarrez le backend

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Utilisation

### Dans l'application:

1. **Ouvrez un produit** (cliquez sur une carte produit)
2. **Cliquez "🎨 Generate Real 3D"**
3. **Attendez 1-2 minutes** pendant que l'IA génère le modèle
4. **Cliquez "✅ View My 3D Model"** pour voir en AR!

### Ce qui se passe:

1. 📸 L'image du produit est envoyée à Tripo AI
2. 🤖 L'IA génère un modèle 3D à partir de la photo
3. 💾 Le modèle GLB est téléchargé dans `Frontend/public/models/`
4. 💿 Le résultat est mis en cache (génération une seule fois)
5. 📱 Utilisez l'AR pour voir le vrai meuble dans votre chambre!

## Fonctionnalités

✅ **Cache intelligent**: Une fois généré, le modèle est réutilisé  
✅ **Stockage local**: Les modèles sont sauvegardés localement  
✅ **Progression**: Notifications de progression en temps réel  
✅ **AR Ready**: Modèles optimisés pour AR mobile

## Pour la démo hackathon

**Dites au jury:**

> "Notre app utilise l'IA générative pour créer des modèles 3D à partir de simples photos 2D. En 1 minute, on transforme une image produit en modèle 3D complet que vous pouvez visualiser en réalité augmentée dans votre propre espace. C'est du vrai machine learning appliqué au e-commerce!"

**Points impressionnants:**

- ✨ IA générative (Tripo AI)
- 📸 Image 2D → Modèle 3D
- 📱 AR immédiat sur mobile
- 💾 Système de cache
- 🎯 Experience utilisateur fluide

## Limites API gratuite Tripo

- **200 crédits/mois** gratuits
- **1 génération ≈ 2-5 crédits**
- Donc ~40-100 modèles/mois

Pour le hackathon, choisissez 2-3 produits à générer pour la démo!

## Troubleshooting

**"TRIPO_API_KEY not configured"**
→ Vérifiez que `.env` existe et contient la clé

**"Task timed out"**
→ Image trop complexe, essayez une photo plus simple

**"Task failed"**
→ Image inadaptée (trop floue, angle bizarre)
→ Utilisez des images de face, fond neutre

## Cache

Les modèles générés sont stockés dans:

- `Frontend/public/models/product-{id}.glb` - Fichier 3D
- `Backend/3d_model_cache.json` - Cache des URLs

Pour régénérer un modèle, supprimez l'entrée du cache.

🚀 Vous êtes prêts pour impressionner le jury!
