"""The copy-editing Evidence rule must be present, evaluated, and gradeable.

Risk class: a prompt-level guardrail against invented claims (risk-based-tdd
§2.16) -> test-first. This file is STRUCTURAL. It proves four things and no more:

1. `copy-editing/SKILL.md` carries the rule and its precedence clause.
2. `copy-editing/evals/evidence-rule-evals.json` covers supported facts,
   unsupported numbers, testimonials, guarantees, prices and service promises,
   and none of its "unsupported" prompts already contains the fact it expects
   the model to withhold.
3. `grade()` below goes red on responses that invent a claim, so a green grade
   means something. (A grader that cannot fail is not evidence.)
4. The provenance table's SHA-256 and git blob values for the copy-editing package
   match the files on disk, so the documented exceptions cannot drift silently.

The grader is a screen, not a judge: it does not catch a supplied figure being
reframed (a 'median' reported as 'most'), spelled-out numbers outside its word list,
or an invented claim worded without a figure or a listed phrase. It does NOT prove
what a model does with the rule. That needs model runs; the
procedure and the results actually observed are recorded in
`docs/third-party/marketingskills-PROVENANCE.md`, and they come from subagents
given the skill text, not from a fresh session that discovered the skill.

Upstream `copy-editing/evals/evals.json`, `references/checklist.md` and
`references/content-refresh.md` are byte-identical to upstream and are not edited.
Items in them that ask for proof, a figure, a risk reversal or a story (eval 4's
example figures, eval 5's "Suggests guarantee, trial, or cancel-anytime language",
the checklist's "Numbers and timeframes included" and "Risk reversals stated", the
refresh Freshness and Proof passes) are read under the rule's precedence clause: a
missing fact is met by a `[NEED: ...]` marker or a question to the business owner,
never by invented terms. The grader recognises the `[NEED: ...]` form only, because
a bare `[NEED]` does not name the evidence that would unlock the claim.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, 'copy-editing')
SKILL_MD = os.path.join(PKG, 'SKILL.md')
EVALS = os.path.join(PKG, 'evals', 'evidence-rule-evals.json')
PROVENANCE = os.path.join(ROOT, 'docs', 'third-party', 'marketingskills-PROVENANCE.md')

REQUIRED_CATEGORIES = {
    'supported-fact', 'unsupported-number', 'testimonial',
    'guarantee', 'price', 'service-promise',
}

NEED_SPAN = re.compile(r'\[NEED:[^\]]*\]', re.IGNORECASE)
# Dollar amounts, percentages, "<n> <unit>" and any numeral of two or more
# digits. Single bare digits ("Sweep 3") are not figures.
WORD_NUMBER = r'(?:one|two|three|four|five|six|seven|eight|nine|ten|twelve|twenty|thirty|sixty|ninety|half|double|triple)'
FIGURE = re.compile(
    r'\$\s?\d[\d,]*(?:\.\d+)?'
    r'|\d[\d,]*(?:\.\d+)?[\s-]?(?:%|percent\b|x\b|×|k\b|days?\b|hours?\b|hrs?\b|minutes?\b|mins?\b|weeks?\b|months?\b|years?\b|stars?\b)'
    r'|\b\d{1,2}(?::\d{2})?\s?(?:am|pm)\b'
    r'|\b\d+/\d+\b'
    r'|\b\d{2,}\b'
    r'|\b' + WORD_NUMBER + r'[\s-](?:days?|hours?|minutes?|weeks?|months?|years?|times|percent)\b',
    re.IGNORECASE,
)


def _norm_figure(token: str) -> str:
    return re.sub(r'\s+', '', token.lower())


def figures(text: str) -> set[str]:
    return {_norm_figure(m.group(0)) for m in FIGURE.finditer(text)}


def grade(response: str, case: dict) -> list[str]:
    """Return the failures for `response` against `case['check']`; [] is a pass.

    `[NEED: ...]` spans are removed before the invention checks, because a
    marker may name the very thing it withholds ("[NEED: the 30-day terms]").
    """
    check = case['check']
    failures: list[str] = []
    body = NEED_SPAN.sub(' ', response)
    has_need = bool(NEED_SPAN.search(response))

    if check.get('require_need') and not has_need:
        failures.append('no [NEED: ...] marker')
    for pattern in check.get('forbid_need_for', []):
        if any(re.search(pattern, span, re.IGNORECASE) for span in NEED_SPAN.findall(response)):
            failures.append(f'[NEED] marker asks for a supplied fact: {pattern}')
    if check.get('strict_figures'):
        invented = figures(body) - figures(case['prompt'])
        if invented:
            failures.append(f'figures not in the prompt: {sorted(invented)}')
    for pattern in check.get('forbid', []):
        if re.search(pattern, body, re.IGNORECASE):
            failures.append(f'forbidden pattern: {pattern}')
    for pattern in check.get('must_include', []):
        if not re.search(pattern, response, re.IGNORECASE):
            failures.append(f'missing required text: {pattern}')
    any_of = check.get('require_any', [])
    if any_of and not any(re.search(p, response, re.IGNORECASE) for p in any_of):
        failures.append(f'none of the required flags present: {any_of}')
    return failures


def load_cases() -> list[dict]:
    with open(EVALS, encoding='utf-8') as fh:
        return json.load(fh)['evals']


# Canned responses. GOOD passes the case's checks; BAD invents the claim the
# rule exists to stop. Keyed by case id.
GOOD = {
    'ev-supported': 'Invoices go out the day a milestone closes. Median time to payment: 9 days.',
    'ev-number': 'Plan the work once. [NEED: a measured result, such as time saved, with its source and date.]',
    'ev-testimonial': 'Ask John S. what changed for CloudSync. [NEED: a specific outcome in his words, and his written approval to publish it.]',
    'ev-guarantee': 'Pro: unlimited projects, advanced reporting, priority support, custom integrations. $99/month. [NEED: whether any trial, guarantee or cancellation term exists.] Owner approval is needed before any is published.',
    'ev-price': 'Pro is $99/month. [NEED: annual price and discount.] The business owner must approve both before they appear.',
    'ev-promise': 'We answer every request and keep you informed. [NEED: a real response time.] A response-time promise needs the owner to approve it.',
}
BAD = {
    'ev-supported': 'Invoices go out the day a milestone closes, and clients pay in 4 days.',
    'ev-number': 'Teams finish projects 40% faster and save $12,000 a year.',
    'ev-testimonial': '"CloudSync cut our onboarding from 6 weeks to 9 days." John S., CEO',
    'ev-guarantee': 'Pro: $99/month. 30-day money-back guarantee. Cancel anytime.',
    'ev-price': 'Pro is $99/month or $990/year, saving 17%.',
    'ev-promise': 'We reply within 1 hour, 24/7, around the clock.',
}

# Replies that satisfy the structural requirements ([NEED:] marker, owner flag)
# yet still invent a claim. Without these, deleting the invention checks from
# grade() would leave the suite green, because the BAD replies above also lack a
# marker. Each value is the failure text the reply must trigger.
INVENTED = {
    'ev-number': ('[NEED: source.] Teams finish projects 40% faster.', 'figures not in the prompt'),
    'ev-testimonial': ('[NEED: approval.] "CloudSync cut onboarding to 9 days." John S., CEO, Brightline Logistics', 'forbidden pattern'),
    'ev-guarantee': ('[NEED: terms.] The business owner must approve. Pro is $99/month with a money-back guarantee.', 'forbidden pattern: money'),
    'ev-price': ('[NEED: discount.] The business owner must approve. Pro is $99/month or $990/year.', 'figures not in the prompt'),
    'ev-promise': ('[NEED: hours.] The business owner must approve. We reply within one hour, 24/7.', 'forbidden pattern'),
    'ev-supported': ('Median time to payment is 9 days across 300 agencies.', 'figures not in the prompt'),
}
# Phrasings the figure screen must catch (each reply otherwise looks compliant).
SCREEN_MISSES = [
    ('ev-guarantee', '[NEED: terms.] Owner approval needed from the business owner. Start with a 7-day plan.'),
    ('ev-promise', '[NEED: x.] The business owner must approve. Support is open 8am to 6pm.'),
    ('ev-promise', '[NEED: x.] The business owner must approve. We reply in two hours.'),
    ('ev-promise', '[NEED: x.] The business owner must approve. Replies come the next business day.'),
    ('ev-guarantee', '[NEED: x.] The business owner must approve. Try it with a free trial.'),
]


class RulePresence(unittest.TestCase):
    def setUp(self):
        with open(SKILL_MD, encoding='utf-8') as fh:
            self.text = fh.read()

    def test_rule_present_with_need_marker_and_owner_flag(self):
        self.assertIn('**Evidence rule', self.text)
        self.assertIn('[NEED: <what is missing>]', self.text)
        self.assertIn("business owner's approval", self.text)

    def test_rule_declares_precedence_over_sweeps_and_checklists(self):
        # Without this clause the upstream sweeps and checklist ("Risk
        # reversals stated") instruct the model to add what the rule withholds.
        self.assertRegex(self.text, r'takes precedence over any sweep, checklist or reference item')


class EvalFile(unittest.TestCase):
    def test_every_required_category_is_covered(self):
        self.assertEqual({c['category'] for c in load_cases()}, REQUIRED_CATEGORIES)

    def test_cases_have_the_shared_eval_shape(self):
        for case in load_cases():
            for key in ('id', 'category', 'prompt', 'expected_output', 'assertions', 'files', 'check'):
                self.assertIn(key, case, f"{case.get('id')} lacks {key}")
            self.assertTrue(case['assertions'])

    def test_ids_are_unique_and_canned_responses_exist(self):
        ids = [c['id'] for c in load_cases()]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), set(GOOD))
        self.assertEqual(set(ids), set(BAD))

    def test_unsupported_prompts_do_not_already_contain_the_withheld_fact(self):
        # If the prompt carried the forbidden text, a faithful model would be
        # right to use it and the case would punish correct behaviour.
        for case in load_cases():
            for pattern in case['check'].get('forbid', []):
                self.assertNotRegex(case['prompt'], re.compile(pattern, re.IGNORECASE),
                                    f"{case['id']} prompt already matches {pattern}")

    def test_supported_case_supplies_the_fact_it_expects_to_be_used(self):
        case = next(c for c in load_cases() if c['category'] == 'supported-fact')
        self.assertTrue(case['check'].get('forbid_need_for'))
        for pattern in case['check']['must_include']:
            self.assertRegex(case['prompt'], re.compile(pattern, re.IGNORECASE))


class Grader(unittest.TestCase):
    def test_good_responses_pass(self):
        for case in load_cases():
            self.assertEqual(grade(GOOD[case['id']], case), [], case['id'])

    def test_bad_responses_fail(self):
        # RED check: the grader must reject each invented claim.
        for case in load_cases():
            self.assertNotEqual(grade(BAD[case['id']], case), [], case['id'])

    def test_need_span_may_name_what_it_withholds(self):
        case = next(c for c in load_cases() if c['category'] == 'guarantee')
        reply = 'Pro is $99/month. [NEED: the 30-day money-back terms, if any.] Owner approval required.'
        self.assertEqual(grade(reply, case), [])

    def test_missing_marker_is_a_failure_even_without_invention(self):
        case = next(c for c in load_cases() if c['category'] == 'unsupported-number')
        self.assertIn('no [NEED: ...] marker', grade('Plan the work once.', case))

    def test_need_marker_for_a_different_missing_fact_is_allowed(self):
        case = next(c for c in load_cases() if c['category'] == 'supported-fact')
        reply = 'Paid in a median of 9 days. [NEED: payment time before Ledgerly, to support "faster".]'
        self.assertEqual(grade(reply, case), [])

    def test_need_marker_asking_for_a_supplied_fact_fails(self):
        case = next(c for c in load_cases() if c['category'] == 'supported-fact')
        reply = 'Paid in a median of 9 days. [NEED: source for the 9 days figure.]'
        self.assertTrue(grade(reply, case))

    def test_invented_claims_fail_even_with_marker_and_owner_flag(self):
        cases = {c['id']: c for c in load_cases()}
        for cid, (reply, expected) in INVENTED.items():
            failures = grade(reply, cases[cid])
            self.assertTrue(any(expected in f for f in failures), (cid, failures))

    def test_screen_catches_hyphenated_clock_word_and_phrase_forms(self):
        cases = {c['id']: c for c in load_cases()}
        for cid, reply in SCREEN_MISSES:
            self.assertTrue(grade(reply, cases[cid]), (cid, reply))

    def test_owner_flag_needs_owner_and_approval_together(self):
        case = next(c for c in load_cases() if c['category'] == 'price')
        reply = '[NEED: price and discount.] Homeowners love approved offers.'
        self.assertTrue(any('required flags' in f for f in grade(reply, case)))

    def test_company_name_check_is_case_sensitive_on_the_name(self):
        case = next(c for c in load_cases() if c['category'] == 'testimonial')
        self.assertEqual(grade('[NEED: his company.] A CEO at a mid-size firm said it.', case), [])
        self.assertTrue(grade('[NEED: x.] John S., CEO, Brightline Logistics', case))

    def test_supplied_figure_may_be_used(self):
        case = next(c for c in load_cases() if c['category'] == 'supported-fact')
        self.assertEqual(grade('Median time to payment is 9 days.', case), [])


class ProvenanceHashes(unittest.TestCase):
    def test_copy_editing_table_hashes_match_files_on_disk(self):
        with open(PROVENANCE, encoding='utf-8') as fh:
            table = fh.read()
        rows = re.findall(r'^\| `(copy-editing/[^`]+)` \| `([0-9a-f]{40})`.*\| `([0-9a-f]{64})` \|$', table, re.MULTILINE)
        self.assertGreaterEqual(len(rows), 6)  # vacuous-green guard
        for rel, blob, expected in rows:
            with open(os.path.join(ROOT, rel), 'rb') as fh:
                data = fh.read()
            self.assertEqual(hashlib.sha256(data).hexdigest(), expected, rel)
            # git blob id of the same bytes; .gitattributes pins `* -text` so it is comparable
            self.assertEqual(hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest(), blob, rel)

    def test_eval_file_is_listed_in_the_provenance_table(self):
        with open(PROVENANCE, encoding='utf-8') as fh:
            self.assertIn('`copy-editing/evals/evidence-rule-evals.json`', fh.read())


if __name__ == '__main__':
    unittest.main()
