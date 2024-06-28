# Utiliser une image Python slim avec la version 3.9 (ou une autre version compatible avec vos dépendances)
FROM python:3.10

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier pyproject.toml et poetry.lock dans le conteneur
COPY pyproject.toml poetry.lock ./

# Installer Poetry
RUN pip install --no-cache-dir poetry

# Installer les dépendances spécifiées dans le pyproject.toml (sans les dépendances de développement)
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi
# Copier tous les fichiers de l'application dans le conteneur
COPY . .

# Exposer le port 5000 utilisé par Flask
EXPOSE 5000

# Commande pour démarrer l'application Flask
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
