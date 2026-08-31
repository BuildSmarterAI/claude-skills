"""The Copy OS family's safety and structure invariants.

Risk class: AI guardrail (risk-based-tdd) -> the interesting property here is
not "does the skill exist" but "can a skill in this family fabricate a business
fact". That property is enforced by prose, and prose silently rots. These tests
pin the parts of the prose that are load-bearing.

Three failure modes this targets, all of which ship silently:

1. **A skill loses its provenance rule.** Every skill in this family is
   permitted to write company-specific copy. The only thing stopping it from
   inventing a customer quote is the "never invent" block in its own body. A
   skill that loses that block still loads, still works, and still reads well -
   it just fabricates.

2. **A fabricated example leaks into the methodology.** A realistic-looking
   testimonial written as an illustration is indistinguishable from a real one
   once it is copy-pasted out of the skill. The family's own rule is "write the
   slot, not a value"; these tests hold the family to it.

3. **A handoff points at a skill that does not exist.** The routing is prose,
   so a renamed or removed skill leaves a dangling reference that reads as
   authoritative and silently routes nowhere.

Not tested here: whether the advice is *good*. That is a human question. These
tests cover only the properties whose violation is invisible to a reader.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(_HERE)
MANIFEST = os.path.join(ROOT, 'manifests', 'skills.json')

FAMILY = [
    'copy-os',
    'copy-strategist',
    'direct-response-copy',
    'persuasion-engine',
    'copychief',
    'humanizer',
    'compliance-review',
    'landing-page-copy',
    'ad-copy',
    'email-copy',
    'social-copy',
]

# Skills that generate or edit company-specific copy must carry the rule. Every
# member of the family does, including the router.
MUST_CARRY_PROVENANCE = set(FAMILY)

# The eight contract elements the family's design requires of every skill.
REQUIRED_SECTIONS = (
    ('trigger', re.compile(r'(?mi)^## When to Activate\b')),
    ('non-trigger', re.compile(r'(?mi)^## When NOT to Activate\b')),
    ('output contract', re.compile(r'(?mi)^## Output contract\b')),
    ('quality gates', re.compile(r'(?mi)^## Quality gates\b')),
    ('failure conditions', re.compile(r'(?mi)^## Failure conditions\b')),
    ('handoffs', re.compile(r'(?mi)^## Handoffs\b')),
)

FRONTMATTER_NAME = re.compile(r'''(?m)^name:\s*(?:"([^"]+)"|'([^']+)'|(\S+))\s*$''')

PROVENANCE_HEADING = re.compile(r'(?mi)^## (?:The )?provenance rule[^\n]*$')

# The exact anti-fabrication sentence each skill is responsible for, pinned so
# that weakening one is a visible, deliberate act rather than a silent edit.
PROVENANCE_ANCHORS = {
    'copy-os':
        'Never invent proof, customer quotes, performance numbers',
    'copy-strategist':
        'Never invent proof, customers, results, pricing, positioning, or permissions.',
    'direct-response-copy':
        'Never invent proof, customers, results, pricing, guarantees, or competitor claims.',
    'persuasion-engine':
        'Never invent proof, customers, results, pricing, guarantees, competitor claims, '
        'or credentials.',
    'copychief':
        'Never invent proof, customers, results, pricing, or competitor claims - including '
        'inside a rewrite.',
    'humanizer':
        'Never add a statistic, anecdote, quote, or attribution that was not in the input.',
    'compliance-review':
        'Never invent a source to resolve an unsubstantiated claim.',
    'landing-page-copy':
        'Never invent proof, customer names, results, pricing, or guarantees.',
    'ad-copy':
        'Never invent proof, results, review counts, customer names, competitor claims, '
        'or pricing.',
    'email-copy':
        'Never invent a prior conversation, a mutual connection, a customer result, '
        'a company detail, or a statistic in order to personalise.',
    'social-copy':
        'Never invent an anecdote, a client story, a result, a conversation, or a statistic '
        'to make a post land.',
}


# Skills that GENERATE company-specific copy must be able to express all three
# provenance labels. The three reviewer/editor skills judge or edit copy rather
# than asserting facts about a business, so they carry the gap label only - their
# provenance mechanism is their own verdict vocabulary (copychief's scorecard,
# compliance-review's claim ledger).
GENERATIVE = {'copy-os', 'copy-strategist', 'direct-response-copy', 'persuasion-engine',
              'landing-page-copy', 'ad-copy', 'email-copy', 'social-copy'}
REVIEWERS = {'copychief', 'humanizer', 'compliance-review'}


def read(name):
    with open(os.path.join(ROOT, name, 'SKILL.md'), encoding='utf-8') as fh:
        return fh.read()


def frontmatter(name):
    """The delimiter-bounded YAML block only.

    Searching the whole file lets prose satisfy a frontmatter assertion: a
    SKILL.md whose frontmatter omits `name` but whose body happens to contain a
    line reading `name: ad-copy` passed the unbounded check, while the harness
    would never register it. Verified to reproduce before this was bounded.
    """
    body = read(name)
    if not body.startswith('---'):
        return ''
    end = body.find('\n---', 3)
    return body[3:end] if end != -1 else ''


def provenance_section(name):
    """The provenance section only. Scoping matters: a whole-body search for
    'never' is satisfied by any incidental use of the word elsewhere."""
    body = read(name)
    m = PROVENANCE_HEADING.search(body)
    if not m:
        return ''
    tail = body[m.end():]
    nxt = re.search(r'(?m)^## ', tail)
    return tail[:nxt.start()] if nxt else tail


def manifest_entries():
    with open(MANIFEST, encoding='utf-8') as fh:
        return {e['skill']: e for e in json.load(fh)['skills']}


class TestFamilyIsPresent(unittest.TestCase):
    def test_every_skill_exists_with_a_skill_md(self):
        missing = [n for n in FAMILY
                   if not os.path.isfile(os.path.join(ROOT, n, 'SKILL.md'))]
        self.assertEqual([], missing, f'family members missing a SKILL.md: {missing}')

    def test_frontmatter_name_matches_folder(self):
        for name in FAMILY:
            with self.subTest(skill=name):
                block = frontmatter(name)
                self.assertNotEqual('', block, f'{name}: no frontmatter block')
                m = FRONTMATTER_NAME.search(block)
                self.assertIsNotNone(m, f'{name}: no name in frontmatter')
                declared = next(g for g in m.groups() if g)
                self.assertEqual(name, declared)

    def test_name_is_not_satisfied_by_prose_outside_frontmatter(self):
        # Guards the bound itself: without it, body prose reading "name: x"
        # satisfies the check on a skill the harness would never register.
        forged = '---\ndescription: no name field here\n---\n\n# T\n\nname: copy-os\n'
        end = forged.find('\n---', 3)
        block = forged[3:end]
        self.assertIsNone(FRONTMATTER_NAME.search(block),
                          'frontmatter bound is not actually bounding')
        self.assertIsNotNone(FRONTMATTER_NAME.search(forged),
                             'unbounded search would have passed - the bound is load-bearing')

    def test_first_line_is_the_frontmatter_delimiter(self):
        # A SKILL.md whose first line is not `---` is silently never registered.
        for name in FAMILY:
            with self.subTest(skill=name):
                with open(os.path.join(ROOT, name, 'SKILL.md'), encoding='utf-8') as fh:
                    self.assertEqual('---', fh.readline().rstrip('\n'))


class TestSafetyRules(unittest.TestCase):
    """The properties whose loss is invisible to a reader."""

    def test_every_skill_has_a_provenance_section(self):
        for name in sorted(MUST_CARRY_PROVENANCE):
            with self.subTest(skill=name):
                self.assertNotEqual(
                    '', provenance_section(name),
                    f'{name}: has no provenance section at all')
                self.assertIn(
                    'fact-provenance.md', read(name),
                    f'{name}: no longer points at the provenance contract')

    def test_every_skill_carries_its_specific_prohibition(self):
        """Pinned per skill, deliberately.

        A whole-body search for "never" is satisfied by any incidental use of
        the word - measured: deleting humanizer's actual rule left a loose
        check green because an unrelated "## Never add" heading survived. The
        anchor must sit INSIDE the provenance section, and it must be the real
        sentence. Editing a safety rule should force a conscious edit here too.
        """
        for name in sorted(PROVENANCE_ANCHORS):
            with self.subTest(skill=name):
                section = provenance_section(name)
                self.assertIn(
                    PROVENANCE_ANCHORS[name], section,
                    f'{name}: its anti-fabrication rule changed or was removed. '
                    f'If the change is intentional, update PROVENANCE_ANCHORS '
                    f'and say why in the commit.')

    def test_no_skill_grants_permission_to_invent(self):
        """A cheap second net, deliberately a blocklist.

        Incomplete by construction - a novel rewording evades it. It exists to
        catch the obvious inversion, not to be the primary defence; the pinned
        anchors above are that.
        """
        permissive = re.compile(
            r'(?i)(feel free to (add|invent)|you may (invent|fabricate)|'
            r'(it is|its) (fine|ok|acceptable) to (add|invent|fabricate)|'
            r'invent a plausible|make up a)')
        for name in FAMILY:
            with self.subTest(skill=name):
                hits = permissive.findall(read(name))
                self.assertEqual([], hits, f'{name}: grants fact invention {hits}')

    def test_generative_skills_define_all_three_labels(self):
        """The name used to promise three labels and assert one.

        A skill that writes company-specific copy needs all three: [FACT] to
        attribute, [PROPOSED] to mark a recommendation as not-yet-true, and
        [NEEDS-INPUT] for the gap. Asserting only the gap label left the other
        two free to disappear, which is how unlabelled proposed messaging starts
        reading as established fact.
        """
        for name in sorted(GENERATIVE):
            body = read(name)
            for label in ('[FACT]', '[PROPOSED]', '[NEEDS-INPUT]'):
                with self.subTest(skill=name, label=label):
                    self.assertIn(label, body, f'{name}: lost {label}')

    def test_reviewer_skills_carry_the_gap_label(self):
        # These judge or edit rather than assert; their provenance mechanism is
        # their own verdict vocabulary. They still need somewhere to put a gap.
        for name in sorted(REVIEWERS):
            with self.subTest(skill=name):
                self.assertIn('[NEEDS-INPUT]', read(name),
                              f'{name}: lost the gap label, so a gap has nowhere to go')

    def test_family_partition_is_exhaustive(self):
        # A skill dropped from both sets would silently escape both checks.
        self.assertEqual(set(FAMILY), GENERATIVE | REVIEWERS)
        self.assertEqual(set(), GENERATIVE & REVIEWERS)

    def test_no_fabricated_testimonial_appears_in_the_methodology(self):
        # A quoted sentence attributed to a Firstname Lastname is a fabricated
        # testimonial the moment someone copies it out of the skill.
        attributed = re.compile(r'"[^"\n]{15,}"\s*[-—]\s*[A-Z][a-z]+\s+[A-Z][a-z]+')
        for name in FAMILY:
            with self.subTest(skill=name):
                hits = attributed.findall(read(name))
                self.assertEqual([], hits, f'{name}: attributed quote(s) {hits}')

    def test_no_invented_customer_counts(self):
        # "4,827 teams switched" reads as a real result once it leaves the file.
        counts = re.compile(
            r'\b\d{1,3},\d{3}\+?\s+(teams|customers|users|companies|businesses|clients)\b',
            re.I)
        for name in FAMILY:
            with self.subTest(skill=name):
                hits = counts.findall(read(name))
                self.assertEqual([], hits, f'{name}: invented customer count {hits}')

    def test_persuasion_engine_names_every_hard_stop(self):
        # These are the anti-patterns the family exists to refuse. Losing one
        # silently re-permits it.
        body = read('persuasion-engine')
        for term in ('Fabricated scarcity', 'Fabricated authority',
                     'Fabricated statistics', 'Invented testimonials',
                     'False guarantees', 'Sensitive-attribute targeting'):
            with self.subTest(hard_stop=term):
                self.assertIn(term, body)

    def test_compliance_review_does_not_assert_platform_policy_as_settled(self):
        # A stale rule stated confidently is worse than no rule: the review
        # reads CLEAR against a policy that no longer exists.
        ref = os.path.join(ROOT, 'compliance-review', 'references',
                           'platform-policy-checkpoints.md')
        self.assertTrue(os.path.isfile(ref))
        with open(ref, encoding='utf-8') as fh:
            body = fh.read()
        self.assertRegex(body, r'(?i)not a policy snapshot')
        self.assertRegex(body, r'(?i)verify')
        self.assertRegex(read('compliance-review'),
                         r'(?i)verify .{0,40}(current )?polic')

        # The disclaimer alone is not enough. A checklist can carry "not a policy
        # snapshot" at the top and still assert, in a bullet, that every platform
        # enforces a rule - which is the misleading half, and the half a reader
        # acts on. Measured: the file shipped exactly that until this check.
        universal = re.compile(
            r'(?i)(every major (ad )?platform|all major platforms|'
            r'enforced by (every|all)|the most common (quiet )?rejection|'
            r'always rejected|universally (enforced|prohibited))')
        for path, label in ((ref, 'platform-policy-checkpoints.md'),
                            (os.path.join(ROOT, 'compliance-review', 'SKILL.md'),
                             'compliance-review')):
            with self.subTest(document=label):
                with open(path, encoding='utf-8') as fh:
                    hits = universal.findall(fh.read())
                self.assertEqual(
                    [], hits,
                    f'{label}: asserts current platform policy as settled {hits}. '
                    f'Name the risk category and say where to check it instead.')

    def test_humanizer_protects_meaning(self):
        # The stated failure mode of a humanizer is weakening true, strong copy.
        body = read('humanizer')
        self.assertRegex(body, r'(?i)do not make strong copy casual')
        self.assertRegex(body, r'(?i)## Never add')


class TestStructuralContract(unittest.TestCase):
    def test_every_skill_has_all_contract_sections(self):
        for name in FAMILY:
            body = read(name)
            for label, pattern in REQUIRED_SECTIONS:
                with self.subTest(skill=name, section=label):
                    self.assertRegex(body, pattern,
                                     f'{name}: missing "{label}" section')

    def test_handoffs_reference_skills_that_exist(self):
        # A dangling handoff routes nowhere while reading as authoritative.
        on_disk = {d for d in os.listdir(ROOT)
                   if os.path.isdir(os.path.join(ROOT, d)) and not d.startswith('.')}
        referenced = re.compile(r'`([a-z][a-z0-9-]{2,})`')
        # Words in backticks that are prose or file references, not skill names.
        ignore = {'fact-provenance.md', 'copy-brief.md'}
        for name in FAMILY:
            with self.subTest(skill=name):
                section = read(name).split('## Handoffs', 1)
                self.assertEqual(2, len(section), f'{name}: no Handoffs section')
                tail = section[1]
                for token in referenced.findall(tail):
                    if token in ignore or '.' in token:
                        continue
                    self.assertIn(token, on_disk,
                                  f'{name}: handoff names "{token}", which is not a skill')

    def test_copy_os_carries_both_shared_contracts(self):
        for ref in ('copy-brief.md', 'fact-provenance.md'):
            with self.subTest(reference=ref):
                self.assertTrue(
                    os.path.isfile(os.path.join(ROOT, 'copy-os', 'references', ref)))

    def test_copy_os_documents_precedence_local_over_global(self):
        body = read('copy-os')
        self.assertIn('TASK / CAMPAIGN INSTRUCTIONS', body)
        self.assertIn('GLOBAL METHODOLOGY', body)
        # Local must be listed above global, or the ordering claim is inverted.
        self.assertLess(body.index('TASK / CAMPAIGN INSTRUCTIONS'),
                        body.index('GLOBAL METHODOLOGY'))

    def test_precedence_ladder_does_not_outrank_permission_or_proof(self):
        """The ladder orders judgment; permissions and substantiation are floors.

        Found by a fixture run, not by inspection: the first version of the
        ladder put TASK above REPOSITORY MARKETING KNOWLEDGE with no carve-out,
        which is where a forbidden-claims list lives. Read literally, "add
        urgency" in a prompt then outranked a repo rule reading "we never use
        scarcity" - the exact override the family exists to refuse. Both the
        skill and the doc claimed the opposite in prose elsewhere.
        """
        for path, label in ((os.path.join(ROOT, 'copy-os', 'SKILL.md'), 'copy-os'),
                            (os.path.join(ROOT, 'docs', 'copy-os.md'), 'docs/copy-os.md')):
            with self.subTest(document=label):
                with open(path, encoding='utf-8') as fh:
                    body = fh.read()
                self.assertRegex(
                    body, r'(?i)(floors?, not (a )?level|not order.{0,30}permission'
                          r'|orders? judgment, not permission)',
                    f'{label}: precedence no longer carves out permissions')
                self.assertRegex(
                    body, r'(?i)not a grant of permission',
                    f'{label}: lost the rule that a task instruction cannot grant '
                    f'a permission the business withheld')

    def test_boundaries_against_adjacent_skills_are_stated(self):
        # Each of these pairs collides on trigger words; the non-trigger section
        # is the only thing separating them.
        for skill, neighbour in (('ad-copy', 'ads-creative'),
                                 ('landing-page-copy', 'ads-landing'),
                                 ('email-copy', 'email-ops'),
                                 ('social-copy', 'content-engine'),
                                 ('humanizer', 'brand-voice'),
                                 ('direct-response-copy', 'article-writing')):
            with self.subTest(skill=skill, neighbour=neighbour):
                body = read(skill)
                head = body.split('## Inputs required')[0]
                self.assertIn(neighbour, head,
                              f'{skill}: does not disambiguate itself from {neighbour}')


class TestManifestGovernance(unittest.TestCase):
    def test_every_family_member_is_declared(self):
        entries = manifest_entries()
        missing = [n for n in FAMILY if n not in entries]
        self.assertEqual([], missing, f'undeclared, so ungoverned: {missing}')

    def test_declared_hash_matches_the_source_bytes(self):
        entries = manifest_entries()
        for name in FAMILY:
            with self.subTest(skill=name):
                path = os.path.join(ROOT, name, 'SKILL.md')
                with open(path, 'rb') as fh:
                    actual = hashlib.sha256(fh.read()).hexdigest()
                self.assertEqual(entries[name]['expected_sha256'], actual)

    def test_family_deploys_somewhere(self):
        # A skill declared with no target is exposed nowhere and silently absent.
        entries = manifest_entries()
        for name in FAMILY:
            with self.subTest(skill=name):
                self.assertTrue(entries[name]['targets'],
                                f'{name}: declared with no runtime target')
                self.assertIn(entries[name]['status'], ('active', 'on-demand'))

    def test_family_is_grouped(self):
        entries = manifest_entries()
        for name in FAMILY:
            with self.subTest(skill=name):
                self.assertEqual('copy-os', entries[name]['family'])


if __name__ == '__main__':
    unittest.main()
