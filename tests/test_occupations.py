import unittest
from cli.db import (
    classify_occupation,
    match_occupation_query,
    OCCUPATION_DEFINITIONS,
    UnifiedAgentDB,
)


class TestOccupations(unittest.TestCase):
    def test_occupation_definitions_count(self):
        self.assertEqual(len(OCCUPATION_DEFINITIONS), 10)
        for occ in OCCUPATION_DEFINITIONS:
            self.assertIn("id", occ)
            self.assertIn("title", occ)
            self.assertIn("soc", occ)
            self.assertIn("icon", occ)
            self.assertIn("desc", occ)

    def test_classify_occupation_skills(self):
        self.assertEqual(classify_occupation("postgres-tool", "PostgreSQL database management", "Databases", "SQL"), "database-admin")
        self.assertEqual(classify_occupation("docker-deploy", "Kubernetes cluster CI/CD", "DevOps", "CI/CD"), "devops-sre")
        self.assertEqual(classify_occupation("llm-prompt", "OpenAI GPT fine-tuning and RAG", "Data & AI", "LLM"), "ai-data-scientist")
        self.assertEqual(classify_occupation("sec-audit", "Penetration testing and vulnerability scanning", "Testing & Security", "Security"), "security-qa")
        self.assertEqual(classify_occupation("figma-assets", "UI/UX design systems and SVG export", "Content & Media", "Design"), "designer-media")
        self.assertEqual(classify_occupation("jira-sync", "Project management agile boards", "Business", "Project Management"), "product-pm")
        self.assertEqual(classify_occupation("arxiv-search", "Academic paper literature research", "Research", "Academic"), "researcher")
        self.assertEqual(classify_occupation("crypto-trade", "DeFi trading financial metrics", "Business", "Finance & Investment"), "business-finance")
        self.assertEqual(classify_occupation("api-docs", "Markdown documentation and guides", "Documentation", "Technical Docs"), "tech-writer")

    def test_classify_occupation_mcps(self):
        self.assertEqual(classify_occupation("mcp-server-postgres", "PostgreSQL MCP server with connection pooling", "Tools", "Databases"), "database-admin")
        self.assertEqual(classify_occupation("docker-mcp", "Run Docker containers from Claude Desktop", "Tools", "DevOps"), "devops-sre")
        self.assertEqual(classify_occupation("openai-mcp", "Call LLMs and embeddings via MCP", "Tools", "AI"), "ai-data-scientist")
        self.assertEqual(classify_occupation("semgrep-mcp", "Vulnerability auditing MCP server", "Tools", "Security"), "security-qa")

    def test_match_occupation_query(self):
        self.assertTrue(match_occupation_query("devops-sre", "devops-sre"))
        self.assertTrue(match_occupation_query("devops-sre", "devops"))
        self.assertTrue(match_occupation_query("devops-sre", "15-1250"))
        self.assertTrue(match_occupation_query("devops-sre", "all"))
        self.assertFalse(match_occupation_query("devops-sre", "database-admin"))

    def test_unified_db_occupations(self):
        db = UnifiedAgentDB()
        occupations = db.get_occupations()
        self.assertGreaterEqual(len(occupations), 10)
        found_devops = any(o["id"] == "devops-sre" for o in occupations)
        self.assertTrue(found_devops)


if __name__ == "__main__":
    unittest.main()
