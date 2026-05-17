"""End-to-end tests for the compliance verification workflow."""

import sys
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings
from app.models.database import init_db, enable_pgvector
from app.agents.graph import run_compliance_verification
from app.services.document_processor import DocumentProcessor
import asyncio

# Get settings
settings = get_settings()

# Database setup
engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def test_compliance_workflow():
    """Test the entire compliance verification workflow."""

    print("=" * 80)
    print("COMPLIANCE VERIFICATION WORKFLOW TEST")
    print("=" * 80)

    # Initialize database
    print("\n[1/4] Initializing database...")
    try:
        enable_pgvector(SessionLocal())
        init_db(engine)
        print("✓ Database initialized")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return

    # Get database session
    db = SessionLocal()

    try:
        # Test contract texts
        test_contracts = {
            "statuts_entreprise": """
STATUTS DE LA SOCIETE
Titre I: Constitution et Siège Social
Article 1: Forme et Dénomination
La société est constituée sous la forme d'une Société Anonyme (SA) dénommée
"EXAMPLE CORPORATION S.A.R.L".

Article 2: Siège Social
Le siège social est situé à Nouakchott, Mauritanie. Il peut être transféré par
décision de l'assemblée générale.

Article 3: Objet Social
La société a pour objet l'exercice de toute activité commerciale, industrielle
et de services.

Article 4: Durée
La durée de la société est fixée à 99 ans à compter de son immatriculation
au registre du commerce.

Titre II: Capital Social
Article 5: Montant du Capital
Le capital social est fixé à cinq millions d'ouguiyas (5.000.000 UM) divisé
en actions.

Article 6: Actions
Les actions sont nominatives et indivisibles. Elles ne peuvent être cédées
que selon les conditions prévues aux présents statuts.

Titre III: Gestion et Administration
Article 7: Conseil d'Administration
La société est administrée par un Conseil d'Administration composé de trois
à neuf administrateurs nommés par l'assemblée générale.

Article 8: Président du Conseil
Le Conseil d'Administration élit en son sein un Président parmi ses membres
pour une durée d'un an.

Article 9: Réunions du Conseil
Le Conseil d'Administration se réunit autant que l'intérêt de la société
l'exige et au moins deux fois par an.

Titre IV: Assemblée Générale
Article 10: Convocation
L'assemblée générale est convoquée par le Président du Conseil
d'Administration selon les modalités prévues par la loi.

Article 11: Quorum et Majorité
Aucun quorum n'est requis pour la tenue d'une assemblée générale.
Les décisions sont prises à la majorité des voix présentes ou représentées.

Titre V: Dissolution et Liquidation
Article 12: Causes de Dissolution
La société se dissout par caducité du délai de sa durée, par décision
de l'assemblée générale ou par impossibilité de réaliser son objet social.

Article 13: Liquidation
La liquidation de la société est confiée à un ou plusieurs liquidateurs
désignés par l'assemblée générale.
            """,

            "contrat_travail": """
CONTRAT DE TRAVAIL INDIVIDUEL

Les présentes conditions d'emploi entrent en vigueur à compter de
la date de signature.

Article 1: Identité des Parties
EMPLOYEUR: EXAMPLE CORPORATION S.A.R.L, société anonyme au capital de
5.000.000 UM, immatriculée au registre du commerce sous le numéro 12345.

SALARIÉ: [Nom du Salarié] né(e) le [date], de nationalité [nationalité],
demeurant à [adresse].

Article 2: Nature et Lieu de l'Emploi
Le salarié est engagé en qualité de [Titre du Poste].
Les fonctions seront exercées au siège de la société à Nouakchott.

Article 3: Période d'Essai
Le contrat est soumis à une période d'essai d'une durée de trois (3) mois,
renouvelable une fois. Pendant cette période, le contrat peut être résilié
par l'une ou l'autre des parties sans préavis.

Article 4: Durée du Contrat
Le contrat est conclu pour une durée indéterminée, à compter de la date
de la première embauche.

Article 5: Rémunération
La rémunération mensuelle du salarié est fixée à [Montant] ouguiyas, versée
en fin de mois. Elle comprend le salaire de base et les primes éventuelles.

Article 6: Horaires de Travail
La durée hebdomadaire du travail est de quarante (40) heures, réparties
sur cinq jours. Le salarié bénéficie du repos hebdomadaire le samedi et dimanche.

Article 7: Congés Annuels
Le salarié a droit à un congé payé de deux jours et demi par mois de service
soit trente (30) jours de congé par an.

Article 8: Avantages Sociaux
Le salarié bénéficie de la couverture sociale conformément à la législation
en vigueur et de l'assurance maladie professionnelle.

Article 9: Obligations du Salarié
Le salarié s'engage à respecter le règlement intérieur de la société,
à exercer ses fonctions avec conscience et diligence.

Article 10: Résiliation
Le contrat peut être résilié par l'employeur ou le salarié selon les modalités
prévues par le Code du Travail mauritanien.

Article 11: Litiges
Tout litige résultant de l'application du présent contrat sera soumis aux
juridictions compétentes de Nouakchott.

Fait en double exemplaire à Nouakchott, le [date]
            """
        }

        # Test each document type
        for doc_type, contract_text in test_contracts.items():
            print(f"\n[2/4] Testing {doc_type}...")
            contract_id = f"test_{doc_type}_{abs(hash(contract_text)) % 10000}"

            try:
                print(f"  - Running compliance verification for {contract_id}...")

                # Run the compliance workflow
                result = await run_compliance_verification(
                    db=db,
                    contract_id=contract_id,
                    contract_text=contract_text,
                    document_type=doc_type,
                )

                # Display results
                print(f"\n  Results for {doc_type}:")
                print(f"  - Overall Status: {result.get('overall_status')}")
                print(f"  - Compliance Score: {result.get('compliance_score'):.1f}%")
                print(f"  - Total Issues: {result.get('issue_summary', {}).get('total_issues', 0)}")
                print(f"  - Summary: {result.get('summary', 'N/A')[:100]}...")

                # Show issues
                issues = result.get('compliance_issues', [])
                if issues:
                    print(f"\n  Issues found ({len(issues)}):")
                    for issue in issues[:3]:  # Show first 3
                        print(f"    - [{issue.get('severity')}] {issue.get('type')}: {issue.get('description')[:80]}...")

                # Show recommendations
                recommendations = result.get('recommendations', [])
                if recommendations:
                    print(f"\n  Recommendations ({len(recommendations)}):")
                    for rec in recommendations[:3]:  # Show first 3
                        print(f"    - {rec[:80]}...")

                print(f"  ✓ {doc_type} workflow completed successfully")

            except Exception as e:
                print(f"  ✗ {doc_type} workflow failed: {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "=" * 80)
        print("WORKFLOW TEST COMPLETED")
        print("=" * 80)

    finally:
        db.close()


if __name__ == "__main__":
    print("Starting compliance workflow test...")
    asyncio.run(test_compliance_workflow())
