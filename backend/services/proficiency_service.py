import sqlite3
from pathlib import Path

DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "its.db"
)


class ProficiencyService:

    @staticmethod
    def get_connection():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def save_initial_proficiency(user_id, proficiency):
        """
        Salva o resultado do diagnóstico.

        Exemplo:

        {
            1: 66.67,
            2: 100.0,
            3: 33.33
        }
        """

        conn = ProficiencyService.get_connection()
        cursor = conn.cursor()

        for concept_id, level in proficiency.items():

            cursor.execute("""
                INSERT OR REPLACE INTO proficiencia (
                    usuario_id,
                    conceito_id,
                    nivel
                )
                VALUES (?, ?, ?)
            """, (
                user_id,
                concept_id,
                level
            ))

        conn.commit()
        conn.close()

    @staticmethod
    def get_user_proficiency(user_id):
        """
        Retorna:

        {
            1: 66.67,
            2: 100.0,
            3: 33.33
        }
        """

        conn = ProficiencyService.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                conceito_id,
                nivel
            FROM proficiencia
            WHERE usuario_id = ?
        """, (user_id,))

        rows = cursor.fetchall()

        conn.close()

        result = {}

        for row in rows:
            result[row["conceito_id"]] = row["nivel"]

        return result

    @staticmethod
    def get_user_proficiency_with_names(user_id):
        """
        Retorna:

        {
            "SELECT": 66.67,
            "WHERE": 100.0,
            "JOINS": 33.33
        }
        """

        conn = ProficiencyService.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                c.nome,
                p.nivel
            FROM proficiencia p
            JOIN conceitos c
                ON c.id = p.conceito_id
            WHERE p.usuario_id = ?
        """, (user_id,))

        rows = cursor.fetchall()

        conn.close()

        result = {}

        for row in rows:
            result[row["nome"]] = row["nivel"]

        return result

    @staticmethod
    def update_proficiency(
        user_id,
        concept_id,
        correct
    ):
        """
        Atualiza a proficiência após cada exercício.

        Acertou:
            +10

        Errou:
            -5

        Limite:
            0 a 100
        """

        conn = ProficiencyService.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT nivel
            FROM proficiencia
            WHERE usuario_id = ?
            AND conceito_id = ?
        """, (
            user_id,
            concept_id
        ))

        row = cursor.fetchone()

        if row is None:

            current_level = 0

            cursor.execute("""
                INSERT INTO proficiencia (
                    usuario_id,
                    conceito_id,
                    nivel
                )
                VALUES (?, ?, ?)
            """, (
                user_id,
                concept_id,
                current_level
            ))

        else:

            current_level = row["nivel"]

        if correct:

            new_level = current_level + 10

        else:

            new_level = current_level - 5

        new_level = max(
            0,
            min(100, new_level)
        )

        cursor.execute("""
            UPDATE proficiencia
            SET nivel = ?
            WHERE usuario_id = ?
            AND conceito_id = ?
        """, (
            new_level,
            user_id,
            concept_id
        ))

        conn.commit()
        conn.close()

        return round(new_level, 2)

    @staticmethod
    def get_weakest_concept(user_id):
        """
        Retorna o conceito mais fraco.

        Exemplo:

        {
            "id": 3,
            "nome": "ORDER BY",
            "nivel": 20
        }
        """

        conn = ProficiencyService.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                c.id,
                c.nome,
                p.nivel
            FROM proficiencia p
            JOIN conceitos c
                ON c.id = p.conceito_id
            WHERE p.usuario_id = ?
            ORDER BY p.nivel ASC
            LIMIT 1
        """, (user_id,))

        row = cursor.fetchone()

        conn.close()

        if row is None:
            return None

        return {
            "id": row["id"],
            "nome": row["nome"],
            "nivel": row["nivel"]
        }
