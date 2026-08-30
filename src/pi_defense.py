import re

BLOCKLIST_PATTERNS = [
    r"ignore (all|any|the)? ?(previous|prior|above|earlier) instructions",
    r"disregard (all|any|the)? ?(previous|prior|above|earlier) (instructions|prompt|rules)",
    r"forget (all|everything|your instructions)",
    r"new instructions?\s*:",
    r"important message\s*:",
    r"\btodo\s*:",
    r"system\s*:",
    r"assistant\s*:",
    r"you are now",
    r"act as (a|an)\b",
    r"pretend (to be|you are)",
    r"reveal (your|the) (system )?prompt",
    r"print the following",
    r"output (the following|exactly)",
    r"do not (summarize|mention|include)",
    r"stop (summarizing|following) (the )?(above|previous) (rules|instructions)",
    r"</?(system|instructions?|prompt)>",
    r"\[/?(system|instructions?|prompt)\]",
    r"#{2,}",
    r"override",
    r"jailbreak",
]
COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in BLOCKLIST_PATTERNS]

DELIM_OPEN = "<<<REVIEW_DATA_START>>>"
DELIM_CLOSE = "<<<REVIEW_DATA_END>>>"


DEFENDED_SUMMARY_PROMPT = """{open_tag}
{reviews_text}
{close_tag}"""

OUTPUT_LEAK_PATTERNS = [
    r"system prompt", r"ignore previous", r"disregard prior",
    r"as an AI language model", r"curable illness|cured my illness",
    r"APPROVED ONLY", r"new instructions?:",
]


def rule_based_filter(text: str):
    if not isinstance(text, str):
        return False, []
    matched = [p.pattern for p in COMPILED_PATTERNS if p.search(text)]
    return (len(matched) > 0), matched


def sanitize_review(text: str):
    is_flagged, matched = rule_based_filter(text)
    if is_flagged:
        return False, None, matched
    return True, text, []


def format_reviews_delimited(review_chunk):
    return "\n".join(f"[REVIEW] {r} [/REVIEW]" for r in review_chunk)


def build_defended_prompt(review_chunk):
    reviews_text = format_reviews_delimited(review_chunk)
    return DEFENDED_SUMMARY_PROMPT.format(
        open_tag=DELIM_OPEN, close_tag=DELIM_CLOSE, reviews_text=reviews_text
    )


def defend_and_build_prompt(review_chunk, log_blocked=True):
    kept_reviews = []
    blocked_log = []
    for review in review_chunk:
        keep, cleaned, matched = sanitize_review(review)
        if keep:
            kept_reviews.append(cleaned)
        else:
            blocked_log.append({"review": review, "matched_patterns": matched})
    if log_blocked and blocked_log:
        print(f"Blocked {len(blocked_log)}/{len(review_chunk)} reviews in this chunk as likely injections.")
    prompt = build_defended_prompt(kept_reviews)
    return prompt, kept_reviews, blocked_log


def verify_summary_safety(summary_text, log_warning=True):
    if not summary_text or not isinstance(summary_text, str):
        return summary_text, True
    for pattern in OUTPUT_LEAK_PATTERNS:
        if re.search(pattern, summary_text, re.IGNORECASE):
            if log_warning:
                print(f"[SECURITY WARNING] Output moderation flagged suspicious text matching pattern: '{pattern}'")
            return "[SECURITY WARNING: Generated summary was flagged by output moderation and sanitized.]", False
    return summary_text, True