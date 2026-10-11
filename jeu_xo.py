import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime


class JeuXO:
    def __init__(self):
        self.fenetre = tk.Tk()
        self.fenetre.title("Jeu XO - Tic Tac Toe")
        self.fenetre.geometry("450x550")
        self.fenetre.resizable(False, False)
        self.fenetre.configure(bg="#34495e")

        self.conn = None
        self.cursor = None
        self.init_database()

        self.joueur_actuel = "X"
        self.grille = [""] * 9
        self.boutons = []
        self.score_x = 0
        self.score_o = 0
        self.nom_joueur_x = ""
        self.nom_joueur_o = ""
        self.partie_en_cours = False

        self.creer_interface()
        self.fenetre.protocol("WM_DELETE_WINDOW", self.fermer_application)

    def init_database(self):
        """Initialise la base de données SQLite."""
        self.conn = sqlite3.connect("jeu_xo.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS parties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                joueur_x TEXT NOT NULL,
                joueur_o TEXT NOT NULL,
                gagnant TEXT,
                date TEXT NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistiques (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_joueur TEXT UNIQUE NOT NULL,
                victoires INTEGER DEFAULT 0,
                defaites INTEGER DEFAULT 0,
                nuls INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def creer_interface(self):
        """Crée l'interface graphique du jeu."""
        frame_noms = tk.Frame(self.fenetre, bg="#2c3e50", pady=10)
        frame_noms.pack(fill=tk.X)

        frame_ligne1 = tk.Frame(frame_noms, bg="#2c3e50")
        frame_ligne1.pack(pady=3)
        tk.Label(
            frame_ligne1, text="Joueur X:", font=("Arial", 10, "bold"),
            bg="#2c3e50", fg="white", width=10
        ).pack(side=tk.LEFT, padx=3)
        self.entry_joueur_x = tk.Entry(frame_ligne1, font=("Arial", 10), width=12)
        self.entry_joueur_x.pack(side=tk.LEFT, padx=3)

        frame_ligne2 = tk.Frame(frame_noms, bg="#2c3e50")
        frame_ligne2.pack(pady=3)
        tk.Label(
            frame_ligne2, text="Joueur O:", font=("Arial", 10, "bold"),
            bg="#2c3e50", fg="white", width=10
        ).pack(side=tk.LEFT, padx=3)
        self.entry_joueur_o = tk.Entry(frame_ligne2, font=("Arial", 10), width=12)
        self.entry_joueur_o.pack(side=tk.LEFT, padx=3)

        frame_btn = tk.Frame(frame_noms, bg="#2c3e50")
        frame_btn.pack(pady=5)
        tk.Button(
            frame_btn, text="DÉMARRER", font=("Arial", 11, "bold"),
            bg="#27ae60", fg="white", command=self.demarrer_jeu,
            padx=30, pady=5, relief=tk.RAISED, bd=3
        ).pack()

        self.label_tour = tk.Label(
            self.fenetre, text="Entrez les noms et cliquez sur DÉMARRER",
            font=("Arial", 11, "bold"), bg="#ecf0f1", pady=8
        )
        self.label_tour.pack(fill=tk.X)

        self.frame_grille = tk.Frame(self.fenetre, bg="#34495e", pady=15)
        self.frame_grille.pack()

        for i in range(9):
            btn = tk.Button(
                self.frame_grille, text="", font=("Arial", 24, "bold"),
                width=4, height=2, bg="#ecf0f1",
                command=lambda pos=i: self.cliquer_case(pos),
                state=tk.DISABLED
            )
            btn.grid(row=i // 3, column=i % 3, padx=3, pady=3)
            self.boutons.append(btn)

        frame_scores = tk.Frame(self.fenetre, bg="#2c3e50", pady=10)
        frame_scores.pack(fill=tk.X)
        self.label_score = tk.Label(
            frame_scores, text="Scores: X = 0 | O = 0",
            font=("Arial", 11, "bold"), bg="#2c3e50", fg="white"
        )
        self.label_score.pack()

        frame_controles = tk.Frame(self.fenetre, bg="#34495e", pady=10)
        frame_controles.pack(fill=tk.X)
        tk.Button(
            frame_controles, text="Nouvelle Partie", font=("Arial", 9, "bold"),
            bg="#3498db", fg="white", command=self.nouvelle_partie,
            width=14, pady=3
        ).pack(side=tk.LEFT, padx=10)
        tk.Button(
            frame_controles, text="Statistiques", font=("Arial", 9, "bold"),
            bg="#9b59b6", fg="white", command=self.afficher_statistiques,
            width=14, pady=3
        ).pack(side=tk.LEFT, padx=10)
        tk.Button(
            frame_controles, text="Réinitialiser", font=("Arial", 9, "bold"),
            bg="#e74c3c", fg="white", command=self.reinitialiser_scores,
            width=14, pady=3
        ).pack(side=tk.LEFT, padx=10)

    def demarrer_jeu(self):
        """Démarre le jeu après validation des noms."""
        nom_x = self.entry_joueur_x.get().strip()
        nom_o = self.entry_joueur_o.get().strip()

        if not nom_x or not nom_o:
            messagebox.showerror("Erreur", "Veuillez entrer les noms des deux joueurs!")
            return
        if nom_x.casefold() == nom_o.casefold():
            messagebox.showerror("Erreur", "Veuillez entrer deux noms différents.")
            return

        self.nom_joueur_x = nom_x
        self.nom_joueur_o = nom_o
        self.ajouter_joueur(self.nom_joueur_x)
        self.ajouter_joueur(self.nom_joueur_o)
        self.nouvelle_partie()

    def ajouter_joueur(self, nom):
        """Ajoute un joueur s'il n'existe pas déjà."""
        try:
            self.cursor.execute("""
                INSERT OR IGNORE INTO statistiques
                    (nom_joueur, victoires, defaites, nuls)
                VALUES (?, 0, 0, 0)
            """, (nom,))
            self.conn.commit()
        except sqlite3.Error as erreur:
            messagebox.showerror("Erreur SQLite", str(erreur))

    def cliquer_case(self, position):
        """Gère le clic sur une case libre."""
        if not self.partie_en_cours or self.grille[position] != "":
            return

        self.grille[position] = self.joueur_actuel
        couleur = "#e74c3c" if self.joueur_actuel == "X" else "#3498db"
        self.boutons[position].config(text=self.joueur_actuel, fg=couleur)

        if self.verifier_victoire():
            self.fin_partie("victoire")
        elif "" not in self.grille:
            self.fin_partie("nul")
        else:
            self.changer_joueur()

    def verifier_victoire(self):
        """Vérifie si le joueur actuel a gagné."""
        combinaisons_gagnantes = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]

        for combo in combinaisons_gagnantes:
            if all(self.grille[pos] == self.joueur_actuel for pos in combo):
                for pos in combo:
                    self.boutons[pos].config(bg="#f39c12")
                return True
        return False

    def changer_joueur(self):
        """Passe au joueur suivant."""
        self.joueur_actuel = "O" if self.joueur_actuel == "X" else "X"
        nom = self.nom_joueur_x if self.joueur_actuel == "X" else self.nom_joueur_o
        self.label_tour.config(text=f"Tour de {nom} ({self.joueur_actuel})")

    def fin_partie(self, resultat):
        """Termine la partie et enregistre le résultat."""
        self.partie_en_cours = False
        for btn in self.boutons:
            btn.config(state=tk.DISABLED)

        try:
            if resultat == "victoire":
                gagnant = self.nom_joueur_x if self.joueur_actuel == "X" else self.nom_joueur_o
                perdant = self.nom_joueur_o if self.joueur_actuel == "X" else self.nom_joueur_x
                messagebox.showinfo(
                    "Victoire!", f"{gagnant} ({self.joueur_actuel}) a gagné!"
                )

                if self.joueur_actuel == "X":
                    self.score_x += 1
                else:
                    self.score_o += 1

                self.enregistrer_partie(gagnant)
                self.mettre_a_jour_statistiques(gagnant, "victoire")
                self.mettre_a_jour_statistiques(perdant, "defaite")
            else:
                messagebox.showinfo("Match nul", "Égalité! Aucun gagnant.")
                self.enregistrer_partie("NUL")
                self.mettre_a_jour_statistiques(self.nom_joueur_x, "nul")
                self.mettre_a_jour_statistiques(self.nom_joueur_o, "nul")

            self.label_score.config(
                text=f"Scores: {self.nom_joueur_x} = {self.score_x} | "
                     f"{self.nom_joueur_o} = {self.score_o}"
            )
            self.label_tour.config(text="Partie terminée — cliquez sur Nouvelle Partie")
        except sqlite3.Error as erreur:
            messagebox.showerror("Erreur SQLite", str(erreur))

    def enregistrer_partie(self, gagnant):
        """Enregistre une partie dans la base SQLite."""
        date_partie = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            INSERT INTO parties (joueur_x, joueur_o, gagnant, date)
            VALUES (?, ?, ?, ?)
        """, (self.nom_joueur_x, self.nom_joueur_o, gagnant, date_partie))
        self.conn.commit()

    def mettre_a_jour_statistiques(self, nom_joueur, resultat):
        """Met à jour les statistiques d'un joueur."""
        colonnes = {
            "victoire": "victoires",
            "defaite": "defaites",
            "nul": "nuls"
        }
        colonne = colonnes.get(resultat)
        if colonne is None:
            return

        # Le nom de colonne vient du dictionnaire interne ci-dessus.
        self.cursor.execute(
            f"UPDATE statistiques SET {colonne} = {colonne} + 1 WHERE nom_joueur = ?",
            (nom_joueur,)
        )
        self.conn.commit()

    def nouvelle_partie(self):
        """Réinitialise la grille et démarre une nouvelle partie."""
        if not self.nom_joueur_x or not self.nom_joueur_o:
            messagebox.showinfo("Information", "Entrez les noms des deux joueurs puis cliquez sur DÉMARRER.")
            return

        self.grille = [""] * 9
        self.joueur_actuel = "X"
        self.partie_en_cours = True

        for btn in self.boutons:
            btn.config(text="", bg="#ecf0f1", state=tk.NORMAL)

        self.label_tour.config(text=f"Tour de {self.nom_joueur_x} (X)")

    def reinitialiser_scores(self):
        """Réinitialise les scores de la session en cours."""
        if messagebox.askyesno(
            "Confirmer", "Voulez-vous réinitialiser les scores de cette session?"
        ):
            self.score_x = 0
            self.score_o = 0
            self.label_score.config(
                text=f"Scores: {self.nom_joueur_x or 'X'} = 0 | "
                     f"{self.nom_joueur_o or 'O'} = 0"
            )
            if self.nom_joueur_x and self.nom_joueur_o:
                self.nouvelle_partie()

    def afficher_statistiques(self):
        """Affiche les statistiques enregistrées dans SQLite."""
        fenetre_stats = tk.Toplevel(self.fenetre)
        fenetre_stats.title("Statistiques des joueurs")
        fenetre_stats.geometry("650x400")
        fenetre_stats.configure(bg="#2c3e50")

        tk.Label(
            fenetre_stats, text="STATISTIQUES DES JOUEURS",
            font=("Arial", 18, "bold"), bg="#2c3e50", fg="white", pady=10
        ).pack()

        frame_tableau = tk.Frame(fenetre_stats, bg="#ecf0f1", padx=10, pady=10)
        frame_tableau.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        headers = ["Joueur", "Victoires", "Défaites", "Nuls", "Total Parties"]
        for col, header in enumerate(headers):
            tk.Label(
                frame_tableau, text=header, font=("Arial", 10, "bold"),
                bg="#34495e", fg="white", padx=8, pady=5
            ).grid(row=0, column=col, sticky="ew")

        self.cursor.execute("""
            SELECT nom_joueur, victoires, defaites, nuls
            FROM statistiques
            ORDER BY victoires DESC, nom_joueur ASC
        """)
        statistiques = self.cursor.fetchall()

        for ligne, stat in enumerate(statistiques, start=1):
            nom, victoires, defaites, nuls = stat
            total = victoires + defaites + nuls
            couleur = "#ecf0f1" if ligne % 2 == 0 else "#bdc3c7"
            valeurs = [nom, victoires, defaites, nuls, total]
            for col, valeur in enumerate(valeurs):
                tk.Label(
                    frame_tableau, text=str(valeur), font=("Arial", 10),
                    bg=couleur, padx=8, pady=5
                ).grid(row=ligne, column=col, sticky="ew")

        if not statistiques:
            tk.Label(
                frame_tableau, text="Aucune donnée disponible",
                font=("Arial", 12), bg="#ecf0f1", pady=20
            ).grid(row=1, column=0, columnspan=5)

        tk.Button(
            fenetre_stats, text="Fermer", font=("Arial", 12, "bold"),
            bg="#e74c3c", fg="white", command=fenetre_stats.destroy, width=15
        ).pack(pady=10)

    def fermer_application(self):
        """Ferme proprement l'application et la base de données."""
        if self.conn is not None:
            self.conn.close()
        self.fenetre.destroy()

    def lancer(self):
        """Lance la boucle principale de l'application."""
        self.fenetre.mainloop()


if __name__ == "__main__":
    jeu = JeuXO()
    jeu.lancer()

