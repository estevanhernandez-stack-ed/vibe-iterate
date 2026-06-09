"""
Pytest configuration for vibe-iterate tests.

vibe-iterate ships no executable scripts — its "logic" lives as prose
procedures the LLM agent follows (the loggers' append/serialize contract,
detect_orphans(), radar staleness, config/cache IO) plus three JSON Schemas
and their fixtures under plugins/vibe-iterate/skills/guide/.

This conftest:
  - puts the tests dir on sys.path so the reference-contract support module
    (iterate_contract.py) imports as a top-level module, and
  - exposes the schema + fixture directories the suite reads.

See iterate_contract.py for why the reference implementations exist.
"""
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).parent
REPO_ROOT = TESTS_DIR.parent

# Make the reference-contract support module importable without installation.
sys.path.insert(0, str(TESTS_DIR))

# The plugin's shipped artifacts under the shared guide.
GUIDE_DIR = REPO_ROOT / "plugins" / "vibe-iterate" / "skills" / "guide"
SCHEMAS_DIR = GUIDE_DIR / "schemas"
FIXTURES_DIR = GUIDE_DIR / "fixtures"
SKILLS_DIR = REPO_ROOT / "plugins" / "vibe-iterate" / "skills"
