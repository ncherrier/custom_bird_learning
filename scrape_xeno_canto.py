import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import urllib.parse


class XenoCantoScraper:
    def __init__(self, base_url, output_folder="data"):
        self.base_url = base_url
        self.output_folder = output_folder
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "fr-FR,fr;q=0.5",
        }

        # Créer le dossier de sortie s'il n'existe pas
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Créer un sous-dossier pour les fichiers audio
        self.audio_folder = os.path.join(output_folder, "audio")
        if not os.path.exists(self.audio_folder):
            os.makedirs(self.audio_folder)

    def get_page(self, url):
        """Récupère une page avec gestion des erreurs et délai entre les requêtes"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            # Délai pour éviter de surcharger le serveur
            time.sleep(1)
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la récupération de la page {url}: {e}")
            return None

    def get_total_pages(self):
        """Détermine le nombre total de pages à scraper"""
        html = self.get_page(self.base_url)
        if not html:
            return 0

        soup = BeautifulSoup(html, "html.parser")
        pagination = soup.select(".results-pages li")

        if not pagination:
            return 1

        # Le dernier élément de pagination contient généralement le nombre total de pages
        last_page_text = pagination[
            -2
        ].text.strip()  # -2 car le dernier est souvent "Next"
        try:
            return int(last_page_text)
        except ValueError:
            print("Impossible de déterminer le nombre total de pages")
            return 1

    def extract_recording_info_from_row(self, row):
        """Extrait les informations d'un enregistrement à partir d'une ligne de tableau"""
        info = {}

        # Audio URL et ID
        audio_elem = row.select_one("audio.xc-mini-player")
        if audio_elem and "src" in audio_elem.attrs:
            audio_url = audio_elem["src"]
            if audio_url.startswith("//"):
                audio_url = "https:" + audio_url
            info["audio_url"] = audio_url

            # Extraire l'ID de l'URL audio
            id_match = re.search(r"XC(\d+)", audio_url)
            if id_match:
                info["id"] = id_match.group(1)
            else:
                info["id"] = None
        else:
            return None

        # Toutes les cellules td
        tds = row.find_all("td")
        if len(tds) < 10:  # Vérifier qu'il y a suffisamment de cellules
            return None

        # Nom commun et scientifique de l'oiseau (2ème colonne)
        name_td = tds[1]
        common_name_elem = name_td.select_one(".common-name a")
        if common_name_elem:
            info["common_name"] = common_name_elem.text.strip()
        else:
            # Si pas de classe common-name, prendre le texte complet
            info["common_name"] = name_td.text.strip()

        if (
            info["common_name"] == "Soundscape"
            or "Identity unknown" in info["common_name"]
        ):
            return None

        # sci_name_elem = name_td.select_one('.sci-name')
        # info['scientific_name'] = sci_name_elem.text.strip() if sci_name_elem else None

        # # Longueur (3ème colonne)
        # info['length'] = tds[2].text.strip() if len(tds) > 2 else None

        # # Enregistreur (4ème colonne)
        # recorder_elem = tds[3].select_one('a')
        # info['recorder'] = recorder_elem.text.strip() if recorder_elem else tds[3].text.strip()

        # # Date (5ème colonne)
        # info['date'] = tds[4].text.strip() if len(tds) > 4 else None

        # # Heure (6ème colonne)
        # info['time'] = tds[5].text.strip() if len(tds) > 5 else None

        # # Pays (7ème colonne)
        # info['country'] = tds[6].text.strip() if len(tds) > 6 else None

        # # Localité (8ème colonne)
        # locality_elem = tds[7].select_one('a')
        # info['locality'] = locality_elem.text.strip() if locality_elem else tds[7].text.strip()

        # # Altitude (9ème colonne)
        # info['altitude'] = tds[8].text.strip() if len(tds) > 8 else None

        # # Type de son (10ème colonne)
        # info['sound_type'] = tds[9].text.strip() if len(tds) > 9 else None

        # # Remarques (11ème colonne) - Extraction du texte brut
        # remarks_div = tds[10].select_one('.remarks')
        # if remarks_div:
        #     # Essayer d'extraire le texte complet (non tronqué)
        #     details_div = remarks_div.select_one('.details')
        #     if details_div:
        #         info['remarks'] = details_div.get_text(strip=True)
        #     else:
        #         info['remarks'] = remarks_div.get_text(strip=True)
        # else:
        #     info['remarks'] = tds[10].get_text(strip=True) if len(tds) > 10 else None

        # # Autres espèces présentes dans l'enregistrement (dans un tooltip)
        # also_tooltip = tds[10].select_one('span.tooltip[data-qtip-header="Autres espèces"]')
        # if also_tooltip and 'data-qtip-content' in also_tooltip.attrs:
        #     content = also_tooltip['data-qtip-content']
        #     # Extraire les noms d'espèces du HTML contenu dans l'attribut
        #     also_soup = BeautifulSoup(content, 'html.parser')
        #     also_species = []
        #     for li in also_soup.find_all('li'):
        #         common = li.select_one('.common-name')
        #         sci = li.select_one('.sci-name')
        #         if common and sci:
        #             also_species.append(f"{common.text.strip()} ({sci.text.strip()})")
        #         elif common:
        #             also_species.append(common.text.strip())
        #     info['also_species'] = also_species
        # else:
        #     info['also_species'] = []

        # # Qualité (12ème colonne)
        # quality_div = tds[11].select_one('.rating')
        # if quality_div:
        #     selected_li = quality_div.select_one('li.selected')
        #     if selected_li:
        #         info['quality'] = selected_li.text.strip()
        #     else:
        #         info['quality'] = None
        # else:
        #     info['quality'] = None

        # # URL de détail et numéro de catalogue (13ème colonne)
        # catalog_link = tds[12].select_one('a')
        # if catalog_link:
        #     info['catalog_number'] = catalog_link.text.strip()
        #     info['detail_url'] = 'https://xeno-canto.org/' + info['id'] if info['id'] else None
        # else:
        #     info['catalog_number'] = None
        #     info['detail_url'] = None

        # # URL de téléchargement
        # download_link = tds[11].select_one('a[href*="download"]')
        # if download_link:
        #     info['download_url'] = 'https://xeno-canto.org' + download_link['href']
        # else:
        #     info['download_url'] = None

        return info

    def download_audio(self, url, filename):
        """Télécharge un fichier audio"""
        try:
            response = requests.get(url, headers=self.headers, stream=True)
            response.raise_for_status()

            # Enregistrer le fichier
            file_path = os.path.join(self.audio_folder, filename)
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Téléchargement réussi: {filename}")
            time.sleep(1)  # Pause entre les téléchargements
            return file_path
        except Exception as e:
            print(f"Erreur lors du téléchargement de {url}: {e}")
            return None

    def scrape_page(self, page_num):
        """Scrape une page spécifique"""
        if page_num == 1:
            url = self.base_url
        else:
            # Construire l'URL de la page
            url = f"{self.base_url}&pg={page_num}"

        print(f"Scraping de la page {page_num}: {url}")
        html = self.get_page(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")

        # Chercher d'abord tous les tr dans la page, puis filtrer
        all_trs = soup.find_all("tr")

        # Les lignes avec des enregistrements ont généralement plusieurs td
        recording_rows = [tr for tr in all_trs if len(tr.find_all("td")) > 5]

        print(f"Trouvé {len(recording_rows)} lignes d'enregistrements")

        results = []
        for row in recording_rows:
            info = self.extract_recording_info_from_row(row)
            if info:
                results.append(info)

        return results

    def scrape_all_pages(self, download_audio=True, max_pages=None):
        """Scrape toutes les pages et télécharge optionnellement les fichiers audio"""
        total_pages = self.get_total_pages()
        print(f"Nombre total de pages à scraper: {total_pages}")

        if max_pages and max_pages < total_pages:
            total_pages = max_pages
            print(f"Limitation à {max_pages} pages")

        all_recordings = []
        for page in range(1, total_pages + 1):
            page_recordings = self.scrape_page(page)
            all_recordings.extend(page_recordings)
            print(
                f"Page {page}/{total_pages} scrapée. {len(page_recordings)} enregistrements trouvés."
            )

        # Enregistrer les métadonnées dans un CSV
        df = pd.DataFrame(all_recordings)
        csv_path = os.path.join(self.output_folder, "xeno_canto.csv")
        df.to_csv(csv_path, index=False)
        print(f"Métadonnées enregistrées dans {csv_path}")

        # Télécharger les fichiers audio si demandé
        if download_audio:
            print("Début du téléchargement des fichiers audio...")
            for idx, recording in enumerate(all_recordings):
                if recording["audio_url"]:
                    # Créer un nom de fichier sécurisé
                    safe_name = f"{recording['id']}_{re.sub(r'[^\w\-_.]', '_', recording['common_name'])}"

                    # Déterminer l'extension à partir de l'URL
                    extension = (
                        recording["audio_url"].split(".")[-1]
                        if "." in recording["audio_url"]
                        else "mp3"
                    )
                    filename = f"{safe_name}.{extension}"

                    print(f"Téléchargement {idx + 1}/{len(all_recordings)}: {filename}")
                    file_path = self.download_audio(recording["audio_url"], filename)

                    if file_path:
                        # Mettre à jour le DataFrame avec le chemin local
                        df.at[idx, "local_file"] = file_path

        # Mettre à jour le CSV avec les chemins locaux
        df.to_csv(csv_path, index=False)
        print(f"Scraping terminé. {len(all_recordings)} enregistrements traités.")
        return df


# URL de base (votre URL)
base_url = "https://xeno-canto.org/explore?query=box%3A47.682%2C0.604%2C49.741%2C4.581+type%3A%22song%22+grp%3A%22birds%22+q%3A%22%3EB%22"

# Exemple d'utilisation
if __name__ == "__main__":
    scraper = XenoCantoScraper(base_url)

    # Scraper toutes les pages avec téléchargement des fichiers audio
    # Vous pouvez limiter le nombre de pages avec max_pages
    # Ou désactiver le téléchargement avec download_audio=False
    results = scraper.scrape_all_pages(download_audio=False)

    print(f"Nombre total d'enregistrements récupérés: {len(results)}")
