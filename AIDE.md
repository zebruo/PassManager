# PassManager v{VERSION} - Guide d'utilisation

## 📌 FONCTIONNALITÉS PRINCIPALES

### Ajouter un mot de passe
Remplissez les champs Site, Utilisateur et Mot de passe, puis cliquez sur "Ajouter".
Vous pouvez également ajouter une note pour chaque entrée.

### Générer un mot de passe sécurisé
Cliquez sur le bouton "Gen ✨" à côté du champ mot de passe.
Configurez la longueur et les options (majuscules, chiffres, symboles).

### Afficher/Masquer les mots de passe
Utilisez l'icône œil (👁) pour afficher temporairement un mot de passe.
Cliquez à nouveau pour le masquer.

### Copier rapidement
Utilisez les boutons avec les icônes utilisateur (👤) et clé (🔑) pour copier
rapidement les informations dans le presse-papier.

⚠️ **Sécurité** : Par mesure de sécurité, le contenu copié dans le presse-papier
est automatiquement effacé après 30 secondes.

### Modifier un mot de passe
Cliquez sur le bouton crayon (✎) pour éditer une entrée existante.

### Supprimer un mot de passe
Cliquez sur le bouton poubelle (🗑️) puis confirmez la suppression.

### Rechercher
Utilisez la barre de recherche pour filtrer vos mots de passe par site,
utilisateur ou note.

---

## 🔒 SÉCURITÉ

### Mot de passe maître
Tous vos mots de passe sont chiffrés avec votre mot de passe maître.
Ne partagez JAMAIS ce mot de passe et choisissez-le suffisamment robuste.

### Déconnexion automatique
Pour votre sécurité, l'application se déconnecte automatiquement après
60 minutes d'inactivité.

### Changer le mot de passe maître
Utilisez le bouton "Changer MdP Maître" dans la barre supérieure.
Tous vos mots de passe seront automatiquement rechiffrés.

---

## 💾 SAUVEGARDE & EXPORTATION

### Exporter les mots de passe (TEXTE CLAIR)
Exporte tous vos mots de passe déchiffrés dans un fichier .txt ou .csv.
⚠️ **ATTENTION**: Ces fichiers contiennent vos mots de passe en clair !

### Exporter la base de données (CHIFFRÉ)
Crée une copie de sauvegarde de votre base de données chiffrée.
Cette sauvegarde est sécurisée et peut être restaurée ultérieurement.

---

## 📁 EMPLACEMENT DES DONNÉES

### Windows
```
C:\Users\[VotreNom]\AppData\Roaming\PassManager\passwords.db
```

### Linux
```
~/.config/PassManager/passwords.db
```

### macOS
```
~/Library/Application Support/PassManager/passwords.db
```

---

## 🔄 GESTION DE LA BASE DE DONNÉES

### Première installation
Lors de votre première utilisation de PassManager :
1. L'application crée automatiquement le dossier `PassManager` dans votre répertoire utilisateur
2. Vous êtes invité à créer un **mot de passe maître** (minimum 8 caractères)
3. Le fichier `passwords.db` est créé et chiffré avec votre mot de passe maître
4. Tous vos futurs mots de passe seront stockés dans ce fichier

### Lors des mises à jour
Quand vous installez une nouvelle version de PassManager :
- ✅ **Votre base de données est conservée** - Elle n'est jamais supprimée
- ✅ **Vos mots de passe restent accessibles** - Utilisez le même mot de passe maître
- ✅ **Aucune migration nécessaire** - La nouvelle version utilise automatiquement votre base existante
- ✅ **Désinstallation sûre** - Même si vous désinstallez PassManager, votre fichier `passwords.db` reste intact

### Sauvegarde recommandée
Pour protéger vos données :
1. Utilisez le bouton **💾 Exporter DB** pour créer une copie de sauvegarde chiffrée
2. Conservez cette sauvegarde dans un endroit sûr (clé USB, cloud personnel, etc.)
3. En cas de problème, renommez simplement votre sauvegarde en `passwords.db` et replacez-la dans :
   - **Windows** : `C:\Users\[VotreNom]\AppData\Roaming\PassManager\`
   - **Linux** : `~/.config/PassManager/`
   - **macOS** : `~/Library/Application Support/PassManager/`

⚠️ **Important** : Sans votre mot de passe maître, il est **impossible** de récupérer vos données. Conservez-le précieusement !

---

## ❓ ASTUCES

- Les icônes changent de couleur pour confirmer vos actions
- Les tooltips (infobulles) vous guident au survol des boutons
- Utilisez le bouton "Afficher tous les MdP" pour voir tous les mots de passe en même temps
- Le générateur de mots de passe permet de créer des mots de passe très sécurisés

---

## 📧 SUPPORT

**Version**: {VERSION}
**Date**: {DATE}
**Développé par**: edurel  
**Usage**: Non-commercial uniquement

Pour toute question ou problème, référez-vous à la documentation ou contactez
le support technique :
📨 **zebruo@gmail.com**
